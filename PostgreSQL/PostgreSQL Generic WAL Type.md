# PostgreSQL - Generic WAL Type

Created by: Mr Dk.

2026 / 04 / 12 18:08

Hangzhou, Zhejiang, China

---

## 背景

对于数据库管理系统来说，如果要让对数据页的修改在崩溃后仍能恢复，或者能够通过物理复制将变更传输到备库，就必须把这些操作历史记录在 WAL 日志中并被持久化，并且之后能按顺序回放到页面上。这是具备持久性的重要保证。

PostgreSQL 对堆表、B-tree 索引、GIN 索引等内置 Access Method，各自定义了一套 WAL 格式。先规定「这类修改在日志里如何描述」（涉及哪些块、二进制布局如何），再实现与之配套的回放逻辑——也就是读出这条日志后，如何把变化应用到修改前的页面上。

PostgreSQL 以可扩展性著称：除了上述内置 AM，开发者还可以通过扩展接入新的索引类型或表类型。只要它们的数据结构仍然以「页」为单位落在磁盘上，就需要和内置 AM 一样，保证在崩溃恢复与物理复制下这些页面上的修改可记录、可恢复——这通常需要为这些 AM 设计和定义专门的 WAL 日志格式，并实现与之对应的回放逻辑。

但等等，先别着急开始设计。[Generic WAL](https://www.postgresql.org/docs/current/generic-wal.html) 正是 PostgreSQL 为上述场景提供的一种捷径：把「旧页变成新页」的差异交给通用模块，用统一的格式写进 WAL，并在恢复时用同一套规则回放，而不必再为每一种新 AM 从头定义一整套专有的 WAL 格式与回放代码。

本文基于 PostgreSQL 18 简析这套能够将持久性扩展到其它 AM 的机制。

## 使用限制

Generic WAL 有一个重要的使用限制，即只能被用于使用了 [PostgreSQL 标准页格式](https://www.postgresql.org/docs/current/storage-page-layout.html) 的 AM：页面前部与后部存放有效数据，中间是空闲空间，边界由页头里的 `pd_lower` 与 `pd_upper` 标出。

```
+------------------+
| PageHeaderData   |
+------------------+
| ItemIdData       |
+------------------+  pd_lower
|                  |
|    free space    |
|                  |
+------------------+  pd_upper
| items            |
+------------------+
| special space    |
+------------------+
```

如果 AM 在页面格式设计上没有把页面组织成上述三段，就无法使用 Generic WAL 机制，必须通过 [Custom WAL Resource Manager](https://www.postgresql.org/docs/current/custom-rmgr.html) 机制自行设计 WAL 格式了。

## 格式定义

为什么 Generic WAL 需要 AM 使用上述结构组织页面呢？这其实和后续计算新旧页面之间的差异有重要关联。由于这套机制会暴露给扩展 AM 使用，因此 PostgreSQL 不对页面内容的语义有任何理解，而是直接逐字节对比页面的差异。

与内置 AM 相比，堆表（以及 B-tree、GIN）的 WAL 日志里记录的是有明确业务含义的操作：例如插入一条元组、删除一条元组、分裂索引页等。回放代码读懂这些记录类型后，按 AM 的规则把变更应用到页面上。日志内容与「这次修改在语义上做了什么」是对齐的。Generic WAL 则不走这条路：它既不区分元组与 ItemId，也不解析索引页结构，只知道「这一页中的内容有变化」，差异用字节片段表达即可。Generic WAL 更像是 **与内容语义无关的通用页级 diff**。

PostgreSQL 使用如下的数据结构来记录一个页面的变更：

```c
#define FRAGMENT_HEADER_SIZE    (2 * sizeof(OffsetNumber))
#define MATCH_THRESHOLD         FRAGMENT_HEADER_SIZE
#define MAX_DELTA_SIZE          (BLCKSZ + 2 * FRAGMENT_HEADER_SIZE)

/* Struct of generic xlog data for single page */
typedef struct
{
    Buffer      buffer;         /* registered buffer */
    int         flags;          /* flags for this buffer */
    int         deltaLen;       /* space consumed in delta field */
    char       *image;          /* copy of page image for modification, do not
                                 * do it in-place to have aligned memory chunk */
    char        delta[MAX_DELTA_SIZE];  /* delta between page images */
} GenericXLogPageData;
```

一个页面相对另一个页面的变化叫作 delta，由许多 fragment 顺序拼接而成。每个 fragment 表示：

- 变更开始位置在页面内的 offset
- 变更内容的长度
- 变更内容

```c
static void
writeFragment(GenericXLogPageData *pageData, OffsetNumber offset, OffsetNumber length,
              const char *data)
{
    char       *ptr = pageData->delta + pageData->deltaLen;

    /* Verify we have enough space */
    Assert(pageData->deltaLen + sizeof(offset) +
           sizeof(length) + length <= sizeof(pageData->delta));

    /* Write fragment data */
    memcpy(ptr, &offset, sizeof(offset));
    ptr += sizeof(offset);
    memcpy(ptr, &length, sizeof(length));
    ptr += sizeof(length);
    memcpy(ptr, data, length);
    ptr += length;

    pageData->deltaLen = ptr - pageData->delta;
}
```

因此 Generic WAL 中只记录页面中内容发生变化的字节片段。若两个 fragment 之间没有被修改的字节序列很短，PostgreSQL 会直接合并相邻 fragment，避免 fragment 的元信息比数据还多。`pd_lower` 与 `pd_upper` 之间的空洞两侧不会跨空洞合并：

```c
static void
computeDelta(GenericXLogPageData *pageData, Page curpage, Page targetpage)
{
    int         targetLower = ((PageHeader) targetpage)->pd_lower,
                targetUpper = ((PageHeader) targetpage)->pd_upper,
                curLower = ((PageHeader) curpage)->pd_lower,
                curUpper = ((PageHeader) curpage)->pd_upper;

    pageData->deltaLen = 0;

    /* Compute delta records for lower part of page ... */
    computeRegionDelta(pageData, curpage, targetpage,
                       0, targetLower,
                       0, curLower);
    /* ... and for upper part, ignoring what's between */
    computeRegionDelta(pageData, curpage, targetpage,
                       targetUpper, BLCKSZ,
                       curUpper, BLCKSZ);
}
```

## 写入过程

Generic WAL 的写入主要由四个 API 完成：

- `GenericXLogStart(Relation relation)`：开始构造一条 Generic WAL
- `GenericXLogRegisterBuffer(state, buffer, flags)`：在这条日志中登记一个页面，返回指向页副本的 `Page` 指针；调用方后续将在该副本上修改内容，这样才可以在页面修改完成之后与原版页面计算 delta
- `GenericXLogFinish(state)`：计算 delta，组装 WAL 日志
- `GenericXLogAbort(state)`：放弃构造日志，不修改任何内容

### 全量写入

当一个页面第一次被 WAL 日志记录时，需要把整个页面的内容记录到 WAL 日志里。这样后续才可以在此基础上进行增量修改。所以需要在 `flags` 中加入 `GENERIC_XLOG_FULL_IMAGE` 表示该块以全页镜像记入 WAL，不做 delta 计算。这通常发生在页面被第一次创建时，比如 `CREATE INDEX`。以构建 Bloom 索引的代码片段为例：

```c
static void
flushCachedPage(Relation index, BloomBuildState *buildstate)
{
    Page        page;
    Buffer      buffer = BloomNewBuffer(index);
    GenericXLogState *state;

    state = GenericXLogStart(index);
    page = GenericXLogRegisterBuffer(state, buffer, GENERIC_XLOG_FULL_IMAGE);
    memcpy(page, buildstate->data.data, BLCKSZ);
    GenericXLogFinish(state);
    UnlockReleaseBuffer(buffer);
}
```

### 增量写入

对一个已经存在的页面进行修改时，首先通常需要对页面加排它锁防止被其它进程修改，然后在 `GenericXLogRegisterBuffer` 返回的页面副本上完成修改。同样以 Bloom 索引页面的修改为例：

```c
state = GenericXLogStart(index);
page = GenericXLogRegisterBuffer(state, buffer, 0);

/*
 * We might have found a page that was recently deleted by VACUUM.  If
 * so, we can reuse it, but we must reinitialize it.
 */
if (PageIsNew(page) || BloomPageIsDeleted(page))
    BloomInitPage(page, 0);

if (BloomPageAddItem(&blstate, page, itup))
{
    /* Success!  Apply the change, clean up, and exit */
    GenericXLogFinish(state);
    UnlockReleaseBuffer(buffer);
    ReleaseBuffer(metaBuffer);
    MemoryContextSwitchTo(oldCtx);
    MemoryContextDelete(insertCtx);
    return false;
}

/* Didn't fit, must try other pages */
GenericXLogAbort(state);
UnlockReleaseBuffer(buffer);
```

如果页面被修改成功，那么在后续的 `GenericXLogFinish` 中将会计算副本页面和原页面之间的差异，并记录到 WAL 日志里：

```c
/*
 * Apply changes represented by GenericXLogState to the actual buffers,
 * and emit a generic xlog record.
 */
XLogRecPtr
GenericXLogFinish(GenericXLogState *state)
{
    XLogRecPtr  lsn;
    int         i;

    if (state->isLogged)
    {
        /* Logged relation: make xlog record in critical section. */
        XLogBeginInsert();

        START_CRIT_SECTION();

        /*
         * Compute deltas if necessary, write changes to buffers, mark buffers
         * dirty, and register changes.
         */
        for (i = 0; i < MAX_GENERIC_XLOG_PAGES; i++)
        {
            /* ... */

            /*
             * Compute delta while we still have both the unmodified page and
             * the new image. Not needed if we are logging the full image.
             */
            if (!(pageData->flags & GENERIC_XLOG_FULL_IMAGE))
                computeDelta(pageData, page, (Page) pageData->image);

            /*
             * Apply the image, being careful to zero the "hole" between
             * pd_lower and pd_upper in order to avoid divergence between
             * actual page state and what replay would produce.
             */
            memcpy(page, pageData->image, pageHeader->pd_lower);
            memset(page + pageHeader->pd_lower, 0,
                   pageHeader->pd_upper - pageHeader->pd_lower);
            memcpy(page + pageHeader->pd_upper,
                   pageData->image + pageHeader->pd_upper,
                   BLCKSZ - pageHeader->pd_upper);

            MarkBufferDirty(pageData->buffer);

            if (pageData->flags & GENERIC_XLOG_FULL_IMAGE)
            {
                XLogRegisterBuffer(i, pageData->buffer,
                                   REGBUF_FORCE_IMAGE | REGBUF_STANDARD);
            }
            else
            {
                XLogRegisterBuffer(i, pageData->buffer, REGBUF_STANDARD);
                XLogRegisterBufData(i, pageData->delta, pageData->deltaLen);
            }
        }

        /* Insert xlog record */
        lsn = XLogInsert(RM_GENERIC_ID, 0);

        /* Set LSN */
        for (i = 0; i < MAX_GENERIC_XLOG_PAGES; i++)
        {
            GenericXLogPageData *pageData = &state->pages[i];

            if (BufferIsInvalid(pageData->buffer))
                continue;
            PageSetLSN(BufferGetPage(pageData->buffer), lsn);
        }
        END_CRIT_SECTION();
    }
    /* ... */

    return lsn;
}
```

注意，同一条 Generic WAL 能原子记录的变更页面数量为 `MAX_GENERIC_XLOG_PAGES`，当前为 4。也就是说目前最多允许对四个页面进行一次原子修改。

## 回放

Generic WAL 的回放过程与写入过程恰好相反。从日志里提取出修改的页面号后，先把页面读入 Buffer Pool，然后从日志中提取这个页面的 delta 并直接应用在这个页面上。然后把页面中间的空闲空间 `memset` 为 0：

```c
page = BufferGetPage(buffers[block_id]);
blockDelta = XLogRecGetBlockData(record, block_id, &blockDeltaSize);
applyPageRedo(page, blockDelta, blockDeltaSize);

/*
 * Since the delta contains no information about what's in the
 * "hole" between pd_lower and pd_upper, set that to zero to
 * ensure we produce the same page state that application of the
 * logged action by GenericXLogFinish did.
 */
pageHeader = (PageHeader) page;
memset(page + pageHeader->pd_lower, 0,
       pageHeader->pd_upper - pageHeader->pd_lower);

PageSetLSN(page, lsn);
MarkBufferDirty(buffers[block_id]);
```

而提取 delta 的操作和 delta 的产生过程也是正好相反的，从 delta 中逐个提取 fragment 并复制到 fragment 开始修改的 offset 上：

```c
/*
 * Apply delta to given page image.
 */
static void
applyPageRedo(Page page, const char *delta, Size deltaSize)
{
    const char *ptr = delta;
    const char *end = delta + deltaSize;

    while (ptr < end)
    {
        OffsetNumber offset,
                    length;

        memcpy(&offset, ptr, sizeof(offset));
        ptr += sizeof(offset);
        memcpy(&length, ptr, sizeof(length));
        ptr += sizeof(length);

        memcpy(page + offset, ptr, length);

        ptr += length;
    }
}
```

## 谁在使用它

- PostgreSQL 源码树中，插件目录列表中的 [Bloom 索引](https://www.postgresql.org/docs/current/bloom.html) 使用了 Generic WAL。
- 第三方插件 [pgvector](https://github.com/pgvector/pgvector) 中的 IVFFlat 和 HNSW 两类向量索引使用了 Generic WAL。
- 第三方插件 [rum](https://github.com/postgrespro/rum) 中的 RUM 索引使用了 Generic WAL。
