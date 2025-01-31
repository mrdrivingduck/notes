# PostgreSQL - WAL Prefetch

Created by: Mr Dk.

2025 / 01 / 31 13:57

Ningbo, Zhejiang, China

---

## 背景

PostgreSQL 通过 redo WAL 日志，可以将不一致的持久化状态（crash / 基础备份）逐步恢复到一致的状态（最后一条 / 某一条 WAL 日志），从而使数据库可以重新对外提供服务。在此期间，数据库无法接受外部连接，startup 进程独自完成所有的恢复工作。因此，startup 进程的工作效率直接决定了 recovery 所需要的时间，也进而决定了业务与数据库断连的时间。

在 startup 进程的主循环中，recovery 需要完成的工作包含：

1. 将 WAL 日志读入内存
2. 解码每一条 WAL 日志记录
3. 根据 WAL 日志记录，将引用的数据页面读入 buffer pool
4. 根据 WAL 日志的操作类型，对 buffer pool 中的数据页面进行更改
5. 必要时，将更改后的状态同步回存储，并更新 recovery 进度
6. ...

上述过程中，对数据页面的修改是基于 buffer pool 中的页面完成的，可以认为是非常迅速的 on CPU 工作。只有文件 I/O 才会使 startup 进程暂停 recovery，离开 CPU 等待 I/O 完成。其中，对 WAL 日志的读取是顺序的，这个 I/O pattern 能够很容易地被 OS 推断出来从而进行 read-ahead，因此 WAL 日志的读取理应基本能够命中 OS page cache，不太会成为 I/O 瓶颈。然而，当 startup 进程根据每一条 WAL 日志记录将对应的数据页面读入 buffer pool 时，I/O pattern 是随机的，被读取的页面没有任何的局部性特征，OS 无法预读相应的页面。这会导致 startup 进程频繁因等待 I/O 而暂停。

OS 并不知道在 recovery 的过程中需要用到哪些页面，而数据库是可以知道的，所以这些页面可以被预读，在真正使用到这些页面时不必再等待 I/O。预读工作可以由数据库指引 OS 完成，甚至由数据库自己完成。在目前阶段，PostgreSQL 依旧还在使用 buffered I/O，依赖 OS 的 page cache 来管理 I/O，所以暂时只能通过 [`posix_fadvise`](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html) 接口提示 OS 将特定页面提前装入 page cache，使后续对该页面的读取可以被优化为内存拷贝。等后续 PostgreSQL 逐渐发展为通过 direct I/O 自行管理 I/O 后，必然会通过 I/O worker 进程异步地将对应页面预读到 buffer pool 中，以减少 startup 进程的暂停。毕竟 `posix_fadvise` 只是对 OS 的提示和建议，而不是强制，OS 并不一定保证会预读页面。

PostgreSQL 15 起开始支持 [XLog Prefetcher](https://www.postgresql.org/message-id/flat/CA%2BhUKGJ4VJN8ttxScUFM8dOKX0BrBiboo5uz1cq%3DAovOddfHpA%40mail.gmail.com)，在支持 `posix_fadvise` 的 OS 上将会尝试提前通知 OS 预读相应页面，同时相关接口也为目前正在进行中的异步 I/O 管理模块进行了预留，以方便后续通过 I/O worker 进程来实现预读。本文基于 PostgreSQL 17 稳定版分析相关模块的实现。

## 实现思路

### Decode 和 Redo 解耦

在 PostgreSQL 14 及以前版本的 recovery 处理逻辑中，在一个大循环内，依次进行如下工作：

1. Decode 一条 WAL 日志记录：由于每条 WAL 日志记录都是变长的，因此在解码过程中需要逐步调用 `WALRead` 函数将这条记录的完整内容从存储读入到内存
2. Redo 一条 WAL 日志记录：每种类型的 WAL 日志都实现了对应的 redo callback，其中会将这条日志引用的数据页面读入 buffer pool，然后再根据日志的类型对页面做相应的修改

以 Heap 类型的 WAL 日志为例。解码完毕后，startup 进程将会调用 `heap_redo` 函数，再根据日志记录的子类型进入对应的 redo 逻辑，比如 `heap_xlog_insert`。其中会将这条记录修改的页面读入 buffer pool，然后根据日志中记录的数据 redo 这个 INSERT 操作：

```c
void
heap_redo(XLogReaderState *record)
{
    uint8       info = XLogRecGetInfo(record) & ~XLR_INFO_MASK;

    /* ... */

    switch (info & XLOG_HEAP_OPMASK)
    {
        case XLOG_HEAP_INSERT:
            heap_xlog_insert(record);
            break;
        case XLOG_HEAP_DELETE:
            heap_xlog_delete(record);
            break;
        case XLOG_HEAP_UPDATE:
            heap_xlog_update(record, false);
            break;
        case XLOG_HEAP_TRUNCATE:
        /* ... */
    }
}
```

按照这个逻辑，decode 一条记录就立刻 redo 一条记录，那么完全没有时机去完成页面的预读。因此，decode 和 redo 这两个动作需要解耦：由于 WAL 日志一旦写入就不会被修改了，因此在 decode 一条记录时，可以提前 decode 若干条后续的记录。而每解码完一条记录以后，就可以立刻获知这条记录将会引用到的数据页面，从而使 startup 进程可以立刻发起对这些页面的预读请求，然后回过头来开始 redo 最早解码完毕的记录。在 redo 向后推进的过程中，被发起预读请求的页面会被 OS 异步地读入 page cache 中，从而在真正对这些页面调用 `pread` 时能够以极低的时延返回。

Decode 和 redo 的解耦实现在提交 [`3f1ce973`](https://github.com/postgres/postgres/commit/3f1ce973467a0d285961bf2f99b11d06e264e2c1) 中：

```
commit 3f1ce973467a0d285961bf2f99b11d06e264e2c1
Author: Thomas Munro <tmunro@postgresql.org>
Date:   Fri Mar 18 17:45:04 2022 +1300

    Add circular WAL decoding buffer, take II.

    Teach xlogreader.c to decode the WAL into a circular buffer.  This will
    support optimizations based on looking ahead, to follow in a later
    commit.

     * XLogReadRecord() works as before, decoding records one by one, and
       allowing them to be examined via the traditional XLogRecGetXXX()
       macros and certain traditional members like xlogreader->ReadRecPtr.

     * An alternative new interface XLogReadAhead()/XLogNextRecord() is
       added that returns pointers to DecodedXLogRecord objects so that it's
       now possible to look ahead in the WAL stream while replaying.

     * In order to be able to use the new interface effectively while
       streaming data, support is added for the page_read() callback to
       respond to a new nonblocking mode with XLREAD_WOULDBLOCK instead of
       waiting for more data to arrive.

    No direct user of the new interface is included in this commit, though
    XLogReadRecord() uses it internally.  Existing code doesn't need to
    change, except in a few places where it was accessing reader internals
    directly and now needs to go through accessor macros.

    Reviewed-by: Julien Rouhaud <rjuju123@gmail.com>
    Reviewed-by: Tomas Vondra <tomas.vondra@enterprisedb.com>
    Reviewed-by: Andres Freund <andres@anarazel.de> (earlier versions)
    Discussion: https://postgr.es/m/CA+hUKGJ4VJN8ttxScUFM8dOKX0BrBiboo5uz1cq=AovOddfHpA@mail.gmail.com
```

这次提交对用于维护 WAL 日志读取状态的 `XLogReaderState` 结构体增加了两组控制变量，分别用于维护两个数据结构：

- 一段被称为 decode buffer 的连续内存，配合头尾指针作为环形缓冲区使用，用于存放已经被解码后的 WAL 日志记录
- 解码后的日志按顺序串连为队列 decode queue，队头是最早解码完毕的日志记录，后续的记录被解码后不断加入队尾

```c
struct XLogReaderState
{
    /* ... */

    /*
     * Buffer for decoded records.  This is a circular buffer, though
     * individual records can't be split in the middle, so some space is often
     * wasted at the end.  Oversized records that don't fit in this space are
     * allocated separately.
     */
    char       *decode_buffer;
    size_t      decode_buffer_size;
    bool        free_decode_buffer; /* need to free? */
    char       *decode_buffer_head; /* data is read from the head */
    char       *decode_buffer_tail; /* new data is written at the tail */

    /*
     * Queue of records that have been decoded.  This is a linked list that
     * usually consists of consecutive records in decode_buffer, but may also
     * contain oversized records allocated with palloc().
     */
    DecodedXLogRecord *decode_queue_head;   /* oldest decoded record */
    DecodedXLogRecord *decode_queue_tail;   /* newest decoded record */

    /* ... */
```

通过函数 `XLogReadRecordAlloc` 在 decode buffer 中为一条记录分配空间：

```c
/*
 * Allocate space for a decoded record.  The only member of the returned
 * object that is initialized is the 'oversized' flag, indicating that the
 * decoded record wouldn't fit in the decode buffer and must eventually be
 * freed explicitly.
 *
 * The caller is responsible for adjusting decode_buffer_tail with the real
 * size after successfully decoding a record into this space.  This way, if
 * decoding fails, then there is nothing to undo unless the 'oversized' flag
 * was set and pfree() must be called.
 *
 * Return NULL if there is no space in the decode buffer and allow_oversized
 * is false, or if memory allocation fails for an oversized buffer.
 */
static DecodedXLogRecord *
XLogReadRecordAlloc(XLogReaderState *state, size_t xl_tot_len, bool allow_oversized)
{
    size_t      required_space = DecodeXLogRecordRequiredSpace(xl_tot_len);

    /* ... */
}
```

在函数 `XLogDecodeNextRecord` 中将记录解码并放入 decode queue 队尾：

```c
static XLogPageReadResult
XLogDecodeNextRecord(XLogReaderState *state, bool nonblocking)
{
    /* ... */

    if (DecodeXLogRecord(state, decoded, record, RecPtr, &errormsg))
    {
        /* Record the location of the next record. */
        decoded->next_lsn = state->NextRecPtr;

        /*
         * If it's in the decode buffer, mark the decode buffer space as
         * occupied.
         */
        if (!decoded->oversized)
        {
            /* The new decode buffer head must be MAXALIGNed. */
            Assert(decoded->size == MAXALIGN(decoded->size));
            if ((char *) decoded == state->decode_buffer)
                state->decode_buffer_tail = state->decode_buffer + decoded->size;
            else
                state->decode_buffer_tail += decoded->size;
        }

        /* Insert it into the queue of decoded records. */
        Assert(state->decode_queue_tail != decoded);
        if (state->decode_queue_tail)
            state->decode_queue_tail->next = decoded;
        state->decode_queue_tail = decoded;
        if (!state->decode_queue_head)
            state->decode_queue_head = decoded;
        return XLREAD_SUCCESS;
    }

    /* ... */
}
```

有了这两组数据结构，decode 和 redo 就可以解耦了：decode queue 中存放着已经被解码完的多条记录，只要 decode buffer 够大，向后多解码一些 WAL 日志记录也不是问题；startup 进程进行 redo 时，只需要从队头不断消费解码完的记录就可以了。

函数 `XLogNextRecord` 用于从 decode queue 的队头消费已经解码完的记录：

```c
/*
 * Attempt to read an XLOG record.
 *
 * XLogBeginRead() or XLogFindNextRecord() and then XLogReadAhead() must be
 * called before the first call to XLogNextRecord().  This functions returns
 * records and errors that were put into an internal queue by XLogReadAhead().
 *
 * On success, a record is returned.
 *
 * The returned record (or *errormsg) points to an internal buffer that's
 * valid until the next call to XLogNextRecord.
 */
DecodedXLogRecord *
XLogNextRecord(XLogReaderState *state, char **errormsg)
{
    /* ... */

    /*
     * Record this as the most recent record returned, so that we'll release
     * it next time.  This also exposes it to the traditional
     * XLogRecXXX(xlogreader) macros, which work with the decoder rather than
     * the record for historical reasons.
     */
    state->record = state->decode_queue_head;

    /*
     * Update the pointers to the beginning and one-past-the-end of this
     * record, again for the benefit of historical code that expected the
     * decoder to track this rather than accessing these fields of the record
     * itself.
     */
    state->ReadRecPtr = state->record->lsn;
    state->EndRecPtr = state->record->next_lsn;

    *errormsg = NULL;

    return state->record;
}
```

### 预读状态管理

有了上述基础设施的支持，接下来可以重点关注如何实现预读了：

1. 如何维护和管理所有预读请求的状态？
2. 如何避免侵入原有逻辑太多？

这些需要解决的问题在提交 [`5dc0418f`](https://github.com/postgres/postgres/commit/5dc0418fab281d017a61a5756240467af982bdfd) 中完成了实现：

```
commit 5dc0418fab281d017a61a5756240467af982bdfd
Author: Thomas Munro <tmunro@postgresql.org>
Date:   Thu Apr 7 19:28:40 2022 +1200

    Prefetch data referenced by the WAL, take II.

    Introduce a new GUC recovery_prefetch.  When enabled, look ahead in the
    WAL and try to initiate asynchronous reading of referenced data blocks
    that are not yet cached in our buffer pool.  For now, this is done with
    posix_fadvise(), which has several caveats.  Since not all OSes have
    that system call, "try" is provided so that it can be enabled where
    available.  Better mechanisms for asynchronous I/O are possible in later
    work.

    Set to "try" for now for test coverage.  Default setting to be finalized
    before release.

    The GUC wal_decode_buffer_size limits the distance we can look ahead in
    bytes of decoded data.

    The existing GUC maintenance_io_concurrency is used to limit the number
    of concurrent I/Os allowed, based on pessimistic heuristics used to
    infer that I/Os have begun and completed.  We'll also not look more than
    maintenance_io_concurrency * 4 block references ahead.

    Reviewed-by: Julien Rouhaud <rjuju123@gmail.com>
    Reviewed-by: Tomas Vondra <tomas.vondra@2ndquadrant.com>
    Reviewed-by: Alvaro Herrera <alvherre@2ndquadrant.com> (earlier version)
    Reviewed-by: Andres Freund <andres@anarazel.de> (earlier version)
    Reviewed-by: Justin Pryzby <pryzby@telsasoft.com> (earlier version)
    Tested-by: Tomas Vondra <tomas.vondra@2ndquadrant.com> (earlier version)
    Tested-by: Jakub Wartak <Jakub.Wartak@tomtom.com> (earlier version)
    Tested-by: Dmitry Dolgov <9erthalion6@gmail.com> (earlier version)
    Tested-by: Sait Talha Nisanci <Sait.Nisanci@microsoft.com> (earlier version)
    Discussion: https://postgr.es/m/CA%2BhUKGJ4VJN8ttxScUFM8dOKX0BrBiboo5uz1cq%3DAovOddfHpA%40mail.gmail.com
```

首先，由于所有与 decode 和 redo 相关的状态信息已经记录在结构体 `XLogReaderState` 中，原有代码也基本需要持有这个状态结构来完成所有动作。因此，PostgreSQL 使用了一个包含 `XLogReaderState` 结构体的 `XLogPrefetcher` 结构体来额外记录与预读相关的所有信息。

为了封装预读的逻辑，原先所有的 `XLogReader*` 函数接口被全部包装为 `XLogPrefetcher*`，入参由 `XLogReaderState` 结构体变为 `XLogPrefetcher` 结构体。这样设计带来的好处是可以最大程度复用已有的代码：包装后新接口内部的原有代码需要使用 `XLogReaderState` 的地方，只需要改为使用 `XLogPrefetcher` 的 `->reader` 即可。

```c
/*
 * A prefetcher.  This is a mechanism that wraps an XLogReader, prefetching
 * blocks that will be soon be referenced, to try to avoid IO stalls.
 */
struct XLogPrefetcher
{
    /* WAL reader and current reading state. */
    XLogReaderState *reader;
    DecodedXLogRecord *record;
    int         next_block_id;

    /* ... */

    /* IO depth manager. */
    LsnReadQueue *streaming_read;

    /* ... */
};
```

预读的状态由 `LsnReadQueue` 这个核心数据结构管理：

- `next`：发起下一次预读请求的回调函数
- `lrq_private`：持有对预读状态结构 `XLogPrefetcher` 的指针引用
- `max_inflight`：控制未完成 I/O 的最大数量
- `inflight` / `completed`：统计进行中或已完成的 I/O 数量
- 长度为 `size` 的定长队列 `queue`，配合头尾指针 `head` / `tail` 实现循环使用；队列中记录每次预读请求对应的 WAL 日志记录序列号 `lsn` 和是否发出 I/O 请求的标识 `io`；队尾是最旧的预读请求

```c
/*
 * A simple circular queue of LSNs, using to control the number of
 * (potentially) inflight IOs.  This stands in for a later more general IO
 * control mechanism, which is why it has the apparently unnecessary
 * indirection through a function pointer.
 */
typedef struct LsnReadQueue
{
    LsnReadQueueNextFun next;
    uintptr_t   lrq_private;
    uint32      max_inflight;
    uint32      inflight;
    uint32      completed;
    uint32      head;
    uint32      tail;
    uint32      size;
    struct
    {
        bool        io;
        XLogRecPtr  lsn;
    }           queue[FLEXIBLE_ARRAY_MEMBER];
} LsnReadQueue;
```

### 预读触发时机

当 startup 进程 redo 完一条 WAL 记录后，与这条记录相关的 I/O 可以被认为已经完成了。此时，从 decode queue 的队头取出下一条解码完的记录进行 redo 之前，就是触发预读的时机。

首先，获取到当前将要 redo 的记录，把这条记录之前的所有预读请求从预读队列中清除：

```c
/*
 * A wrapper for XLogReadRecord() that provides the same interface, but also
 * tries to initiate I/O for blocks referenced in future WAL records.
 */
XLogRecord *
XLogPrefetcherReadRecord(XLogPrefetcher *prefetcher, char **errmsg)
{
    /* ... */

    /*
     * Release last returned record, if there is one, as it's now been
     * replayed.
     */
    replayed_up_to = XLogReleasePreviousRecord(prefetcher->reader);

    /* ... */

    /*
     * All IO initiated by earlier WAL is now completed.  This might trigger
     * further prefetching.
     */
    lrq_complete_lsn(prefetcher->streaming_read, replayed_up_to);

    /* ... */

    /* Read the next record. */
    record = XLogNextRecord(prefetcher->reader, errmsg);

    /* ... */
}
```

清除的具体方法是从预读队列的队尾开始，删除对应 WAL 日志记录的 LSN 小于当前 redo LSN 的所有请求。然后从上次发起预读请求的位置开始，发起更多预读请求，尽量填满预读队列：

```c
static inline void
lrq_complete_lsn(LsnReadQueue *lrq, XLogRecPtr lsn)
{
    /*
     * We know that LSNs before 'lsn' have been replayed, so we can now assume
     * that any IOs that were started before then have finished.
     */
    while (lrq->tail != lrq->head &&
           lrq->queue[lrq->tail].lsn < lsn)
    {
        if (lrq->queue[lrq->tail].io)
            lrq->inflight--;
        else
            lrq->completed--;
        lrq->tail++;
        if (lrq->tail == lrq->size)
            lrq->tail = 0;
    }
    if (RecoveryPrefetchEnabled())
        lrq_prefetch(lrq);
}
```

发起更多预读请求的方式是回调 `LsnReadQueue` 的 `next` 函数。该函数可能返回三种结果，需要根据返回值记录每一个请求的不同状态：

- `LRQ_NEXT_AGAIN`：暂无更多 WAL 日志可以解析，因此对队列无操作，直接返回
- `LRQ_NEXT_IO`：已经发起 I/O 请求，将该请求标识为 `inflight` 并放入队列头部
- `LRQ_NEXT_NO_IO`：对应页面无需预读，将该请求标识为 `completed` 并放入队列头部

```c
static inline void
lrq_prefetch(LsnReadQueue *lrq)
{
    /* Try to start as many IOs as we can within our limits. */
    while (lrq->inflight < lrq->max_inflight &&
           lrq->inflight + lrq->completed < lrq->size - 1)
    {
        Assert(((lrq->head + 1) % lrq->size) != lrq->tail);
        switch (lrq->next(lrq->lrq_private, &lrq->queue[lrq->head].lsn))
        {
            case LRQ_NEXT_AGAIN:
                return;
            case LRQ_NEXT_IO:
                lrq->queue[lrq->head].io = true;
                lrq->inflight++;
                break;
            case LRQ_NEXT_NO_IO:
                lrq->queue[lrq->head].io = false;
                lrq->completed++;
                break;
        }
        lrq->head++;
        if (lrq->head == lrq->size)
            lrq->head = 0;
    }
}

/*
 * A callback that examines the next block reference in the WAL, and possibly
 * starts an IO so that a later read will be fast.
 *
 * Returns LRQ_NEXT_AGAIN if no more WAL data is available yet.
 *
 * Returns LRQ_NEXT_IO if the next block reference is for a main fork block
 * that isn't in the buffer pool, and the kernel has been asked to start
 * reading it to make a future read system call faster. An LSN is written to
 * *lsn, and the I/O will be considered to have completed once that LSN is
 * replayed.
 *
 * Returns LRQ_NEXT_NO_IO if we examined the next block reference and found
 * that it was already in the buffer pool, or we decided for various reasons
 * not to prefetch.
 */
static LsnReadQueueNextStatus
XLogPrefetcherNextBlock(uintptr_t pgsr_private, XLogRecPtr *lsn)
{
    /* ... */
}
```

### 预读条件

上述函数控制了何时触发预读。而对于某一个页面是否需要被预读的决策，实现在函数 `XLogPrefetcherNextBlock` 中。并不是所有的页面都可以或需要被预读，在 `XLogPrefetcher` 结构中维护了以下几个结构来对预读请求进行过滤：

- `filter_table` / `filter_queue`：动态过滤条件，记录了 redo 到某个 LSN 之前，不要预读某个物理文件中大于一定长度的所有页面；因为在 redo 到某条记录之前，对应的页面在存储上可能暂时还不存在，因而无法预读
- `recent_rlocator` / `recent_block` / `recent_idx`：记录了最近已经发起的预读请求，被维护为环形缓冲区，可以避免对同一个页面重复发起预读请求
- `no_readahead_until`：对某些类型的日志，在这条记录之前都不再需要预读了

```c
struct XLogPrefetcher
{
    /* ... */

    /* Book-keeping to avoid accessing blocks that don't exist yet. */
    HTAB       *filter_table;
    dlist_head  filter_queue;

    /* Book-keeping to avoid repeat prefetches. */
    RelFileLocator recent_rlocator[XLOGPREFETCHER_SEQ_WINDOW_SIZE];
    BlockNumber recent_block[XLOGPREFETCHER_SEQ_WINDOW_SIZE];
    int         recent_idx;

    /* Book-keeping to disable prefetching temporarily. */
    XLogRecPtr  no_readahead_until;

    /* ... */
};
```

首先，对部分 WAL 日志类型构造一些动态过滤条件。比如，对于创建数据库、创建表的日志记录，在这些记录被 redo 之前，相应的文件都不存在，因此无法预读。所以在 redo 到这条记录的 LSN 之前，直接跳过对相关物理文件的预读：

```c
/*
 * Check for operations that require us to filter out block ranges, or
 * pause readahead completely.
 */
if (replaying_lsn < record->lsn)
{
    uint8       rmid = record->header.xl_rmid;
    uint8       record_type = record->header.xl_info & ~XLR_INFO_MASK;

    if (rmid == RM_XLOG_ID)
    {
        if (record_type == XLOG_CHECKPOINT_SHUTDOWN ||
            record_type == XLOG_END_OF_RECOVERY)
        {
            /*
             * These records might change the TLI.  Avoid potential
             * bugs if we were to allow "read TLI" and "replay TLI" to
             * differ without more analysis.
             */
            prefetcher->no_readahead_until = record->lsn;

            /* Fall through so we move past this record. */
        }
    }
    else if (rmid == RM_DBASE_ID)
    {
        /*
         * When databases are created with the file-copy strategy,
         * there are no WAL records to tell us about the creation of
         * individual relations.
         */
        if (record_type == XLOG_DBASE_CREATE_FILE_COPY)
        {
            xl_dbase_create_file_copy_rec *xlrec =
                (xl_dbase_create_file_copy_rec *) record->main_data;
            RelFileLocator rlocator =
            {InvalidOid, xlrec->db_id, InvalidRelFileNumber};

            /*
             * Don't try to prefetch anything in this database until
             * it has been created, or we might confuse the blocks of
             * different generations, if a database OID or
             * relfilenumber is reused.  It's also more efficient than
             * discovering that relations don't exist on disk yet with
             * ENOENT errors.
             */
            XLogPrefetcherAddFilter(prefetcher, rlocator, 0, record->lsn);
        }
    }
    else if (rmid == RM_SMGR_ID)
    {
        if (record_type == XLOG_SMGR_CREATE)
        {
            xl_smgr_create *xlrec = (xl_smgr_create *)
                record->main_data;

            if (xlrec->forkNum == MAIN_FORKNUM)
            {
                /*
                 * Don't prefetch anything for this whole relation
                 * until it has been created.  Otherwise we might
                 * confuse the blocks of different generations, if a
                 * relfilenumber is reused.  This also avoids the need
                 * to discover the problem via extra syscalls that
                 * report ENOENT.
                 */
                XLogPrefetcherAddFilter(prefetcher, xlrec->rlocator, 0,
                                        record->lsn);
            }
        }
        else if (record_type == XLOG_SMGR_TRUNCATE)
        {
            xl_smgr_truncate *xlrec = (xl_smgr_truncate *)
                record->main_data;

            /*
             * Don't consider prefetching anything in the truncated
             * range until the truncation has been performed.
             */
            XLogPrefetcherAddFilter(prefetcher, xlrec->rlocator,
                                    xlrec->blkno,
                                    record->lsn);
        }
    }
}
```

然后从还未进行预读的下一个页面开始继续处理。

跳过预读非 [main fork](https://www.postgresql.org/docs/current/storage.html) 的页面，因为 WAL 日志中绝大部分修改都是基于 main fork 的，其余部分 fork 甚至不记录 WAL 日志：

```c
/* We don't try to prefetch anything but the main fork for now. */
if (block->forknum != MAIN_FORKNUM)
{
    return LRQ_NEXT_NO_IO;
}
```

跳过预读 FPI (full page image) 类型的日志对应的页面，因为日志中已经有完整的页面内容了，无需再读数据页面：

```c
/*
 * If there is a full page image attached, we won't be reading the
 * page, so don't bother trying to prefetch.
 */
if (block->has_image)
{
    XLogPrefetchIncrement(&SharedStats->skip_fpw);
    return LRQ_NEXT_NO_IO;
}
```

跳过预读将会被抹零的页面：

```c
/* There is no point in reading a page that will be zeroed. */
if (block->flags & BKPBLOCK_WILL_INIT)
{
    XLogPrefetchIncrement(&SharedStats->skip_init);
    return LRQ_NEXT_NO_IO;
}
```

跳过预读符合上述动态过滤条件的页面：

```c
/* Should we skip prefetching this block due to a filter? */
if (XLogPrefetcherIsFiltered(prefetcher, block->rlocator, block->blkno))
{
    XLogPrefetchIncrement(&SharedStats->skip_new);
    return LRQ_NEXT_NO_IO;
}
```

跳过最近已经发起预读的页面，避免重复预读；并将当前页面记录为最近已预读：

```c
/* There is no point in repeatedly prefetching the same block. */
for (int i = 0; i < XLOGPREFETCHER_SEQ_WINDOW_SIZE; ++i)
{
    if (block->blkno == prefetcher->recent_block[i] &&
        RelFileLocatorEquals(block->rlocator, prefetcher->recent_rlocator[i]))
    {
        /*
         * XXX If we also remembered where it was, we could set
         * recent_buffer so that recovery could skip smgropen()
         * and a buffer table lookup.
         */
        XLogPrefetchIncrement(&SharedStats->skip_rep);
        return LRQ_NEXT_NO_IO;
    }
}
prefetcher->recent_rlocator[prefetcher->recent_idx] = block->rlocator;
prefetcher->recent_block[prefetcher->recent_idx] = block->blkno;
prefetcher->recent_idx =
    (prefetcher->recent_idx + 1) % XLOGPREFETCHER_SEQ_WINDOW_SIZE;
```

此时，开始通过存储管理层接口试图打开物理文件。如果物理文件不存在，也直接跳过预读，然后把这个物理文件加入到动态过滤条件中：

```c
/*
 * We could try to have a fast path for repeated references to the
 * same relation (with some scheme to handle invalidations
 * safely), but for now we'll call smgropen() every time.
 */
reln = smgropen(block->rlocator, INVALID_PROC_NUMBER);

/*
 * If the relation file doesn't exist on disk, for example because
 * we're replaying after a crash and the file will be created and
 * then unlinked by WAL that hasn't been replayed yet, suppress
 * further prefetching in the relation until this record is
 * replayed.
 */
if (!smgrexists(reln, MAIN_FORKNUM))
{
    XLogPrefetcherAddFilter(prefetcher, block->rlocator, 0,
                            record->lsn);
    XLogPrefetchIncrement(&SharedStats->skip_new);
    return LRQ_NEXT_NO_IO;
}
```

如果要预读的页面超过了当前文件的最大长度，也跳过预读：

```c
/*
 * If the relation isn't big enough to contain the referenced
 * block yet, suppress prefetching of this block and higher until
 * this record is replayed.
 */
if (block->blkno >= smgrnblocks(reln, block->forknum))
{
    XLogPrefetcherAddFilter(prefetcher, block->rlocator, block->blkno,
                            record->lsn);
    XLogPrefetchIncrement(&SharedStats->skip_new);
    return LRQ_NEXT_NO_IO;
}
```

最终，如果上述条件全都满足，则调用 `PrefetchSharedBuffer` 预读：

```c
/* Try to initiate prefetching. */
result = PrefetchSharedBuffer(reln, block->forknum, block->blkno);
if (BufferIsValid(result.recent_buffer))
{
    /* Cache hit, nothing to do. */
    XLogPrefetchIncrement(&SharedStats->hit);
    block->prefetch_buffer = result.recent_buffer;
    return LRQ_NEXT_NO_IO;
}
else if (result.initiated_io)
{
    /* Cache miss, I/O (presumably) started. */
    XLogPrefetchIncrement(&SharedStats->prefetch);
    block->prefetch_buffer = InvalidBuffer;
    return LRQ_NEXT_IO;
}
```

其中会根据 WAL 日志记录引用的物理文件编号和页面号构造 buffer tag，然后通过 buffer mapping 查询页面是否已经在 buffer pool 中。如果不存在，则调用存储管理层接口 `smgrprefetch` 发起预读：

```c
/*
 * Implementation of PrefetchBuffer() for shared buffers.
 */
PrefetchBufferResult
PrefetchSharedBuffer(SMgrRelation smgr_reln,
                     ForkNumber forkNum,
                     BlockNumber blockNum)
{
    PrefetchBufferResult result = {InvalidBuffer, false};
    BufferTag   newTag;         /* identity of requested block */
    uint32      newHash;        /* hash value for newTag */
    LWLock     *newPartitionLock;   /* buffer partition lock for it */
    int         buf_id;

    Assert(BlockNumberIsValid(blockNum));

    /* create a tag so we can lookup the buffer */
    InitBufferTag(&newTag, &smgr_reln->smgr_rlocator.locator,
                  forkNum, blockNum);

    /* determine its hash code and partition lock ID */
    newHash = BufTableHashCode(&newTag);
    newPartitionLock = BufMappingPartitionLock(newHash);

    /* see if the block is in the buffer pool already */
    LWLockAcquire(newPartitionLock, LW_SHARED);
    buf_id = BufTableLookup(&newTag, newHash);
    LWLockRelease(newPartitionLock);

    /* If not in buffers, initiate prefetch */
    if (buf_id < 0)
    {
#ifdef USE_PREFETCH
        /*
         * Try to initiate an asynchronous read.  This returns false in
         * recovery if the relation file doesn't exist.
         */
        if ((io_direct_flags & IO_DIRECT_DATA) == 0 &&
            smgrprefetch(smgr_reln, forkNum, blockNum, 1))
        {
            result.initiated_io = true;
        }
#endif                          /* USE_PREFETCH */
    }
    else
    {
        /*
         * Report the buffer it was in at that time.  The caller may be able
         * to avoid a buffer table lookup, but it's not pinned and it must be
         * rechecked!
         */
        result.recent_buffer = buf_id + 1;
    }

    /*
     * If the block *is* in buffers, we do nothing.  This is not really ideal:
     * the block might be just about to be evicted, which would be stupid
     * since we know we are going to need it soon.  But the only easy answer
     * is to bump the usage_count, which does not seem like a great solution:
     * when the caller does ultimately touch the block, usage_count would get
     * bumped again, resulting in too much favoritism for blocks that are
     * involved in a prefetch sequence. A real fix would involve some
     * additional per-buffer state, and it's not clear that there's enough of
     * a problem to justify that.
     */

    return result;
}
```

存储管理层接口最终将预读请求封装为 `posix_fadvise` 调用并发送出去。向 OS 提供的建议是 `POSIX_FADV_WILLNEED`，表示这个页面在不久的将来即将被使用。在 startup 进程 redo 早些时候的 WAL 日志记录时，OS 可以在后台提前将这些页面装入 page cache 中：

```c
/*
 * FilePrefetch - initiate asynchronous read of a given range of the file.
 *
 * Currently the only implementation of this function is using posix_fadvise
 * which is the simplest standardized interface that accomplishes this.
 * We could add an implementation using libaio in the future; but note that
 * this API is inappropriate for libaio, which wants to have a buffer provided
 * to read into.
 */
int
FilePrefetch(File file, off_t offset, off_t amount, uint32 wait_event_info)
{
#if defined(USE_POSIX_FADVISE) && defined(POSIX_FADV_WILLNEED)
    int         returnCode;

    Assert(FileIsValid(file));

    DO_DB(elog(LOG, "FilePrefetch: %d (%s) " INT64_FORMAT " " INT64_FORMAT,
               file, VfdCache[file].fileName,
               (int64) offset, (int64) amount));

    returnCode = FileAccess(file);
    if (returnCode < 0)
        return returnCode;

retry:
    pgstat_report_wait_start(wait_event_info);
    returnCode = posix_fadvise(VfdCache[file].fd, offset, amount,
                               POSIX_FADV_WILLNEED);
    pgstat_report_wait_end();

    if (returnCode == EINTR)
        goto retry;

    return returnCode;
#else
    Assert(FileIsValid(file));
    return 0;
#endif
}
```

## 参考资料

[PostgreSQL Documentation: Chapter 28. Reliability and the Write-Ahead Log](https://www.postgresql.org/docs/current/wal.html)

[WIP: WAL prefetch (another approach)](https://www.postgresql.org/message-id/flat/CA%2BhUKGJ4VJN8ttxScUFM8dOKX0BrBiboo5uz1cq%3DAovOddfHpA%40mail.gmail.com)
