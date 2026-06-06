# PostgreSQL - VACUUM Eager Scan

Created by: Mr Dk.

Co-authored by: Claude Opus 4.6

2026 / 06 / 05 19:00

Hangzhou, Zhejiang, China

---

## 背景

PostgreSQL 的 [VACUUM](./PostgreSQL%20VACUUM.md) 机制负责回收死亡元组、冻结旧事务 ID、维护 Visibility Map。其中，冻结（freeze）是防止事务 ID 回卷的关键操作。然而，冻结机制存在一个长期困扰用户的性能问题：aggressive vacuum I/O 风暴。

生产环境中常见这样的场景：一个数据库平稳运行了几周甚至几个月，监控指标一切正常。某天凌晨，autovacuum 突然触发了一次 aggressive vacuum，磁盘 I/O 瞬间飙升，导致前台查询的延迟出现明显毛刺甚至超时。日志显示某张大表的事务 ID 老化到了阈值，触发了一次全表级别的冻结扫描。

这不是偶发现象，而是 PostgreSQL MVCC 冻结机制的结构性问题。根源在于日常的 normal vacuum 只关心回收死亡元组的空间，顺手把页面标记为 all-visible，但并不急着冻结页面上元组的事务 ID。于是，表中会静默积累大量 "可见但未冻结" 的页面。这些页面对 normal vacuum 来说不再有工作需要做了，因此是可以被跳过的。然而一旦表的冻结水位线老化到阈值，aggressive vacuum 被触发，它的所有未冻结页面都需要被扫描一遍。更糟糕的是，这些页面可能长期不被访问，早已从 buffer pool 甚至 OS page cache 中被淘汰，扫描它们意味着大量的冷读 I/O，甚至可能冲击到前台业务。

PostgreSQL 18 引入了 eager scan 机制来解决这个问题。核心思路是：在每次 normal vacuum 中，"顺手" 扫描一部分 all-visible 但未 all-frozen 的页面并尝试冻结它们，将 aggressive vacuum 的冻结负担分摊到多次 normal vacuum 中。这个设计最初由核心开发者 Robert Haas 提出，经过 Andres Freund、Tomas Vondra 和 Melanie Plageman 的改进完善，最终由 Melanie Plageman 提交：

```
commit 052026c9b903380b428a4c9ba2ec90726db81288
Author: Melanie Plageman <melanieplageman@gmail.com>
Date:   Tue Feb 11 13:52:19 2025 -0500

    Eagerly scan all-visible pages to amortize aggressive vacuum

    Aggressive vacuums must scan every unfrozen tuple in order to advance
    the relfrozenxid/relminmxid. Because data is often vacuumed before it is
    old enough to require freezing, relations may build up a large backlog
    of pages that are set all-visible but not all-frozen in the visibility
    map. When an aggressive vacuum is triggered, all of these pages must be
    scanned. These pages have often been evicted from shared buffers and
    even from the kernel buffer cache. Thus, aggressive vacuums often incur
    large amounts of extra I/O at the expense of foreground workloads.

    To amortize the cost of aggressive vacuums, eagerly scan some
    all-visible but not all-frozen pages during normal vacuums.

    All-visible pages that are eagerly scanned and set all-frozen in the
    visibility map are counted as successful eager freezes and those not
    frozen are counted as failed eager freezes.

    If too many eager scans fail in a row, eager scanning is temporarily
    suspended until a later portion of the relation. The number of failures
    tolerated is configurable globally and per table.

    To effectively amortize aggressive vacuums, we cap the number of
    successes as well. Capping eager freeze successes also limits the amount
    of potentially wasted work if these pages are modified again before the
    next aggressive vacuum. Once we reach the maximum number of blocks
    successfully eager frozen, eager scanning is disabled for the remainder
    of the vacuum of the relation.

    Original design idea from Robert Haas, with enhancements from
    Andres Freund, Tomas Vondra, and me

    Reviewed-by: Robert Haas <robertmhaas@gmail.com>
    Reviewed-by: Masahiko Sawada <sawada.mshk@gmail.com>
    Reviewed-by: Andres Freund <andres@anarazel.de>
    Reviewed-by: Robert Treat <rob@xzilla.net>
    Reviewed-by: Bilal Yavuz <byavuz81@gmail.com>
    Discussion: https://postgr.es/m/flat/CAAKRu_ZF_KCzZuOrPrOqjGVe8iRVWEAJSpzMgRQs%3D5-v84cXUg%40mail.gmail.com
```

本文先回顾 vacuum 中的各个阈值，再分析 eager scan 的设计思路和配额机制。

## XID 阈值体系

要理解 eager scan 的触发条件，需要先理清 vacuum 中几个关键的 XID 阈值。下图展示了 XID 时间线上各阈值的相对位置，从老到新依次为：

```
XID timeline (old → new)

 failsafe  anti-wraparound  aggressiveXIDCutoff  FreezeLimit  OldestXmin  NextXID
     |            |                  |                 |            |          |
     v            v                  v                 v            v          v
─────┼────────────┼──────────────────┼─────────────────┼────────────┼──────────┼──→
     |            |                  |                 |            |          |
     |            |                  |                 |<-- freeze_min_age --->|
     |            |                  |                 |                       |
     |            |                  |<---- freeze_table_age (default 150M)--->|
     |            |                                                            |
     |            |<-------- autovacuum_freeze_max_age (default 200M) -------->|
     |                                                                         |
     |<------------ failsafe_age (default 1.6B, >= max_age * 1.05) ----------->|
```

这些 XID 阈值的比较对象是 `relfrozenxid`——这是记录在 `pg_class` 中的表级属性，保证该表的元组头部中不存在任何小于该值的未冻结事务 ID。表的 `relfrozenxid` 与最新事务 ID 的距离可以理解为表的 "冻结年龄"。

各阈值的具体含义：

- NextXID：下一个将要分配的事务 ID，是时间线的"当前位置"。
- OldestXmin：vacuum 的回收边界。只有 XID 小于此值的已提交事务所删除的元组，才能被 vacuum 安全回收——因为不会再有任何活跃事务需要看到它们。
- FreezeLimit：vacuum 的冻结边界。当元组头部的事务 ID（xmin、xmax 等）小于此值时，vacuum 扫描到该元组会将其冻结。由 `vacuum_freeze_min_age`（默认 5000 万）控制，意味着元组至少要存活 5000 万个事务之后才有资格被冻结。
- aggressiveXIDCutoff：aggressive vacuum 的触发线。当表的冻结年龄超过此值时，vacuum 进入 aggressive 模式，必须扫描所有未冻结页面来推进 `relfrozenxid`。由 `vacuum_freeze_table_age`（默认 1.5 亿）控制，但会被限制在 `autovacuum_freeze_max_age * 0.95` 以内，以确保用户手动调度的 vacuum 有机会在 anti-wraparound autovacuum 介入之前完成冻结工作。
- Anti-wraparound 阈值：autovacuum 强制介入的触发线。当表的冻结年龄超过此值时，autovacuum 会强制对该表发起 vacuum，无论表上有多少死亡元组。由 `autovacuum_freeze_max_age`（默认 2 亿）控制。这是防止 XID 回卷的最后一道常规防线。
- Failsafe 阈值：XID 回卷灾难前的最后兜底机制。当表的冻结年龄超过此值时，vacuum 进入 failsafe 模式——跳过索引清理，全力推进冻结。由 `vacuum_failsafe_age`（默认 16 亿）控制，但不会低于 `autovacuum_freeze_max_age * 1.05`。

MultiXact 有一套类似的阈值体系（`OldestMxact`、`MultiXactCutoff`、`relminmxid`），逻辑对称，不再赘述。

## Normal VACUUM 与 Aggressive VACUUM

Normal vacuum 和 aggressive vacuum 走的是同一套代码路径，但目标不同。这导致两者对 all-visible 页面的处理策略不同：

- Normal vacuum 利用 Visibility Map 跳过 all-visible 的页面，因为这些页面上没有死亡元组需要清理。Normal vacuum 的目标是回收空间，冻结只是 "顺手做" 的事情：在回收某个页面的空间时，如果恰好上面的元组足够老，就冻结它们。
- Aggressive vacuum 不能跳过 all-visible 但未 all-frozen 的页面，它的目标是推进 `relfrozenxid`。而要安全推进这个值，就必须确保表中所有旧元组都被冻结。只有 all-frozen 的页面才能被 aggressive vacuum 跳过。

Aggressive vacuum 一旦触发就需要扫描所有不是 all-frozen 的页面。对于一张长期被 normal vacuum 维护的大表，可能有大量页面处于 all-visible 但未 all-frozen 的状态——这些页面上的元组早就不再被修改，但因为 "不够老"，之前的 normal vacuum 扫描它们时没有做冻结。等到 aggressive vacuum 终于到来，这些页面可能已经被淘汰出 buffer pool，读取它们需要消耗大量的物理 I/O。

这就是 aggressive vacuum 问题的本质：冻结工作长期推迟，最终集中爆发。

## Eager Scan 的设计

Eager scan 的核心思想是，在 normal vacuum 中，主动扫描一部分原本可以跳过的 all-visible 但未 all-frozen 页面，尝试冻结它们。如果冻结成功，那么下一次 aggressive vacuum 就可以跳过它们。相当于把 aggressive vacuum 的冻结负担，分摊到了多次 normal vacuum 中。

Eager scan 带来的收益是削平 I/O 峰值：aggressive vacuum 需要扫描的页面数量减少，I/O 负载更平滑。

但 eager scan 不是免费的午餐，它在 normal vacuum 中引入了额外的 I/O 和 CPU 开销。更重要的是：如果一个页面被 eager scan 冻结后，在下一次 aggressive vacuum 之前又被修改了（比如有新的 UPDATE），那么这个页面的 all-frozen 状态会被清除，冻结工作等于白做了。这种场景下 eager scan 的开销变成了纯粹的浪费。

因此，eager scan 的设计需要在两个方向上做限制：

1. 限制成功次数：不要一次冻结太多页面。Eager scan 的初衷是为了分摊，而不是包揽。另外冻结太多页面，浪费的概率也会上升。
2. 限制失败次数：如果某个区域的页面因为元组太新而无法冻结，继续在这个区域尝试大概率也是浪费，应该及时止损。

## 配额设计

Eager scan 的配额系统用两个独立的计数器分别限制成功和失败的次数，并且两者的作用域不同。这一选择充分体现了工程上的妥协艺术。

### 成功上限：全局配额

成功上限是单次 vacuum 内对整张表的全局配额。这是为了避免一次 normal vacuum 就可能把所有能冻结的页面都处理完，那和 aggressive vacuum 就没有区别了。计算公式为：

```c
visibilitymap_count(vacrel->rel, &allvisible, &allfrozen);

vacrel->eager_scan_remaining_successes =
    (BlockNumber) (MAX_EAGER_FREEZE_SUCCESS_RATE *
                   (allvisible - allfrozen));
```

`MAX_EAGER_FREEZE_SUCCESS_RATE` 硬编码为 0.2（20%）。也就是说，一次 normal vacuum 最多冻结表中 all-visible 但未 all-frozen 页面数的 20%。每成功冻结一个页面，计数器减一。当计数器归零时，本次 vacuum 的 eager scan 永久关闭：

```c
if (vm_page_frozen)
{
    if (vacrel->eager_scan_remaining_successes > 0)
        vacrel->eager_scan_remaining_successes--;

    if (vacrel->eager_scan_remaining_successes == 0)
    {
        /*
         * If we hit our success cap, permanently disable eager
         * scanning by setting the other eager scan management
         * fields to their disabled values.
         */
        vacrel->eager_scan_remaining_fails = 0;
        vacrel->next_eager_scan_region_start = InvalidBlockNumber;
        vacrel->eager_scan_max_fails_per_region = 0;
    }
}
else if (vacrel->eager_scan_remaining_fails > 0)
    vacrel->eager_scan_remaining_fails--;
```

### 失败上限：按区域配额

与成功上限不同，失败上限采用按区域的配额。表被划分为多个大小为 `EAGER_SCAN_REGION_SIZE`（4096 块，即 32 MB）的区域，每个区域有独立的失败计数器。

这是因为表中不同区域的数据年龄往往相近——如果某个区域的元组太新无法冻结，那么这个区域内的其他页面大概率也是如此，继续尝试只会浪费 I/O。但表的其他区域可能包含年龄更老的数据，还是值得去尝试的。

```c
vacrel->eager_scan_max_fails_per_region =
    params->max_eager_freeze_failure_rate *
    EAGER_SCAN_REGION_SIZE;
```

`vacuum_max_eager_freeze_failure_rate` 是一个 GUC 参数，默认 0.03（3%），也可以通过表级存储参数覆盖。以默认值计算，每个 4096 块的区域中允许最多 122 次失败（4096 × 0.03 ≈ 122）。当 eager scan 在某个区域的失败次数耗尽时，eager scan 在该区域内被临时挂起——`eager_scan_remaining_fails` 归零后，all-visible 但非 all-frozen 的页面会被跳过：

```c
/*
 * Normal vacuums with eager scanning enabled only skip all-visible
 * but not all-frozen pages if they have hit the failure limit for the
 * current eager scan region.
 */
if (vacrel->eager_scan_remaining_fails > 0)
{
    next_unskippable_eager_scanned = true;
    break;
}
```

进入下一个区域时，失败计数器重置，eager scan 恢复运行：

```c
if (next_unskippable_block >= vacrel->next_eager_scan_region_start)
{
    vacrel->eager_scan_remaining_fails =
        vacrel->eager_scan_max_fails_per_region;
    vacrel->next_eager_scan_region_start += EAGER_SCAN_REGION_SIZE;
}
```

### 随机起始偏移

Eager scan 的失败探索是分区域的。其中，第一个失败探索区域的结束位置是随机确定的：

```c
randseed = pg_prng_uint32(&pg_global_prng_state);
vacrel->next_eager_scan_region_start = randseed % EAGER_SCAN_REGION_SIZE;
```

这个随机偏移使得每次 vacuum 的 eager scan 区域边界都不同。如图所示：

```
Block number:
0                    4096                 8192                12288
|--------------------|--------------------|--------------------|--->



VACUUM #1 (offset = 1000):
|----|--------------------|--------------------|-----------...
0  1000                 5096                 9192

VACUUM #2 (offset = 3500):
|------------|--------------------|--------------------|-...
0          3500                 7596                 11692

VACUUM #3 (offset = 500):
|--|--------------------|--------------------|--------------...
0 500                 4596                 8692
     <--- 4096 blks --->
```

如果区域边界固定，某些还不够老的页面每次都落在某个区域的开头，每次都消耗该区域的失败配额，导致该区域后面的页面永远没有机会被尝试冻结。随机偏移能让这些页面每次落在区域内的不同位置上，因而能够让其他页面得到被尝试冻结的机会。

### 启用条件

Eager scan 不是无条件启用的。`heap_vacuum_eager_scan_setup()` 中有几个前置检查：

```c
/* If eager scanning is explicitly disabled, just return. */
if (params->max_eager_freeze_failure_rate == 0)
    return;

if (vacrel->aggressive)
    return;

if (vacrel->rel_pages < 2 * EAGER_SCAN_REGION_SIZE)
    return;

if (!oldest_unfrozen_before_cutoff)
    return;

/* If every all-visible page is frozen, eager scanning is disabled. */
if (vacrel->eager_scan_remaining_successes == 0)
    return;
```

1. 未被显式禁用：`vacuum_max_eager_freeze_failure_rate` 设为 0 时禁用。
2. 不是 aggressive vacuum：aggressive vacuum 本身就会扫描所有未冻结页面，eager scan 的概念不适用。
3. 表足够大：小于 `2 × EAGER_SCAN_REGION_SIZE`（8192 块，64 MB）的表被跳过——小表的 aggressive vacuum 本身就很快，不值得分摊。
4. 数据足够老：只有当 `relfrozenxid < FreezeLimit` 或 `relminmxid < MultiXactCutoff` 时才启用。这意味着表中确实存在已经超过冻结年龄的元组，eager scan 去扫描才有可能成功冻结。如果表中最老的元组还没到冻结年龄，eager scan 也冻结不了什么，纯属浪费。
5. 存在可冻结的页面：如果 VM 中所有 all-visible 页面都已经是 all-frozen，那么就没有工作可做了。

这些条件的组合确保 eager scan 只在 "有必要且有可能成功" 的场景下运行。

## 实现概览

Eager scan 的状态通过 `LVRelState` 中的几个字段跟踪：

```c
/*
 * next_eager_scan_region_start is the block number of the first block
 * eligible for resumed eager scanning.
 *
 * When eager scanning is permanently disabled, either initially
 * (including for aggressive vacuum) or due to hitting the success cap,
 * this is set to InvalidBlockNumber.
 */
BlockNumber next_eager_scan_region_start;

/*
 * The remaining number of blocks a normal vacuum will consider eager
 * scanning when it is successful. When eager scanning is enabled, this
 * is initialized to MAX_EAGER_FREEZE_SUCCESS_RATE of the total number
 * of all-visible but not all-frozen pages. For each eager freeze
 * success, this is decremented. Once it hits 0, eager scanning is
 * permanently disabled.
 */
BlockNumber eager_scan_remaining_successes;

/*
 * The maximum number of blocks which may be eagerly scanned and not
 * frozen before eager scanning is temporarily suspended. Calculated as
 * vacuum_max_eager_freeze_failure_rate of EAGER_SCAN_REGION_SIZE
 * blocks. It is 0 when eager scanning is disabled.
 */
BlockNumber eager_scan_max_fails_per_region;

/*
 * The number of eagerly scanned blocks vacuum failed to freeze (due to
 * age) in the current eager scan region. Vacuum resets it to
 * eager_scan_max_fails_per_region each time it enters a new region of
 * the relation. If eager_scan_remaining_fails hits 0, eager scanning
 * is suspended until the next region.
 */
BlockNumber eager_scan_remaining_fails;
```

在页面扫描循环中，`find_next_unskippable_block()` 是决定哪些页面需要被扫描的核心函数。引入 eager scan 后，它的跳过逻辑变为：

```c
for (;; next_unskippable_block++)
{
    uint8 mapbits = visibilitymap_get_status(vacrel->rel,
                                             next_unskippable_block,
                                             &next_unskippable_vmbuffer);

    /* 进入新区域时，重置失败计数器 */
    if (next_unskippable_block >= vacrel->next_eager_scan_region_start)
    {
        vacrel->eager_scan_remaining_fails =
            vacrel->eager_scan_max_fails_per_region;
        vacrel->next_eager_scan_region_start += EAGER_SCAN_REGION_SIZE;
    }

    /* 非 all-visible：必须扫描（可能有死亡元组） */
    if ((mapbits & VISIBILITYMAP_ALL_VISIBLE) == 0)
        break;

    /* ... */

    /* all-frozen：所有模式都可以安全跳过 */
    if ((mapbits & VISIBILITYMAP_ALL_FROZEN) != 0)
        continue;

    /* aggressive vacuum：必须扫描所有未冻结页面 */
    if (vacrel->aggressive)
        break;

    /* eager scan：失败配额未耗尽，不跳过 */
    /* 条件隐含成功配额也未耗尽 */
    if (vacrel->eager_scan_remaining_fails > 0)
    {
        next_unskippable_eager_scanned = true;
        break;
    }

    /* normal vacuum 默认行为：跳过 all-visible 但非 all-frozen 的页面 */
    *skipsallvis = true;
}
```

需要注意的是，如果因为锁竞争无法获取 cleanup lock，那么这个页面不算成功也不算失败，不影响配额计数。这避免了因偶发的锁冲突而错误地消耗配额。

Vacuum 结束后的日志中会记录 eager scan 的统计信息，包括 eagerly scanned 的页面数。用户可以通过这些日志判断 eager scan 是否在有效工作。

## 总结

Eager scan 的设计体现了几个重要的工程权衡，这也是系统软件设计中最精妙的部分：

- 抹平两种 vacuum 之间的代价差异：冻结事务 ID 本身是一件不可避免的工作，问题在于应该在什么时候做。Eager scan 利用 normal vacuum 已经在扫描表的时机，以较低的边际成本 "搭便车" 完成冻结——相比 aggressive vacuum 从冷存储中重新读取页面，代价小得多。
- 用配额来限制探索性工作的不确定性：eager scan 本质上是一种投机行为——扫描一个 all-visible 页面，赌它上面的元组够老可以冻结。投机这种不确定性的代价需要被约束在可控范围内，否则 normal vacuum 本身的代价会变得不可预测。配额机制为这种探索性工作设定了明确的边界：成功上限控制总工作量，失败上限控制无效尝试。
- 非对称的配额设计：成功上限是全局的，失败上限是按区域的。这不是随意的选择，而是反映了两者代价的不对称性：为了成功冻结而消耗的 I/O 与位置无关，而失败具有空间局部性，同一区域的数据年龄大概率相近，一个页面冻结不了，相邻页面大概率也不行。
- 用随机性打破周期性：区域边界的随机偏移是一种简易而有效的去相关手段——不需要记录历史状态，不需要复杂的调度逻辑，仅靠一次随机数生成就能避免多次 vacuum 之间的系统性盲区。

## 参考资料

- [PostgreSQL commit 052026c9b](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commit;h=052026c9b903380b428a4c9ba2ec90726db81288) - Eagerly scan all-visible pages to amortize aggressive vacuum
- [Mailing list discussion](https://www.postgresql.org/message-id/flat/CAAKRu_ZF_KCzZuOrPrOqjGVe8iRVWEAJSpzMgRQs%3D5-v84cXUg%40mail.gmail.com)
- [PostgreSQL Source - src/backend/access/heap/vacuumlazy.c](https://github.com/postgres/postgres/blob/master/src/backend/access/heap/vacuumlazy.c)
- [PostgreSQL Source - src/backend/commands/vacuum.c](https://github.com/postgres/postgres/blob/master/src/backend/commands/vacuum.c)
- [PostgreSQL Documentation - Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html)
