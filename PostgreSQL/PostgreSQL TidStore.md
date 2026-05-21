# PostgreSQL - Tid Store

Created by: Mr Dk.

Co-authored by: Claude Opus 4.6

2026 / 05 / 18 15:30

Hangzhou, Zhejiang, China

---

## 背景

在 PostgreSQL 的 [VACUUM](./PostgreSQL%20VACUUM.md) 流程中，Phase I 的堆表扫描需要把扫描到的死亡元组 TID（页面号 + 页内偏移）收集起来，供后续 Phase II 和 III 的索引清理和堆页面回收使用。在 PostgreSQL 17 之前，这个集合的底层存储是一个排序数组。

PostgreSQL 17 开始引入 Tid Store 数据结构替代原先的排序数组。Tid Store 底层基于 Leis, V., Kemper, A., Neumann, T. 在 ICDE 2013 上发表的 _The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases_ 实现的 Adaptive Radix Tree (ART)，不仅将内存占用降低了一到两个数量级，还大幅提升了 TID 查找效率，使 VACUUM 的性能得到了明显改善。

本文将从 Radix Tree 讲起，分析 ART 的改进思路以及 PostgreSQL 引入 Tid Store 前后的变化。整体上涉及三个提交：

- `ee1b30f128` - Add template for adaptive radix tree.
- `30e144287a` - Add TIDStore, to store sets of TIDs (ItemPointerData) efficiently.
- `667e65aac3` - Use TidStore for dead tuple TIDs storage during lazy vacuum.

## Trie 与 Radix Tree

### Trie（前缀树）

Trie 是一种用于高效检索序列集合的树形结构。它的特点是：从根到叶的路径本身就编码了键值，查找时间只与键的长度 k 相关，和集合大小 n 无关。不同键的公共前缀共享同一段路径。比如：

```
存储 "data", "database", "datastore", "datum":

    (root)
      |
      d
      |
      a
      |
      t
     / \
    a*   u
   / \    \
  b   s    m*
  |   |
  a   t
  |   |
  s   o
  |   |
  e*  r
      |
      e*

（* 标记有值的节点）
```

整棵 Trie 有 16 个节点。但 Trie 有个问题：如果字符集大小为 σ（比如按一个字节来分层就是 256），每个节点都要维护一个大小为 σ 的指针数组用于存放下层节点。当树的下层比较稀疏的时候，大部分指针都是 NULL，内存浪费将会非常严重。

### Radix Tree（基数树）

Radix Tree 是 Trie 的一种空间压缩变体。核心思想是把只有单个子节点的连续边合并成一条边（路径压缩），消除冗余节点。还是上面那个例子，Radix Tree 压缩后只需要 6 个节点：

```
     (root)
       |
      dat
      / \
    a*   um*
   / \
base* store*
```

另一个常见的变体是按固定长度的 bit 组（span）进行分支。比如 Linux 内核的 [XArray](https://github.com/torvalds/linux/blob/v6.19/include/linux/xarray.h#L1154) 使用 span=6，每个节点有 64 个槽位，每层消费键的 6 个 bit。这种按 span 分层的方式让 Radix Tree 适用于整数键的场景——键被拆成若干个固定宽度的 chunk，每层用一个 chunk 做索引。

Span 的选择是一个权衡：span 越大，树越矮、查找路径越短，但节点的指针数组越大，稀疏时浪费越严重；span 越小，节点紧凑，但树变高，访问层数增加。

传统 Radix Tree 的根本矛盾在于：每个内部节点的指针数组大小是 **固定** 的，在构建之前无法预知每个节点实际会有几个子节点。Span 选大了，稀疏节点浪费严重；选小了，稠密节点又要多走层数。无论怎么选，都是在用一个静态策略去应对动态的数据分布。

### 典型应用场景

Trie / Radix Tree 在系统软件中被广泛使用：

- 路由表查找：IP 地址是固定长度的 bit 序列，Radix Tree 做最长前缀匹配
- 内存页面管理：Linux 内核的 page cache，键是页面偏移量
- 文件系统：目录项索引、inode 映射
- 数据库索引：内存数据库的主键索引、字符串字典编码

共同特点是：键为整数或定长序列，查找频繁，需要有序遍历或范围查询。

## Adaptive Radix Tree（ART）

ART 源自 Leis, V., Kemper, A., Neumann, T. 在 ICDE 2013 上发表的论文 [_The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases_](https://db.in.tum.de/~leis/papers/ART.pdf)。它要解决的核心问题是：在保持 Radix Tree 有序性和查找效率的前提下，消除稀疏节点的内存浪费。

### 自适应节点类型

ART 的核心创新是：根据子节点数量 **动态选择** 不同的节点表示。其定义了四种节点类型：

| 节点类型 | 容量上限 | 查找方式               | 适用场景         |
| -------- | -------- | ---------------------- | ---------------- |
| Node4    | 4        | 线性扫描 key 数组      | 极稀疏           |
| Node16   | 16       | SIMD 并行比较 key 数组 | 中低密度         |
| Node48   | 48       | 256 项索引 → 紧凑数组  | 中高密度         |
| Node256  | 256      | 直接索引               | 稠密（传统方式） |

当节点的子节点数量超出当前类型容量时，节点升级为下一级别；反之则降级。这使得 ART 在稀疏时接近 Hash Table 的内存效率，在稠密时又保持传统 Radix Tree 的性能。

```
一个内部节点只有 3 个子节点时，使用 Node4：
  Node4 { keys: [0x0A, 0x1F, 0x80, _], children: [ptr1, ptr2, ptr3, _] }

当第 5 个子节点插入，升级为 Node16：
  Node16 { keys: [0x0A, 0x1F, 0x42, 0x80, 0xCC, _, ...], children: [...] }

超过 16 个子节点，升级为 Node48：
  Node48 { index[256]: 大部分为空, 有值的字节指向 children 数组的槽位 }

超过 48 个子节点，升级为 Node256：
  Node256 { children[256]: 直接用字节值做下标索引 }
```

### 性能特征

论文的实验表明，ART 在内存数据库工作负载中：

- 查找性能接近 Hash Table，优于 B+ 树和传统 Radix Tree
- 稀疏键分布下，空间效率远优于固定 span=8 的传统 Radix Tree（后者每个节点 2KB，ART 的 Node4 只要数十字节）
- 键天然有序，范围扫描的缓存友好性远优于 Hash Table
- 插入/删除的代价是节点类型切换时的拷贝，但分摊后依旧高效

## VACUUM 中旧的 Dead Tuple 存储

在 Tid Store 引入之前（PostgreSQL 16 及更早），VACUUM 用一个扁平的 `ItemPointerData` 数组存储死亡元组的 TID。数据结构定义如下：

```c
typedef struct VacDeadItems
{
    int         max_items;      /* # slots allocated in array */
    int         num_items;      /* current # of entries */

    /* Sorted array of TIDs to delete from indexes */
    ItemPointerData items[FLEXIBLE_ARRAY_MEMBER];
} VacDeadItems;

#define MAXDEADITEMS(avail_mem) \
    (((avail_mem) - offsetof(VacDeadItems, items)) / sizeof(ItemPointerData))
```

每个 `ItemPointerData` 占 6 字节（4 字节 `BlockNumber` + 2 字节 `OffsetNumber`）。这个方案存在几个问题：

- 1GB 硬上限：数组内存分配受 `MaxAllocSize`（1GB）限制，最多只能存放约 1.78 亿条 TID。对死元组较多的表来说可能不够，在放满后不得不中断扫描、先清理索引、清空数组后再继续——而每次中断都意味着重新扫描所有索引，带来极大的 I/O 放大。
- 悲观预分配：数组大小在 VACUUM 开始时就根据表大小和 `maintenance_work_mem` 计算并一次性分配。即使最终只有很少的 dead tuple，内存也已经分配出去了。
- 查找效率差：索引清理阶段需要对每个索引条目判断它指向的 heap TID 是否是 dead tuple。对于数千万元素的数组，二分查找在大范围内跳跃，CPU cache miss 率高，分支预测表现糟糕。
- 并行 VACUUM 受限：数组放在共享内存中时必须预先确定大小，无法按需扩展。

## PostgreSQL 的 ART 实现

PostgreSQL 的 ART 实现位于 `radixtree.h`，被设计为 C 宏模板模式。通过在 `#include` 之前定义一组宏，为特定值类型和内存模型生成特化代码：

```c
#define RT_PREFIX       local_ts        // 符号前缀
#define RT_VALUE_TYPE   BlocktableEntry // 值类型
#define RT_VARLEN_VALUE_SIZE(page) \
    (offsetof(BlocktableEntry, words) + \
    sizeof(bitmapword) * (page)->nwords)
#include "lib/radixtree.h"
```

### 键与 Span

固定使用 64 位无符号整数键，span 为 8（每层消费一个字节）。PostgreSQL 中实现了非常简易的路径压缩：跳过键高位全为零的层级，树不会因为键空间的理论上限而变得不必要的深。这意味着：

- 每层使用键的一个字节来索引，最多 8 层
- Fan-out 最大 256，字节可直接寻址，不需要位运算提取
- 树高度随键值范围自适应：如果所有键都小于 2^24，那么树最多只有 3 层

### 四种节点

```c
/* Common header for all nodes */
typedef struct RT_NODE
{
    uint8       kind;       /* Node kind: 4/16/48/256 */
    uint8       fanout;     /* Max capacity for current size class */
    uint8       count;      /* Number of children */
}           RT_NODE;

typedef struct RT_NODE_4
{
    RT_NODE     base;
    uint8       chunks[RT_FANOUT_4_MAX];
    RT_PTR_ALLOC children[FLEXIBLE_ARRAY_MEMBER];
}           RT_NODE_4;

typedef struct RT_NODE_16
{
    RT_NODE     base;
    uint8       chunks[RT_FANOUT_16_MAX];
    RT_PTR_ALLOC children[FLEXIBLE_ARRAY_MEMBER];
}           RT_NODE_16;

typedef struct RT_NODE_48
{
    RT_NODE     base;
    uint8       slot_idxs[RT_NODE_MAX_SLOTS];  /* 256-element index */
    bitmapword  isset[...];
    RT_PTR_ALLOC children[FLEXIBLE_ARRAY_MEMBER];
}           RT_NODE_48;

typedef struct RT_NODE_256
{
    RT_NODE     base;
    bitmapword  isset[...];
    RT_PTR_ALLOC children[RT_FANOUT_256];      /* 256 slots, direct index */
}           RT_NODE_256;
```

Node4 和 Node16 把 key chunk 排好序放在 `chunks[]` 数组中，查找时线性扫描或 SIMD 并行比较。Node48 用一个 256 元素的 `slot_idxs` 数组做间接索引——给一个 chunk 值，查 `slot_idxs[chunk]` 得到子节点在 `children[]` 中的位置。Node256 就是传统方式，chunk 直接作为 `children[]` 的下标。

### Size Class 解耦

PostgreSQL 实现的一个创新是将节点 kind 与 size class 解耦。同一个 kind 可以有不同容量。比如 Node16 有两个子类（`RT_FANOUT_16_LO` 和 `RT_FANOUT_16_HI`），用于适配 DSA 的固定大小分配块，减少内存碎片：

```c
#define RT_FANOUT_16_LO ((160 - offsetof(RT_NODE_16, children)) / sizeof(RT_PTR_ALLOC))
#define RT_FANOUT_16_HI Min(RT_FANOUT_16_MAX, (320 - offsetof(RT_NODE_16, children)) / sizeof(RT_PTR_ALLOC))
```

### 叶节点存储

如果值类型的大小不超过指针大小，值直接嵌入最后一层节点的子指针槽位中；否则单独分配内存，槽位存指针。走哪条路径在编译期就已经确定，运行时没有额外的判断开销。

## Tid Store 的设计

Tid Store（`tidstore.c`）是 ART 在 PostgreSQL 内核中的使用者。它用 Radix Tree 做两级索引：

- Key：`BlockNumber`（uint32，作为 uint64 使用）
- Value：`BlocktableEntry`，一个变长的 bitmapword 数组，每个 bit 代表该页面上对应 offset 是否为 dead tuple

```c
typedef struct BlocktableEntry
{
    uint16      nwords;
    bitmapword  words[FLEXIBLE_ARRAY_MEMBER];
} BlocktableEntry;
```

逻辑上看，整个结构是这样的：

```
radix tree (key = BlockNumber)
├── 42   → bitmap [offset 3, 7, 15]
├── 100  → bitmap [offset 1, 2]
└── 999  → bitmap [offset 5, 12, 200]
```

### 插入

`TidStoreSetBlockOffsets` 接收一个 `BlockNumber` 和一组 `OffsetNumber`，把 offset 编码成 bitmap 后写入 Radix Tree：

```c
void
TidStoreSetBlockOffsets(TidStore *ts, BlockNumber blkno,
                        OffsetNumber *offsets, int num_offsets)
{
    char        data[MaxBlocktableEntrySize];
    BlocktableEntry *page = (BlocktableEntry *) data;

    for (wordnum = 0; wordnum <= WORDNUM(offsets[num_offsets - 1]); wordnum++)
    {
        word = 0;
        while (idx < num_offsets)
        {
            OffsetNumber off = offsets[idx];
            if (off >= next_word_threshold)
                break;
            word |= ((bitmapword) 1 << BITNUM(off));
            idx++;
        }
        page->words[wordnum] = word;
    }

    page->nwords = wordnum;

    /* Insert into the radix tree */
    if (TidStoreIsShared(ts))
        shared_ts_set(ts->tree.shared, blkno, page);
    else
        local_ts_set(ts->tree.local, blkno, page);
}
```

### 查找

`TidStoreIsMember` 判断一个 TID 是否在集合中：先用 `BlockNumber` 在 Radix Tree 中定位叶节点（O(k)，k 为键的字节数），再在 bitmap 中 O(1) 检查 offset bit：

```c
bool
TidStoreIsMember(TidStore *ts, ItemPointer tid)
{
    BlocktableEntry *page;
    BlockNumber blk = ItemPointerGetBlockNumber(tid);
    OffsetNumber off = ItemPointerGetOffsetNumber(tid);

    if (TidStoreIsShared(ts))
        page = shared_ts_find(ts->tree.shared, blk);
    else
        page = local_ts_find(ts->tree.local, blk);

    if (page == NULL)
        return false;

    int wordnum = WORDNUM(off);
    int bitnum = BITNUM(off);

    if (wordnum >= page->nwords)
        return false;

    return (page->words[wordnum] & ((bitmapword) 1 << bitnum)) != 0;
}
```

相比旧方案的二分查找，这里不存在跨越大段内存的随机跳跃，对分支预测也更加友好。

### 共享内存支持

通过定义 `RT_SHMEM` 宏，Radix Tree 创建在 DSA（Dynamic Shared Memory Area）中，多个进程可以并发访问。这是支持并行 VACUUM 的关键：

```c
#define RT_PREFIX shared_ts
#define RT_SHMEM
#define RT_VALUE_TYPE BlocktableEntry
#define RT_VARLEN_VALUE_SIZE(page) \
    (offsetof(BlocktableEntry, words) + \
    sizeof(bitmapword) * (page)->nwords)
#include "lib/radixtree.h"
```

## VACUUM 中的变化

提交 `667e65aac3` 用 Tid Store 替换了 VACUUM 中的扁平数组。先看关键数据结构的变化：

```c
/* Before: */
typedef struct LVRelState {
    VacDeadItems *dead_items;       /* sorted array of dead TIDs */
    ...
} LVRelState;

/* After: */
typedef struct LVRelState {
    TidStore   *dead_items;         /* radix tree backed TID storage */
    VacDeadItemsInfo *dead_items_info;
    ...
} LVRelState;
```

分配方式的变化——不再一次性 `palloc` 一大块，而是按实际数据量渐进增长：

```c
/* Before: */
dead_items = (VacDeadItems *) palloc(vac_max_items_to_alloc_size(max_items));
dead_items->max_items = max_items;
dead_items->num_items = 0;

/* After: */
dead_items_info = (VacDeadItemsInfo *) palloc(sizeof(VacDeadItemsInfo));
dead_items_info->max_bytes = vac_work_mem * 1024L;
dead_items_info->num_items = 0;
vacrel->dead_items = TidStoreCreateLocal(dead_items_info->max_bytes);
```

收集 dead tuple 的方式也变了。以前是逐个构造 `ItemPointerData` 然后追加到数组里：

```c
/* Before: */
ItemPointerSetBlockNumber(&tmp, blkno);
for (int i = 0; i < lpdead_items; i++)
{
    ItemPointerSetOffsetNumber(&tmp, deadoffsets[i]);
    dead_items->items[dead_items->num_items++] = tmp;
}
```

现在是按页面批量写入，offset 用 bitmap 压缩：

```c
/* After: */
static void
dead_items_add(LVRelState *vacrel, BlockNumber blkno,
               OffsetNumber *offsets, int num_offsets)
{
    TidStoreSetBlockOffsets(vacrel->dead_items, blkno, offsets, num_offsets);
    vacrel->dead_items_info->num_items += num_offsets;
}
```

判断是否满的逻辑也从"条目数是否达到上限"变成了"内存使用是否超出阈值"：

```c
/* Before: */
if (dead_items->max_items - dead_items->num_items < MaxHeapTuplesPerPage)

/* After: */
if (TidStoreMemoryUsage(dead_items) > dead_items_info->max_bytes)
```

用 Tid Store 替换扁平数组后，前文提到的旧方案的几个问题都得到了解决：

- 渐进式内存增长：Radix Tree 按需做小粒度分配，不再受单次 `MaxAllocSize` 的 1GB 上限限制，也不需要预估表有多少 dead tuple。小表 VACUUM 不会浪费内存。
- 内存效率提升一到两个数量级：旧方案每个 TID 占 6 字节，新方案中同一个页面上的所有 dead offset 共享一个 bitmap。
- 大幅减少 I/O：大表 VACUUM 因 TID 存储满而中断扫描的场景大幅减少，因此避免了重复全量扫描索引。
- 查找速度大幅提升：索引清理阶段对每个 TID 做成员判断时，Radix Tree 的查找路径是固定的（取决于 `BlockNumber` 的字节数，不随集合大小增长），然后通过 bitmap 做一次 bit 测试。相比于数千万元素上的二分查找，CPU cache 的行为好得多。
- 共享内存友好：通过 DSA 后端，并行 VACUUM 的多个 worker 可以共享同一个 Tid Store，且不需要预先确定共享内存大小。

整体来看，Tid Store 把 dead tuple TID 的存储从 "排序数组 + 二分查找" 替换为 "ART + bitmap"。对日常运维来说最直观的体感是：VACUUM 占用更少的内存，中断清理索引的频率更低，索引清理阶段的 TID 查找更快。

## 参考

- Leis, V., Kemper, A., Neumann, T. (2013). "The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases". _ICDE 2013_.
- PostgreSQL 源码：`radixtree.h`、`tidstore.c`
- [PostgreSQL commit ee1b30f128](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commit;h=ee1b30f128d8f63a5184d2bcf1c48a3efc3fcbf9)
- [PostgreSQL commit 30e144287a](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commit;h=30e144287a72529c9cd9fd6b07fe96eb8a1e270e)
- [PostgreSQL commit 667e65aac3](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commit;h=667e65aac354975c6f8090c6146fceb8d7b762d6)
