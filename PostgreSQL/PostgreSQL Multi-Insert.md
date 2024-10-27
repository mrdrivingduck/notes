# PostgreSQL - Multi Insert

Created by: Mr Dk.

2024 / 10 / 27 14:11

Hangzhou, Zhejiang, China, @Alibaba Xixi Campus (Park C)

---

## 背景

PostgreSQL 目前提供了两种将数据插入数据库的方法，一种是通过 [`INSERT`](https://www.postgresql.org/docs/current/sql-insert.html) 语法，一种是通过 [`COPY`](https://www.postgresql.org/docs/current/sql-copy.html) 语法。从 SQL 语法的层面可以看出两者有一定的差异，但功能上的重合点是非常多的，因为本质上都是把新的数据行加入到表中。

本文基于 PostgreSQL 17 浅析这两种数据插入方法的内部实现。除语法层面的差异外，两者在 Table Access Method、Buffer 层算法、WAL 日志记录等方面的设计也是完全不同的。其中最核心的区别可被归纳为：**攒批**。这也为 PostgreSQL 的后续性能优化提供了一些思路。

## 执行器算法

`INSERT` 和 `COPY` 核心执行函数的输入都是一行待插入的数据，在执行器内被表示为一个存放在 `TupleTableSlot` 中的元组。

`INSERT` 的核心执行逻辑位于 `ExecInsert` 函数中。对于一行待插入数据，需要处理 `ROW INSERT` 相关的触发器、生成列计算、行级别安全规则检查、表级约束条件检查、`ON CONFLICT` 等复杂语法处理、索引更新等逻辑，最终调用 Table Access Method 层的 `table_tuple_insert` 函数将元组传入 AM 层：

```c
/* ----------------------------------------------------------------
 *      ExecInsert
 *
 *      For INSERT, we have to insert the tuple into the target relation
 *      (or partition thereof) and insert appropriate tuples into the index
 *      relations.
 *
 *      slot contains the new tuple value to be stored.
 *
 *      Returns RETURNING result if any, otherwise NULL.
 *      *inserted_tuple is the tuple that's effectively inserted;
 *      *insert_destrel is the relation where it was inserted.
 *      These are only set on success.
 *
 *      This may change the currently active tuple conversion map in
 *      mtstate->mt_transition_capture, so the callers must take care to
 *      save the previous value to avoid losing track of it.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecInsert(ModifyTableContext *context,
           ResultRelInfo *resultRelInfo,
           TupleTableSlot *slot,
           bool canSetTag,
           TupleTableSlot **inserted_tuple,
           ResultRelInfo **insert_destrel)
{
    /* ... */

    /*
     * BEFORE ROW INSERT Triggers.
     *
     * Note: We fire BEFORE ROW TRIGGERS for every attempted insertion in an
     * INSERT ... ON CONFLICT statement.  We cannot check for constraint
     * violations before firing these triggers, because they can change the
     * values to insert.  Also, they can run arbitrary user-defined code with
     * side-effects that we can't cancel by just not inserting the tuple.
     */
    /* ... */

    /* INSTEAD OF ROW INSERT Triggers */
    if (resultRelInfo->ri_TrigDesc &&
        resultRelInfo->ri_TrigDesc->trig_insert_instead_row)
    {
        /* ... */
    }
    else if (resultRelInfo->ri_FdwRoutine)
    {
        /* ... */
    }
    else
    {
        /* ... */

        /*
         * Compute stored generated columns
         */
        /* ... */

        /*
         * Check any RLS WITH CHECK policies.
         *
         * Normally we should check INSERT policies. But if the insert is the
         * result of a partition key update that moved the tuple to a new
         * partition, we should instead check UPDATE policies, because we are
         * executing policies defined on the target table, and not those
         * defined on the child partitions.
         *
         * If we're running MERGE, we refer to the action that we're executing
         * to know if we're doing an INSERT or UPDATE to a partition table.
         */
        /* ... */

        /*
         * ExecWithCheckOptions() will skip any WCOs which are not of the kind
         * we are looking for at this point.
         */
        /* ... */

        /*
         * Check the constraints of the tuple.
         */
        /* ... */

        /*
         * Also check the tuple against the partition constraint, if there is
         * one; except that if we got here via tuple-routing, we don't need to
         * if there's no BR trigger defined on the partition.
         */
        /* ... */

        if (onconflict != ONCONFLICT_NONE && resultRelInfo->ri_NumIndices > 0)
        {
            /* ... */
        }
        else
        {
            /* insert the tuple normally */
            table_tuple_insert(resultRelationDesc, slot,
                               estate->es_output_cid,
                               0, NULL);

            /* insert index entries for tuple */
            if (resultRelInfo->ri_NumIndices > 0)
                recheckIndexes = ExecInsertIndexTuples(resultRelInfo,
                                                       slot, estate, false,
                                                       false, NULL, NIL,
                                                       false);
        }
    }

    if (canSetTag)
        (estate->es_processed)++;

    /* ... */

    /* AFTER ROW INSERT Triggers */
    /* ... */

    /*
     * Check any WITH CHECK OPTION constraints from parent views.  We are
     * required to do this after testing all constraints and uniqueness
     * violations per the SQL spec, so we do it after actually inserting the
     * record into the heap and all indexes.
     *
     * ExecWithCheckOptions will elog(ERROR) if a violation is found, so the
     * tuple will never be seen, if it violates the WITH CHECK OPTION.
     *
     * ExecWithCheckOptions() will skip any WCOs which are not of the kind we
     * are looking for at this point.
     */
    /* ... */

    /* Process RETURNING if present */
    /* ... */

    return result;
}
```

`COPY` 的核心执行逻辑位于 `CopyFrom` 函数中，与 `ExecInsert` 函数较大的区别是其会在内存中维护一段 `TupleTableSlot` 数组，对于输入的数据行会先通过 `CopyMultiInsertInfoStore` 在内存中缓存：

```c
/*
 * Copy FROM file to relation.
 */
uint64
CopyFrom(CopyFromState cstate)
{
    /* ... */

    for (;;)
    {
        /* ... */

        /* select slot to (initially) load row into */
        if (insertMethod == CIM_SINGLE || proute)
        {
            myslot = singleslot;
            Assert(myslot != NULL);
        }
        else
        {
            Assert(resultRelInfo == target_resultRelInfo);
            Assert(insertMethod == CIM_MULTI);

            myslot = CopyMultiInsertInfoNextFreeSlot(&multiInsertInfo,
                                                     resultRelInfo);
        }

        /* ... */

        /* Directly store the values/nulls array in the slot */
        if (!NextCopyFrom(cstate, econtext, myslot->tts_values, myslot->tts_isnull))
            break;

        /* ... */

        ExecStoreVirtualTuple(myslot);

        /*
         * Constraints and where clause might reference the tableoid column,
         * so (re-)initialize tts_tableOid before evaluating them.
         */
        myslot->tts_tableOid = RelationGetRelid(target_resultRelInfo->ri_RelationDesc);

        /* ... */

        if (!skip_tuple)
        {
            /*
             * If there is an INSTEAD OF INSERT ROW trigger, let it handle the
             * tuple.  Otherwise, proceed with inserting the tuple into the
             * table or foreign table.
             */
            if (has_instead_insert_row_trig)
            {
                /* ... */
            }
            else
            {
                /* Compute stored generated columns */
                /* ... */

                /*
                 * If the target is a plain table, check the constraints of
                 * the tuple.
                 */
                /* ... */

                /*
                 * Also check the tuple against the partition constraint, if
                 * there is one; except that if we got here via tuple-routing,
                 * we don't need to if there's no BR trigger defined on the
                 * partition.
                 */
                /* ... */

                /* Store the slot in the multi-insert buffer, when enabled. */
                if (insertMethod == CIM_MULTI || leafpart_use_multi_insert)
                {
                    /*
                     * The slot previously might point into the per-tuple
                     * context. For batching it needs to be longer lived.
                     */
                    ExecMaterializeSlot(myslot);

                    /* Add this tuple to the tuple buffer */
                    CopyMultiInsertInfoStore(&multiInsertInfo,
                                             resultRelInfo, myslot,
                                             cstate->line_buf.len,
                                             cstate->cur_lineno);

                    /*
                     * If enough inserts have queued up, then flush all
                     * buffers out to their tables.
                     */
                    if (CopyMultiInsertInfoIsFull(&multiInsertInfo))
                        CopyMultiInsertInfoFlush(&multiInsertInfo,
                                                 resultRelInfo,
                                                 &processed);

                    /*
                     * We delay updating the row counter and progress of the
                     * COPY command until after writing the tuples stored in
                     * the buffer out to the table, as in single insert mode.
                     * See CopyMultiInsertBufferFlush().
                     */
                    continue;   /* next tuple please */
                }
                else
                {
                    /* ... */
                }
            }

            /* ... */
        }
    }

    /* Flush any remaining buffered tuples */
    if (insertMethod != CIM_SINGLE)
    {
        if (!CopyMultiInsertInfoIsEmpty(&multiInsertInfo))
            CopyMultiInsertInfoFlush(&multiInsertInfo, NULL, &processed);
    }

    /* ... */

    return processed;
}
```

达到 `CopyMultiInsertInfoIsFull` 的条件后，会触发调用 `CopyMultiInsertInfoFlush`，将所有缓存的元组一次性传入 Table AM 接口 `table_multi_insert`：

```c
/*
 * Returns true if the buffers are full
 */
static inline bool
CopyMultiInsertInfoIsFull(CopyMultiInsertInfo *miinfo)
{
    if (miinfo->bufferedTuples >= MAX_BUFFERED_TUPLES ||
        miinfo->bufferedBytes >= MAX_BUFFERED_BYTES)
        return true;
    return false;
}

/*
 * Write out all stored tuples in all buffers out to the tables.
 *
 * Once flushed we also trim the tracked buffers list down to size by removing
 * the buffers created earliest first.
 *
 * Callers should pass 'curr_rri' as the ResultRelInfo that's currently being
 * used.  When cleaning up old buffers we'll never remove the one for
 * 'curr_rri'.
 */
static inline void
CopyMultiInsertInfoFlush(CopyMultiInsertInfo *miinfo, ResultRelInfo *curr_rri,
                         int64 *processed)
{
    ListCell   *lc;

    foreach(lc, miinfo->multiInsertBuffers)
    {
        CopyMultiInsertBuffer *buffer = (CopyMultiInsertBuffer *) lfirst(lc);

        CopyMultiInsertBufferFlush(miinfo, buffer, processed);
    }

    miinfo->bufferedTuples = 0;
    miinfo->bufferedBytes = 0;

    /* ... */
}

/*
 * Write the tuples stored in 'buffer' out to the table.
 */
static inline void
CopyMultiInsertBufferFlush(CopyMultiInsertInfo *miinfo,
                           CopyMultiInsertBuffer *buffer,
                           int64 *processed)
{
    /* ... */

    if (resultRelInfo->ri_FdwRoutine)
    {
        /* ... */
    }
    else
    {
        /* ... */

        /*
         * table_multi_insert may leak memory, so switch to short-lived memory
         * context before calling it.
         */
        oldcontext = MemoryContextSwitchTo(GetPerTupleMemoryContext(estate));
        table_multi_insert(resultRelInfo->ri_RelationDesc,
                           slots,
                           nused,
                           mycid,
                           ti_options,
                           buffer->bistate);
        MemoryContextSwitchTo(oldcontext);

        /* ... */
    }

    /* Mark that all slots are free */
    buffer->nused = 0;
}
```

## Table Access Method

此时两种 SQL 语法的执行都已进入 Table AM 层。可以看到两者在执行层算法存在区别的原因是最终使用的 Table AM 接口不同。所以接下来对比下 Heap AM 如何实现这两个 Table AM 接口：

```c
/*
 * Insert a tuple from a slot into table AM routine.
 *
 * ...
 */
static inline void
table_tuple_insert(Relation rel, TupleTableSlot *slot, CommandId cid,
                   int options, struct BulkInsertStateData *bistate)
{
    rel->rd_tableam->tuple_insert(rel, slot, cid, options,
                                  bistate);
}

/*
 * Insert multiple tuples into a table.
 *
 * ...
 */
static inline void
table_multi_insert(Relation rel, TupleTableSlot **slots, int nslots,
                   CommandId cid, int options, struct BulkInsertStateData *bistate)
{
    rel->rd_tableam->multi_insert(rel, slots, nslots,
                                  cid, options, bistate);
}

/* ------------------------------------------------------------------------
 * Definition of the heap table access method.
 * ------------------------------------------------------------------------
 */

static const TableAmRoutine heapam_methods = {
    .type = T_TableAmRoutine,

    /* ... */
    .tuple_insert = heapam_tuple_insert,
    /* ... */
    .multi_insert = heap_multi_insert,
    /* ... */
};
```

Heap AM 通过 `heapam_tuple_insert` 函数实现了 `tuple_insert` 接口，主要逻辑位于 `heap_insert` 函数中。输入的 `TupleTableSlot` 此时还是一个纯内存状态的元组，在它能够被真正插入表之前，还需要做几件事：

1. `heap_prepare_insert`：填充元组头部的标志位、事务 ID 等用于 MVCC 可见性判断的信息
2. `RelationGetBufferForTuple`：找一个能够放得下这个元组的数据页，并锁定；如果找不到任何空闲页面，则将物理文件扩展一个新页面
3. `RelationPutHeapTuple`：将元组放入数据页对应的 buffer 中，并把这个 buffer 标记为脏页
4. 将这一行元组的修改记录到 WAL 日志中
5. 释放锁

```c
/*
 *  heap_insert     - insert tuple into a heap
 *
 * The new tuple is stamped with current transaction ID and the specified
 * command ID.
 *
 * See table_tuple_insert for comments about most of the input flags, except
 * that this routine directly takes a tuple rather than a slot.
 *
 * There's corresponding HEAP_INSERT_ options to all the TABLE_INSERT_
 * options, and there additionally is HEAP_INSERT_SPECULATIVE which is used to
 * implement table_tuple_insert_speculative().
 *
 * On return the header fields of *tup are updated to match the stored tuple;
 * in particular tup->t_self receives the actual TID where the tuple was
 * stored.  But note that any toasting of fields within the tuple data is NOT
 * reflected into *tup.
 */
void
heap_insert(Relation relation, HeapTuple tup, CommandId cid,
            int options, BulkInsertState bistate)
{
    /* ... */

    /*
     * Fill in tuple header fields and toast the tuple if necessary.
     *
     * Note: below this point, heaptup is the data we actually intend to store
     * into the relation; tup is the caller's original untoasted data.
     */
    heaptup = heap_prepare_insert(relation, tup, xid, cid, options);

    /*
     * Find buffer to insert this tuple into.  If the page is all visible,
     * this will also pin the requisite visibility map page.
     */
    buffer = RelationGetBufferForTuple(relation, heaptup->t_len,
                                       InvalidBuffer, options, bistate,
                                       &vmbuffer, NULL,
                                       0);

    /* ... */

    /* NO EREPORT(ERROR) from here till changes are logged */
    START_CRIT_SECTION();

    RelationPutHeapTuple(relation, buffer, heaptup,
                         (options & HEAP_INSERT_SPECULATIVE) != 0);

    /* ... */

    /*
     * XXX Should we set PageSetPrunable on this page ?
     *
     * The inserting transaction may eventually abort thus making this tuple
     * DEAD and hence available for pruning. Though we don't want to optimize
     * for aborts, if no other tuple in this page is UPDATEd/DELETEd, the
     * aborted tuple will never be pruned until next vacuum is triggered.
     *
     * If you do add PageSetPrunable here, add it in heap_xlog_insert too.
     */

    MarkBufferDirty(buffer);

    /* XLOG stuff */
    if (RelationNeedsWAL(relation))
    {
        /* ... */
    }

    END_CRIT_SECTION();

    UnlockReleaseBuffer(buffer);
    if (vmbuffer != InvalidBuffer)
        ReleaseBuffer(vmbuffer);

    /* ... */
}
```

另一边，`heap_multi_insert` 函数用于实现 `multi_insert` 这个 Table AM 接口。与前一个 Table AM 接口 `tuple_insert` 的区别是传入了一个 `TupleTableSlot` 数组。要将这些元组插入表中要做的事情也是类似的，但有一些区别：

1. 依旧需要通过 `heap_prepare_insert` 填充每一个待插入元组的头部
2. `heap_multi_insert_pages`：根据待插入的元组所需要的总空间和预期在每个数据页中保留的空闲空间，计算出插入这一批元组需要多少个页面的空间
3. 同样通过 `RelationGetBufferForTuple` 找到一个能够放下当前正在插入的元组的数据页，并锁定；如果已没有空闲页面了，则根据上一步计算出的空闲页面需求，一次性扩展物理文件到满足需求的长度
4. 依旧通过 `RelationPutHeapTuple` 将当前元组放入数据页对应的 buffer 中
5. 如果当前锁住的数据页还有空闲空间，则继续放入下一个待插入元组，直到元组全部已经插入完毕，或数据页中已经没有空闲空间为止
6. 将当前 buffer 标记为脏页
7. 将插入到这一个 buffer 内的所有元组记录到 WAL 日志中
8. 释放锁

```c
/*
 *  heap_multi_insert   - insert multiple tuples into a heap
 *
 * This is like heap_insert(), but inserts multiple tuples in one operation.
 * That's faster than calling heap_insert() in a loop, because when multiple
 * tuples can be inserted on a single page, we can write just a single WAL
 * record covering all of them, and only need to lock/unlock the page once.
 *
 * Note: this leaks memory into the current memory context. You can create a
 * temporary context before calling this, if that's a problem.
 */
void
heap_multi_insert(Relation relation, TupleTableSlot **slots, int ntuples,
                  CommandId cid, int options, BulkInsertState bistate)
{
    /* ... */

    saveFreeSpace = RelationGetTargetPageFreeSpace(relation,
                                                   HEAP_DEFAULT_FILLFACTOR);

    /* Toast and set header data in all the slots */
    heaptuples = palloc(ntuples * sizeof(HeapTuple));
    for (i = 0; i < ntuples; i++)
    {
        HeapTuple   tuple;

        tuple = ExecFetchSlotHeapTuple(slots[i], true, NULL);
        slots[i]->tts_tableOid = RelationGetRelid(relation);
        tuple->t_tableOid = slots[i]->tts_tableOid;
        heaptuples[i] = heap_prepare_insert(relation, tuple, xid, cid,
                                            options);
    }

    /* ... */

    ndone = 0;
    while (ndone < ntuples)
    {
        Buffer      buffer;
        bool        all_visible_cleared = false;
        bool        all_frozen_set = false;
        int         nthispage;

        CHECK_FOR_INTERRUPTS();

        /*
         * Compute number of pages needed to fit the to-be-inserted tuples in
         * the worst case.  This will be used to determine how much to extend
         * the relation by in RelationGetBufferForTuple(), if needed.  If we
         * filled a prior page from scratch, we can just update our last
         * computation, but if we started with a partially filled page,
         * recompute from scratch, the number of potentially required pages
         * can vary due to tuples needing to fit onto the page, page headers
         * etc.
         */
        if (ndone == 0 || !starting_with_empty_page)
        {
            npages = heap_multi_insert_pages(heaptuples, ndone, ntuples,
                                             saveFreeSpace);
            npages_used = 0;
        }
        else
            npages_used++;

        /*
         * Find buffer where at least the next tuple will fit.  If the page is
         * all-visible, this will also pin the requisite visibility map page.
         *
         * Also pin visibility map page if COPY FREEZE inserts tuples into an
         * empty page. See all_frozen_set below.
         */
        buffer = RelationGetBufferForTuple(relation, heaptuples[ndone]->t_len,
                                           InvalidBuffer, options, bistate,
                                           &vmbuffer, NULL,
                                           npages - npages_used);
        page = BufferGetPage(buffer);

        starting_with_empty_page = PageGetMaxOffsetNumber(page) == 0;

        if (starting_with_empty_page && (options & HEAP_INSERT_FROZEN))
            all_frozen_set = true;

        /* NO EREPORT(ERROR) from here till changes are logged */
        START_CRIT_SECTION();

        /*
         * RelationGetBufferForTuple has ensured that the first tuple fits.
         * Put that on the page, and then as many other tuples as fit.
         */
        RelationPutHeapTuple(relation, buffer, heaptuples[ndone], false);

        /* ... */

        for (nthispage = 1; ndone + nthispage < ntuples; nthispage++)
        {
            HeapTuple   heaptup = heaptuples[ndone + nthispage];

            if (PageGetHeapFreeSpace(page) < MAXALIGN(heaptup->t_len) + saveFreeSpace)
                break;

            RelationPutHeapTuple(relation, buffer, heaptup, false);

            /* ... */
        }

        /* ... */

        /*
         * XXX Should we set PageSetPrunable on this page ? See heap_insert()
         */

        MarkBufferDirty(buffer);

        /* XLOG stuff */
        if (needwal)
        {
            /* ... */
        }

        END_CRIT_SECTION();

        /* ... */

        UnlockReleaseBuffer(buffer);
        ndone += nthispage;

        /*
         * NB: Only release vmbuffer after inserting all tuples - it's fairly
         * likely that we'll insert into subsequent heap pages that are likely
         * to use the same vm page.
         */
    }

    /* We're done with inserting all tuples, so release the last vmbuffer. */
    if (vmbuffer != InvalidBuffer)
        ReleaseBuffer(vmbuffer);

    /* ... */
}
```

对比上述两种实现，当批量插入多行数据时，`heap_multi_insert` 比 `heap_insert` 更具优势。

首先是物理文件的扩展频率变低了。在调用 `RelationGetBufferForTuple` 函数之前，`heap_multi_insert` 中已经预计算了这一批元组所需要的整体空闲空间。当表中找不到任何有空闲空间的数据页而必须扩展文件长度时，`heap_multi_insert` 可以一次性扩展多个页面。扩展页面是一个同步路径上的 I/O 操作，受到 I/O 时延的影响；并且在做页面扩展时是需要互斥加锁的。所以页面扩展的频率越低，浪费在 I/O 等待上的时间就越少，多进程扩展页面时的加锁冲突也越少。

```c
Buffer
RelationGetBufferForTuple(Relation relation, Size len,
                          Buffer otherBuffer, int options,
                          BulkInsertState bistate,
                          Buffer *vmbuffer, Buffer *vmbuffer_other,
                          int num_pages)
{
    /* ... */

    /* Have to extend the relation */
    buffer = RelationAddBlocks(relation, bistate, num_pages, use_fsm,
                               &unlockedTargetBuffer);

    /* ... */
}

/*
 * Implementation of ExtendBufferedRelBy() and ExtendBufferedRelTo() for
 * shared buffers.
 */
static BlockNumber
ExtendBufferedRelShared(BufferManagerRelation bmr,
                        ForkNumber fork,
                        BufferAccessStrategy strategy,
                        uint32 flags,
                        uint32 extend_by,
                        BlockNumber extend_upto,
                        Buffer *buffers,
                        uint32 *extended_by)
{
    /* ... */

    /*
     * Lock relation against concurrent extensions, unless requested not to.
     *
     * We use the same extension lock for all forks. That's unnecessarily
     * restrictive, but currently extensions for forks don't happen often
     * enough to make it worth locking more granularly.
     *
     * Note that another backend might have extended the relation by the time
     * we get the lock.
     */
    if (!(flags & EB_SKIP_EXTENSION_LOCK))
        LockRelationForExtension(bmr.rel, ExclusiveLock);

    /*
     * If requested, invalidate size cache, so that smgrnblocks asks the
     * kernel.
     */
    if (flags & EB_CLEAR_SIZE_CACHE)
        bmr.smgr->smgr_cached_nblocks[fork] = InvalidBlockNumber;

    first_block = smgrnblocks(bmr.smgr, fork);

    /* ... */

    /*
     * Note: if smgrzeroextend fails, we will end up with buffers that are
     * allocated but not marked BM_VALID.  The next relation extension will
     * still select the same block number (because the relation didn't get any
     * longer on disk) and so future attempts to extend the relation will find
     * the same buffers (if they have not been recycled) but come right back
     * here to try smgrzeroextend again.
     *
     * We don't need to set checksum for all-zero pages.
     */
    smgrzeroextend(bmr.smgr, fork, first_block, extend_by, false);

    /*
     * Release the file-extension lock; it's now OK for someone else to extend
     * the relation some more.
     *
     * We remove IO_IN_PROGRESS after this, as waking up waiting backends can
     * take noticeable time.
     */
    if (!(flags & EB_SKIP_EXTENSION_LOCK))
        UnlockRelationForExtension(bmr.rel, ExclusiveLock);

    /* ... */
}
```

其次是页面空闲空间的搜索代价和数据页的锁定频率也变低了。为了找到一个具有足够空间放入当前元组的数据页，需要使用 [Free Space Map (FSM)](https://www.postgresql.org/docs/current/storage-fsm.html)，但 FSM 中的信息不一定是准确的。在找到一个目标数据页以后，必须对这个页面加锁，然后查看这个页面的空闲空间是否真的足够。如果不够，还需要把锁释放掉并更新 FSM，然后重新搜索。这个过程中数据页面和 FSM 页面都会有较多的锁竞争。而 `heap_multi_insert` 中，在锁住一个确认能够放得下当前元组的数据页后，还会将后续的元组也一次性插入到这个页面上，直到这个页面放不下。对于插入到这个页面内的后续元组来说，空闲空间搜索和页面锁定的开销就被省掉了。

```c
Buffer
RelationGetBufferForTuple(Relation relation, Size len,
                          Buffer otherBuffer, int options,
                          BulkInsertState bistate,
                          Buffer *vmbuffer, Buffer *vmbuffer_other,
                          int num_pages)
{
    bool        use_fsm = !(options & HEAP_INSERT_SKIP_FSM);

    /* ... */

    /* Compute desired extra freespace due to fillfactor option */
    saveFreeSpace = RelationGetTargetPageFreeSpace(relation,
                                                   HEAP_DEFAULT_FILLFACTOR);

    /* ... */

    /*
     * We first try to put the tuple on the same page we last inserted a tuple
     * on, as cached in the BulkInsertState or relcache entry.  If that
     * doesn't work, we ask the Free Space Map to locate a suitable page.
     * Since the FSM's info might be out of date, we have to be prepared to
     * loop around and retry multiple times. (To ensure this isn't an infinite
     * loop, we must update the FSM with the correct amount of free space on
     * each page that proves not to be suitable.)  If the FSM has no record of
     * a page with enough free space, we give up and extend the relation.
     *
     * When use_fsm is false, we either put the tuple onto the existing target
     * page or extend the relation.
     */
    if (bistate && bistate->current_buf != InvalidBuffer)
        targetBlock = BufferGetBlockNumber(bistate->current_buf);
    else
        targetBlock = RelationGetTargetBlock(relation);

    if (targetBlock == InvalidBlockNumber && use_fsm)
    {
        /*
         * We have no cached target page, so ask the FSM for an initial
         * target.
         */
        targetBlock = GetPageWithFreeSpace(relation, targetFreeSpace);
    }

    /*
     * If the FSM knows nothing of the rel, try the last page before we give
     * up and extend.  This avoids one-tuple-per-page syndrome during
     * bootstrapping or in a recently-started system.
     */
    if (targetBlock == InvalidBlockNumber)
    {
        BlockNumber nblocks = RelationGetNumberOfBlocks(relation);

        if (nblocks > 0)
            targetBlock = nblocks - 1;
    }

loop:
    while (targetBlock != InvalidBlockNumber)
    {
        /*
         * Read and exclusive-lock the target block, as well as the other
         * block if one was given, taking suitable care with lock ordering and
         * the possibility they are the same block.
         *
         * If the page-level all-visible flag is set, caller will need to
         * clear both that and the corresponding visibility map bit.  However,
         * by the time we return, we'll have x-locked the buffer, and we don't
         * want to do any I/O while in that state.  So we check the bit here
         * before taking the lock, and pin the page if it appears necessary.
         * Checking without the lock creates a risk of getting the wrong
         * answer, so we'll have to recheck after acquiring the lock.
         */
        if (otherBuffer == InvalidBuffer)
        {
            /* easy case */
            buffer = ReadBufferBI(relation, targetBlock, RBM_NORMAL, bistate);
            if (PageIsAllVisible(BufferGetPage(buffer)))
                visibilitymap_pin(relation, targetBlock, vmbuffer);

            /*
             * If the page is empty, pin vmbuffer to set all_frozen bit later.
             */
            if ((options & HEAP_INSERT_FROZEN) &&
                (PageGetMaxOffsetNumber(BufferGetPage(buffer)) == 0))
                visibilitymap_pin(relation, targetBlock, vmbuffer);

            LockBuffer(buffer, BUFFER_LOCK_EXCLUSIVE);
        }
        else if (otherBlock == targetBlock)
        {
            /* also easy case */
            buffer = otherBuffer;
            if (PageIsAllVisible(BufferGetPage(buffer)))
                visibilitymap_pin(relation, targetBlock, vmbuffer);
            LockBuffer(buffer, BUFFER_LOCK_EXCLUSIVE);
        }
        else if (otherBlock < targetBlock)
        {
            /* lock other buffer first */
            buffer = ReadBuffer(relation, targetBlock);
            if (PageIsAllVisible(BufferGetPage(buffer)))
                visibilitymap_pin(relation, targetBlock, vmbuffer);
            LockBuffer(otherBuffer, BUFFER_LOCK_EXCLUSIVE);
            LockBuffer(buffer, BUFFER_LOCK_EXCLUSIVE);
        }
        else
        {
            /* lock target buffer first */
            buffer = ReadBuffer(relation, targetBlock);
            if (PageIsAllVisible(BufferGetPage(buffer)))
                visibilitymap_pin(relation, targetBlock, vmbuffer);
            LockBuffer(buffer, BUFFER_LOCK_EXCLUSIVE);
            LockBuffer(otherBuffer, BUFFER_LOCK_EXCLUSIVE);
        }

        /* ... */

        pageFreeSpace = PageGetHeapFreeSpace(page);
        if (targetFreeSpace <= pageFreeSpace)
        {
            /* use this page as future insert target, too */
            RelationSetTargetBlock(relation, targetBlock);
            return buffer;
        }

        /*
         * Not enough space, so we must give up our page locks and pin (if
         * any) and prepare to look elsewhere.  We don't care which order we
         * unlock the two buffers in, so this can be slightly simpler than the
         * code above.
         */
        LockBuffer(buffer, BUFFER_LOCK_UNLOCK);
        if (otherBuffer == InvalidBuffer)
            ReleaseBuffer(buffer);
        else if (otherBlock != targetBlock)
        {
            LockBuffer(otherBuffer, BUFFER_LOCK_UNLOCK);
            ReleaseBuffer(buffer);
        }

        /* Is there an ongoing bulk extension? */
        if (bistate && bistate->next_free != InvalidBlockNumber)
        {
            Assert(bistate->next_free <= bistate->last_free);

            /*
             * We bulk extended the relation before, and there are still some
             * unused pages from that extension, so we don't need to look in
             * the FSM for a new page. But do record the free space from the
             * last page, somebody might insert narrower tuples later.
             */
            if (use_fsm)
                RecordPageWithFreeSpace(relation, targetBlock, pageFreeSpace);

            targetBlock = bistate->next_free;
            if (bistate->next_free >= bistate->last_free)
            {
                bistate->next_free = InvalidBlockNumber;
                bistate->last_free = InvalidBlockNumber;
            }
            else
                bistate->next_free++;
        }
        else if (!use_fsm)
        {
            /* Without FSM, always fall out of the loop and extend */
            break;
        }
        else
        {
            /*
             * Update FSM as to condition of this page, and ask for another
             * page to try.
             */
            targetBlock = RecordAndGetPageWithFreeSpace(relation,
                                                        targetBlock,
                                                        pageFreeSpace,
                                                        targetFreeSpace);
        }
    }

    /* ... */
}
```

## WAL 日志

在上面两个 Heap AM 函数的分析中，记录 WAL 日志的部分被我暂时隐去了。在 WAL 日志层面，两者最显著的区别是，`heap_multi_insert` 需要记录一个页面上插入的多个元组，而 `heap_insert` 只需要记录一个页面上插入的一个元组。

`heap_insert` 通过插入一条 `XLOG_HEAP_INSERT` 类型的 Heap 日志记录对页面的修改：

```c
void
heap_insert(Relation relation, HeapTuple tup, CommandId cid,
            int options, BulkInsertState bistate)
{
    /* ... */

    /* XLOG stuff */
    if (RelationNeedsWAL(relation))
    {
        /* ... */
        uint8       info = XLOG_HEAP_INSERT;
        /* ... */

        XLogBeginInsert();
        XLogRegisterData((char *) &xlrec, SizeOfHeapInsert);

        xlhdr.t_infomask2 = heaptup->t_data->t_infomask2;
        xlhdr.t_infomask = heaptup->t_data->t_infomask;
        xlhdr.t_hoff = heaptup->t_data->t_hoff;

        /*
         * note we mark xlhdr as belonging to buffer; if XLogInsert decides to
         * write the whole page to the xlog, we don't need to store
         * xl_heap_header in the xlog.
         */
        XLogRegisterBuffer(0, buffer, REGBUF_STANDARD | bufflags);
        XLogRegisterBufData(0, (char *) &xlhdr, SizeOfHeapHeader);
        /* PG73FORMAT: write bitmap [+ padding] [+ oid] + data */
        XLogRegisterBufData(0,
                            (char *) heaptup->t_data + SizeofHeapTupleHeader,
                            heaptup->t_len - SizeofHeapTupleHeader);

        /* filtering by origin on a row level is much more efficient */
        XLogSetRecordFlags(XLOG_INCLUDE_ORIGIN);

        recptr = XLogInsert(RM_HEAP_ID, info);

        PageSetLSN(page, recptr);
    }

    /* ... */
}
```

而 `heap_multi_insert` 并不是通过多条 Heap 日志来记录在页面中插入的多行数据，而是通过记录一条 `XLOG_HEAP2_MULTI_INSERT` 类型的 Heap2 日志，一次搞定。

```c
void
heap_multi_insert(Relation relation, TupleTableSlot **slots, int ntuples,
                  CommandId cid, int options, BulkInsertState bistate)
{
    /* ... */

    ndone = 0;
    while (ndone < ntuples)
    {
        /* ... */

        /* XLOG stuff */
        if (needwal)
        {
            /* ... */
            uint8       info = XLOG_HEAP2_MULTI_INSERT;
            /* ... */

            /*
             * Write out an xl_multi_insert_tuple and the tuple data itself
             * for each tuple.
             */
            for (i = 0; i < nthispage; i++)
            {
                HeapTuple   heaptup = heaptuples[ndone + i];
                xl_multi_insert_tuple *tuphdr;
                int         datalen;

                if (!init)
                    xlrec->offsets[i] = ItemPointerGetOffsetNumber(&heaptup->t_self);
                /* xl_multi_insert_tuple needs two-byte alignment. */
                tuphdr = (xl_multi_insert_tuple *) SHORTALIGN(scratchptr);
                scratchptr = ((char *) tuphdr) + SizeOfMultiInsertTuple;

                tuphdr->t_infomask2 = heaptup->t_data->t_infomask2;
                tuphdr->t_infomask = heaptup->t_data->t_infomask;
                tuphdr->t_hoff = heaptup->t_data->t_hoff;

                /* write bitmap [+ padding] [+ oid] + data */
                datalen = heaptup->t_len - SizeofHeapTupleHeader;
                memcpy(scratchptr,
                       (char *) heaptup->t_data + SizeofHeapTupleHeader,
                       datalen);
                tuphdr->datalen = datalen;
                scratchptr += datalen;
            }
            totaldatalen = scratchptr - tupledata;
            Assert((scratchptr - scratch.data) < BLCKSZ);

            /* ... */

            XLogBeginInsert();
            XLogRegisterData((char *) xlrec, tupledata - scratch.data);
            XLogRegisterBuffer(0, buffer, REGBUF_STANDARD | bufflags);

            XLogRegisterBufData(0, tupledata, totaldatalen);

            /* filtering by origin on a row level is much more efficient */
            XLogSetRecordFlags(XLOG_INCLUDE_ORIGIN);

            recptr = XLogInsert(RM_HEAP2_ID, info);

            PageSetLSN(page, recptr);
        }

        /* ... */
    }

    /* ... */
}
```

通过一些简单的 SQL，可以直观看到上述两种 WAL 日志记录方式的差异：

```sql
CREATE TABLE test (id int, txt text);

INSERT INTO test VALUES
    (1, '1'), (2, '2'), (3, '3'), (4, '4'),
    (5, '5'), (6, '6'), (7, '7'), (8, '8');

COPY test FROM stdin;
1	'1'
2	'2'
3	'3'
4	'4'
5	'5'
6	'6'
7	'7'
8	'8'
\.
```

通过 PostgreSQL 的 [`pg_waldump`](https://www.postgresql.org/docs/current/pgwaldump.html) 工具查看 WAL 日志记录，可以发现 `INSERT` 语句插入的每一行数据都被记录了一条 Heap 日志，而 `COPY` 用一条 Heap2 日志记录了这个页面上的所有插入行。

```
rmgr: Heap        len (rec/tot):     61/    61, tx:        785, lsn: 0/40BE21D0, prev 0/40BE20C0, desc: INSERT+INIT off: 1, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        786, lsn: 0/40BE2270, prev 0/40BE2238, desc: INSERT off: 2, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        787, lsn: 0/40BE22D8, prev 0/40BE22B0, desc: INSERT off: 3, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        788, lsn: 0/40BE2340, prev 0/40BE2318, desc: INSERT off: 4, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        789, lsn: 0/40BE23A8, prev 0/40BE2380, desc: INSERT off: 5, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        790, lsn: 0/40BE2410, prev 0/40BE23E8, desc: INSERT off: 6, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        791, lsn: 0/40BE2478, prev 0/40BE2450, desc: INSERT off: 7, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
rmgr: Heap        len (rec/tot):     61/    61, tx:        792, lsn: 0/40BE24E0, prev 0/40BE24B8, desc: INSERT off: 8, flags: 0x00, blkref #0: rel 1663/5/16412 blk 0
```

```
rmgr: Heap2       len (rec/tot):    194/   194, tx:        793, lsn: 0/40BE2548, prev 0/40BE2520, desc: MULTI_INSERT ntuples: 8, flags: 0x02, offsets: [9, 10, 11, 12, 13, 14, 15, 16], blkref #0: rel 1663/5/16412 blk 0
```

使用 PostgreSQL 的 [`pg_walinspect`](https://www.postgresql.org/docs/current/pgwalinspect.html) 插件可以查看每条 WAL 日志的详细信息：

```sql
=> CREATE EXTENSION IF NOT EXISTS pg_walinspect;
CREATE EXTENSION

=> SELECT * FROM pg_get_wal_record_info('0/40BE24E0');
-[ RECORD 1 ]----+--------------------------------------------
start_lsn        | 0/40BE24E0
end_lsn          | 0/40BE2520
prev_lsn         | 0/40BE24B8
xid              | 792
resource_manager | Heap
record_type      | INSERT
record_length    | 61
main_data_length | 3
fpi_length       | 0
description      | off: 8, flags: 0x00
block_ref        | blkref #0: rel 1663/5/16412 fork main blk 0

=> SELECT * FROM pg_get_wal_record_info('0/40BE2548');
-[ RECORD 1 ]----+------------------------------------------------------------------
start_lsn        | 0/40BE2548
end_lsn          | 0/40BE2610
prev_lsn         | 0/40BE2520
xid              | 793
resource_manager | Heap2
record_type      | MULTI_INSERT
record_length    | 194
main_data_length | 20
fpi_length       | 0
description      | ntuples: 8, flags: 0x02, offsets: [9, 10, 11, 12, 13, 14, 15, 16]
block_ref        | blkref #0: rel 1663/5/16412 fork main blk 0
```

从上面的结果可以看出，通过 `INSERT` 插入八行数据，需要占用 61 \* 8 = 488 字节；而通过 `COPY` 插入八行数据，只需要 194 字节。由此可见 Heap2 日志比 Heap 日志紧凑得多：特别是对于列比较窄的表来说，WAL 日志元信息所占的开销可能比实际数据还要多。使用 Heap2 日志能够有效减少冗余信息。

## 总结

`INSERT` 和 `COPY` 这两种数据插入方式，在执行器的算法、Table AM 的实现、WAL 日志的类型上都有明显的不同。在待插入行数较多时，后者有明显的优势。其实 PostgreSQL 内部还有很多隐式的数据导入，比如物化视图的创建和刷新，`CREATE TABLE AS` 等语法。这些地方目前依旧是使用与 `INSERT` 相同的算法实现的。

PostgreSQL 社区邮件列表从 2020 年就开始讨论将若干处代码路径改为使用内存元组攒批 + `heap_multi_insert` + Heap2 日志来实现。为了减少代码冗余，目前正在讨论的方案是将内存元组攒批下沉到 Table AM 层，对上层代码暴露几个新的 Table AM 接口。接入这条路径的代码只需要使用新的 Table AM 接口即可。目前看这套新的 Table AM 接口有希望合入 PostgreSQL 18/19。

## 参考资料

[WAL Internals of PostgreSQL](https://www.pgcon.org/2012/schedule/attachments/258_212_Internals%20Of%20PostgreSQL%20Wal.pdf)

[PostgreSQL: refactoring relation extension and BufferAlloc(), faster COPY](https://www.postgresql.org/message-id/flat/20221029025420.eplyow6k7tgu6he3%40awork3.anarazel.de)

[PostgreSQL: Multi Inserts in CREATE TABLE AS - revived patch](https://www.postgresql.org/message-id/flat/CALj2ACUr8Vnu3dMkiU47v-dh55tnY2Lr8m2xoSaRZeiCaNeVqQ%40mail.gmail.com)

[PostgreSQL: New Table Access Methods for Multi and Single Inserts](https://www.postgresql.org/message-id/flat/CALj2ACVi9eTRYR%3Dgdca5wxtj3Kk_9q9qVccxsS1hngTGOCjPwQ%40mail.gmail.com)
