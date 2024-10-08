# PostgreSQL: WAL Insert

Created by: Mr Dk.

2024 / 10 / 02 01:04

Ningbo, Zhejiang, China

---

## 背景

为什么需要 WAL 日志？

从根本上来说，当数据库的所有数据都在非易失性存储上时，才可以被认为是可靠的。当需要修改数据时，数据将会被装载到内存中并被处理。处理完毕后，理论上应该立刻被写回存储上，这样才可以保证对数据的修改被永久保留下来。但是由于存储的读写速度相对于内存来说慢了多个数量级，因此我们肯定不希望每对数据做了一点修改就立刻同步回存储，这样会很慢，数据修改的吞吐率将会很低。为了解决这个问题，常见的做法是把内存中被修改过的数据页标记为 dirty，让脏页保留在内存中，然后定期把脏页同步回存储。这样，绝大部分对数据的修改实际上都是纯内存操作了。

然而，内存是易失性存储，机器一掉电或崩溃，内存里的数据会立即丢失，所以数据在内存中是不可靠的。这种情况随时可能发生，比如机房进水 (敲木头呸呸呸)。。。OS Panic 等。此时，从上一次同步回存储，到故障发生时，对内存页面的所有修改都会丢失。存储上的数据可能也会是一个不一致的页面：比如 [ext4 文件系统](https://ext4.wiki.kernel.org/index.php/Ext4_Disk_Layout) 的默认块大小是 4kB，[PostgreSQL](https://www.postgresql.org/docs/current/storage-page-layout.html) 的默认页大小是 8kB，断电发生时，可能文件系统只来得及向存储写完第一个 4kB。此时，这个 8kB 的 PostgreSQL 页在存储上是个半旧半新的损坏页面，既无法回退到全旧版本，也无法前进到全新版本。

上述问题都可以被 WAL 日志解决。WAL 日志全称 Write-Ahead Log，即 **预写日志**。在对数据做修改之前，必须先把本次要对数据做的修改记录到 WAL 日志中，然后再去修改内存中的数据。在事务提交时，数据可以不立即同步回存储，但是 WAL 日志必须已经同步到存储。这样即使数据库因为上述各种原因发生非预期内的关闭，内存中未被同步回存储的数据全部丢失，数据库在重新启动以后依旧可以通过 WAL 日志从合适的位置开始进行崩溃恢复 (crash recovery)，根据日志中记录的内容 REDO，把存储上的数据恢复到正确、一致的状态。

此外，由于 WAL 日志中记录了对物理文件的所有修改，所以天然就可以被用于做数据库之间的复制 (replication)，保持两份数据之间的同步。直接使用 WAL 日志进行的复制被称为物理复制，前提是复制两端需要对 WAL 日志格式有完全相同的理解；将 WAL 日志中的内容做进一步的解码和格式转换以后，可以得到任意格式（SQL、JSON、ProtoBuf、...）的逻辑数据变更，这种复制被称为逻辑复制。

由此可见，WAL 日志对数据库发生极端灾难时的可靠性、数据的正确性和一致性、数据库的主备复制，都有着重要的作用。带来的代价是，在数据库的日常运行中，每当需要对数据做修改时，都引入了额外的日志写入工作。这个开销极大决定了数据库的写入吞吐率。

本文基于 PostgreSQL 17 稳定版本分析 WAL 日志从产生到写入、落盘等一系列过程，以及 PostgreSQL 17 这些过程所做的一些优化。

## 总览

多个进程会同时产生 WAL 日志，它们产生的每一条日志记录在日志文件中都需要是原子的、连续的，不能和其它记录相互穿插。另外，每个事务内并不需要每产生一条 WAL 日志就立刻向存储同步一次，只需要等到事务提交时一起 flush 就好了。因此，PostgreSQL 维护了一段称为 WAL Buffer 的共享内存，并设计了一系列元信息，控制这段内存的空间使用和向存储 flush 的进度，通过几种不同的锁保护 WAL buffer 的元信息。每个进程将会做如下三件事：

1. 在 WAL buffer 中分配一段共享内存空间用于写入日志
2. 将产生的日志内容拷贝到在 WAL buffer 中分配好的空间里
3. 自行/等待后台进程将 WAL buffer 中的内容刷盘

```c
/*
 * Insert an XLOG record represented by an already-constructed chain of data
 * chunks.  This is a low-level routine; to construct the WAL record header
 * and data, use the higher-level routines in xloginsert.c.
 *
 * If 'fpw_lsn' is valid, it is the oldest LSN among the pages that this
 * WAL record applies to, that were not included in the record as full page
 * images.  If fpw_lsn <= RedoRecPtr, the function does not perform the
 * insertion and returns InvalidXLogRecPtr.  The caller can then recalculate
 * which pages need a full-page image, and retry.  If fpw_lsn is invalid, the
 * record is always inserted.
 *
 * 'flags' gives more in-depth control on the record being inserted. See
 * XLogSetRecordFlags() for details.
 *
 * 'topxid_included' tells whether the top-transaction id is logged along with
 * current subtransaction. See XLogRecordAssemble().
 *
 * The first XLogRecData in the chain must be for the record header, and its
 * data must be MAXALIGNed.  XLogInsertRecord fills in the xl_prev and
 * xl_crc fields in the header, the rest of the header must already be filled
 * by the caller.
 *
 * Returns XLOG pointer to end of record (beginning of next record).
 * This can be used as LSN for data pages affected by the logged action.
 * (LSN is the XLOG point up to which the XLOG must be flushed to disk
 * before the data page can be written out.  This implements the basic
 * WAL rule "write the log before the data".)
 */
XLogRecPtr
XLogInsertRecord(XLogRecData *rdata,
                 XLogRecPtr fpw_lsn,
                 uint8 flags,
                 int num_fpi,
                 bool topxid_included)
{
    /* ... */

    /*----------
     *
     * We have now done all the preparatory work we can without holding a
     * lock or modifying shared state. From here on, inserting the new WAL
     * record to the shared WAL buffer cache is a two-step process:
     *
     * 1. Reserve the right amount of space from the WAL. The current head of
     *    reserved space is kept in Insert->CurrBytePos, and is protected by
     *    insertpos_lck.
     *
     * 2. Copy the record to the reserved WAL space. This involves finding the
     *    correct WAL buffer containing the reserved space, and copying the
     *    record in place. This can be done concurrently in multiple processes.
     *
     * To keep track of which insertions are still in-progress, each concurrent
     * inserter acquires an insertion lock. In addition to just indicating that
     * an insertion is in progress, the lock tells others how far the inserter
     * has progressed. There is a small fixed number of insertion locks,
     * determined by NUM_XLOGINSERT_LOCKS. When an inserter crosses a page
     * boundary, it updates the value stored in the lock to the how far it has
     * inserted, to allow the previous buffer to be flushed.
     *
     * Holding onto an insertion lock also protects RedoRecPtr and
     * fullPageWrites from changing until the insertion is finished.
     *
     * Step 2 can usually be done completely in parallel. If the required WAL
     * page is not initialized yet, you have to grab WALBufMappingLock to
     * initialize it, but the WAL writer tries to do that ahead of insertions
     * to avoid that from happening in the critical path.
     *
     *----------
     */
    START_CRIT_SECTION();

    if (likely(class == WALINSERT_NORMAL))
    {
        WALInsertLockAcquire();

        /* ... */

        /*
         * Reserve space for the record in the WAL. This also sets the xl_prev
         * pointer.
         */
        ReserveXLogInsertLocation(rechdr->xl_tot_len, &StartPos, &EndPos,
                                  &rechdr->xl_prev);

        /* Normal records are always inserted. */
        inserted = true;
    }
    else if (class == WALINSERT_SPECIAL_SWITCH)
    {
        /*
         * In order to insert an XLOG_SWITCH record, we need to hold all of
         * the WAL insertion locks, not just one, so that no one else can
         * begin inserting a record until we've figured out how much space
         * remains in the current WAL segment and claimed all of it.
         *
         * Nonetheless, this case is simpler than the normal cases handled
         * below, which must check for changes in doPageWrites and RedoRecPtr.
         * Those checks are only needed for records that can contain buffer
         * references, and an XLOG_SWITCH record never does.
         */
        Assert(fpw_lsn == InvalidXLogRecPtr);
        WALInsertLockAcquireExclusive();
        inserted = ReserveXLogSwitch(&StartPos, &EndPos, &rechdr->xl_prev);
    }
    else
    {
        Assert(class == WALINSERT_SPECIAL_CHECKPOINT);

        /*
         * We need to update both the local and shared copies of RedoRecPtr,
         * which means that we need to hold all the WAL insertion locks.
         * However, there can't be any buffer references, so as above, we need
         * not check RedoRecPtr before inserting the record; we just need to
         * update it afterwards.
         */
        Assert(fpw_lsn == InvalidXLogRecPtr);
        WALInsertLockAcquireExclusive();
        ReserveXLogInsertLocation(rechdr->xl_tot_len, &StartPos, &EndPos,
                                  &rechdr->xl_prev);
        RedoRecPtr = Insert->RedoRecPtr = StartPos;
        inserted = true;
    }

    if (inserted)
    {
        /*
         * Now that xl_prev has been filled in, calculate CRC of the record
         * header.
         */
        rdata_crc = rechdr->xl_crc;
        COMP_CRC32C(rdata_crc, rechdr, offsetof(XLogRecord, xl_crc));
        FIN_CRC32C(rdata_crc);
        rechdr->xl_crc = rdata_crc;

        /*
         * All the record data, including the header, is now ready to be
         * inserted. Copy the record in the space reserved.
         */
        CopyXLogRecordToWAL(rechdr->xl_tot_len,
                            class == WALINSERT_SPECIAL_SWITCH, rdata,
                            StartPos, EndPos, insertTLI);

        /* ... */
    }

    /* ... */

    /*
     * Done! Let others know that we're finished.
     */
    WALInsertLockRelease();

    END_CRIT_SECTION();

    /* ... */
}
```

## WAL 日志空间分配

当进程需要写入一条 WAL 日志记录时，首先需要在 WAL 日志文件中分配预留空间，也即对应了在共享内存 WAL buffer 中预留空间。为了保证每条日志记录的原子性，分配预留空间的操作是必须是串行的，每次只能有一个进程操作当前已被分配的 WAL 日志位置指针。核心数据结构为 `XLogCtlInsert`：

```c
/*
 * Shared state data for WAL insertion.
 */
typedef struct XLogCtlInsert
{
    slock_t     insertpos_lck;  /* protects CurrBytePos and PrevBytePos */

    /*
     * CurrBytePos is the end of reserved WAL. The next record will be
     * inserted at that position. PrevBytePos is the start position of the
     * previously inserted (or rather, reserved) record - it is copied to the
     * prev-link of the next record. These are stored as "usable byte
     * positions" rather than XLogRecPtrs (see XLogBytePosToRecPtr()).
     */
    uint64      CurrBytePos;
    uint64      PrevBytePos;

    /* ... */
} XLogCtlInsert;
```

`CurrBytePos` 和 `PrevBytePos` 共同表示当前已经分配完空间的最后一条 WAL 日志记录的区间，下一条 WAL 日志的分配应该从 `CurrBytePos` 开始。为确保空间分配的原子性，这两个字段由自旋锁 `insertpos_lck` 保护。持有这把锁时，临界区需要尽可能小：

```c
/*
 * Reserves the right amount of space for a record of given size from the WAL.
 * *StartPos is set to the beginning of the reserved section, *EndPos to
 * its end+1. *PrevPtr is set to the beginning of the previous record; it is
 * used to set the xl_prev of this record.
 *
 * This is the performance critical part of XLogInsert that must be serialized
 * across backends. The rest can happen mostly in parallel. Try to keep this
 * section as short as possible, insertpos_lck can be heavily contended on a
 * busy system.
 *
 * NB: The space calculation here must match the code in CopyXLogRecordToWAL,
 * where we actually copy the record to the reserved space.
 *
 * NB: Testing shows that XLogInsertRecord runs faster if this code is inlined;
 * however, because there are two call sites, the compiler is reluctant to
 * inline. We use pg_attribute_always_inline here to try to convince it.
 */
static pg_attribute_always_inline void
ReserveXLogInsertLocation(int size, XLogRecPtr *StartPos, XLogRecPtr *EndPos,
                          XLogRecPtr *PrevPtr)
{
    XLogCtlInsert *Insert = &XLogCtl->Insert;
    uint64      startbytepos;
    uint64      endbytepos;
    uint64      prevbytepos;

    size = MAXALIGN(size);

    /* All (non xlog-switch) records should contain data. */
    Assert(size > SizeOfXLogRecord);

    /*
     * The duration the spinlock needs to be held is minimized by minimizing
     * the calculations that have to be done while holding the lock. The
     * current tip of reserved WAL is kept in CurrBytePos, as a byte position
     * that only counts "usable" bytes in WAL, that is, it excludes all WAL
     * page headers. The mapping between "usable" byte positions and physical
     * positions (XLogRecPtrs) can be done outside the locked region, and
     * because the usable byte position doesn't include any headers, reserving
     * X bytes from WAL is almost as simple as "CurrBytePos += X".
     */
    SpinLockAcquire(&Insert->insertpos_lck);

    startbytepos = Insert->CurrBytePos;
    endbytepos = startbytepos + size;
    prevbytepos = Insert->PrevBytePos;
    Insert->CurrBytePos = endbytepos;
    Insert->PrevBytePos = startbytepos;

    SpinLockRelease(&Insert->insertpos_lck);

    *StartPos = XLogBytePosToRecPtr(startbytepos);
    *EndPos = XLogBytePosToEndRecPtr(endbytepos);
    *PrevPtr = XLogBytePosToRecPtr(prevbytepos);

    /*
     * Check that the conversions between "usable byte positions" and
     * XLogRecPtrs work consistently in both directions.
     */
    Assert(XLogRecPtrToBytePos(*StartPos) == startbytepos);
    Assert(XLogRecPtrToBytePos(*EndPos) == endbytepos);
    Assert(XLogRecPtrToBytePos(*PrevPtr) == prevbytepos);
}
```

熟知的 `pg_current_wal_insert_lsn()` 也是通过上自旋锁以后获取到 `CurrBytePos` 的值：

```c
/*
 * Get latest WAL insert pointer
 */
XLogRecPtr
GetXLogInsertRecPtr(void)
{
    XLogCtlInsert *Insert = &XLogCtl->Insert;
    uint64      current_bytepos;

    SpinLockAcquire(&Insert->insertpos_lck);
    current_bytepos = Insert->CurrBytePos;
    SpinLockRelease(&Insert->insertpos_lck);

    return XLogBytePosToRecPtr(current_bytepos);
}
```

## 拷贝日志到 WAL Buffer

在每个进程都通过前一步分配好自己独占的 WAL 日志空间后，就可以将自己要产生的 WAL 日志拷贝到与空间相对应的 WAL buffer 中。由于空间分配是串行的，各进程要拷贝的目标地址互不重合，因此可以并发。但是多进程在并行工作的时候依旧需要加不同的锁来保证正确性。

### WALInsertLock

当进程要向 WAL buffer 中拷贝内容时，需要先加 WALInsertLock。

```c
/*
 * Inserting to WAL is protected by a small fixed number of WAL insertion
 * locks. To insert to the WAL, you must hold one of the locks - it doesn't
 * matter which one. To lock out other concurrent insertions, you must hold
 * of them. Each WAL insertion lock consists of a lightweight lock, plus an
 * indicator of how far the insertion has progressed (insertingAt).
 *
 * The insertingAt values are read when a process wants to flush WAL from
 * the in-memory buffers to disk, to check that all the insertions to the
 * region the process is about to write out have finished. You could simply
 * wait for all currently in-progress insertions to finish, but the
 * insertingAt indicator allows you to ignore insertions to later in the WAL,
 * so that you only wait for the insertions that are modifying the buffers
 * you're about to write out.
 *
 * This isn't just an optimization. If all the WAL buffers are dirty, an
 * inserter that's holding a WAL insert lock might need to evict an old WAL
 * buffer, which requires flushing the WAL. If it's possible for an inserter
 * to block on another inserter unnecessarily, deadlock can arise when two
 * inserters holding a WAL insert lock wait for each other to finish their
 * insertion.
 *
 * Small WAL records that don't cross a page boundary never update the value,
 * the WAL record is just copied to the page and the lock is released. But
 * to avoid the deadlock-scenario explained above, the indicator is always
 * updated before sleeping while holding an insertion lock.
 *
 * lastImportantAt contains the LSN of the last important WAL record inserted
 * using a given lock. This value is used to detect if there has been
 * important WAL activity since the last time some action, like a checkpoint,
 * was performed - allowing to not repeat the action if not. The LSN is
 * updated for all insertions, unless the XLOG_MARK_UNIMPORTANT flag was
 * set. lastImportantAt is never cleared, only overwritten by the LSN of newer
 * records.  Tracking the WAL activity directly in WALInsertLock has the
 * advantage of not needing any additional locks to update the value.
 */
typedef struct
{
    LWLock      lock;
    pg_atomic_uint64 insertingAt;
    XLogRecPtr  lastImportantAt;
} WALInsertLock;

/*
 * All the WAL insertion locks are allocated as an array in shared memory. We
 * force the array stride to be a power of 2, which saves a few cycles in
 * indexing, but more importantly also ensures that individual slots don't
 * cross cache line boundaries. (Of course, we have to also ensure that the
 * array start address is suitably aligned.)
 */
typedef union WALInsertLockPadded
{
    WALInsertLock l;
    char        pad[PG_CACHE_LINE_SIZE];
} WALInsertLockPadded;

/*
 * Shared state data for WAL insertion.
 */
typedef struct XLogCtlInsert
{
    /* ... */

    /*
     * WAL insertion locks.
     */
    WALInsertLockPadded *WALInsertLocks;
} XLogCtlInsert;

/*
 * Number of WAL insertion locks to use. A higher value allows more insertions
 * to happen concurrently, but adds some CPU overhead to flushing the WAL,
 * which needs to iterate all the locks.
 */
#define NUM_XLOGINSERT_LOCKS  8
```

这是一个固定数量的轻量级锁，锁内附带了一个 `insertingAt` 字段，表示当前持有锁的进程已经完成插入的位置。该字段表示，对当前进程来说，该位置之前的 WAL 日志已经可以被 flush 到存储上了。每个进程具体要使用哪一把 WALInsertLock 并不重要，这里是想通过锁的数量来控制并发插入 WAL 日志的进程数。

### WALBufMappingLock

WALBufMappingLock 是一个单独的轻量级锁，当进程需要修改一块 WAL buffer 与一个 WAL 日志文件页面的映射关系时，需要独占持有该锁，防止并发进程重复初始化页面和修改映射。

```c
/*----------
 *
 * WALBufMappingLock: must be held to replace a page in the WAL buffer cache.
 * It is only held while initializing and changing the mapping.  If the
 * contents of the buffer being replaced haven't been written yet, the mapping
 * lock is released while the write is done, and reacquired afterwards.
 *
 *----------
 */
```

### WALWriteLock

单独的轻量级锁，在进程将 WAL buffer 中的内容同步到存储时独占使用。

```c
/*----------
 *
 * WALWriteLock: must be held to write WAL buffers to disk (XLogWrite or
 * XLogFlush).
 *
 *----------
 */
```

### WAL Buffer

WAL buffer 由 `XLogCtlData` 结构中的三个字段维护，其大小受 `wal_buffers` 参数控制：

```c
/*
 * Total shared-memory state for XLOG.
 */
typedef struct XLogCtlData
{
    /* ... */

    /*
     * These values do not change after startup, although the pointed-to pages
     * and xlblocks values certainly do.  xlblocks values are protected by
     * WALBufMappingLock.
     */
    char       *pages;          /* buffers for unwritten XLOG pages */
    pg_atomic_uint64 *xlblocks; /* 1st byte ptr-s + XLOG_BLCKSZ */
    int         XLogCacheBlck;  /* highest allocated xlog buffer index */

    /* ... */
} XLogCtlData;
```

其中 `XLogCacheBlck` 用于标识 WAL buffer 的长度，`pages` 指向实际的 buffer 页面。原子变量 `xlblocks` 与每一块 WAL buffer 一一对应，表示与当前 WAL buffer 对应的 WAL 日志位置。

给定一个要插入的 WAL 日志位置，可以通过以下函数定位到对应的 WAL buffer 页面：

```c
/*
 * Get a pointer to the right location in the WAL buffer containing the
 * given XLogRecPtr.
 *
 * If the page is not initialized yet, it is initialized. That might require
 * evicting an old dirty buffer from the buffer cache, which means I/O.
 *
 * The caller must ensure that the page containing the requested location
 * isn't evicted yet, and won't be evicted. The way to ensure that is to
 * hold onto a WAL insertion lock with the insertingAt position set to
 * something <= ptr. GetXLogBuffer() will update insertingAt if it needs
 * to evict an old page from the buffer. (This means that once you call
 * GetXLogBuffer() with a given 'ptr', you must not access anything before
 * that point anymore, and must not call GetXLogBuffer() with an older 'ptr'
 * later, because older buffers might be recycled already)
 */
static char *
GetXLogBuffer(XLogRecPtr ptr, TimeLineID tli)
{
    /* ... */

    /*
     * Fast path for the common case that we need to access again the same
     * page as last time.
     */
    if (ptr / XLOG_BLCKSZ == cachedPage)
    {
        Assert(((XLogPageHeader) cachedPos)->xlp_magic == XLOG_PAGE_MAGIC);
        Assert(((XLogPageHeader) cachedPos)->xlp_pageaddr == ptr - (ptr % XLOG_BLCKSZ));
        return cachedPos + ptr % XLOG_BLCKSZ;
    }

    /*
     * The XLog buffer cache is organized so that a page is always loaded to a
     * particular buffer.  That way we can easily calculate the buffer a given
     * page must be loaded into, from the XLogRecPtr alone.
     */
    idx = XLogRecPtrToBufIdx(ptr);

    /*
     * See what page is loaded in the buffer at the moment. It could be the
     * page we're looking for, or something older. It can't be anything newer
     * - that would imply the page we're looking for has already been written
     * out to disk and evicted, and the caller is responsible for making sure
     * that doesn't happen.
     *
     * We don't hold a lock while we read the value. If someone is just about
     * to initialize or has just initialized the page, it's possible that we
     * get InvalidXLogRecPtr. That's ok, we'll grab the mapping lock (in
     * AdvanceXLInsertBuffer) and retry if we see anything other than the page
     * we're looking for.
     */
    expectedEndPtr = ptr;
    expectedEndPtr += XLOG_BLCKSZ - ptr % XLOG_BLCKSZ;

    endptr = pg_atomic_read_u64(&XLogCtl->xlblocks[idx]);
    if (expectedEndPtr != endptr)
    {
        XLogRecPtr  initializedUpto;

        /*
         * Before calling AdvanceXLInsertBuffer(), which can block, let others
         * know how far we're finished with inserting the record.
         *
         * NB: If 'ptr' points to just after the page header, advertise a
         * position at the beginning of the page rather than 'ptr' itself. If
         * there are no other insertions running, someone might try to flush
         * up to our advertised location. If we advertised a position after
         * the page header, someone might try to flush the page header, even
         * though page might actually not be initialized yet. As the first
         * inserter on the page, we are effectively responsible for making
         * sure that it's initialized, before we let insertingAt to move past
         * the page header.
         */
        /* ... */

        WALInsertLockUpdateInsertingAt(initializedUpto);

        AdvanceXLInsertBuffer(ptr, tli, false);
        endptr = pg_atomic_read_u64(&XLogCtl->xlblocks[idx]);

        /* ... */
    }
    else
    {
        /*
         * Make sure the initialization of the page is visible to us, and
         * won't arrive later to overwrite the WAL data we write on the page.
         */
        pg_memory_barrier();
    }

    /* ... */
}
```

对于要插入的 WAL 日志位置，根据 WAL 日志页面大小和 WAL buffer 的大小进行取模运算后，可以定位到对应的 WAL buffer 地址。然后再通过比较这块 buffer 的 `xlblocks` 确认当前 buffer 里的内容是不是属于当前 WAL 日志页面的。如果是，就可以直接使用；如果不是，则需要更新一下当前 WALInsertLock 上的 `insertingAt`，表示在此之前的 WAL 日志已经可以被 flush 到存储了，然后再通过 `AdvanceXLInsertBuffer` 把当前的 buffer 给腾出来。

```c
/*
 * Initialize XLOG buffers, writing out old buffers if they still contain
 * unwritten data, upto the page containing 'upto'. Or if 'opportunistic' is
 * true, initialize as many pages as we can without having to write out
 * unwritten data. Any new pages are initialized to zeros, with pages headers
 * initialized properly.
 */
static void
AdvanceXLInsertBuffer(XLogRecPtr upto, TimeLineID tli, bool opportunistic)
{
    XLogCtlInsert *Insert = &XLogCtl->Insert;
    int         nextidx;
    XLogRecPtr  OldPageRqstPtr;
    XLogwrtRqst WriteRqst;
    XLogRecPtr  NewPageEndPtr = InvalidXLogRecPtr;
    XLogRecPtr  NewPageBeginPtr;
    XLogPageHeader NewPage;
    int         npages pg_attribute_unused() = 0;

    LWLockAcquire(WALBufMappingLock, LW_EXCLUSIVE);

    /*
     * Now that we have the lock, check if someone initialized the page
     * already.
     */
    while (upto >= XLogCtl->InitializedUpTo || opportunistic)
    {
        nextidx = XLogRecPtrToBufIdx(XLogCtl->InitializedUpTo);

        /*
         * Get ending-offset of the buffer page we need to replace (this may
         * be zero if the buffer hasn't been used yet).  Fall through if it's
         * already written out.
         */
        OldPageRqstPtr = pg_atomic_read_u64(&XLogCtl->xlblocks[nextidx]);
        if (LogwrtResult.Write < OldPageRqstPtr)
        {
            /*
             * Nope, got work to do. If we just want to pre-initialize as much
             * as we can without flushing, give up now.
             */
            if (opportunistic)
                break;

            /* Advance shared memory write request position */
            SpinLockAcquire(&XLogCtl->info_lck);
            if (XLogCtl->LogwrtRqst.Write < OldPageRqstPtr)
                XLogCtl->LogwrtRqst.Write = OldPageRqstPtr;
            SpinLockRelease(&XLogCtl->info_lck);

            /*
             * Acquire an up-to-date LogwrtResult value and see if we still
             * need to write it or if someone else already did.
             */
            RefreshXLogWriteResult(LogwrtResult);
            if (LogwrtResult.Write < OldPageRqstPtr)
            {
                /*
                 * Must acquire write lock. Release WALBufMappingLock first,
                 * to make sure that all insertions that we need to wait for
                 * can finish (up to this same position). Otherwise we risk
                 * deadlock.
                 */
                LWLockRelease(WALBufMappingLock);

                WaitXLogInsertionsToFinish(OldPageRqstPtr);

                LWLockAcquire(WALWriteLock, LW_EXCLUSIVE);

                RefreshXLogWriteResult(LogwrtResult);
                if (LogwrtResult.Write >= OldPageRqstPtr)
                {
                    /* OK, someone wrote it already */
                    LWLockRelease(WALWriteLock);
                }
                else
                {
                    /* Have to write it ourselves */
                    TRACE_POSTGRESQL_WAL_BUFFER_WRITE_DIRTY_START();
                    WriteRqst.Write = OldPageRqstPtr;
                    WriteRqst.Flush = 0;
                    XLogWrite(WriteRqst, tli, false);
                    LWLockRelease(WALWriteLock);
                    PendingWalStats.wal_buffers_full++;
                    TRACE_POSTGRESQL_WAL_BUFFER_WRITE_DIRTY_DONE();
                }
                /* Re-acquire WALBufMappingLock and retry */
                LWLockAcquire(WALBufMappingLock, LW_EXCLUSIVE);
                continue;
            }
        }

        /*
         * Now the next buffer slot is free and we can set it up to be the
         * next output page.
         */
        NewPageBeginPtr = XLogCtl->InitializedUpTo;
        NewPageEndPtr = NewPageBeginPtr + XLOG_BLCKSZ;

        Assert(XLogRecPtrToBufIdx(NewPageBeginPtr) == nextidx);

        NewPage = (XLogPageHeader) (XLogCtl->pages + nextidx * (Size) XLOG_BLCKSZ);

        /*
         * Mark the xlblock with InvalidXLogRecPtr and issue a write barrier
         * before initializing. Otherwise, the old page may be partially
         * zeroed but look valid.
         */
        pg_atomic_write_u64(&XLogCtl->xlblocks[nextidx], InvalidXLogRecPtr);
        pg_write_barrier();

        /* init WAL ... */

        /*
         * Make sure the initialization of the page becomes visible to others
         * before the xlblocks update. GetXLogBuffer() reads xlblocks without
         * holding a lock.
         */
        pg_write_barrier();

        pg_atomic_write_u64(&XLogCtl->xlblocks[nextidx], NewPageEndPtr);
        XLogCtl->InitializedUpTo = NewPageEndPtr;

        npages++;
    }
    LWLockRelease(WALBufMappingLock);
}
```

该函数从 WAL buffer 中最老的页面开始检查，如果 WAL 日志的刷盘进度已经落后于当前 WAL buffer，则需要将当前的 WAL buffer 内容刷盘。如果 WAL buffer 页面还有正在进行中的拷入，则等待拷入完成。完成后，释放 WALBufMappingLock，然后独占 WALWriteLock 将日志写入到存储，然后再次获取 WALBufMappingLock 重试。直到当前要插入的 WAL buffer 页面可以被腾出来使用。页面腾空后，做必要的初始化然后返回。

### 日志拷入

借助上述函数和锁的支持，多个进程可以并发向 WAL buffer 中预留好的空间拷贝日志，完成写入。该函数主要借助上面的 `GetXLogBuffer` 完成：

```c
/*
 * Subroutine of XLogInsertRecord.  Copies a WAL record to an already-reserved
 * area in the WAL.
 */
static void
CopyXLogRecordToWAL(int write_len, bool isLogSwitch, XLogRecData *rdata,
                    XLogRecPtr StartPos, XLogRecPtr EndPos, TimeLineID tli)
{
    /* ... */
}
```

## 后台日志刷盘

此外，后台的 WAL Writer 进程也会周期性地调用 `XLogBackgroundFlush` 将 WAL buffer 中未被写入存储的页面刷到磁盘。刷盘完毕后，已被下刷完毕的 WAL buffer 页面可以被复用。这些 WAL buffer 将会被提前清零，预分配给后续的 WAL 日志写入使用。

```c
/*
 * Write & flush xlog, but without specifying exactly where to.
 *
 * We normally write only completed blocks; but if there is nothing to do on
 * that basis, we check for unwritten async commits in the current incomplete
 * block, and write through the latest one of those.  Thus, if async commits
 * are not being used, we will write complete blocks only.
 *
 * If, based on the above, there's anything to write we do so immediately. But
 * to avoid calling fsync, fdatasync et. al. at a rate that'd impact
 * concurrent IO, we only flush WAL every wal_writer_delay ms, or if there's
 * more than wal_writer_flush_after unflushed blocks.
 *
 * We can guarantee that async commits reach disk after at most three
 * wal_writer_delay cycles. (When flushing complete blocks, we allow XLogWrite
 * to write "flexibly", meaning it can stop at the end of the buffer ring;
 * this makes a difference only with very high load or long wal_writer_delay,
 * but imposes one extra cycle for the worst case for async commits.)
 *
 * This routine is invoked periodically by the background walwriter process.
 *
 * Returns true if there was any work to do, even if we skipped flushing due
 * to wal_writer_delay/wal_writer_flush_after.
 */
bool
XLogBackgroundFlush(void)
{
    /* ... */

    START_CRIT_SECTION();

    /* now wait for any in-progress insertions to finish and get write lock */
    WaitXLogInsertionsToFinish(WriteRqst.Write);
    LWLockAcquire(WALWriteLock, LW_EXCLUSIVE);
    RefreshXLogWriteResult(LogwrtResult);
    if (WriteRqst.Write > LogwrtResult.Write ||
        WriteRqst.Flush > LogwrtResult.Flush)
    {
        XLogWrite(WriteRqst, insertTLI, flexible);
    }
    LWLockRelease(WALWriteLock);

    END_CRIT_SECTION();

    /* wake up walsenders now that we've released heavily contended locks */
    WalSndWakeupProcessRequests(true, !RecoveryInProgress());

    /*
     * Great, done. To take some work off the critical path, try to initialize
     * as many of the no-longer-needed WAL buffers for future use as we can.
     */
    AdvanceXLInsertBuffer(InvalidXLogRecPtr, insertTLI, true);

    /*
     * If we determined that we need to write data, but somebody else
     * wrote/flushed already, it should be considered as being active, to
     * avoid hibernating too early.
     */
    return true;
}
```

## 更多

在上面的流程中，可以看到对各级锁的获取与释放、对共享内存中 WAL buffer 的分配和使用、对日志空间分配/拷入/刷盘的共享状态的读取或更新，都是非常频繁的。为确保正确性需要频繁加锁。PostgreSQL 17 中优化了不少与 WAL 日志写入相关的共享状态信息。原先，不少状态变量需要被自旋锁保护，在 PostgreSQL 17 中被修改为使用原子变量。此后这些状态字段可以被多进程无锁地读写，相关代码被移出了由自旋锁保护的临界区。

这也为后续的其它优化提供了可能。比如 PostgreSQL 17 起物理复制的 WAL sender 进程支持直接从 WAL buffer 中消费 WAL 日志，以节省从磁盘读取日志的开销。在确认 WAL buffer 中的内容是否可用时，WAL sender 进程不需要加任何的锁，只需要在做内存拷贝的前后对 WAL buffer 的 `xlblocks` 进行两次原子读取，如果两次的结果相同，则说明本次内存拷贝的结果有效。这个过程对 WAL 日志的写入不会产生任何影响。但是如果像之前一样需要使用自旋锁来保证读写正确，则会对 WAL 日志的写入带来更多的锁冲突。

## 参考资料

[PostgreSQL Source Code - xlog.c](https://github.com/postgres/postgres/blob/REL_17_STABLE/src/backend/access/transam/xlog.c)

[PostgreSQL: Documentation 17: 28.3. Write-Ahead Logging (WAL)](https://www.postgresql.org/docs/current/wal-intro.html)

[Use 64-bit atomics for xlblocks array elements](https://github.com/postgres/postgres/commit/c3a8e2a7cb16d55e3b757934b538cb8b8a0eab02)

[Read WAL directly from WAL buffers](https://www.postgresql.org/message-id/flat/CALj2ACXKKK%3DwbiG5_t6dGao5GoecMwRkhr7GjVBM_jg54%2BNa%3DQ%40mail.gmail.com)
