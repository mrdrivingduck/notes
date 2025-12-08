# PostgreSQL - WALBufMappingLock

Created by: Mr Dk.

2025 / 08 / 09 20:19

Hangzhou, Zhejiang, China

---

## 背景

在 [PostgreSQL - WAL Insert](./PostgreSQL%20WAL%20Insert.md) 中已经分析过，当多个进程想要并发记录 WAL 日志时，需要先串行地在 WAL 日志中分配预留空间，然后再各自获取 WALInsertLock 并发地将 WAL 日志拷贝到预留空间所对应的 WAL Buffer 中。在进行拷贝之前，如果 WAL Buffer 对应空间中的被替换页面还没来得及写入存储，则需要获取 WALWriteLock 将日志写到存储，然后获取 WALBufMappingLock 将这个页面重新初始化，才能开始使用。

在写入较重的场景中，特别是数据导入场景，一条内容密集的 WAL 日志可能会横跨多个 WAL 日志页面。以索引创建为例，一条未被压缩的 XLOG FPI 日志达到了 229 kB；即使设置 `wal_compression` 使用 ZSTD 压缩算法，也能够达到 61 kB：

```
=> SELECT * FROM pg_get_wal_record_info('1/0C15A768');
start_lsn        | 1/C15A768
end_lsn          | 1/C193FE0
prev_lsn         | 1/C120868
xid              | 762
resource_manager | XLOG
record_type      | FPI
record_length    | 234964
main_data_length | 0
fpi_length       | 234512
description      |
block_ref        | blkref #0: rel 1663/5/16400 fork main blk 27080 (FPW); hole: offset: 1164, length: 2460 blkref #1: ...
```

显然，这样的日志将会占据多个 WAL Buffer 页面。WALBufMappingLock 是一个全局互斥锁，同一时间只有一个进程可以持有该锁，修改 WAL Buffer 页面所映射到的 WAL 日志物理页面。当多个进程需要同时初始化相互独立的 WAL Buffer 页面时，将因为这个互斥锁的存在而互相等待。这实际上并没有必要，多个进程可以并发初始化不同的 WAL Buffer 页面。虽然 WAL Writer 进程会在后台异步地提前初始化页面，尽量避免 Backend 进程在 critical path 上进行初始化。但在重度写入场景中，WAL Writer 也只能尽力而为，Backend 进程将会不可避免地加入竞争。

即将发布的 PostgreSQL 18 对 WAL Buffer 的页面初始化进行了无锁化改造，通过原子变量和条件变量在 WAL Buffer 中限制出了一段可以被多个进程并发初始化的区域，从而彻底移除了 WALBufMappingLock。相关提交为：

```
commit bc22dc0e0ddc2dcb6043a732415019cc6b6bf683
Author: Alexander Korotkov <akorotkov@postgresql.org>
Date:   Wed Apr 2 12:44:24 2025 +0300

    Get rid of WALBufMappingLock

    Allow multiple backends to initialize WAL buffers concurrently.  This way
    `MemSet((char *) NewPage, 0, XLOG_BLCKSZ);` can run in parallel without
    taking a single LWLock in exclusive mode.

    The new algorithm works as follows:
     * reserve a page for initialization using XLogCtl->InitializeReserved,
     * ensure the page is written out,
     * once the page is initialized, try to advance XLogCtl->InitializedUpTo and
       signal to waiters using XLogCtl->InitializedUpToCondVar condition
       variable,
     * repeat previous steps until we reserve initialization up to the target
       WAL position,
     * wait until concurrent initialization finishes using a
       XLogCtl->InitializedUpToCondVar.

    Now, multiple backends can, in parallel, concurrently reserve pages,
    initialize them, and advance XLogCtl->InitializedUpTo to point to the latest
    initialized page.

    Author: Yura Sokolov <y.sokolov@postgrespro.ru>
    Co-authored-by: Alexander Korotkov <aekorotkov@gmail.com>
    Reviewed-by: Pavel Borisov <pashkin.elfe@gmail.com>
    Reviewed-by: Tomas Vondra <tomas@vondra.me>
    Tested-by: Michael Paquier <michael@paquier.xyz>
```

本文基于这次 commit 分析如何实现 WAL Buffer 的并发初始化。

## WAL Buffer 控制结构修改

在 PostgreSQL 17 及之前的版本中，WAL Buffer 共享内存控制结构中的 `InitializedUpTo` 保存了已经初始化完毕的最后一个 WAL 日志页面的结尾 LSN + 1，实际上也就是下一个将要被初始化的 WAL 日志页面的起始 LSN。后续成功竞争到 WALBufMappingLock 的进程将在这把锁的保护下重新初始化页面内容，并修改页面对应的 `xlblocks` 改变页面与物理空间的映射关系，然后向前推进 `InitializedUpTo`：

```c
/*
 * Total shared-memory state for XLOG.
 */
typedef struct XLogCtlData
{
    /* ... */

    /*
     * Latest initialized page in the cache (last byte position + 1).
     *
     * To change the identity of a buffer (and InitializedUpTo), you need to
     * hold WALBufMappingLock.  To change the identity of a buffer that's
     * still dirty, the old page needs to be written out first, and for that
     * you need WALWriteLock, and you need to ensure that there are no
     * in-progress insertions to the page by calling
     * WaitXLogInsertionsToFinish().
     */
    XLogRecPtr  InitializedUpTo;

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

如图所示：

```
     initializing
        |<->|
+---+---+---+---+---+---+---+------+
| 0 | 0 |///| x | x | x |   |      |
+---+---+---+---+---+---+---+------+
        ^
        |
        InitializedUpTo
```

自 PostgreSQL 18 起，引入另一个 `InitializeReserved` 变量并将这两个变量同时修改为原子变量，以便多进程能够无锁修改。此外，通过条件变量 `InitializedUpToCondVar` 约束正在进行初始化的页面区间：

```c
/*
 * Total shared-memory state for XLOG.
 */
typedef struct XLogCtlData
{
    /* ... */

    /*
     * Latest reserved for inititalization page in the cache (last byte
     * position + 1).
     *
     * To change the identity of a buffer, you need to advance
     * InitializeReserved first.  To change the identity of a buffer that's
     * still dirty, the old page needs to be written out first, and for that
     * you need WALWriteLock, and you need to ensure that there are no
     * in-progress insertions to the page by calling
     * WaitXLogInsertionsToFinish().
     */
    pg_atomic_uint64 InitializeReserved;

    /*
     * Latest initialized page in the cache (last byte position + 1).
     *
     * InitializedUpTo is updated after the buffer initialization.  After
     * update, waiters got notification using InitializedUpToCondVar.
     */
    pg_atomic_uint64 InitializedUpTo;
    ConditionVariable InitializedUpToCondVar;

    /* ... */
} XLogCtlData;
```

`InitializeReserved` 指向已经开始初始化的最新页面的结束地址，与 `InitializedUpTo` 形成了一段 _正在初始化_ 的 WAL Buffer 页面区间，多个进程可以在这个区间中对页面进行并发 `memset` 清零以及页面映射关系修改。如图所示：

```
              initializing
        |<--------------------->|
+---+---+---+---+---+---+---+---+---+------+
| 0 | 0 |///|\\\|\\\|///|\\\|///|   |      |
+---+---+---+---+---+---+---+---+---+------+
        ^                       ^
        |                       |
        InitializedUpTo         InitializeReserved
```

## 无锁算法

对 WAL Buffer 页面进行初始化的流程依旧由 `AdvanceXLInsertBuffer` 函数实现，功能是将 WAL Buffer 初始化到参数传入的 `upto` 位置为止：

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
```

### 整体目标

该函数的整体目标是，先将共享内存中的 `InitializeReserved` 推进到大于当前进程希望初始化到的 `upto` 位置，然后等待 `InitializedUpTo` 推进到 `upto` 位置才返回：

- 如果当前页面正被其它进程初始化中，则继续初始化后续页面
- 如果没有进程正在参与当前页面的初始化，则由当前进程来进行
- 如果所有页面都正被其它进程初始化中，那么通过条件变量 `InitializedUpToCondVar` 等待其它进程初始化结束

```c
START_CRIT_SECTION();

/*--
 * Loop till we get all the pages in WAL buffer before 'upto' reserved for
 * initialization.  Multiple process can initialize different buffers with
 * this loop in parallel as following.
 *
 * 1. Reserve page for initialization using XLogCtl->InitializeReserved.
 * 2. Initialize the reserved page.
 * 3. Attempt to advance XLogCtl->InitializedUpTo,
 */
ReservedPtr = pg_atomic_read_u64(&XLogCtl->InitializeReserved);
while (upto >= ReservedPtr || opportunistic)
{
    /* ... */
}

END_CRIT_SECTION();

/*
 * All the pages in WAL buffer before 'upto' were reserved for
 * initialization.  However, some pages might be reserved by concurrent
 * processes.  Wait till they finish initialization.
 */
while (upto >= pg_atomic_read_u64(&XLogCtl->InitializedUpTo))
    ConditionVariableSleep(&XLogCtl->InitializedUpToCondVar, WAIT_EVENT_WAL_BUFFER_INIT);
ConditionVariableCancelSleep();
```

那么每个进程如何确定自己是否要做初始化还是等待其它进程初始化呢？

### 计算被替换页面的地址

由于 WAL Buffer 是个环形缓冲区，每个进程首先需要从共享内存中获取下一个未被初始化的页面位置，并计算出这个位置对应的被替换页面地址：通常是减去整个环形缓冲区的大小。只有被替换页面已被写入存储了，当前页面才能被重新初始化：

```c
/*
 * Get ending-offset of the buffer page we need to replace.
 *
 * We don't lookup into xlblocks, but rather calculate position we
 * must wait to be written. If it was written, xlblocks will have this
 * position (or uninitialized)
 */
if (ReservedPtr + XLOG_BLCKSZ > XLOG_BLCKSZ * XLOGbuffers)
    OldPageRqstPtr = ReservedPtr + XLOG_BLCKSZ - XLOG_BLCKSZ * XLOGbuffers;
else
    OldPageRqstPtr = InvalidXLogRecPtr;
```

如图所示：

```
   To Be Replaced         To Be Initialized
        |<->|                   |<->|
        |<-- WAL Buffer Size -->|
+---+---+---+---+---+---+---+---+---+------+
|...|...|///|\\\|\\\|///|\\\|///|...|      |
+---+---+---+---+---+---+---+---+---+------+
                                ^
                                |
                                InitializeReserved
```

### 推进 InitializeReserved

计算出被替换页面的地址后，首先通过 CAS 操作来推进共享内存中的 `InitializeReserved`，如果 CAS 成功，则当前进程成功得到了对这个页面进行初始化的工作；如果 CAS 失败，则说明其它进程已经得到了这个工作，当前进程可以继续尝试初始化后续的页面：

```c
/*
 * Attempt to reserve the page for initialization.  Failure means that
 * this page got reserved by another process.
 */
if (!pg_atomic_compare_exchange_u64(&XLogCtl->InitializeReserved,
                                    &ReservedPtr,
                                    ReservedPtr + XLOG_BLCKSZ))
    continue;
```

### 等待被替换页面写入完成

在开始初始化之前，需要检查当前页面位置的被替换页面是否已被写入，如果没有，则由当前进程尝试完成写入。这里需要竞争 WALWriteLock 锁，由上锁成功的进程真正完成写入。

在 PostgreSQL 18 之前，需要先释放 WALBufMappingLock 再尝试获取 WALWriteLock，将 WAL 日志页面写入存储后释放 WALWriteLock 然后重新获取 WALBufMappingLock。PostgreSQL 18 起 WALBufMappingLock 已被移除，不再有相关的上锁动作：

```c
/* Fall through if it's already written out. */
if (LogwrtResult.Write < OldPageRqstPtr)
{
    /* Nope, got work to do. */

    /* ... */
}
```

### 页面初始化

被替换页面已经被写入存储后，可以开始对当前页面进行重新初始化了。更新这个页面的 `xlblocks` 映射关系并将页面内容抹为全零：

```c
/*
 * Now the next buffer slot is free and we can set it up to be the
 * next output page.
 */
NewPageBeginPtr = ReservedPtr;
NewPageEndPtr = NewPageBeginPtr + XLOG_BLCKSZ;
nextidx = XLogRecPtrToBufIdx(ReservedPtr);

NewPage = (XLogPageHeader) (XLogCtl->pages + nextidx * (Size) XLOG_BLCKSZ);

/* initialize NewPage ... */
/* ... */
pg_atomic_write_u64(&XLogCtl->xlblocks[nextidx], InvalidXLogRecPtr);
pg_write_barrier();
/* ... */
MemSet(NewPage, 0, XLOG_BLCKSZ);
/* ... */
pg_write_barrier();
pg_atomic_write_u64(&XLogCtl->xlblocks[nextidx], NewPageEndPtr);
/* ... */
```

### 推进 InitializedUpTo

页面初始化完毕后，当前进程将会通过 CAS 操作尝试推进共享内存中的 `InitializedUpTo`。如果 CAS 失败，说明还有更早的页面仍在被其它进程初始化中，此时当前进程不可以推进进度，否则就表示更早之前的页面已经全部初始化完毕了。因此，当前进程将会直接放弃推进 `InitializedUpTo`，而是由初始化完最早页面的进程来推进 `InitializedUpTo`，并在推进到最后一个已经初始化完毕的页面后，通过条件变量唤醒所有等待进程：

```c
/*
 * Try to advance XLogCtl->InitializedUpTo.
 *
 * If the CAS operation failed, then some of previous pages are not
 * initialized yet, and this backend gives up.
 *
 * Since initializer of next page might give up on advancing of
 * InitializedUpTo, this backend have to attempt advancing until it
 * find page "in the past" or concurrent backend succeeded at
 * advancing.  When we finish advancing XLogCtl->InitializedUpTo, we
 * notify all the waiters with XLogCtl->InitializedUpToCondVar.
 */
while (pg_atomic_compare_exchange_u64(&XLogCtl->InitializedUpTo, &NewPageBeginPtr, NewPageEndPtr))
{
    NewPageBeginPtr = NewPageEndPtr;
    NewPageEndPtr = NewPageBeginPtr + XLOG_BLCKSZ;
    nextidx = XLogRecPtrToBufIdx(NewPageBeginPtr);

    if (pg_atomic_read_u64(&XLogCtl->xlblocks[nextidx]) != NewPageEndPtr)
    {
        /*
         * Page at nextidx wasn't initialized yet, so we cann't move
         * InitializedUpto further. It will be moved by backend which
         * will initialize nextidx.
         */
        ConditionVariableBroadcast(&XLogCtl->InitializedUpToCondVar);
        break;
    }
}
```

## 相关信息

[PostgreSQL Mailing List: Get rid of WALBufMappingLock](https://www.postgresql.org/message-id/flat/39b39e7a-41b4-4f34-b3f5-db735e74a723%40postgrespro.ru)
