# PostgreSQL - VACUUM

Created by: Mr Dk.

Co-authored by: Claude Opus 4.6

2026 / 05 / 13 17:48

Hangzhou, Zhejiang, China

---

## 背景

PostgreSQL 使用 MVCC（多版本并发控制）来实现事务隔离。当你执行 UPDATE 时，PostgreSQL 不会原地修改元组，而是在堆中写入一个新版本，旧版本仍然保留，因为可能还有其他事务需要看到它。DELETE 也类似，只是给元组打了个"已删除"标记，并不真的释放空间。

这意味着随着 DML 的执行，表中会持续积累"死亡元组"，也就是那些对任何活跃事务都不再可见、但仍然占用磁盘空间的旧版本。如果没有机制来回收这些空间，就会出问题。PostgreSQL 用 VACUUM 来解决这个问题。

本文基于 PostgreSQL master 分支（版本 19-devel）的源码，分析 lazy VACUUM 的处理流程。

## 为什么需要 VACUUM

综合来看，VACUUM 不是一个"有空再做"的后台任务，而是 PostgreSQL 正常运行的刚性需求。autovacuum 默认开启正是基于这个考虑：让数据库自动在后台持续执行 VACUUM，避免上述问题积累到不可控的程度。

如果长期不做 VACUUM，会面临三个层面的问题：

### 表和索引膨胀

死亡元组持续占用空间，表的物理文件越来越大。顺序扫描需要读取更多的页面（其中大量是无用数据），随机 I/O 也因为数据分散而增加。索引的情况更糟：索引条目仍然指向这些死亡元组，导致索引体积膨胀，B-tree 的层数可能增加，每次索引扫描都要做更多无效的回表操作。

```
正常状态:
  表: [活跃] [活跃] [活跃] [空闲]
  索引: 3 entries → 3 valid tuples

长期不 VACUUM:
  表: [活跃] [死亡] [死亡] [活跃] [死亡] [死亡] [死亡] [活跃]
  索引: 8 entries → 其中 5 个指向死亡元组
  (顺序扫描 I/O 翻倍, 索引扫描大量无效回表)
```

这种膨胀会自我加剧：表越膨胀，VACUUM 需要扫描的页面越多，耗时越长，VACUUM 就更容易跟不上 DML 产生死亡元组的速度。

### 事务 ID 回卷

这是比膨胀严重得多的问题。PostgreSQL 使用 32 位无符号整数作为事务 ID（XID），总共约 42 亿个。XID 空间是循环使用的：PostgreSQL 把 42 亿个 XID 看作一个环，对于当前 XID，环的一半（约 20 亿）被视为"过去"，另一半被视为"未来"。可见性判断依赖这个划分：xmin 落在"过去"半边的元组可见，落在"未来"半边的元组不可见（因为从当前事务的视角看，创建它的事务"还没发生"）。问题在于：如果一个很老的元组始终没有被冻结，随着新事务不断消耗 XID，它的 xmin 终将从"过去"半边越过边界滑入"未来"半边。此时 PostgreSQL 会把这条实际存在的老数据误判为"未来事务创建的"，导致数据丢失。

VACUUM 的一个关键职责是"冻结"旧元组：将非常老的 xmin 标记为 `FrozenTransactionId`（一个特殊值，对所有事务永远可见），这样这些元组就不再参与 XID 比较。冻结后，VACUUM 可以安全地推进表的 `relfrozenxid`，即所有小于该值的 XID 都已经被冻结，可以被回收重用。

如果 `relfrozenxid` 停留不动（因为 VACUUM 没有运行或运行不完整），而新事务不断消耗 XID，最终 `relfrozenxid` 和当前 XID 之间的距离会逼近 20 亿。PostgreSQL 在距离达到约 4000 万时会开始报警，在距离达到约 100 万时会拒绝执行任何新事务（强制关库），只允许单用户模式下运行 VACUUM FREEZE。这是数据库的"紧急刹车"，宁可停服也不能让 XID 回卷导致数据损坏。

### 可见性信息失效

VACUUM 不仅回收空间，还负责维护 Visibility Map（VM）。VM 告诉 PostgreSQL 哪些页面上的所有元组对所有事务都可见（all-visible），这是 index-only scan 能否生效的前提。如果 VM 不更新，index-only scan 退化为普通 index scan（每次都要回表确认可见性），查询性能会明显下降。

## VACUUM 的五个阶段

VACUUM 的处理流程在代码中被分为五个阶段：

```c
typedef enum {
    VACUUM_ERRCB_PHASE_UNKNOWN,
    VACUUM_ERRCB_PHASE_SCAN_HEAP,      -- 阶段 I
    VACUUM_ERRCB_PHASE_VACUUM_INDEX,   -- 阶段 II
    VACUUM_ERRCB_PHASE_VACUUM_HEAP,    -- 阶段 III
    VACUUM_ERRCB_PHASE_INDEX_CLEANUP,  -- 阶段 IV
    VACUUM_ERRCB_PHASE_TRUNCATE,       -- 阶段 V
} VacErrPhase;
```

每个阶段做的事情：

- **阶段 I（SCAN_HEAP）**：从头到尾扫描堆页面，对每个页面做 prune（清理 HOT 链中的旧版本）和 freeze（冻结旧事务 ID），同时把死亡元组的 TID 收集到 TID store 中。
- **阶段 II（VACUUM_INDEX）**：扫描所有索引，删除引用死亡元组的索引条目。
- **阶段 III（VACUUM_HEAP）**：回到堆页面，将已完成索引清理的 `LP_DEAD` 标记为 `LP_UNUSED`，真正释放空间。
- **阶段 IV（INDEX_CLEANUP）**：对每个索引进行收尾清理（回收空索引页、更新统计信息等）。
- **阶段 V（TRUNCATE）**：如果表尾部有连续的空页面，截断物理文件以缩小表的磁盘占用。

这五个阶段并不是简单的线性执行。其中，阶段 I/II/III 构成一个循环：阶段 I 扫描过程中，如果收集到的死亡元组超出了单次处理的量，就会暂停扫描，先执行一轮阶段 II + III 处理已收集的部分，然后回到阶段 I 继续扫描。大多数情况下一轮就够，但对于大表可能循环多次。阶段 IV 和 V 则只在所有扫描和清理完成后执行一次。

用户执行 `VACUUM` 语句后，经过 SQL 解析和执行器的标准路径，最终进入 VACUUM 的处理逻辑。整体调用链如下：

```
standard_ProcessUtility()                          -- utility.c
  └─ ExecVacuum()                                  -- vacuum.c
       └─ vacuum()                                 -- vacuum.c
            └─ vacuum_rel()                        -- vacuum.c
                 └─ table_relation_vacuum()        -- tableam.h (inline)
                      └─ heap_vacuum_rel()         -- vacuumlazy.c
                           ├─ lazy_scan_heap()     -- 阶段 I：堆扫描
                           │    ├─ lazy_scan_new_or_empty()
                           │    ├─ lazy_scan_prune()
                           │    ├─ lazy_scan_noprune()
                           │    ├─ lazy_vacuum()   -- TID store 满时触发
                           │    │    ├─ lazy_vacuum_all_indexes()  -- 阶段 II
                           │    │    └─ lazy_vacuum_heap_rel()     -- 阶段 III
                           │    └─ lazy_cleanup_all_indexes()      -- 阶段 IV
                           └─ lazy_truncate_heap() -- 阶段 V：截断
```

对照上面的阶段划分，调用树中每个叶子函数都可以直接对应到它所属的阶段。逐层展开来看：

- `ExecVacuum` 负责解析 VACUUM 命令的各种选项（FREEZE、VERBOSE、PARALLEL 等），将它们转换为 `VacuumParams` 结构体中的标志位，然后调用 `vacuum`。
- `vacuum` 是 VACUUM 和 ANALYZE 共用的内部入口。它做了一件很重要的事情：提交当前事务，然后为每张表启动独立的事务去执行 `vacuum_rel`。这样做的目的是让每张表的 VACUUM 运行在独立事务中，一旦完成就可以立刻释放锁，不用等到所有表都处理完。
- `vacuum_rel` 是单张表 VACUUM 的核心调度。它负责获取表锁、权限检查、决定是否处理 TOAST 表等。对于 lazy VACUUM，它在这里获取 ShareUpdateExclusiveLock，这个锁级别允许其他事务正常读写表，但阻止其他 VACUUM 并发执行。锁获取后，通过 table AM 接口调用到 `heap_vacuum_rel`。
- `table_relation_vacuum` 是 table AM 的 inline wrapper。它通过函数指针调用到 heapam_handler.c 中注册的 `heap_vacuum_rel`。这一层抽象使得非 heap 类型的表（如果有的话）可以实现自己的 VACUUM 逻辑。
- `heap_vacuum_rel` 是 heap 表 VACUUM 的真正起点。它初始化各种状态（`LVRelState` 结构体）和冻结阈值，打开所有索引，然后依次调用前面提到的五个阶段对应的函数。

## 阶段 I：堆扫描

`lazy_scan_heap` 是整个 VACUUM 中最核心的函数。它从头到尾扫描整张表的每一个 heap page（可能跳过一些），对每个页面做 prune（清理 HOT 链）和 freeze（冻结旧事务 ID），同时收集死亡元组的 TID 到 TID store 中，供后续阶段使用。

### Normal VACUUM 与 Aggressive VACUUM

先区分两个概念：normal VACUUM 和 aggressive VACUUM。两者都是 lazy VACUUM，走同一套代码路径，区别在于对冻结的"积极程度"。Normal VACUUM 只关心回收死亡元组的空间，对冻结的态度是"能顺手做就做"。Aggressive VACUUM 则必须尽可能冻结所有旧元组来推进 relfrozenxid。当表的 relfrozenxid 年龄超过 `vacuum_freeze_table_age` 时，autovacuum 会自动触发 aggressive 模式。这个区别直接影响后面的页面跳过策略。

### 页面跳过策略

VACUUM 并不一定要扫描每一个页面。它利用 visibility map（VM）来判断哪些页面可以跳过。VM 为每个 heap page 维护两个 bit：all-visible（页面上所有元组对所有活跃事务可见）和 all-frozen（页面上所有元组已冻结）。

如果一个页面已经 all-visible，说明上面没有死亡元组需要清理，normal VACUUM 可以跳过它。但 aggressive VACUUM（当 `relfrozenxid` 过老时自动触发）不能跳过 all-visible 但未 all-frozen 的页面，它必须扫描这些页面来冻结旧元组。只有同时满足 all-visible 和 all-frozen 的页面才能被所有类型的 VACUUM 跳过。

为了减轻 aggressive VACUUM 的负担，normal VACUUM 引入了 eager scan 机制：在跳过 all-visible 页面时，"顺手"扫描其中一部分还未 all-frozen 的页面来尝试冻结。这样做相当于把 aggressive VACUUM 的工作分摊到了平时。Eager scan 有两个限制来控制额外开销：成功上限（最多冻结 20% 的 all-visible 非 all-frozen 页面）和失败上限（在每个 4096 块的 region 内，如果失败率超过 `vacuum_max_eager_freeze_failure_rate` 就暂停该 region 的 eager scan）。

另外还有一个针对 I/O 的优化：如果连续跳过的页面数不到 32 个（`SKIP_PAGES_THRESHOLD`），VACUUM 就不跳了，直接扫描。零散的跳跃会破坏内核的 readahead，反而不如顺序读完。

### 页面处理

在一个 heap page 内部，元组通过 line pointer（LP）数组进行索引。每个 LP 有四种状态：

- **`LP_NORMAL`**：指向一个正常的元组。
- **`LP_REDIRECT`**：HOT 链中使用的重定向指针。HOT（Heap-Only Tuple）是 PostgreSQL 的一个优化：如果 UPDATE 没有修改任何索引列，新版本元组不需要创建新的索引条目，而是通过堆内 `LP_REDIRECT` 链接到旧版本。
- **`LP_DEAD`**：元组已经对所有事务不可见，但索引中可能还有条目指向它，暂时不能释放空间。
- **`LP_UNUSED`**：完全空闲，可以被新元组复用。

`lazy_scan_heap` 使用 read stream API 批量读取页面。对于每个页面，VACUUM 首先尝试获取 cleanup lock。Cleanup lock 是一种特殊的 buffer lock，要求持有者是该 buffer 唯一的 pin holder，保证没有其他后端正在访问该页面。根据是否获取到 cleanup lock，走两条不同的路径：

- **获取到 cleanup lock → `lazy_scan_prune`**：执行完整的 prune + freeze，处理完成后收集页面中的死亡元组 TID。Prune 判断页面中哪些元组对所有活跃事务已不可见，将它们的 LP 标记为 `LP_DEAD`（对于 HOT 链的根节点，如果链中还有存活后继，则标记为 `LP_REDIRECT` 保持索引转发），然后重整页面空间回收碎片；Freeze 冻结足够老的事务 ID。
- **未获取到 cleanup lock → `lazy_scan_noprune`**：跳过 prune，只收集页面中已有的 `LP_DEAD` 条目。不过如果当前是 aggressive 模式且该页面必须被冻结，则会等待 cleanup lock，然后回到 `lazy_scan_prune` 执行完整处理。

对于 prune 后产生的 `LP_DEAD` 条目，如果表没有索引，可以直接标记为 `LP_UNUSED`（因为不存在索引条目指向它）。如果表有索引，则 `LP_DEAD` 的 TID 会被收集到 TID store 中，必须等待阶段 II 清理完索引条目后，才能在阶段 III 中标记为 `LP_UNUSED`。

### TID Store 满时的处理

VACUUM 使用 `maintenance_work_mem`（或 `autovacuum_work_mem`）限制 TID store 的内存使用。当 TID store 的内存用量超过阈值时，`lazy_scan_heap` 会暂停扫描，调用 `lazy_vacuum` 触发一轮阶段 II + III 的处理，清空 TID store 后继续扫描。

```
lazy_scan_heap 主循环:

  while (还有页面) {
      if (TID store 满了 && 已有 dead items) {
          lazy_vacuum();           // 阶段 II + III
          FreeSpaceMapVacuumRange();
      }

      buf = read_stream_next_buffer();
      // ... 处理页面 ...
  }

  // 扫描完成后，处理最后一批 dead items
  if (有 dead items)
      lazy_vacuum();               // 最后一轮阶段 II + III

  // 最终索引清理
  if (有索引 && 需要做 index cleanup)
      lazy_cleanup_all_indexes();  // 阶段 IV
```

大多数情况下，整张表的 dead items 不会超出 `maintenance_work_mem` 的限制，所以通常只需要一轮阶段 II + III。但对于大表或 `maintenance_work_mem` 设置较小的情况，可能会多次循环。

### Failsafe 机制

堆扫描过程中，VACUUM 会定期检查 `relfrozenxid` 的年龄是否接近危险阈值（`vacuum_failsafe_age`，默认 16 亿）。如果是，VACUUM 立即进入 failsafe 模式，放弃除冻结以外的一切工作：

- 跳过后续所有阶段
- 关闭 cost-based delay（不再主动让出 CPU）
- 放弃使用 buffer access strategy（允许使用全部 shared buffers 加速扫描）

这是一种"丢卒保车"的策略：牺牲空间回收，换取阶段 I 尽快完成冻结，从而在单表 VACUUM 的末尾尽早推进 `relfrozenxid`，避免事务 ID 回卷。检查频率为每扫描 4GB 数据一次（阶段 II 中则是每完成一个索引检查一次），一旦触发就不可逆转。

## 阶段 II：索引清理

当 `lazy_scan_heap` 收集到了一批 dead item TIDs，阶段 II 负责从所有索引中删除引用这些 dead items 的索引条目。

`lazy_vacuum_all_indexes` 对每个索引调用 `lazy_vacuum_one_index`，后者通过 index AM 的 `ambulkdelete` 接口执行实际的删除。对于 B-tree 索引，`ambulkdelete` 会扫描整棵索引树，用 TID store 作为过滤条件，删除匹配的索引条目。

这里有一个重要的设计：每个索引的 `ambulkdelete` 都需要扫描整个索引。所以如果 TID store 被迫多次清空重填（表很大、`maintenance_work_mem` 很小），每个索引就要被扫描多次。这也是为什么增大 `maintenance_work_mem` 能明显提升大表 VACUUM 性能。

进入阶段 II 前，会先经过 `lazy_vacuum` 函数。这个函数有一个 bypass 优化：如果 dead items 非常少，则等到未来某次 VACUUM 累积量超过阈值时再统一处理。这避免了在 HOT 优化效果好的表上，因为少量偶发的 `LP_DEAD` 而触发完整的索引扫描。该优化会让 VACUUM 跳过阶段 II 和 III，直接丢弃本轮收集的 dead item TIDs。

```
lazy_vacuum() 逻辑:

  if (不需要索引清理)
      dead_items_reset();  // 直接丢弃, 不做清理
      return;

  if (bypass 条件满足: LP_DEAD 页面很少)
      跳过索引清理, 但仍做后续的 index cleanup (阶段 IV)
  else if (lazy_vacuum_all_indexes() 成功)
      lazy_vacuum_heap_rel();  // 阶段 III
  else
      failsafe 触发, 放弃所有后续清理

  dead_items_reset();
```

如果用户指定了 `PARALLEL` 选项，阶段 II 和阶段 IV 可以并行执行，多个 worker 各自负责不同的索引。这种并行是索引级别的：每个索引的 `ambulkdelete`（阶段 II）和 `amvacuumcleanup`（阶段 IV）彼此独立，可以安全地分配给不同 worker。堆扫描（阶段 I）、堆清理（阶段 III）和表截断（阶段 V）始终由 leader 进程串行执行。

## 阶段 III：堆清理

阶段 II 从索引中删除了引用 dead items 的条目后，阶段 III 负责回到堆页面，将这些 `LP_DEAD` 的 line pointer 标记为 `LP_UNUSED`，真正释放空间。

```
阶段 II + III 的协作:

  索引条目          堆页面 LP 状态
  ──────────────────────────────────
  初始状态:
    idx_entry ──► LP_DEAD (tuple)

  阶段 II 之后:
    (已删除)       LP_DEAD (tuple)

  阶段 III 之后:
    (已删除)       LP_UNUSED
                   (空间可复用)
```

为什么不能在阶段 I 中直接将 `LP_DEAD` 标记为 `LP_UNUSED`？因为索引条目还指向这些 TID。如果先释放了堆中的空间，新元组占用了这个位置，索引条目就会指向错误的元组。所以必须先删除索引条目（阶段 II），再释放堆空间（阶段 III）。

`lazy_vacuum_heap_rel` 使用 TID store 的迭代器来确定需要访问哪些堆页面。它使用 read stream API 提前读取这些页面，对每个页面获取 exclusive lock（注意不是 cleanup lock，因为只修改 LP 标志，不需要排除其他 pin holder），然后调用 `lazy_vacuum_heap_page`。

`lazy_vacuum_heap_page` 在一个 critical section 中将所有 `LP_DEAD` 标记为 `LP_UNUSED`，尝试截断页面尾部连续的 `LP_UNUSED` 条目以缩短 line pointer 数组，然后检查页面是否变为 all-visible 或 all-frozen 并更新 VM。最后写 WAL 日志。

## 阶段 IV：索引清理收尾

阶段 IV 在所有堆扫描和死亡条目清理完成后执行。它调用每个索引 AM 的 `amvacuumcleanup` 接口。

阶段 IV 和阶段 II 的区别在于：阶段 II（`ambulkdelete`）是删除特定的死亡索引条目，阶段 IV（`amvacuumcleanup`）是在所有删除完成后做收尾工作。对于 B-tree 索引，`amvacuumcleanup` 主要做的是：回收完全空的索引页面、更新索引的统计信息（用于 planner），以及处理一些阶段 II 的遗留工作。

如果整个 VACUUM 过程中没有任何 `ambulkdelete` 被调用过（比如没有 dead items，或者 bypass 优化生效了），`amvacuumcleanup` 通常会很快完成，因为没什么需要清理的。

## 阶段 V：表截断

如果表尾部有连续的空页面，VACUUM 会尝试截断这些页面，把物理文件缩小。这在 DELETE 了大量数据之后尤其有用。

尝试截断需要满足：

- `TRUNCATE` 选项没有被禁用
- failsafe 没有被触发
- 可释放的页面数 >= 1000 或 >= 表总页面数的 1/16

截断过程需要 `AccessExclusiveLock`，这是 PostgreSQL 中最重的锁，会阻塞所有其他对该表的访问。由于这个锁的影响太大，VACUUM 不会等待这个锁，而是通过 `ConditionalLockRelation` 尝试获取，拿不到就放弃。

```
lazy_truncate_heap 流程:

  do {
      尝试获取 AccessExclusiveLock (不等待)
          └─ 失败? 重试, 最多等 5 秒
              └─ 还是失败? 放弃截断

      检查表是否在我们等待期间增长了
          └─ 是? 释放锁, 放弃

      count_nondeletable_pages(): 从尾部向前扫描
      确认尾部页面确实为空

      RelationTruncate(): 执行截断

      释放 AccessExclusiveLock
  } while (还有可截断的空页面 && 检测到有锁等待者)
```

在持有 AE 锁从表尾部向前扫描找最后一个非空页面期间，它每 32 个块检查一次是否有其他进程在等锁，如果有就提前结束扫描、释放锁，尽量缩短 AE 锁的持有时间。这不仅让 primary 上等待的进程更快获得访问，也减少了 hot standby 上的阻塞：AE 锁的获取和释放都会写入 WAL，standby 回放时会在同等时间窗口内阻塞该表的读查询。

## 锁的全景

整个 VACUUM 过程中用到的锁：

关系级锁：

| 锁类型                        | 持有时间                 | 用途                          |
| ----------------------------- | ------------------------ | ----------------------------- |
| ShareUpdateExclusiveLock (表) | 整个 vacuum_rel (事务级) | 阻止并发 VACUUM，允许正常 DML |
| RowExclusiveLock (索引)       | 整个 heap_vacuum_rel     | 防止索引 DDL (DROP/REINDEX)   |
| AccessExclusiveLock (表)      | 阶段 V 截断时 (尽量短)   | 截断物理文件                  |

Buffer 锁：

| 锁类型                     | 持有时间                     | 用途                          |
| -------------------------- | ---------------------------- | ----------------------------- |
| Cleanup lock               | 阶段 I 处理单个页面时 (很短) | prune HOT 链，defragment 页面 |
| Exclusive lock             | 阶段 III 处理页面时 (很短)   | 修改 LP 标志                  |
| Exclusive lock (VM buffer) | 更新 VM 页面时 (很短)        | 设置 all-visible / all-frozen |

可以看到，lazy VACUUM 的设计充分考虑了并发性。表级锁使用了较低的等级以允许并发，buffer 级别的锁粒度精确到单个页面且持有时间极短。只有在最后截断时才需要 AE 锁，而且是条件获取、拿不到就放弃。

## 总结

Lazy VACUUM 是 PostgreSQL 中不可或缺的后台维护机制。它通过五个阶段的协作，在尽量不干扰正常业务的前提下，完成死亡元组回收、事务 ID 冻结和物理空间释放。理解这些阶段的工作原理和它们之间的交互，有助于在实际运维中做出更合理的参数调优决策，也有助于诊断 VACUUM 相关的性能问题。

## 参考资料

- [PostgreSQL Source - src/backend/access/heap/vacuumlazy.c](https://github.com/postgres/postgres/blob/master/src/backend/access/heap/vacuumlazy.c)
- [PostgreSQL Source - src/backend/commands/vacuum.c](https://github.com/postgres/postgres/blob/master/src/backend/commands/vacuum.c)
- [PostgreSQL Documentation - VACUUM](https://www.postgresql.org/docs/current/sql-vacuum.html)
- [PostgreSQL Documentation - Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html)
