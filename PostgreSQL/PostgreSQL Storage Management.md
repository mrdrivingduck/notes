# PostgreSQL - Storage Management

Created by: Mr Dk.

2024 / 07 / 26 20:26

Hangzhou, Zhejiang, China

---

## Background

PostgreSQL 对文件系统上所有表数据文件的操作全部通过存储管理层 (Storage Manager, Smgr) 提供的函数完成。[Smgr](https://doxygen.postgresql.org/smgr_8c.html) 函数集在语义上表示对表的逻辑文件进行操作，并提供了一套虚拟存储管理接口，由下层对接的物理存储管理引擎实现这套接口，完成对物理文件的实际操作，比如打开、关闭、读写等。类似于 Linux kernel 中的 VFS 之于各种各样的文件系统。

20 多年过去了，非易失性存储介质经历了从 HDD 到 SSD 的发展，而 PostgreSQL 中内置的依旧只有 [Magnetic Disk (md)](https://doxygen.postgresql.org/md_8c.html) 这一个物理存储管理引擎，如今依旧发光发热。

本文截止 PostgreSQL 17 正式发布前的代码版本，分析存储管理层各个接口的语义和用途。

## Virtual Storage Management Interface

逻辑存储管理层对接物理存储管理引擎的接口如下：

- `smgr_init`：初始化物理存储管理引擎，包括一些私有状态
- `smgr_shutdown`：关闭物理存储管理引擎
- `smgr_open`：打开表文件
- `smgr_close`：关闭表文件
- `smgr_create`：创建表文件
- `smgr_exists`：判断物理文件是否存在
- `smgr_unlink`：删除物理文件
- `smgr_extend`：扩展物理文件一个页面
- `smgr_zeroextend`：扩展物理文件多个全 0 页面
- `smgr_prefetch`：异步预取某个表的某个页面
- `smgr_readv`：读取表的某个页面
- `smgr_writev`：将表的某个页面写入文件
- `smgr_writeback`：使文件系统将指定范围内的页面 sync 到存储
- `smgr_nblocks`：返回物理文件中的块数量
- `smgr_truncate`：将物理文件截断到指定块数量
- `smgr_immedsync`：立刻将表的所有页面 sync 到存储
- `smgr_registersync`：将表的所有页面标记为需要被 sync 到存储（但不立刻开始）

```c
/*
 * This struct of function pointers defines the API between smgr.c and
 * any individual storage manager module.  Note that smgr subfunctions are
 * generally expected to report problems via elog(ERROR).  An exception is
 * that smgr_unlink should use elog(WARNING), rather than erroring out,
 * because we normally unlink relations during post-commit/abort cleanup,
 * and so it's too late to raise an error.  Also, various conditions that
 * would normally be errors should be allowed during bootstrap and/or WAL
 * recovery --- see comments in md.c for details.
 */
typedef struct f_smgr
{
    void        (*smgr_init) (void);    /* may be NULL */
    void        (*smgr_shutdown) (void);    /* may be NULL */
    void        (*smgr_open) (SMgrRelation reln);
    void        (*smgr_close) (SMgrRelation reln, ForkNumber forknum);
    void        (*smgr_create) (SMgrRelation reln, ForkNumber forknum,
                                bool isRedo);
    bool        (*smgr_exists) (SMgrRelation reln, ForkNumber forknum);
    void        (*smgr_unlink) (RelFileLocatorBackend rlocator, ForkNumber forknum,
                                bool isRedo);
    void        (*smgr_extend) (SMgrRelation reln, ForkNumber forknum,
                                BlockNumber blocknum, const void *buffer, bool skipFsync);
    void        (*smgr_zeroextend) (SMgrRelation reln, ForkNumber forknum,
                                    BlockNumber blocknum, int nblocks, bool skipFsync);
    bool        (*smgr_prefetch) (SMgrRelation reln, ForkNumber forknum,
                                  BlockNumber blocknum, int nblocks);
    void        (*smgr_readv) (SMgrRelation reln, ForkNumber forknum,
                               BlockNumber blocknum,
                               void **buffers, BlockNumber nblocks);
    void        (*smgr_writev) (SMgrRelation reln, ForkNumber forknum,
                                BlockNumber blocknum,
                                const void **buffers, BlockNumber nblocks,
                                bool skipFsync);
    void        (*smgr_writeback) (SMgrRelation reln, ForkNumber forknum,
                                   BlockNumber blocknum, BlockNumber nblocks);
    BlockNumber (*smgr_nblocks) (SMgrRelation reln, ForkNumber forknum);
    void        (*smgr_truncate) (SMgrRelation reln, ForkNumber forknum,
                                  BlockNumber nblocks);
    void        (*smgr_immedsync) (SMgrRelation reln, ForkNumber forknum);
    void        (*smgr_registersync) (SMgrRelation reln, ForkNumber forknum);
} f_smgr;
```

在这套虚拟存储管理接口下，目前 PostgreSQL 内置只有一个物理存储管理引擎独苗——Magnetic Disk：

```c
static const f_smgr smgrsw[] = {
    /* magnetic disk */
    {
        .smgr_init = mdinit,
        .smgr_shutdown = NULL,
        .smgr_open = mdopen,
        .smgr_close = mdclose,
        .smgr_create = mdcreate,
        .smgr_exists = mdexists,
        .smgr_unlink = mdunlink,
        .smgr_extend = mdextend,
        .smgr_zeroextend = mdzeroextend,
        .smgr_prefetch = mdprefetch,
        .smgr_readv = mdreadv,
        .smgr_writev = mdwritev,
        .smgr_writeback = mdwriteback,
        .smgr_nblocks = mdnblocks,
        .smgr_truncate = mdtruncate,
        .smgr_immedsync = mdimmedsync,
        .smgr_registersync = mdregistersync,
    }
};

static const int NSmgr = lengthof(smgrsw);
```

正如其名，这个物理存储管理引擎在 20 世纪 90 年代被设计为用于管理磁盘介质的非易失性存储（是真的 **磁** 盘）。与如今人们依旧非正式地用 _磁盘_ 这个词指代已经更新迭代了不知道多少轮的非易失性存储介质一样，Magnetic Disk 引擎也依旧管理着这 20 多年来日新月异的所有存储设备。PostgreSQL 社区近年一直在不断完善和细化 Smgr 层的虚拟存储管理接口和对应的 Magnetic Disk 实现，但短期内确实不像是有第二个物理存储管理引擎要出现的样子。当然目前各类的 PostgreSQL-fork 产品层出不穷，面向特定场景实现一套新的物理存储管理引擎就完全是各个产品的自由了。比如面向全内存、压缩、加密，都可以通过这层接口定制物理存储管理的细节。

## Implementation

有了对物理存储管理引擎的调用接口，在逻辑存储管理层还需要做哪些事？需要向更上层的其他数据库子模块提供什么样的接口？这些接口的用户都是哪些子模块？接下来逐个分析下逻辑存储管理层对外暴露的接口。

### smgrinit / smgrshutdown

存储管理引擎的初始化和关闭接口，直接调用物理存储管理引擎的 `smgr_init` 和 `smgr_shutdown`。PostgreSQL 目前是多进程架构的数据库，存储管理的初始化和关闭发生在新进程被 PostMaster 主进程 fork 出来后的进程初始化阶段，是每个进程独立的动作。

### smgropen

构造/复用一个 `SMgrRelationData` 存储层对象。这里并不意味着一定要在物理存储管理层打开一次物理文件：由于存储管理的初始化位于每一个进程内，每一个进程在私有内存中都会维护一张键值对为 `<RelFileLocatorBackend, SMgrRelationData>` 的哈希表，同时对其引用计数。因此进程对同一张表的重复 `smgropen` 不会重复创建 `SMgrRelationData` 结构，也不会在物理存储管理层反复打开物理文件。进程通常借助 RelCache 来调用 `smgropen`，并缓存对存储层对象的引用；当然一些后台进程及 DDL 操作也会绕开 RelCache 直接打开存储层对象。

根据 [社区邮件](https://www.postgresql.org/message-id/flat/CA%2BhUKGJ8NTvqLHz6dqbQnt2c8XCki4r2QvXjBQcXpVwxTY_pvA%40mail.gmail.com) 的讨论，PostgreSQL 17 开始对被 `smgropen` 后的存储层对象有了明确的 [生命周期定义](https://github.com/postgres/postgres/commit/21d9c3ee4ef74e2229341d39811c97f85071c90a)，保证事务结束前存储层对象不会失效。

```c
/*
 * smgropen() -- Return an SMgrRelation object, creating it if need be.
 *
 * In versions of PostgreSQL prior to 17, this function returned an object
 * with no defined lifetime.  Now, however, the object remains valid for the
 * lifetime of the transaction, up to the point where AtEOXact_SMgr() is
 * called, making it much easier for callers to know for how long they can
 * hold on to a pointer to the returned object.  If this function is called
 * outside of a transaction, the object remains valid until smgrdestroy() or
 * smgrdestroyall() is called.  Background processes that use smgr but not
 * transactions typically do this once per checkpoint cycle.
 *
 * This does not attempt to actually open the underlying files.
 */
SMgrRelation
smgropen(RelFileLocator rlocator, ProcNumber backend)
{
    RelFileLocatorBackend brlocator;
    SMgrRelation reln;
    bool        found;

    Assert(RelFileNumberIsValid(rlocator.relNumber));

    if (SMgrRelationHash == NULL)
    {
        /* First time through: initialize the hash table */
        HASHCTL     ctl;

        ctl.keysize = sizeof(RelFileLocatorBackend);
        ctl.entrysize = sizeof(SMgrRelationData);
        SMgrRelationHash = hash_create("smgr relation table", 400,
                                       &ctl, HASH_ELEM | HASH_BLOBS);
        dlist_init(&unpinned_relns);
    }

    /* Look up or create an entry */
    brlocator.locator = rlocator;
    brlocator.backend = backend;
    reln = (SMgrRelation) hash_search(SMgrRelationHash,
                                      &brlocator,
                                      HASH_ENTER, &found);

    /* Initialize it if not present before */
    if (!found)
    {
        /* hash_search already filled in the lookup key */
        reln->smgr_targblock = InvalidBlockNumber;
        for (int i = 0; i <= MAX_FORKNUM; ++i)
            reln->smgr_cached_nblocks[i] = InvalidBlockNumber;
        reln->smgr_which = 0;   /* we only have md.c at present */

        /* implementation-specific initialization */
        smgrsw[reln->smgr_which].smgr_open(reln);

        /* it is not pinned yet */
        reln->pincount = 0;
        dlist_push_tail(&unpinned_relns, &reln->node);
    }

    return reln;
}
```

### smgrpin / smgrunpin

增加或减少对存储层对象的引用计数。引用计数为 0 的存储层对象将会在事务结束时被销毁。其使用者为 RelCache。

```c
/*
 * RelationGetSmgr
 *      Returns smgr file handle for a relation, opening it if needed.
 *
 * Very little code is authorized to touch rel->rd_smgr directly.  Instead
 * use this function to fetch its value.
 */
static inline SMgrRelation
RelationGetSmgr(Relation rel)
{
    if (unlikely(rel->rd_smgr == NULL))
    {
        rel->rd_smgr = smgropen(rel->rd_locator, rel->rd_backend);
        smgrpin(rel->rd_smgr);
    }
    return rel->rd_smgr;
}

/*
 * RelationCloseSmgr
 *      Close the relation at the smgr level, if not already done.
 */
static inline void
RelationCloseSmgr(Relation relation)
{
    if (relation->rd_smgr != NULL)
    {
        smgrunpin(relation->rd_smgr);
        smgrclose(relation->rd_smgr);
        relation->rd_smgr = NULL;
    }
}
```

### smgrclose / smgrrelease / smgrreleaserellocator / smgrreleaseall

通过 `smgr_close` 关闭（特定/所有）存储层对象所打开的物理文件，但保留存储层对象不被销毁。其使用者为对存储层的操作已经结束或 RelCache 失效时的处理逻辑中。

```c
/*
 * smgrclose() -- Close an SMgrRelation object.
 *
 * The SMgrRelation reference should not be used after this call.  However,
 * because we don't keep track of the references returned by smgropen(), we
 * don't know if there are other references still pointing to the same object,
 * so we cannot remove the SMgrRelation object yet.  Therefore, this is just a
 * synonym for smgrrelease() at the moment.
 */
void
smgrclose(SMgrRelation reln)
{
    smgrrelease(reln);
}

/*
 * smgrrelease() -- Release all resources used by this object.
 *
 * The object remains valid.
 */
void
smgrrelease(SMgrRelation reln)
{
    for (ForkNumber forknum = 0; forknum <= MAX_FORKNUM; forknum++)
    {
        smgrsw[reln->smgr_which].smgr_close(reln, forknum);
        reln->smgr_cached_nblocks[forknum] = InvalidBlockNumber;
    }
    reln->smgr_targblock = InvalidBlockNumber;
}

/*
 * smgrreleaserellocator() -- Release resources for given RelFileLocator, if
 *                            it's open.
 *
 * This has the same effects as smgrrelease(smgropen(rlocator)), but avoids
 * uselessly creating a hashtable entry only to drop it again when no
 * such entry exists already.
 */
void
smgrreleaserellocator(RelFileLocatorBackend rlocator)
{
    SMgrRelation reln;

    /* Nothing to do if hashtable not set up */
    if (SMgrRelationHash == NULL)
        return;

    reln = (SMgrRelation) hash_search(SMgrRelationHash,
                                      &rlocator,
                                      HASH_FIND, NULL);
    if (reln != NULL)
        smgrrelease(reln);
}

/*
 * smgrreleaseall() -- Release resources used by all objects.
 */
void
smgrreleaseall(void)
{
    HASH_SEQ_STATUS status;
    SMgrRelation reln;

    /* Nothing to do if hashtable not set up */
    if (SMgrRelationHash == NULL)
        return;

    hash_seq_init(&status, SMgrRelationHash);

    while ((reln = (SMgrRelation) hash_seq_search(&status)) != NULL)
    {
        smgrrelease(reln);
    }
}
```

### smgrdestroyall

对于所有未被 pin 住的存储层对象，不仅关闭其物理文件，还销毁存储层对象本身。其使用者为事务结束时，或做完 CHECKPOINT 后。

```c
/*
 * smgrdestroy() -- Delete an SMgrRelation object.
 */
static void
smgrdestroy(SMgrRelation reln)
{
    ForkNumber  forknum;

    Assert(reln->pincount == 0);

    for (forknum = 0; forknum <= MAX_FORKNUM; forknum++)
        smgrsw[reln->smgr_which].smgr_close(reln, forknum);

    dlist_delete(&reln->node);

    if (hash_search(SMgrRelationHash,
                    &(reln->smgr_rlocator),
                    HASH_REMOVE, NULL) == NULL)
        elog(ERROR, "SMgrRelation hashtable corrupted");
}

/*
 * smgrdestroyall() -- Release resources used by all unpinned objects.
 *
 * It must be known that there are no pointers to SMgrRelations, other than
 * those pinned with smgrpin().
 */
void
smgrdestroyall(void)
{
    dlist_mutable_iter iter;

    /*
     * Zap all unpinned SMgrRelations.  We rely on smgrdestroy() to remove
     * each one from the list.
     */
    dlist_foreach_modify(iter, &unpinned_relns)
    {
        SMgrRelation rel = dlist_container(SMgrRelationData, node,
                                           iter.cur);

        smgrdestroy(rel);
    }
}

/*
 * AtEOXact_SMgr
 *
 * This routine is called during transaction commit or abort (it doesn't
 * particularly care which).  All unpinned SMgrRelation objects are destroyed.
 *
 * We do this as a compromise between wanting transient SMgrRelations to
 * live awhile (to amortize the costs of blind writes of multiple blocks)
 * and needing them to not live forever (since we're probably holding open
 * a kernel file descriptor for the underlying file, and we need to ensure
 * that gets closed reasonably soon if the file gets deleted).
 */
void
AtEOXact_SMgr(void)
{
    smgrdestroyall();
}
```

### smgrexists / smgrcreate

判断对应的物理文件是否存在 / 创建对应的物理文件。通常一起使用。其使用者为创建数据库、创建表、创建索引以及对应的 WAL 日志回放逻辑中。

### smgrimmedsync / smgrdosyncall

使特定表在内存中的 buffer 全部写入文件，然后立刻 sync 到存储上。其使用者为事务结束时或者批量导入结束时。

```c
/*
 * smgrimmedsync() -- Force the specified relation to stable storage.
 *
 * Synchronously force all previous writes to the specified relation
 * down to disk.
 *
 * This is useful for building completely new relations (eg, new
 * indexes).  Instead of incrementally WAL-logging the index build
 * steps, we can just write completed index pages to disk with smgrwrite
 * or smgrextend, and then fsync the completed index file before
 * committing the transaction.  (This is sufficient for purposes of
 * crash recovery, since it effectively duplicates forcing a checkpoint
 * for the completed index.  But it is *not* sufficient if one wishes
 * to use the WAL log for PITR or replication purposes: in that case
 * we have to make WAL entries as well.)
 *
 * The preceding writes should specify skipFsync = true to avoid
 * duplicative fsyncs.
 *
 * Note that you need to do FlushRelationBuffers() first if there is
 * any possibility that there are dirty buffers for the relation;
 * otherwise the sync is not very meaningful.
 *
 * Most callers should use the bulk loading facility in bulk_write.c
 * instead of calling this directly.
 */
void
smgrimmedsync(SMgrRelation reln, ForkNumber forknum)
{
    smgrsw[reln->smgr_which].smgr_immedsync(reln, forknum);
}

/*
 * smgrdosyncall() -- Immediately sync all forks of all given relations
 *
 * All forks of all given relations are synced out to the store.
 *
 * This is equivalent to FlushRelationBuffers() for each smgr relation,
 * then calling smgrimmedsync() for all forks of each relation, but it's
 * significantly quicker so should be preferred when possible.
 */
void
smgrdosyncall(SMgrRelation *rels, int nrels)
{
    int         i = 0;
    ForkNumber  forknum;

    if (nrels == 0)
        return;

    FlushRelationsAllBuffers(rels, nrels);

    /*
     * Sync the physical file(s).
     */
    for (i = 0; i < nrels; i++)
    {
        int         which = rels[i]->smgr_which;

        for (forknum = 0; forknum <= MAX_FORKNUM; forknum++)
        {
            if (smgrsw[which].smgr_exists(rels[i], forknum))
                smgrsw[which].smgr_immedsync(rels[i], forknum);
        }
    }
}
```

### smgrwriteback

将某个表的特定数据块 sync 到存储上。其使用者为将 Buffer Cache 中的脏页刷回存储时。

```c
/*
 * smgrwriteback() -- Trigger kernel writeback for the supplied range of
 *                     blocks.
 */
void
smgrwriteback(SMgrRelation reln, ForkNumber forknum, BlockNumber blocknum,
              BlockNumber nblocks)
{
    smgrsw[reln->smgr_which].smgr_writeback(reln, forknum, blocknum,
                                            nblocks);
}
```

### smgrregistersync

将特定表注册到下一次 CHECKPOINT 要 sync 到存储的对象中。其使用者目前为批量导入。

### smgrdounlinkall

立刻删除所有给定表对应的所有物理文件。其使用者为事务结束时删除不再需要的表文件

首先从 Buffer Cache 中清除待删除表对应的 buffer，然后解除对所有待清除表物理文件的引用，同时也同步向其它进程发送消息解除对该存储层对象的引用，最终删除物理文件。

```c
/*
 * smgrdounlinkall() -- Immediately unlink all forks of all given relations
 *
 * All forks of all given relations are removed from the store.  This
 * should not be used during transactional operations, since it can't be
 * undone.
 *
 * If isRedo is true, it is okay for the underlying file(s) to be gone
 * already.
 */
void
smgrdounlinkall(SMgrRelation *rels, int nrels, bool isRedo)
{
    int         i = 0;
    RelFileLocatorBackend *rlocators;
    ForkNumber  forknum;

    if (nrels == 0)
        return;

    /*
     * Get rid of any remaining buffers for the relations.  bufmgr will just
     * drop them without bothering to write the contents.
     */
    DropRelationsAllBuffers(rels, nrels);

    /*
     * create an array which contains all relations to be dropped, and close
     * each relation's forks at the smgr level while at it
     */
    rlocators = palloc(sizeof(RelFileLocatorBackend) * nrels);
    for (i = 0; i < nrels; i++)
    {
        RelFileLocatorBackend rlocator = rels[i]->smgr_rlocator;
        int         which = rels[i]->smgr_which;

        rlocators[i] = rlocator;

        /* Close the forks at smgr level */
        for (forknum = 0; forknum <= MAX_FORKNUM; forknum++)
            smgrsw[which].smgr_close(rels[i], forknum);
    }

    /*
     * Send a shared-inval message to force other backends to close any
     * dangling smgr references they may have for these rels.  We should do
     * this before starting the actual unlinking, in case we fail partway
     * through that step.  Note that the sinval messages will eventually come
     * back to this backend, too, and thereby provide a backstop that we
     * closed our own smgr rel.
     */
    for (i = 0; i < nrels; i++)
        CacheInvalidateSmgr(rlocators[i]);

    /*
     * Delete the physical file(s).
     *
     * Note: smgr_unlink must treat deletion failure as a WARNING, not an
     * ERROR, because we've already decided to commit or abort the current
     * xact.
     */

    for (i = 0; i < nrels; i++)
    {
        int         which = rels[i]->smgr_which;

        for (forknum = 0; forknum <= MAX_FORKNUM; forknum++)
            smgrsw[which].smgr_unlink(rlocators[i], forknum, isRedo);
    }

    pfree(rlocators);
}
```

### smgrextend / smgrzeroextend

用于将特定表的特定文件扩展到指定长度，语义上认为扩展后的文件在文件结尾之前的内容都是 0。其使用者为批量导入、缓冲区管理层分配新 buffer。

`smgrzeroextend` 是 PostgreSQL 16 中 [新引入的接口](https://github.com/postgres/postgres/commit/4d330a61bb1969df31f2cebfe1ba9d1d004346d8)，相比于 `smgrextend` 一次只能扩展一个页面，`smgrzeroextend` 可以一次扩展多个页面。根据 [社区邮件](https://www.postgresql.org/message-id/flat/20221029025420.eplyow6k7tgu6he3%40awork3.anarazel.de) 的讨论，`smgrzeroextend` 使用 `posix_fallocate()` 扩展页面，不会在 OS page cache 中产生脏页。另外一次扩展多个页面能够降低扩展物理文件时的加锁冲突。

```c
/*
 * smgrextend() -- Add a new block to a file.
 *
 * The semantics are nearly the same as smgrwrite(): write at the
 * specified position.  However, this is to be used for the case of
 * extending a relation (i.e., blocknum is at or beyond the current
 * EOF).  Note that we assume writing a block beyond current EOF
 * causes intervening file space to become filled with zeroes.
 */
void
smgrextend(SMgrRelation reln, ForkNumber forknum, BlockNumber blocknum,
           const void *buffer, bool skipFsync)
{
    smgrsw[reln->smgr_which].smgr_extend(reln, forknum, blocknum,
                                         buffer, skipFsync);

    /*
     * Normally we expect this to increase nblocks by one, but if the cached
     * value isn't as expected, just invalidate it so the next call asks the
     * kernel.
     */
    if (reln->smgr_cached_nblocks[forknum] == blocknum)
        reln->smgr_cached_nblocks[forknum] = blocknum + 1;
    else
        reln->smgr_cached_nblocks[forknum] = InvalidBlockNumber;
}

/*
 * smgrzeroextend() -- Add new zeroed out blocks to a file.
 *
 * Similar to smgrextend(), except the relation can be extended by
 * multiple blocks at once and the added blocks will be filled with
 * zeroes.
 */
void
smgrzeroextend(SMgrRelation reln, ForkNumber forknum, BlockNumber blocknum,
               int nblocks, bool skipFsync)
{
    smgrsw[reln->smgr_which].smgr_zeroextend(reln, forknum, blocknum,
                                             nblocks, skipFsync);

    /*
     * Normally we expect this to increase the fork size by nblocks, but if
     * the cached value isn't as expected, just invalidate it so the next call
     * asks the kernel.
     */
    if (reln->smgr_cached_nblocks[forknum] == blocknum)
        reln->smgr_cached_nblocks[forknum] = blocknum + nblocks;
    else
        reln->smgr_cached_nblocks[forknum] = InvalidBlockNumber;
}
```

### smgrtruncate

将指定表的文件截断到指定长度。其使用者为 VACUUM，在做完对表或索引的清理后，截断物理文件尾部的未使用空间。

首先从 Buffer Cache 中清除待删除的文件块对应的 buffer，同时也同步向其它进程发送消息解除对该存储对象的引用，最终截断物理文件。

```c
/*
 * smgrtruncate() -- Truncate the given forks of supplied relation to
 *                   each specified numbers of blocks
 *
 * The truncation is done immediately, so this can't be rolled back.
 *
 * The caller must hold AccessExclusiveLock on the relation, to ensure that
 * other backends receive the smgr invalidation event that this function sends
 * before they access any forks of the relation again.
 */
void
smgrtruncate(SMgrRelation reln, ForkNumber *forknum, int nforks, BlockNumber *nblocks)
{
    int         i;

    /*
     * Get rid of any buffers for the about-to-be-deleted blocks. bufmgr will
     * just drop them without bothering to write the contents.
     */
    DropRelationBuffers(reln, forknum, nforks, nblocks);

    /*
     * Send a shared-inval message to force other backends to close any smgr
     * references they may have for this rel.  This is useful because they
     * might have open file pointers to segments that got removed, and/or
     * smgr_targblock variables pointing past the new rel end.  (The inval
     * message will come back to our backend, too, causing a
     * probably-unnecessary local smgr flush.  But we don't expect that this
     * is a performance-critical path.)  As in the unlink code, we want to be
     * sure the message is sent before we start changing things on-disk.
     */
    CacheInvalidateSmgr(reln->smgr_rlocator);

    /* Do the truncation */
    for (i = 0; i < nforks; i++)
    {
        /* Make the cached size is invalid if we encounter an error. */
        reln->smgr_cached_nblocks[forknum[i]] = InvalidBlockNumber;

        smgrsw[reln->smgr_which].smgr_truncate(reln, forknum[i], nblocks[i]);

        /*
         * We might as well update the local smgr_cached_nblocks values. The
         * smgr cache inval message that this function sent will cause other
         * backends to invalidate their copies of smgr_fsm_nblocks and
         * smgr_vm_nblocks, and these ones too at the next command boundary.
         * But these ensure they aren't outright wrong until then.
         */
        reln->smgr_cached_nblocks[forknum[i]] = nblocks[i];
    }
}
```

### smgrreadv / smgrwritev

向量化地读取或写入一定范围的 buffer。其使用者为缓冲区管理模块，更上层使用者为需要一次读取多个 buffer 的场景，比如顺序扫描。

### smgrnblocks / smgrnblocks_cached

获取物理文件中的数据块数量，本质上为获取文件长度后除以数据块大小。其使用者为：

- 缓冲区管理模块读取数据块时
- 物理文件的拷贝/扩展时
- 优化器的代价估算时

`smgrnblocks` 会将结果缓存在进程私有内存中，`smgrnblocks_cached` 将会直接返回上一次调用 `smgrnblocks` 的缓存值。根据 [社区邮件](https://www.postgresql.org/message-id/flat/CAEepm%3D3SSw-Ty1DFcK%3D1rU-K6GSzYzfdD4d%2BZwapdN7dTa6%3DnQ%40mail.gmail.com) 的讨论，频繁调用 `smgrnblocks`（本质上是对物理文件的 `lseek(SEEK_END)`）将会对性能有一定影响，但目前又缺少文件长度发生变化时的同步机制，所以暂时只在 [recovery 阶段使用缓存值](https://github.com/postgres/postgres/commit/c5315f4f44843c20ada876fdb0d0828795dfbdf5)，因为此时是单进程执行的。在文件大小发生变化的存储管理层接口中（extend / truncate），也需要同步更新这个缓存值，或直接使这个缓存值失效。

```c
/*
 * smgrnblocks() -- Calculate the number of blocks in the
 *                  supplied relation.
 */
BlockNumber
smgrnblocks(SMgrRelation reln, ForkNumber forknum)
{
    BlockNumber result;

    /* Check and return if we get the cached value for the number of blocks. */
    result = smgrnblocks_cached(reln, forknum);
    if (result != InvalidBlockNumber)
        return result;

    result = smgrsw[reln->smgr_which].smgr_nblocks(reln, forknum);

    reln->smgr_cached_nblocks[forknum] = result;

    return result;
}

/*
 * smgrnblocks_cached() -- Get the cached number of blocks in the supplied
 *                         relation.
 *
 * Returns an InvalidBlockNumber when not in recovery and when the relation
 * fork size is not cached.
 */
BlockNumber
smgrnblocks_cached(SMgrRelation reln, ForkNumber forknum)
{
    /*
     * For now, this function uses cached values only in recovery due to lack
     * of a shared invalidation mechanism for changes in file size.  Code
     * elsewhere reads smgr_cached_nblocks and copes with stale data.
     */
    if (InRecovery && reln->smgr_cached_nblocks[forknum] != InvalidBlockNumber)
        return reln->smgr_cached_nblocks[forknum];

    return InvalidBlockNumber;
}
```

另一个很有意思的讨论发生在 2011 年，Robert Haas 发起了对获取文件长度使用 `lseek` 还是 `fstat` 更快的 [讨论](https://www.postgresql.org/message-id/flat/CA%2BTgmoawRfpan35wzvgHkSJ0%2Bi-W%3DVkJpKnRxK2kTDR%2BHsanWA%40mail.gmail.com)。两者都能够达到获取文件长度的目的，但他在测试中发现 `lseek` 在并发数较高场景下扩展性差于 `fstat`。同年，Intel 的工程师 Andi Kleen 向 Linux VFS 提交了优化 `lseek` 加锁模式的 [补丁](https://lore.kernel.org/linux-fsdevel/1314046152-2175-3-git-send-email-andi@firstfloor.org/)，对于 `SEEK_END` 不再需要加锁：

> SEEK_END: This behaves like SEEK_SET plus it reads the maximum size too. Reading the maximum size would have the 32bit atomic problem. But luckily we already have a way to read the maximum size without locking (i_size_read), so we can just use that instead.
>
> &nbsp;
>
> Without i_mutex there is no synchronization with write() anymore, however since the write() update is atomic on 64bit it just behaves like another racy SEEK_SET. On non atomic 32bit it's the same as SEEK_SET.
>
> &nbsp;
>
> => Don't need a lock, but need to use i_size_read()

对照看了下目前最新的 Linux kernel 代码依旧如此，对于 `SEEK_END` 不再需要对 inode 加锁了。如下代码片段严格遵循 Linux kernel 一个 Tab 等于八个空格的代码风格：

```c:no-line-numbers
/*
 * ext4_llseek() handles both block-mapped and extent-mapped maxbytes values
 * by calling generic_file_llseek_size() with the appropriate maxbytes
 * value for each.
 */
loff_t ext4_llseek(struct file *file, loff_t offset, int whence)
{
        struct inode *inode = file->f_mapping->host;
        loff_t maxbytes;

        if (!(ext4_test_inode_flag(inode, EXT4_INODE_EXTENTS)))
                maxbytes = EXT4_SB(inode->i_sb)->s_bitmap_maxbytes;
        else
                maxbytes = inode->i_sb->s_maxbytes;

        switch (whence) {
        default:
                return generic_file_llseek_size(file, offset, whence,
                                                maxbytes, i_size_read(inode));
        case SEEK_HOLE:
                inode_lock_shared(inode);
                offset = iomap_seek_hole(inode, offset,
                                         &ext4_iomap_report_ops);
                inode_unlock_shared(inode);
                break;
        case SEEK_DATA:
                inode_lock_shared(inode);
                offset = iomap_seek_data(inode, offset,
                                         &ext4_iomap_report_ops);
                inode_unlock_shared(inode);
                break;
        }

        if (offset < 0)
                return offset;
        return vfs_setpos(file, offset, maxbytes);
}

/**
 * generic_file_llseek_size - generic llseek implementation for regular files
 * @file:       file structure to seek on
 * @offset:     file offset to seek to
 * @whence:     type of seek
 * @maxsize:    max size of this file in file system
 * @eof:        offset used for SEEK_END position
 *
 * This is a variant of generic_file_llseek that allows passing in a custom
 * maximum file size and a custom EOF position, for e.g. hashed directories
 *
 * Synchronization:
 * SEEK_SET and SEEK_END are unsynchronized (but atomic on 64bit platforms)
 * SEEK_CUR is synchronized against other SEEK_CURs, but not read/writes.
 * read/writes behave like SEEK_SET against seeks.
 */
loff_t
generic_file_llseek_size(struct file *file, loff_t offset, int whence,
                loff_t maxsize, loff_t eof)
{
        switch (whence) {
        case SEEK_END:
                offset += eof;
                break;
        case SEEK_CUR:
                /*
                 * Here we special-case the lseek(fd, 0, SEEK_CUR)
                 * position-querying operation.  Avoid rewriting the "same"
                 * f_pos value back to the file because a concurrent read(),
                 * write() or lseek() might have altered it
                 */
                if (offset == 0)
                        return file->f_pos;
                /*
                 * f_lock protects against read/modify/write race with other
                 * SEEK_CURs. Note that parallel writes and reads behave
                 * like SEEK_SET.
                 */
                spin_lock(&file->f_lock);
                offset = vfs_setpos(file, file->f_pos + offset, maxsize);
                spin_unlock(&file->f_lock);
                return offset;
        case SEEK_DATA:
                /*
                 * In the generic case the entire file is data, so as long as
                 * offset isn't at the end of the file then the offset is data.
                 */
                if ((unsigned long long)offset >= eof)
                        return -ENXIO;
                break;
        case SEEK_HOLE:
                /*
                 * There is a virtual hole at the end of the file, so as long as
                 * offset isn't i_size or larger, return i_size.
                 */
                if ((unsigned long long)offset >= eof)
                        return -ENXIO;
                offset = eof;
                break;
        }

        return vfs_setpos(file, offset, maxsize);
}
EXPORT_SYMBOL(generic_file_llseek_size);
```
