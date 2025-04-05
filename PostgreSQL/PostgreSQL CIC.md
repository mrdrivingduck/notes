# PostgreSQL - CREATE INDEX CONCURRENTLY

Created by: Mr Dk.

2025 / 04 / 05 14:50

Ningbo, Zhejiang, China

---

## Background

索引通常被用于加速数据库的查询性能。理论上，在一张表上构建索引需要至少把表的全量数据扫描一遍，对于比较大的表来说，可能需要持续较长的时间；在此期间，表的内容不能被修改，否则构建出的索引与表的内容将会不一致。

对于在线系统来说，长时间锁住一张表无法修改是不可接受的。PostgreSQL 支持 [并发创建索引](https://www.postgresql.org/docs/17/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY) (CREATE INDEX CONCURRENTLY, CIC)。并发创建索引将会以较低的锁等级对表上锁，不阻塞 DML 操作的进行。并发索引构建会持续多个阶段完成，其消耗的整体资源和时间远大于非并发的索引创建。本文基于 PostgreSQL 17 源代码简析这个过程。

## Related: Heap Only Tuples

由于 CIC 与 PostgreSQL 的 [HOT (Heap-Only Tuples)](https://github.com/postgres/postgres/blob/REL_17_STABLE/src/backend/access/heap/README.HOT) 有一定关联，所以需要先简析一下 HOT 的原理。PostgreSQL 使用 [MVCC](https://www.postgresql.org/docs/17/mvcc-intro.html) 来存储表中的数据。对于每行数据，物理文件中可能会同时保存多个版本，每个事务根据其获取的快照来决定可见的版本是哪一个。当一行数据发生更新时，被更新的旧数据保持不变，表中将会插入一行新版本的数据。如果表上有索引，那么这行数据也需要被加入到索引中；如果表上有多个索引，那么每个索引都需要被更新，一次更新操作代价将会很大。

索引元组中保存的内容为：

- ScanKey：被索引列的值
- CTID：被索引行的位置（块号 + 块内偏移量）

当非索引列值被更新，并且当前页面中可以同时存放新旧两个版本的元组时，新元组会被直接插入到同一个页面中，并在旧元组的 header 中保存新元组的位置，形成 HOT 链。这样索引就不再需要被更新了，CTID 依旧指向旧版本元组。旧版本元组被标记为 `HEAP_HOT_UPDATED`，新版本元组被标记为 `HEAP_ONLY_TUPLE`。

```
    Index points to 1
    lp [1]  [2]

    [111111111]->[2222222222]
```

在后续查询时，虽然新版本的元组没有被索引直接引用到，但依旧可以通过旧元组 + HOT 链被查找到。索引扫描回表时，只要发现元组被标记为 `HEAP_HOT_UPDATED`，就需要沿着 HOT 链继续搜索。HOT 仅可能发生在一个页面内，所以沿着 HOT 链的搜索不会有额外的 I/O 开销。

后续当旧版本的元组不再可见而被删除时，其页内空间将会被回收，但行指针空间依旧被保留，保证 HOT 链不断裂：

```
    Index points to 1
    lp [1]->[2]

    [2222222222]
```

HOT 链并不会无限延长下去。当这一行被再次更新时，原先的新版本元组也会被标记为 `HEAP_HOT_UPDATED`，形成：

```
    Index points to 1
    lp [1]->[2]  [3]

    [2222222222]->[3333333333]
```

当所有能够看到 `[2]` 版本的事务结束后，由于任何索引都没有直接引用这个版本，所以这个版本的数据和行指针都可以被安全回收；索引元组依旧不用更新。HOT 链变为：

```
    Index points to 1
    lp [1]------>[3]

    [3333333333]
```

为什么 HOT 和创建索引有关呢？正是因为是否能够 HOT 的决策条件中包含了当前更新列上是否有索引。存在一个索引之前，某行数据更新是可以 HOT 的；但有了索引之后可能就不行了。所以在并发创建索引时，需要控制好新建索引的过程中依旧能够维持 HOT 的定义。

## CIC

创建索引属于 DDL，从下面的执行器的入口函数开始：

```c
/*
 * The "Slow" variant of ProcessUtility should only receive statements
 * supported by the event triggers facility.  Therefore, we always
 * perform the trigger support calls if the context allows it.
 */
static void
ProcessUtilitySlow(ParseState *pstate,
                   PlannedStmt *pstmt,
                   const char *queryString,
                   ProcessUtilityContext context,
                   ParamListInfo params,
                   QueryEnvironment *queryEnv,
                   DestReceiver *dest,
                   QueryCompletion *qc)
{
    /* ... */

    /* PG_TRY block is to ensure we call EventTriggerEndCompleteQuery */
    PG_TRY();
    {
        /* ... */

        switch (nodeTag(parsetree))
        {
            /* ... */

            case T_IndexStmt:   /* CREATE INDEX */
                {
                    IndexStmt  *stmt = (IndexStmt *) parsetree;
                    Oid         relid;
                    LOCKMODE    lockmode;
                    int         nparts = -1;
                    bool        is_alter_table;

                    if (stmt->concurrent)
                        PreventInTransactionBlock(isTopLevel,
                                                  "CREATE INDEX CONCURRENTLY");

                    /*
                     * Look up the relation OID just once, right here at the
                     * beginning, so that we don't end up repeating the name
                     * lookup later and latching onto a different relation
                     * partway through.  To avoid lock upgrade hazards, it's
                     * important that we take the strongest lock that will
                     * eventually be needed here, so the lockmode calculation
                     * needs to match what DefineIndex() does.
                     */
                    lockmode = stmt->concurrent ? ShareUpdateExclusiveLock
                        : ShareLock;
                    relid =
                        RangeVarGetRelidExtended(stmt->relation, lockmode,
                                                 0,
                                                 RangeVarCallbackOwnsRelation,
                                                 NULL);

                    /* ... */

                    /* Run parse analysis ... */
                    stmt = transformIndexStmt(relid, stmt, queryString);

                    /* ... and do it */
                    EventTriggerAlterTableStart(parsetree);
                    address =
                        DefineIndex(relid,  /* OID of heap relation */
                                    stmt,
                                    InvalidOid, /* no predefined OID */
                                    InvalidOid, /* no parent index */
                                    InvalidOid, /* no parent constraint */
                                    nparts, /* # of partitions, or -1 */
                                    is_alter_table,
                                    true,   /* check_rights */
                                    true,   /* check_not_in_use */
                                    false,  /* skip_build */
                                    false); /* quiet */

                    /* ... */
                }
                break;

            /* ... */

            default:
                elog(ERROR, "unrecognized node type: %d",
                     (int) nodeTag(parsetree));
                break;
        }

        /* ... */
    }
    PG_FINALLY();
    {
        /* ... */
    }
    PG_END_TRY();
}
```

从上面的代码片段可以看出，由于并发索引创建是通过多个事务完成的，所以无法在事务块内执行。另外，传统索引创建与并发索引创建对表的上锁等级不同。根据 PostgreSQL 的 [表锁兼容矩阵](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-TABLES)：

```c
#define AccessShareLock         1   /* SELECT */
#define RowShareLock            2   /* SELECT FOR UPDATE/FOR SHARE */
#define RowExclusiveLock        3   /* INSERT, UPDATE, DELETE */
#define ShareUpdateExclusiveLock 4  /* VACUUM (non-FULL), ANALYZE, CREATE
                                     * INDEX CONCURRENTLY */
#define ShareLock               5   /* CREATE INDEX (WITHOUT CONCURRENTLY) */
#define ShareRowExclusiveLock   6   /* like EXCLUSIVE MODE, but allows ROW
                                     * SHARE */
#define ExclusiveLock           7   /* blocks ROW SHARE/SELECT...FOR UPDATE */
#define AccessExclusiveLock     8   /* ALTER TABLE, DROP TABLE, VACUUM FULL,
                                     * and unqualified LOCK TABLE */
```

传统索引创建的 `ShareLock` 锁阻塞了一切写操作；而 CIC 的 `ShareUpdateExclusiveLock` 与 DML 操作所需要的 `RowExclusiveLock` 不冲突，所以不阻塞 DML。

后续的索引创建逻辑全部在 `DefineIndex` 函数中完成。

### Phase 1：创建空的无效索引，避免不一致的 HOT 更新

CIC 需要首先创建一个空的无效索引并将事务提交，使其能够被其它事务感知到。可见这个新索引的事务并不需要维护这个索引，也不能使用这个索引。创建这个空索引的作用是影响其它事务对 HOT 更新的决策：由于此时新索引已经存在，因此后续的更新操作如果修改了这个索引包含的列值，则不能再使用 HOT 更新了。这样可以避免后续索引创建完毕后，存在不符合定义的 HOT 链。

```c
ObjectAddress
DefineIndex(Oid tableId,
            IndexStmt *stmt,
            Oid indexRelationId,
            Oid parentIndexId,
            Oid parentConstraintId,
            int total_parts,
            bool is_alter_table,
            bool check_rights,
            bool check_not_in_use,
            bool skip_build,
            bool quiet)
{
    /* ... */

    /*
     * Force non-concurrent build on temporary relations, even if CONCURRENTLY
     * was requested.  Other backends can't access a temporary relation, so
     * there's no harm in grabbing a stronger lock, and a non-concurrent DROP
     * is more efficient.  Do this before any use of the concurrent option is
     * done.
     */
    if (stmt->concurrent && get_rel_persistence(tableId) != RELPERSISTENCE_TEMP)
        concurrent = true;
    else
        concurrent = false;

    /* ... */

    /*
     * Make the catalog entries for the index, including constraints. This
     * step also actually builds the index, except if caller requested not to
     * or in concurrent mode, in which case it'll be done later, or doing a
     * partitioned index (because those don't have storage).
     */
    flags = constr_flags = 0;
    if (stmt->isconstraint)
        flags |= INDEX_CREATE_ADD_CONSTRAINT;
    if (skip_build || concurrent || partitioned)
        flags |= INDEX_CREATE_SKIP_BUILD;
    if (stmt->if_not_exists)
        flags |= INDEX_CREATE_IF_NOT_EXISTS;
    if (concurrent)
        flags |= INDEX_CREATE_CONCURRENT;
    /* ... */

    indexRelationId =
        index_create(rel, indexRelationName, indexRelationId, parentIndexId,
                     parentConstraintId,
                     stmt->oldNumber, indexInfo, indexColNames,
                     accessMethodId, tablespaceId,
                     collationIds, opclassIds, opclassOptions,
                     coloptions, NULL, reloptions,
                     flags, constr_flags,
                     allowSystemTableMods, !check_rights,
                     &createdConstraintId);

    /* ... */
}
```

上述代码首先完成索引创建前的各项准备，包含索引列确认、权限检查、索引名称确定、索引表达式编译等。然后根据索引创建的类型确认标志位。对于 CIC 来说，需要设置的标志位有 `INDEX_CREATE_SKIP_BUILD` 和 `INDEX_CREATE_CONCURRENT`。前者表示先不创建索引本身，仅更新系统表，使其它事务能够可见这个索引；后者表示当前要进行的是并发索引创建。将这个标志位传入 `index_create` 函数中：

```c
Oid
index_create(Relation heapRelation,
			 const char *indexRelationName,
			 Oid indexRelationId,
			 Oid parentIndexRelid,
			 Oid parentConstraintId,
			 RelFileNumber relFileNumber,
			 IndexInfo *indexInfo,
			 const List *indexColNames,
			 Oid accessMethodId,
			 Oid tableSpaceId,
			 const Oid *collationIds,
			 const Oid *opclassIds,
			 const Datum *opclassOptions,
			 const int16 *coloptions,
			 const NullableDatum *stattargets,
			 Datum reloptions,
			 bits16 flags,
			 bits16 constr_flags,
			 bool allow_system_table_mods,
			 bool is_internal,
			 Oid *constraintId)
{
    /* ... */

	bool		concurrent = (flags & INDEX_CREATE_CONCURRENT) != 0;

    /* ... */

	/*
	 * create the index relation's relcache entry and, if necessary, the
	 * physical disk file. (If we fail further down, it's the smgr's
	 * responsibility to remove the disk file again, if any.)
	 */
	indexRelation = heap_create(indexRelationName,
								namespaceId,
								tableSpaceId,
								indexRelationId,
								relFileNumber,
								accessMethodId,
								indexTupDesc,
								relkind,
								relpersistence,
								shared_relation,
								mapped_relation,
								allow_system_table_mods,
								&relfrozenxid,
								&relminmxid,
								create_storage);

	Assert(relfrozenxid == InvalidTransactionId);
	Assert(relminmxid == InvalidMultiXactId);
	Assert(indexRelationId == RelationGetRelid(indexRelation));

	/*
	 * Obtain exclusive lock on it.  Although no other transactions can see it
	 * until we commit, this prevents deadlock-risk complaints from lock
	 * manager in cases such as CLUSTER.
	 */
	LockRelation(indexRelation, AccessExclusiveLock);

	/*
	 * Fill in fields of the index's pg_class entry that are not set correctly
	 * by heap_create.
	 *
	 * XXX should have a cleaner way to create cataloged indexes
	 */
	indexRelation->rd_rel->relowner = heapRelation->rd_rel->relowner;
	indexRelation->rd_rel->relam = accessMethodId;
	indexRelation->rd_rel->relispartition = OidIsValid(parentIndexRelid);

	/*
	 * store index's pg_class entry
	 */
	InsertPgClassTuple(pg_class, indexRelation,
					   RelationGetRelid(indexRelation),
					   (Datum) 0,
					   reloptions);

	/* done with pg_class */
	table_close(pg_class, RowExclusiveLock);

	/*
	 * now update the object id's of all the attribute tuple forms in the
	 * index relation's tuple descriptor
	 */
	InitializeAttributeOids(indexRelation,
							indexInfo->ii_NumIndexAttrs,
							indexRelationId);

	/*
	 * append ATTRIBUTE tuples for the index
	 */
	AppendAttributeTuples(indexRelation, opclassOptions, stattargets);

	/* ----------------
	 *	  update pg_index
	 *	  (append INDEX tuple)
	 *
	 *	  Note that this stows away a representation of "predicate".
	 *	  (Or, could define a rule to maintain the predicate) --Nels, Feb '92
	 * ----------------
	 */
	UpdateIndexRelation(indexRelationId, heapRelationId, parentIndexRelid,
						indexInfo,
						collationIds, opclassIds, coloptions,
						isprimary, is_exclusion,
						(constr_flags & INDEX_CONSTR_CREATE_DEFERRABLE) == 0,
						!concurrent && !invalid,
						!concurrent);

	/*
	 * Register relcache invalidation on the indexes' heap relation, to
	 * maintain consistency of its index list
	 */
	CacheInvalidateRelcache(heapRelation);

    /* ... */

	/*
	 * Advance the command counter so that we can see the newly-entered
	 * catalog tuples for the index.
	 */
	CommandCounterIncrement();

    /* ... */

	/*
	 * If this is bootstrap (initdb) time, then we don't actually fill in the
	 * index yet.  We'll be creating more indexes and classes later, so we
	 * delay filling them in until just before we're done with bootstrapping.
	 * Similarly, if the caller specified to skip the build then filling the
	 * index is delayed till later (ALTER TABLE can save work in some cases
	 * with this).  Otherwise, we call the AM routine that constructs the
	 * index.
	 */
	if (IsBootstrapProcessingMode())
	{
		index_register(heapRelationId, indexRelationId, indexInfo);
	}
	else if ((flags & INDEX_CREATE_SKIP_BUILD) != 0)
	{
		/*
		 * Caller is responsible for filling the index later on.  However,
		 * we'd better make sure that the heap relation is correctly marked as
		 * having an index.
		 */
		index_update_stats(heapRelation,
						   true,
						   -1.0);
		/* Make the above update visible */
		CommandCounterIncrement();
	}
	else
	{
		index_build(heapRelation, indexRelation, indexInfo, false, true);
	}

	/*
	 * Close the index; but we keep the lock that we acquired above until end
	 * of transaction.  Closing the heap is caller's responsibility.
	 */
	index_close(indexRelation, NoLock);

	return indexRelationId;
}
```

此处向 [`pg_class`](https://www.postgresql.org/docs/17/catalog-pg-class.html) 和 [`pg_index`](https://www.postgresql.org/docs/17/catalog-pg-index.html) 系统表中插入了新索引的元数据，根据标志位 `INDEX_CREATE_SKIP_BUILD` 跳过了填充索引内容的 `index_build` 并直接返回。在函数 `UpdateIndexRelation` 更新 `pg_index` 系统表时，CIC 将索引的 `indisvalid` 和 `indisready` 全部设置为 `false`，表示这个索引既不需要被 DML 维护，也不能被用于查询。

系统表更新完毕后将事务提交，并打开一个新事务进入下一阶段：

```c
ObjectAddress
DefineIndex(Oid tableId,
			IndexStmt *stmt,
			Oid indexRelationId,
			Oid parentIndexId,
			Oid parentConstraintId,
			int total_parts,
			bool is_alter_table,
			bool check_rights,
			bool check_not_in_use,
			bool skip_build,
			bool quiet)
{
    /* ... */

	/* save lockrelid and locktag for below, then close rel */
	heaprelid = rel->rd_lockInfo.lockRelId;
	SET_LOCKTAG_RELATION(heaplocktag, heaprelid.dbId, heaprelid.relId);
	table_close(rel, NoLock);

	/*
	 * For a concurrent build, it's important to make the catalog entries
	 * visible to other transactions before we start to build the index. That
	 * will prevent them from making incompatible HOT updates.  The new index
	 * will be marked not indisready and not indisvalid, so that no one else
	 * tries to either insert into it or use it for queries.
	 *
	 * We must commit our current transaction so that the index becomes
	 * visible; then start another.  Note that all the data structures we just
	 * built are lost in the commit.  The only data we keep past here are the
	 * relation IDs.
	 *
	 * Before committing, get a session-level lock on the table, to ensure
	 * that neither it nor the index can be dropped before we finish. This
	 * cannot block, even if someone else is waiting for access, because we
	 * already have the same lock within our transaction.
	 *
	 * Note: we don't currently bother with a session lock on the index,
	 * because there are no operations that could change its state while we
	 * hold lock on the parent table.  This might need to change later.
	 */
	LockRelationIdForSession(&heaprelid, ShareUpdateExclusiveLock);

	PopActiveSnapshot();
	CommitTransactionCommand();
	StartTransactionCommand();

	/* Tell concurrent index builds to ignore us, if index qualifies */
	if (safe_index)
		set_indexsafe_procflags();

    /* ... */
}
```

### Phase 2：填充索引主体数据

在上一步的事务提交后，可见索引的事务不再会产生非预期的 HOT 更新。但目前已在进行中的事务已经产生了非预期的 HOT。所以，需要首先等待这些事务全都结束，所有事务才都不再会产生非预期的 HOT。此时才可以开始填充新索引的数据。

在具体实现上，等待对该表持有 `ShareLock` 的旧事务结束：

```c
{
    /* ... */

	/*
	 * The index is now visible, so we can report the OID.  While on it,
	 * include the report for the beginning of phase 2.
	 */
	{
		const int	progress_cols[] = {
			PROGRESS_CREATEIDX_INDEX_OID,
			PROGRESS_CREATEIDX_PHASE
		};
		const int64 progress_vals[] = {
			indexRelationId,
			PROGRESS_CREATEIDX_PHASE_WAIT_1
		};

		pgstat_progress_update_multi_param(2, progress_cols, progress_vals);
	}

	/*
	 * Phase 2 of concurrent index build (see comments for validate_index()
	 * for an overview of how this works)
	 *
	 * Now we must wait until no running transaction could have the table open
	 * with the old list of indexes.  Use ShareLock to consider running
	 * transactions that hold locks that permit writing to the table.  Note we
	 * do not need to worry about xacts that open the table for writing after
	 * this point; they will see the new index when they open it.
	 *
	 * Note: the reason we use actual lock acquisition here, rather than just
	 * checking the ProcArray and sleeping, is that deadlock is possible if
	 * one of the transactions in question is blocked trying to acquire an
	 * exclusive lock on our table.  The lock code will detect deadlock and
	 * error out properly.
	 */
	WaitForLockers(heaplocktag, ShareLock, true);

    /* ... */
}
```

接下来，获取新快照，并通过 `index_concurrently_build` 函数填充索引内容，然后提交事务：

```c
{
    /* ... */

	/*
	 * At this moment we are sure that there are no transactions with the
	 * table open for write that don't have this new index in their list of
	 * indexes.  We have waited out all the existing transactions and any new
	 * transaction will have the new index in its list, but the index is still
	 * marked as "not-ready-for-inserts".  The index is consulted while
	 * deciding HOT-safety though.  This arrangement ensures that no new HOT
	 * chains can be created where the new tuple and the old tuple in the
	 * chain have different index keys.
	 *
	 * We now take a new snapshot, and build the index using all tuples that
	 * are visible in this snapshot.  We can be sure that any HOT updates to
	 * these tuples will be compatible with the index, since any updates made
	 * by transactions that didn't know about the index are now committed or
	 * rolled back.  Thus, each visible tuple is either the end of its
	 * HOT-chain or the extension of the chain is HOT-safe for this index.
	 */

	/* Set ActiveSnapshot since functions in the indexes may need it */
	PushActiveSnapshot(GetTransactionSnapshot());

	/* Perform concurrent build of index */
	index_concurrently_build(tableId, indexRelationId);

	/* we can do away with our snapshot */
	PopActiveSnapshot();

	/*
	 * Commit this transaction to make the indisready update visible.
	 */
	CommitTransactionCommand();
	StartTransactionCommand();

	/* Tell concurrent index builds to ignore us, if index qualifies */
	if (safe_index)
		set_indexsafe_procflags();

    /* ... */
}
```

这里构建索引元组时，ScanKey 使用的是当前事务快照内可见元组的列值，但 CTID 使用的是可见元组在 HOT 链中的 root CTID。这样可以保证所有索引中引用同一个元组的 CTID 都是相同的。可见元组在 HOT 链中的前序元组在当前事务中是不可见的，所以使用该索引进行回表时，前序元组也必然不可见。

在索引填充完毕，提交事务之前，`index_concurrently_build` 将索引的 `indisready` 设置为 `true`，表示自此所有事务都需要开始维护这个索引：

```c
/*
 * index_concurrently_build
 *
 * Build index for a concurrent operation.  Low-level locks are taken when
 * this operation is performed to prevent only schema changes, but they need
 * to be kept until the end of the transaction performing this operation.
 * 'indexOid' refers to an index relation OID already created as part of
 * previous processing, and 'heapOid' refers to its parent heap relation.
 */
void
index_concurrently_build(Oid heapRelationId,
						 Oid indexRelationId)
{
	/* ... */

	/* Now build the index */
	index_build(heapRel, indexRelation, indexInfo, false, true);

	/* ... */

	/*
	 * Update the pg_index row to mark the index as ready for inserts. Once we
	 * commit this transaction, any new transactions that open the table must
	 * insert new entries into the index for insertions and non-HOT updates.
	 */
	index_set_state_flags(indexRelationId, INDEX_CREATE_SET_READY);
}
```

### Phase 3：补全填充索引期间缺失的数据

截止目前，phase 2 开始之前提交的所有数据都已经在索引中了，phase 2 提交之后所有事务中的 DML 也会开始维护这个索引了。所以现在还缺两部分数据：

1. 在 phase 2 事务开始之后才提交的事务，因这些元组在 phase 2 的快照中不可见，而缺失对应的索引元组
2. 在 phase 2 事务期间开始的事务，因 phase 2 期间索引属性 `indisready` 依旧为 `false`，因此没有维护索引，缺失索引元组

Phase 3 开始补全这两部分缺失的数据。理论上现在立刻新开始一个事务，就可以可见并补全第一部分缺失数据。但第二部分缺失的数据因事务未提交暂不可见，所以依旧无法补全。所以这里需要等待在 phase 2 事务期间开始的，对表有过修改的事务结束，然后再获取快照扫描一次全表。此时两部分缺失数据都已经对当前快照可见，因此能够补回数据。

```c
{
    /* ... */

	/*
	 * Phase 3 of concurrent index build
	 *
	 * We once again wait until no transaction can have the table open with
	 * the index marked as read-only for updates.
	 */
	pgstat_progress_update_param(PROGRESS_CREATEIDX_PHASE,
								 PROGRESS_CREATEIDX_PHASE_WAIT_2);
	WaitForLockers(heaplocktag, ShareLock, true);

	/*
	 * Now take the "reference snapshot" that will be used by validate_index()
	 * to filter candidate tuples.  Beware!  There might still be snapshots in
	 * use that treat some transaction as in-progress that our reference
	 * snapshot treats as committed.  If such a recently-committed transaction
	 * deleted tuples in the table, we will not include them in the index; yet
	 * those transactions which see the deleting one as still-in-progress will
	 * expect such tuples to be there once we mark the index as valid.
	 *
	 * We solve this by waiting for all endangered transactions to exit before
	 * we mark the index as valid.
	 *
	 * We also set ActiveSnapshot to this snap, since functions in indexes may
	 * need a snapshot.
	 */
	snapshot = RegisterSnapshot(GetTransactionSnapshot());
	PushActiveSnapshot(snapshot);

	/*
	 * Scan the index and the heap, insert any missing index entries.
	 */
	validate_index(tableId, indexRelationId, snapshot);

	/*
	 * Drop the reference snapshot.  We must do this before waiting out other
	 * snapshot holders, else we will deadlock against other processes also
	 * doing CREATE INDEX CONCURRENTLY, which would see our snapshot as one
	 * they must wait for.  But first, save the snapshot's xmin to use as
	 * limitXmin for GetCurrentVirtualXIDs().
	 */
	limitXmin = snapshot->xmin;

	PopActiveSnapshot();
	UnregisterSnapshot(snapshot);

	/*
	 * The snapshot subsystem could still contain registered snapshots that
	 * are holding back our process's advertised xmin; in particular, if
	 * default_transaction_isolation = serializable, there is a transaction
	 * snapshot that is still active.  The CatalogSnapshot is likewise a
	 * hazard.  To ensure no deadlocks, we must commit and start yet another
	 * transaction, and do our wait before any snapshot has been taken in it.
	 */
	CommitTransactionCommand();
	StartTransactionCommand();

	/* Tell concurrent index builds to ignore us, if index qualifies */
	if (safe_index)
		set_indexsafe_procflags();

    /* ... */
}
```

在通过 `validate_index` 函数补全索引内的缺失数据以后，再次提交当前事务。此后，其它事务理论上就可以看见数据完整的索引了，但此时索引暂时还不能被标记为可使用。因为索引中只包含 phase 2 获取的快照及之后的快照可见的数据，不包含更旧事务所使用的旧快照可见的数据。如果此时立刻标记索引可用，那么这些旧事务在使用这个索引时将会查不到预期可见的数据。所以必须等待这些旧事务全部结束，才可以标记索引的 `indisvalid` 为 `true`，开放使用：

```c
{
    /* ... */

	/* We should now definitely not be advertising any xmin. */
	Assert(MyProc->xmin == InvalidTransactionId);

	/*
	 * The index is now valid in the sense that it contains all currently
	 * interesting tuples.  But since it might not contain tuples deleted just
	 * before the reference snap was taken, we have to wait out any
	 * transactions that might have older snapshots.
	 */
	pgstat_progress_update_param(PROGRESS_CREATEIDX_PHASE,
								 PROGRESS_CREATEIDX_PHASE_WAIT_3);
	WaitForOlderSnapshots(limitXmin, true);

	/*
	 * Index can now be marked valid -- update its pg_index entry
	 */
	index_set_state_flags(indexRelationId, INDEX_CREATE_SET_VALID);

	/*
	 * The pg_index update will cause backends (including this one) to update
	 * relcache entries for the index itself, but we should also send a
	 * relcache inval on the parent table to force replanning of cached plans.
	 * Otherwise existing sessions might fail to use the new index where it
	 * would be useful.  (Note that our earlier commits did not create reasons
	 * to replan; so relcache flush on the index itself was sufficient.)
	 */
	CacheInvalidateRelcacheByRelid(heaprelid.relId);

	/*
	 * Last thing to do is release the session-level lock on the parent table.
	 */
	UnlockRelationIdForSession(&heaprelid, ShareUpdateExclusiveLock);

	pgstat_progress_end_command();

	return address;
}
```

此后，新索引开始在所有事务中可用。

## Summary

综上，CIC 全程没有阻塞任何 DML，而是通过多个阶段，使新索引逐渐从中间状态过渡到可用状态。其间通过获取两次事务快照，辅以必要的等待，逐步补全索引数据，保证索引的完整性和一致性。CIC 全程对全表数据扫描了两次，相比于非并发索引创建，有更大的资源开销。此外，新索引何时开始可用，也取决于系统中 CIC 开始前的长事务何时结束：如果这些事务一直不结束，即使新索引的数据已经就绪，也将会一直不可用。

## References

[PostgreSQL: Documentation: 17: 65.7. Heap-Only Tuples (HOT)](https://www.postgresql.org/docs/17/storage-hot.html)

[PostgreSQL: Documentation: 17: CREATE INDEX](https://www.postgresql.org/docs/17/sql-createindex.html)

[Explaining CREATE INDEX CONCURRENTLY](https://www.enterprisedb.com/blog/explaining-create-index-concurrently)

[README.HOT](https://github.com/postgres/postgres/blob/REL_17_STABLE/src/backend/access/heap/README.HOT)
