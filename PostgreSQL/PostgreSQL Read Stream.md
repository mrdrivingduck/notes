# PostgreSQL - Read Stream

Created by: Mr Dk.

2025 / 06 / 29 16:20

Hangzhou, Zhejiang, China

---

## 背景

一直以来，PostgreSQL 的 I/O 模型都是 Buffered I/O，依赖更底层的操作系统/文件系统实现页面缓存和 I/O 合并。这样 PostgreSQL 自身并不需要做太复杂的 I/O 管理，同时也在一定程度上收获了可移植性，但这并不是性能上的极致。

事实上，最希望能够绕过 OS 来自行管理 I/O 的软件就是包括 DBMS 在内的各类数据处理系统。为了提升性能，这类系统通常都有自己的内存缓存，比如 DBMS 的 Buffer Pool。OS 如果也缓存了相同页面，那么实际上是一种浪费；系统处于高吞吐状态时，在 OS 的页面缓存和 DBMS 的页面缓存之间的互相拷贝也会浪费不少 CPU。另外有一句很著名的结论叫作：DBMS **always** knows more than the OS，对于某个页面的缓存应该保留在内存中还是被逐出，OS 的判断并不一定是准确的，DBMS 永远拥有更多的信息。

PostgreSQL 的 I/O 模型自 PostgreSQL 16 开始逐渐向 Direct I/O + Asynchronous I/O 模型过渡。引入 Direct I/O 是为了彻底绕开操作系统，由数据库自身完全管理 I/O；引入 Asynchronous I/O 则是为了补齐并超越原先由 OS 实现的页面预读和 I/O 合并，达成更高的 I/O Concurrency，以获得更好的性能。这对于运行在高带宽、高延时的云存储上的 PostgreSQL 来说意义重大。I/O 模型的过渡并不是在一个版本内完成的：

- PostgreSQL 16 引入了可选的 Direct I/O 参数，但只作为开发者选项
- PostgreSQL 17 引入了 Read Stream，作为 Asynchronous I/O 的更高层接口，兼容现存的 Buffered I/O 模型
- PostgreSQL 18 引入了 Asynchronous I/O 基础设施，但并未正式开始使用

本文编写时 PostgreSQL 18 即将发布 BETA 2。通过分析 PostgreSQL 17 中引入的 Read Stream，窥探 PostgreSQL 的 I/O 模型改造之路。

## Read Stream

Read Stream 是一层抽象接口。使用这层接口的代码需要告诉 Read Stream 接下来将会依次访问的页面编号，然后就可以从 Read Stream 中依次拖出已经在 Buffer Pool 中被 pin 住的所需页面。Read Stream 根据调用方提供的页面编号序列，在内部完成 I/O 合并和页面预读，对调用方屏蔽相关细节。

需要访问的页面编号序列由调用方提供一个回调函数产生，这个函数每被回调一次就返回下一个要访问的页面编号。比如，对于 sequential scan 来说，这个回调函数就应该依次返回从 0 开始的所有页面编号。

Read Stream 的使用模式类似于：

```c
ReadStream *stream = read_stream_begin_relation(..., next_block_cb, ...);

while ((buffer = read_stream_next_buffer(stream, NULL)) != InvalidBuffer)
{
    /* deal with buffer */
}

read_stream_end(stream);
```

因此，Read Stream 要解决的核心问题是：已知一个确定的页面编号序列，如何以最高效的方式管理这些页面的 I/O？针对不同的 I/O pattern，Read Stream 定义了三种场景：

1. Behavior A：需要访问的页面已在 Buffer Pool 中，那么无需任何 I/O，pin 住页面立刻返回
2. Behavior B：需要访问的页面是连续的，那么可以进行 I/O 合并，选择一个最佳的粒度用一次 I/O 将多个页面装入 Buffer Pool 并 pin 住返回，这样上层代码可以一次处理多个页面而无需离开 CPU
3. Behavior C：需要访问的页面是随机离散的，无法合并 I/O，但由于后续要访问的页面编号已知，可以提前让后台进程将这些页面异步地装入 Buffer Pool 中并 pin 住；在未来真正要访问这些页面时，期望这些页面已经在 Buffer Pool 中了，这样上层代码也可以立刻开始处理页面，不再需要等待 I/O 完成

基于这些场景，我们可以归纳出需要被 Read Stream 实现的重点：

1. 额外的状态信息需要被记录：被 pin 住的 Buffer、被提前发起的 I/O 请求
2. 处理某个页面编号的 I/O 请求时，需要展望未来，分析后续访问的页面编号，不仅要吃碗里的还要看锅里的
3. 对连续的页面读取请求，可以进行 I/O 合并；合并粒度不能过大，否则可能冲击其他的并发进程，需要有一个最大值
4. 对离散的页面读取请求，可以同时发起多个 I/O 请求；并发的 I/O 请求数量不能过多，否则同样可能冲击其他并发进程，需要有一个最大的 I/O 并发限度

### 前置条件：Buffer Manager 的改造

I/O 异步化的精髓就是当前进程发起 I/O 请求，委托后台进程代为处理 I/O；当前进程可以先做别的事，稍晚些时候再回来检查 I/O 结果即可。为了过渡到能够委托后台进程来处理 I/O 的 Asynchronous I/O 模式，访问一个 Buffer 的过程被拆分为 `StartReadBuffers` 和 `WaitReadBuffers` 两步：

- `StartReadBuffers`：向后台进程发起一个 I/O 请求，立刻返回
- `WaitReadBuffers`：阻塞等待 I/O 请求完成才返回

这两个步骤中间就是留给 I/O 请求被处理的时间。理论上，尽可能早地发起 I/O 请求，尽可能晚地确认 I/O 结果，中间的时间如果足够 I/O 请求处理完成，那么进程就不需要停滞等待 I/O。

由于 PostgreSQL 17 还在使用 Buffered I/O + Synchronous I/O 模式，因此 `StartReadBuffers` 里实际上不做任何 I/O 工作，仅通过 `fadvise` 建议 OS 的后台线程把页面提前装入页面缓存内；在 `WaitReadBuffers` 里真正进行 I/O 操作时，如果 OS 已经提前将页面装入页面缓存，那么 `WaitReadBuffers` 中的 I/O 操作就只有系统调用 + 内存拷贝的开销了。这也可以算是一种简易的 I/O 异步化。

如果使用 Direct I/O 模式，则需要通过数据库的 I/O 工作进程或特定操作系统的异步 I/O 接口 (比如 Linux 的 [io_uring](https://en.wikipedia.org/wiki/Io_uring)) 代为处理 I/O 请求。这也是 PostgreSQL 后续版本中需要完善的能力。

### Buffer 和 I/O 的状态管理

Read Stream 对象中管理了两个固定长度的环形队列。此处直接复用代码中的注释来进行说明：

- Buffer 队列 (左侧)：`oldest_buffer_index` 和 `next_buffer_index` 中间的部分记录了 Read Stream 已经 pin 住但还未被调用方消费的 Buffer
- In-flight I/O 队列 (右侧)：`oldest_io_index` 和 `next_io_index` 中间的部分记录了 Read Stream 已经发起但还未确认完成的 I/O 请求

```c
/*-------------------------------------------------------------------------
 *
 * ...
 *
 *                          buffers buf/data       ios
 *
 *                          +----+  +-----+       +--------+
 *                          |    |  |     |  +----+ 42..44 | <- oldest_io_index
 *                          +----+  +-----+  |    +--------+
 *   oldest_buffer_index -> | 10 |  |  ?  |  | +--+ 60..60 |
 *                          +----+  +-----+  | |  +--------+
 *                          | 42 |  |  ?  |<-+ |  |        | <- next_io_index
 *                          +----+  +-----+    |  +--------+
 *                          | 43 |  |  ?  |    |  |        |
 *                          +----+  +-----+    |  +--------+
 *                          | 44 |  |  ?  |    |  |        |
 *                          +----+  +-----+    |  +--------+
 *                          | 60 |  |  ?  |<---+
 *                          +----+  +-----+
 *     next_buffer_index -> |    |  |     |
 *                          +----+  +-----+
 *
 * ...
 *
 *-------------------------------------------------------------------------
 */
```

这两个核心队列的长度，分别决定了 Read Stream 对象能一次性持有多少 Buffer，以及能同时发起多少个并发 I/O。它们都由 GUC 参数控制。队列的长度越长，意味着更加超前、贪婪的 I/O 管理，同时也意味着更多的 Buffer 和 I/O 处理能力的资源消耗。

```c
/*
 * State for managing a stream of reads.
 */
struct ReadStream
{
    /* ... */

    /* Read operations that have been started but not waited for yet. */
    InProgressIO *ios;
    int16       oldest_io_index;
    int16       next_io_index;

    /* ... */

    /* Circular queue of buffers. */
    int16       oldest_buffer_index;    /* Next pinned buffer to return */
    int16       next_buffer_index;  /* Index of next buffer to pin */
    Buffer      buffers[FLEXIBLE_ARRAY_MEMBER];
};
```

### 处理 I/O 结果并返回 Buffer

Read Stream 的核心逻辑由 `read_stream_next_buffer` 函数实现。让我们去除所有的非主要路径代码，看看这个函数的主要路径做了什么。

```c
/*
 * Pull one pinned buffer out of a stream.  Each call returns successive
 * blocks in the order specified by the callback.  If per_buffer_data_size was
 * set to a non-zero size, *per_buffer_data receives a pointer to the extra
 * per-buffer data that the callback had a chance to populate, which remains
 * valid until the next call to read_stream_next_buffer().  When the stream
 * runs out of data, InvalidBuffer is returned.  The caller may decide to end
 * the stream early at any time by calling read_stream_end().
 */
Buffer
read_stream_next_buffer(ReadStream *stream, void **per_buffer_data)
{

}
```

首先，确认当前 Read Stream 中是否有已经完成 I/O 可以被立刻消费的 Buffer，如果有，则直接返回。这类 Buffer 可能来自于与前置页面合并 I/O 后被 pin 住的 Buffer。

- 通过 `oldest_buffer_index` 从 Buffer 队列中得到下一个待消费 Buffer
- 通过 I/O 队列确认当前 Buffer 的 I/O 已经完成
- 更新 `oldest_buffer_index` 将 Buffer 移出 Buffer 队列
- 调用 `read_stream_look_ahead` 提前对后续页面发起读取请求，尽量填满 I/O 队列
- 返回 Buffer

```c
Buffer
read_stream_next_buffer(ReadStream *stream, void **per_buffer_data)
{
    /* ... */

    /* Grab the oldest pinned buffer and associated per-buffer data. */
    Assert(stream->pinned_buffers > 0);
    oldest_buffer_index = stream->oldest_buffer_index;
    Assert(oldest_buffer_index >= 0 &&
           oldest_buffer_index < stream->queue_size);
    buffer = stream->buffers[oldest_buffer_index];
    if (per_buffer_data)
        *per_buffer_data = get_per_buffer_data(stream, oldest_buffer_index);

    Assert(BufferIsValid(buffer));

    /* Do we have to wait for an associated I/O first? */
    if (stream->ios_in_progress > 0 &&
        stream->ios[stream->oldest_io_index].buffer_index == oldest_buffer_index)
    {
        /* ... */
    }

    /* Pin transferred to caller. */
    Assert(stream->pinned_buffers > 0);
    stream->pinned_buffers--;

    /* Advance oldest buffer, with wrap-around. */
    stream->oldest_buffer_index++;
    if (stream->oldest_buffer_index == stream->queue_size)
        stream->oldest_buffer_index = 0;

    /* Prepare for the next call. */
    read_stream_look_ahead(stream, false);

    return buffer;
}
```

如果 I/O 队列显示这个 Buffer 的 I/O 请求暂未被确认，则需要调用 `WaitReadBuffers` 一直等待到 I/O 请求完成，然后将 I/O 请求从 I/O 队列中移出。在返回 Buffer 前，决定后续 I/O 请求的大小。通常来说，以之前 I/O 预读窗口大小的两倍快速扩大预读窗口，以便尽量发起更多的 I/O 请求，但不超过 Buffer 队列的长度；如果探测到顺序访问页面的 pattern，则保持 I/O 请求不超过 I/O 合并的最大粒度。

```c
Buffer
read_stream_next_buffer(ReadStream *stream, void **per_buffer_data)
{
    /* ... */

    /* Do we have to wait for an associated I/O first? */
    if (stream->ios_in_progress > 0 &&
        stream->ios[stream->oldest_io_index].buffer_index == oldest_buffer_index)
    {
        int16       io_index = stream->oldest_io_index;
        int16       distance;

        /* Sanity check that we still agree on the buffers. */
        Assert(stream->ios[io_index].op.buffers ==
               &stream->buffers[oldest_buffer_index]);

        WaitReadBuffers(&stream->ios[io_index].op);

        Assert(stream->ios_in_progress > 0);
        stream->ios_in_progress--;
        if (++stream->oldest_io_index == stream->max_ios)
            stream->oldest_io_index = 0;

        if (stream->ios[io_index].op.flags & READ_BUFFERS_ISSUE_ADVICE)
        {
            /* Distance ramps up fast (behavior C). */
            distance = stream->distance * 2;
            distance = Min(distance, stream->max_pinned_buffers);
            stream->distance = distance;
        }
        else
        {
            /* No advice; move towards io_combine_limit (behavior B). */
            if (stream->distance > stream->io_combine_limit)
            {
                stream->distance--;
            }
            else
            {
                distance = stream->distance * 2;
                distance = Min(distance, stream->io_combine_limit);
                distance = Min(distance, stream->max_pinned_buffers);
                stream->distance = distance;
            }
        }
    }

    /* ... */
}
```

此外，用一个单独的 `if` 分支处理读到 Read Stream 结尾的场景，即 Read Stream 对象已经不持有任何 Buffer。向调用方返回 `InvalidBuffer` 表示结束：

```c
Buffer
read_stream_next_buffer(ReadStream *stream, void **per_buffer_data)
{
    /* ... */

    if (unlikely(stream->pinned_buffers == 0))
    {
        Assert(stream->oldest_buffer_index == stream->next_buffer_index);

        /* End of stream reached?  */
        if (stream->distance == 0)
            return InvalidBuffer;

        /*
         * The usual order of operations is that we look ahead at the bottom
         * of this function after potentially finishing an I/O and making
         * space for more, but if we're just starting up we'll need to crank
         * the handle to get started.
         */
        read_stream_look_ahead(stream, true);

        /* End of stream reached? */
        if (stream->pinned_buffers == 0)
        {
            Assert(stream->distance == 0);
            return InvalidBuffer;
        }
    }

    /* ... */
}
```

### I/O 合并

上面的函数可以认为是在消费 I/O 请求的结果。每消费掉一个 Buffer，都需要尽快发起新的 I/O 请求，或合并相邻页面的 I/O 请求，在资源限制的范围内尽可能填满 I/O 队列。这个过程在 `read_stream_look_ahead` 中实现。

在 I/O 队列未满时，不断获取下一个要访问的页面编号：

- 如果目前积攒的 I/O 请求大小已经达到 I/O 合并的最大粒度，那么立刻发起 I/O 请求
- 如果目前积攒的 I/O 请求大小尚未达到 I/O 合并的最大粒度，那么通过 `read_stream_get_block` 确认下一个页面与当前读请求是否相邻
  - 如果相邻，那么 I/O 可以合并，记录合并后继续查看下一个页面
  - 如果不相邻，则 I/O 无法合并，那么立刻发起已积攒的 I/O 请求，然后将下一个页面作为后续积攒 I/O 请求的第一个页面

```c
static void
read_stream_look_ahead(ReadStream *stream, bool suppress_advice)
{
    while (stream->ios_in_progress < stream->max_ios &&
           stream->pinned_buffers + stream->pending_read_nblocks < stream->distance)
    {
        BlockNumber blocknum;
        int16       buffer_index;
        void       *per_buffer_data;

        if (stream->pending_read_nblocks == stream->io_combine_limit)
        {
            read_stream_start_pending_read(stream, suppress_advice);
            suppress_advice = false;
            continue;
        }

        /*
         * See which block the callback wants next in the stream.  We need to
         * compute the index of the Nth block of the pending read including
         * wrap-around, but we don't want to use the expensive % operator.
         */
        buffer_index = stream->next_buffer_index + stream->pending_read_nblocks;
        if (buffer_index >= stream->queue_size)
            buffer_index -= stream->queue_size;
        Assert(buffer_index >= 0 && buffer_index < stream->queue_size);
        per_buffer_data = get_per_buffer_data(stream, buffer_index);
        blocknum = read_stream_get_block(stream, per_buffer_data);
        if (blocknum == InvalidBlockNumber)
        {
            /* End of stream. */
            stream->distance = 0;
            break;
        }

        /* Can we merge it with the pending read? */
        if (stream->pending_read_nblocks > 0 &&
            stream->pending_read_blocknum + stream->pending_read_nblocks == blocknum)
        {
            stream->pending_read_nblocks++;
            continue;
        }

        /* We have to start the pending read before we can build another. */
        while (stream->pending_read_nblocks > 0)
        {
            read_stream_start_pending_read(stream, suppress_advice);
            suppress_advice = false;
            if (stream->ios_in_progress == stream->max_ios)
            {
                /* And we've hit the limit.  Rewind, and stop here. */
                read_stream_unget_block(stream, blocknum);
                return;
            }
        }

        /* This is the start of a new pending read. */
        stream->pending_read_blocknum = blocknum;
        stream->pending_read_nblocks = 1;
    }

    /* ... */
}
```

如果已经没有更多页面需要访问了，那么立刻发出已积攒的读请求：

```c
static void
read_stream_look_ahead(ReadStream *stream, bool suppress_advice)
{
    while (stream->ios_in_progress < stream->max_ios &&
           stream->pinned_buffers + stream->pending_read_nblocks < stream->distance)
    {
        /* ... */
    }

    /*
     * We don't start the pending read just because we've hit the distance
     * limit, preferring to give it another chance to grow to full
     * io_combine_limit size once more buffers have been consumed.  However,
     * if we've already reached io_combine_limit, or we've reached the
     * distance limit and there isn't anything pinned yet, or the callback has
     * signaled end-of-stream, we start the read immediately.
     */
    if (stream->pending_read_nblocks > 0 &&
        (stream->pending_read_nblocks == stream->io_combine_limit ||
         (stream->pending_read_nblocks == stream->distance &&
          stream->pinned_buffers == 0) ||
         stream->distance == 0) &&
        stream->ios_in_progress < stream->max_ios)
        read_stream_start_pending_read(stream, suppress_advice);
}
```

### 获取页面编号序列

上述函数中，需要不断迭代下一个将要访问的页面编号，这是通过 `read_stream_get_block` 函数完成的。该函数中回调了调用方提供的 callback，得到下一个要访问的页面编号：

```c
/*
 * Ask the callback which block it would like us to read next, with a one block
 * buffer in front to allow read_stream_unget_block() to work.
 */
static inline BlockNumber
read_stream_get_block(ReadStream *stream, void *per_buffer_data)
{
    BlockNumber blocknum;

    blocknum = stream->buffered_blocknum;
    if (blocknum != InvalidBlockNumber)
        stream->buffered_blocknum = InvalidBlockNumber;
    else
    {
        /*
         * Tell Valgrind that the per-buffer data is undefined.  That replaces
         * the "noaccess" state that was set when the consumer moved past this
         * entry last time around the queue, and should also catch callbacks
         * that fail to initialize data that the buffer consumer later
         * accesses.  On the first go around, it is undefined already.
         */
        VALGRIND_MAKE_MEM_UNDEFINED(per_buffer_data,
                                    stream->per_buffer_data_size);
        blocknum = stream->callback(stream,
                                    stream->callback_private_data,
                                    per_buffer_data);
    }

    return blocknum;
}
```

回调函数的实现方式因调用方而异。对于 sequential scan 来说，回调函数需要依次返回文件的每一个页面编号：

```c
/*
 * Streaming read API callback for serial sequential and TID range scans.
 * Returns the next block the caller wants from the read stream or
 * InvalidBlockNumber when done.
 */
static BlockNumber
heap_scan_stream_read_next_serial(ReadStream *stream,
                                  void *callback_private_data,
                                  void *per_buffer_data)
{
    HeapScanDesc scan = (HeapScanDesc) callback_private_data;

    if (unlikely(!scan->rs_inited))
    {
        scan->rs_prefetch_block = heapgettup_initial_block(scan, scan->rs_dir);
        scan->rs_inited = true;
    }
    else
        scan->rs_prefetch_block = heapgettup_advance_block(scan,
                                                           scan->rs_prefetch_block,
                                                           scan->rs_dir);

    return scan->rs_prefetch_block;
}
```

对于 [ANALYZE](https://www.postgresql.org/docs/current/sql-analyze.html) 来说，则是返回下一个被采样收集统计信息的页面编号：

```c
/*
 * Read stream callback returning the next BlockNumber as chosen by the
 * BlockSampling algorithm.
 */
static BlockNumber
block_sampling_read_stream_next(ReadStream *stream,
                                void *callback_private_data,
                                void *per_buffer_data)
{
    BlockSamplerData *bs = callback_private_data;

    return BlockSampler_HasMore(bs) ? BlockSampler_Next(bs) : InvalidBlockNumber;
}
```

### 发起 I/O 请求

在分析完后续要访问的页面编号后，Read Stream 组装出了每个 I/O 请求的位置和大小。接下来需要将这些 I/O 请求发送出去，并将这些请求的信息记录到 I/O 队列中，以便后续消费 I/O 结果。这个过程在函数 `read_stream_start_pending_read` 中完成：

- 调用 `StartReadBuffers` 发起 I/O 请求 (PostgreSQL 17 中暂时使用 [`fadvise`](https://man7.org/linux/man-pages/man1/fadvise.1.html))
- 将本次 I/O 需要 pin 住的 Buffer 记录到 Buffer 队列中
- 如果 Buffer 命中 Buffer Pool，则控制好预读窗口，先把碗里的吃完
- 如果 Buffer 未命中，则将 I/O 请求记录到 I/O 队列中

```c
static void
read_stream_start_pending_read(ReadStream *stream, bool suppress_advice)
{
    /* ... */

    /*
     * If advice hasn't been suppressed, this system supports it, and this
     * isn't a strictly sequential pattern, then we'll issue advice.
     */
    if (!suppress_advice &&
        stream->advice_enabled &&
        stream->pending_read_blocknum != stream->seq_blocknum)
        flags = READ_BUFFERS_ISSUE_ADVICE;
    else
        flags = 0;

    /* We say how many blocks we want to read, but may be smaller on return. */
    buffer_index = stream->next_buffer_index;
    io_index = stream->next_io_index;
    nblocks = stream->pending_read_nblocks;
    need_wait = StartReadBuffers(&stream->ios[io_index].op,
                                 &stream->buffers[buffer_index],
                                 stream->pending_read_blocknum,
                                 &nblocks,
                                 flags);
    stream->pinned_buffers += nblocks;

    /* Remember whether we need to wait before returning this buffer. */
    if (!need_wait)
    {
        /* Look-ahead distance decays, no I/O necessary (behavior A). */
        if (stream->distance > 1)
            stream->distance--;
    }
    else
    {
        /*
         * Remember to call WaitReadBuffers() before returning head buffer.
         * Look-ahead distance will be adjusted after waiting.
         */
        stream->ios[io_index].buffer_index = buffer_index;
        if (++stream->next_io_index == stream->max_ios)
            stream->next_io_index = 0;
        Assert(stream->ios_in_progress < stream->max_ios);
        stream->ios_in_progress++;
        stream->seq_blocknum = stream->pending_read_blocknum + nblocks;
    }

    /* ... */

    /* Compute location of start of next read, without using % operator. */
    buffer_index += nblocks;
    if (buffer_index >= stream->queue_size)
        buffer_index -= stream->queue_size;
    Assert(buffer_index >= 0 && buffer_index < stream->queue_size);
    stream->next_buffer_index = buffer_index;

    /* Adjust the pending read to cover the remaining portion, if any. */
    stream->pending_read_blocknum += nblocks;
    stream->pending_read_nblocks -= nblocks;
}
```

## 参考资料

[Thomas Munro, Nazir Bilal Yavuz - Streaming I/O and vectored I/O (PGConf.EU 2024)](https://www.youtube.com/watch?v=8d6YrSByNew)

[Andres Freund: The path to using AIO in postgres (PGConf.EU 2023)](https://www.youtube.com/watch?v=qX50xrHwQa4)
