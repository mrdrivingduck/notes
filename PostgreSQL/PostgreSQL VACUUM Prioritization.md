# PostgreSQL - VACUUM Prioritization

Created by: Mr Dk.

Co-authored by: GPT-6.1 Sol

2026 / 10 / 27 16:02

Hangzhou, Zhejiang, China

---

## 背景

在 PostgreSQL 的 [VACUUM 机制](./PostgreSQL%20VACUUM.md) 中，autovacuum 进程负责在后台周期性地回收死亡元组、冻结旧的事务 ID，并按需执行统计分析。

Autovacuum 的调度分为两层：

1. Autovacuum launcher 决定把 autovacuum worker 分派到哪个数据库
2. Autovacuum worker 连接到数据库后，自行决定处理哪些表以及处理顺序

我们在线上遇到过这样的问题：一个数据库中存在几十万张表，有限的 autovacuum worker 已经持续满负荷工作。其中，有一部分表的冻结年龄已经很高，早就超过了需要被冻结的阈值，却迟迟没有轮到它们做冻结。如果这些表继续得不到及时冻结，冻结年龄会随着事务 ID 的持续分配而增长。一旦逼近事务 ID 回卷边界，实例就会提前拒绝分配新的事务 ID，导致整个实例停写。

其原因在于，PostgreSQL 19 之前，autovacuum worker 按系统表的扫描顺序处理候选表，表的冻结年龄并不影响这个顺序。年龄较高的表可能排在列表中的任意位置，即使已经超过防回卷阈值，也只是进入候选列表，并不会因此优先得到处理。Autovacuum launcher 虽然会优先向有回卷风险的数据库分派 autovacuum worker，但 autovacuum worker 连接到数据库后，仍然可能先处理大量低年龄表，让急需冻结的高年龄表继续排队。

PostgreSQL 19 引入了 autovacuum 表级优先级调度机制。核心思路是：先收集需要处理的表，根据各张表超过清理、统计分析、冻结阈值的程度计算分数，再按分数从高到低处理。引入这个机制的是 Nathan Bossart 的提交 [Add rudimentary table prioritization to autovacuum](https://github.com/postgres/postgres/commit/d7965d65fc5bb2139bc51c051c11428414c65160)：

```
commit d7965d65fc5bb2139bc51c051c11428414c65160
Author: Nathan Bossart <nathan@postgresql.org>
Date:   Fri Mar 27 10:17:05 2026 -0500

    Add rudimentary table prioritization to autovacuum.

    ...

    Reviewed-by: Sami Imseih <samimseih@gmail.com>
    Reviewed-by: David Rowley <dgrowleyml@gmail.com>
    Reviewed-by: Robert Haas <robertmhaas@gmail.com>
    Reviewed-by: wenhui qiu <qiuwenhuifx@gmail.com>
    Reviewed-by: Greg Burd <greg@burd.me>
    Reviewed-by: Bharath Rupireddy <bharath.rupireddyforpostgres@gmail.com>
    Discussion: https://postgr.es/m/aOaAuXREwnPZVISO%40nathan
```

这个优化发生在上述的第二层调度中，决定了 autovacuum worker 处理表的优先级。下面先从数据库选择和 autovacuum worker 的分配说起，再看多个 autovacuum worker 之间如何协同，最后分析优先级分数如何改变表的处理顺序。

## 先处理哪个数据库？

Autovacuum launcher 不连接具体数据库，无法逐表判断是否需要 VACUUM。它扫描共享系统表 `pg_database`，读取各个数据库的标识、名称和冻结水位线，再结合数据库统计信息选择目标数据库。

候选信息保存在以下结构中：

```c
typedef struct avw_dbase
{
    Oid                 adw_datid;
    char               *adw_name;
    TransactionId       adw_frozenxid;
    MultiXactId         adw_minmulti;
    PgStat_StatDBEntry  *adw_entry;
} avw_dbase;
```

`pg_database` 系统表的 `datfrozenxid` 列记录数据库的冻结水位线，是数据库内各张表 `relfrozenxid` 的保守下界；水位线越老，数据库的冻结年龄越大。Autovacuum launcher 根据当前事务 ID 和 `autovacuum_freeze_max_age` 确定防回卷边界，并按以下规则选择数据库：

1. 如果存在冻结年龄超过防回卷阈值的数据库，选择其中冻结年龄最大的一个。
2. 如果没有，则选择上次启动 autovacuum worker 的时间最早的数据库。

MultiXactId 的处理同理。

这里只是决定了要把 autovacuum worker 分派到哪个数据库进行处理。具体哪些表需要被 VACUUM 或统计分析，要等 autovacuum worker 连接到数据库内以后才能确定。

## 如何分配 autovacuum worker？

Autovacuum launcher 记录各个数据库下一次分派 autovacuum worker 的时间，在调度时间到达时选择目标数据库，并尝试启动 autovacuum worker。这个过程不要求此前分派的 autovacuum worker 已经退出，因此同一个数据库可以同时有多个 autovacuum worker。

Autovacuum worker 的并发上限取 `autovacuum_worker_slots` 和 `autovacuum_max_workers` 的较小值：前者决定实例启动时预留的槽位总数，后者决定允许同时使用的槽位数。没有可用槽位时，autovacuum launcher 无法再启动 autovacuum worker：

```c
static bool
av_worker_available(void)
{
    int free_slots;
    int reserved_slots;

    free_slots = dclist_count(&AutoVacuumShmem->av_freeWorkers);

    reserved_slots = autovacuum_worker_slots - autovacuum_max_workers;
    reserved_slots = Max(0, reserved_slots);

    return free_slots > reserved_slots;
}
```

有可用槽位后，autovacuum launcher 将目标数据库写入共享内存，再通知 postmaster 创建 autovacuum worker。新启动的 autovacuum worker 从共享内存读取目标数据库并建立连接，逐表处理候选列表；完成本轮工作后退出、归还槽位，然后唤醒 autovacuum launcher。

## Autovacuum worker 如何协同？

多个 autovacuum worker 进入同一个数据库时，会各自扫描 `pg_class` 系统表，收集需要维护的候选表，列表可能高度重叠。Autovacuum launcher 只分配数据库，不分配具体的表。因此，进入同一个数据库的 autovacuum worker 之间需要进行协同：

1. 通过共享内存认领正在处理的表，避免并发处理同一张表。
2. 通过重新检查统计和冻结水位线，避免重复处理已完成维护的表。

### 避免并发争抢

每个 autovacuum worker 都会在共享内存中记录自己所属的数据库和当前认领的表：

```c
Oid     wi_dboid;
Oid     wi_tableoid;
bool    wi_sharedrel;
```

处理候选表前，autovacuum worker 先取得调度锁，检查该表是否已被其他 autovacuum worker 认领。若已被认领，则跳过并尝试下一张候选表；否则，在释放调度锁之前登记自己的认领信息，保证“检查”和“认领”是一个原子过程。调度锁只在认领阶段持有，各个 autovacuum worker 可以并发处理不同的表，处理结束后再清空认领信息：

```c
LWLockAcquire(AutovacuumScheduleLock, LW_EXCLUSIVE);
LWLockAcquire(AutovacuumLock, LW_SHARED);

skipit = false;
dlist_foreach(iter, &AutoVacuumShmem->av_runningWorkers)
{
    WorkerInfo worker =
        dlist_container(WorkerInfoData, wi_links, iter.cur);

    if (worker == MyWorkerInfo)
        continue;

    if (!worker->wi_sharedrel && worker->wi_dboid != MyDatabaseId)
        continue;

    if (worker->wi_tableoid == relid)
    {
        skipit = true;
        found_concurrent_worker = true;
        break;
    }
}
LWLockRelease(AutovacuumLock);

if (skipit)
{
    LWLockRelease(AutovacuumScheduleLock);
    continue;
}

MyWorkerInfo->wi_tableoid = relid;
MyWorkerInfo->wi_sharedrel = isshared;
LWLockRelease(AutovacuumScheduleLock);
```

上述认领机制负责协调 autovacuum worker 之间的任务。认领成功后，真正对表执行 autovacuum 时仍需取得 `ShareUpdateExclusiveLock`，与其他会话持有的冲突表锁互斥。因为 DDL、手动 VACUUM 和 ANALYZE 等操作不参与 autovacuum worker 的表认领，但它们持有的表锁仍可能与 autovacuum 所需的表锁冲突。

```c
lmode = (params.options & VACOPT_FULL) ?
    AccessExclusiveLock : ShareUpdateExclusiveLock;

rel = vacuum_open_relation(relid, relation, params.options,
                           params.log_vacuum_min_duration >= 0, lmode);
```

普通 autovacuum 取不到表锁时会跳过该表，防回卷 autovacuum 则会等待表锁，因为冻结是必须完成的。

### 避免重复处理

共享内存只记录正在处理的表，不保存已完成的维护记录。Autovacuum worker 完成某张表的维护后会清除认领信息，但其他 autovacuum worker 的候选列表中仍可能保留该表。这些 autovacuum worker 准备处理一张表时，无法仅凭共享内存判断它是否已经完成维护。

因此，autovacuum worker 在认领表后，会通过 `table_recheck_autovac()` 重新读取表的元数据和统计信息，确认是否仍需执行 VACUUM 或 ANALYZE。对于已由其他 autovacuum worker 完成维护、不再满足触发条件的表，当前进程会清除认领信息并跳过处理：

```c
tab = table_recheck_autovac(relid, table_toast_map, pg_class_desc,
                           effective_multixact_freeze_max_age);
if (tab == NULL)
{
    LWLockAcquire(AutovacuumScheduleLock, LW_EXCLUSIVE);
    MyWorkerInfo->wi_tableoid = InvalidOid;
    MyWorkerInfo->wi_sharedrel = false;
    LWLockRelease(AutovacuumScheduleLock);
    continue;
}
```

## 应该优先处理哪张表？

表的维护需求有轻重缓急，处理顺序也应体现这种差异。这正是引入表级优先级调度的目的。下面先看原先的处理方式。

### 基于系统表分布的随机顺序

在引入优先级调度之前，`do_autovacuum()` 扫描两次 `pg_class`：第一次收集普通表和物化视图，第二次收集 TOAST 表。每发现一张需要处理的表，就把 OID 追加到链表尾部，之后从头到尾处理：

```c
/* First pass: ordinary tables and materialized views. */
if (dovacuum || doanalyze)
    table_oids = lappend_oid(table_oids, relid);

/* Second pass: TOAST tables. */
if (dovacuum)
    table_oids = lappend_oid(table_oids, relid);

/* Process tables in list order. */
foreach(cell, table_oids)
{
    Oid relid = lfirst_oid(cell);
    /* ... claim, recheck, and VACUUM / ANALYZE ... */
}
```

这里的顺序来自对 `pg_class` 系统表的顺序扫描，扫描顺序与表的冻结年龄无关，年龄大小在扫描结果中的分布完全是随机的。普通表和物化视图整体排在第二遍扫描收集的 TOAST 表之前；防回卷标志影响一张表是否需要处理、如何处理，但不会把它插入列表头部。

危险表仍然可能位于很靠后的位置。如果危险表是 TOAST 表，还需要排在所有第一遍收集的候选表之后。排队期间，表的冻结年龄还会继续增长。若迟迟得不到冻结，整个实例最终可能因回卷风险而拒绝分配新的事务 ID，导致业务写入中断。

### 基于加权优先级分数的处理顺序

PostgreSQL 19 引入了表级优先级调度机制，根据冻结年龄和其他维护需求计算加权分数，再按分数从高到低处理候选表：

```c
typedef struct
{
    Oid     oid;
    double  score;
} TableToProcess;
```

`relation_needs_vacanalyze()` 在判断是否需要维护的同时计算各项分数。普通表、物化视图和 TOAST 表最终加入同一个候选列表：

```c
if (dovacuum || doanalyze)
{
    TableToProcess *table = palloc_object(TableToProcess);

    table->oid = relid;
    table->score = scores.max;
    tables_to_process = lappend(tables_to_process, table);
}
```

两遍扫描结束后，`list_sort()` 按分数降序排列。比较器的实现很直接，分数越高越优先：

```c
static int
TableToProcessComparator(const ListCell *a, const ListCell *b)
{
    TableToProcess *t1 = (TableToProcess *) lfirst(a);
    TableToProcess *t2 = (TableToProcess *) lfirst(b);

    return (t2->score < t1->score) ? -1 :
           (t2->score > t1->score) ? 1 : 0;
}
```

这样，TOAST 表也可以凭高分排到普通表前面。认领、重新检查和执行 VACUUM 的逻辑不受排序影响，多个 autovacuum worker 仍然维护各自的候选列表并通过共享内存协同。

### 优先级分数计算

不同维护需求的量纲不同。评分系统用“当前值 / 对应阈值”对各项指标进行归一化，再乘以对应权重：

- `autovacuum_freeze_score_weight`：事务 ID 冻结年龄的评分权重。
- `autovacuum_multixact_freeze_score_weight`：MultiXactId 冻结年龄的评分权重，计算方式同理。
- `autovacuum_vacuum_score_weight`：死亡元组数量的评分权重。
- `autovacuum_vacuum_insert_score_weight`：自上次 VACUUM 以来插入元组数量的评分权重。
- `autovacuum_analyze_score_weight`：自上次 ANALYZE 以来插入、更新和删除元组数量的评分权重。

即使未达到维护触发条件，也会对表计算相应分数，但只有至少满足一项触发条件的表才会进入候选列表，分数只决定入选后的处理顺序。各项评分权重默认都是 1.0。调高某项权重，会增强该项维护需求对排序的影响；设为 0 时，该项不再贡献分数。

例如，死亡元组对应的分数和 VACUUM 触发条件分别计算：

```c
scores->vac = (double) vactuples / Max(vacthresh, 1);
scores->vac *= autovacuum_vacuum_score_weight;
scores->max = Max(scores->max, scores->vac);
if (av_enabled && vactuples > vacthresh)
    *dovacuum = true;
```

表的最终分数取各项分数的最大值，任意一项维护需求都可以提高它的优先级：

```text
table_score = max(xid_score, mxid_score,
                  vacuum_score, vacuum_insert_score, analyze_score)
```

所有权重都为 0 时，跳过排序，恢复按系统表扫描顺序处理：

```c
if (autovacuum_freeze_score_weight != 0.0 ||
    autovacuum_multixact_freeze_score_weight != 0.0 ||
    autovacuum_vacuum_score_weight != 0.0 ||
    autovacuum_vacuum_insert_score_weight != 0.0 ||
    autovacuum_analyze_score_weight != 0.0)
    list_sort(tables_to_process, TableToProcessComparator);
```

### 通过幂次放大提高冻结优先级

在上述指标中，冻结年龄最重要，因为一张表冻结不及时可能导致整个实例停写；相比之下，其它指标主要反映空间回收和统计分析，延迟处理的后果温和得多。当表的冻结年龄进入危险区间时，应迅速提高其处理优先级。因此，评分系统在按阈值归一化得到的基础年龄分数上，额外引入了幂次放大：

```c
xid_age = TransactionIdIsNormal(relfrozenxid) ?
    recentXid - relfrozenxid : 0;

scores->xid = (double) xid_age / freeze_max_age;

effective_xid_failsafe_age =
    Max(vacuum_failsafe_age, autovacuum_freeze_max_age * 1.05);

if (autovacuum_freeze_score_weight > 1.0)
    effective_xid_failsafe_age /= autovacuum_freeze_score_weight;

if (xid_age >= effective_xid_failsafe_age && scores->xid > 1.0)
    scores->xid = pow(scores->xid,
                      Max(1.0, (double) xid_age / 100000000));

scores->xid *= autovacuum_freeze_score_weight;
```

幂次放大使冻结分数在危险年龄区间内加速增长，年龄越高，分数的放大幅度越大。这样可以显著提高紧急冻结任务的优先级，让有限的 autovacuum worker 更早处理接近回卷边界的表。

## 思考

回到文章开头的线上场景，优先级调度让急需冻结的高年龄表更早获得 autovacuum worker 的处理机会。按理说，只要这些表及时完成冻结，即使还有大量普通维护任务尚未完成，实例的年龄危机也应该得到解决。

但高年龄表完成冻结，是否就意味着整个实例的停写风险已经解除？

停写判断发生在分配事务 ID 时，比较的是待分配的事务 ID 与实例共享的停写边界，并不会实时检查各张表的冻结年龄。这个边界根据所有数据库冻结水位线中的最老值计算，在回卷边界前预留 300 万个事务 ID：

```c
/* SetTransactionIdLimit() */
xidWrapLimit = oldest_datfrozenxid + (MaxTransactionId >> 1);
xidStopLimit = xidWrapLimit - 3000000;

/* GetNewTransactionId() */
if (IsUnderPostmaster &&
    TransactionIdFollowsOrEquals(xid, xidStopLimit))
{
    /* ... report a wraparound error and refuse new transaction IDs ... */
}
```

停写边界的更新依赖于冻结水位线的逐级汇总：单张表完成冻结后，VACUUM 首先更新该表自身的冻结水位线，随后扫描本数据库各张表的冻结水位线，根据其中冻结年龄最大的表更新数据库级水位线，再根据所有数据库中最老的水位线更新实例共享的停写边界。

关键在于，autovacuum worker 逐表执行 VACUUM 时，显式指定了 `VACOPT_SKIP_DATABASE_STATS`，跳过数据库级冻结水位线的汇总更新。这样省去了逐表重复扫描系统表的开销，但也导致完成单表冻结不会自动触发数据库水位线和停写边界的更新：

```c
if ((params->options & VACOPT_VACUUM) &&
    !(params->options & VACOPT_SKIP_DATABASE_STATS))
{
    vac_update_datfrozenxid();
}
```

Autovacuum worker 将数据库级汇总留到本轮候选列表遍历结束后的收尾阶段：

```c
foreach_ptr(TableToProcess, table, tables_to_process)
{
    /* ... process each table in this round's candidate list ... */
}

/* ... finish up after processing this round ... */
if (did_vacuum || !found_concurrent_worker)
    vac_update_datfrozenxid();
```

在文章开头的线上场景中，高年龄表率先完成冻结后，各个进程仍会继续处理剩余候选表；数据库级水位线的汇总仍在本轮候选列表遍历结束后执行，不会因高年龄表已经完成冻结而提前触发。在此期间，停写判断仍可能沿用旧水位线计算出的边界，业务仍有停写风险。无论有没有这项优化，停写边界更新的时机都是一样的。

显然，这应当是 PostgreSQL 后续需要改进的一个方向。高年龄表完成冻结后，应及时更新数据库级水位线及实例的停写边界。更新数据库级水位线确实存在一定开销，但极端场景下及时更新也是必要的。我正在酝酿一个补丁解决这个问题。

## 参考资料

- [PostgreSQL commit d7965d65fc5](https://github.com/postgres/postgres/commit/d7965d65fc5bb2139bc51c051c11428414c65160) - Add rudimentary table prioritization to autovacuum.
- [Mailing list discussion](https://www.postgresql.org/message-id/flat/aOaAuXREwnPZVISO%40nathan) - another autovacuum scheduling thread
- [PostgreSQL Documentation - Autovacuum Prioritization](https://www.postgresql.org/docs/19/routine-vacuuming.html#AUTOVACUUM-PRIORITY)
- [PostgreSQL Documentation - Vacuuming](https://www.postgresql.org/docs/19/runtime-config-vacuum.html)
