# Tantivy - Architecture

Created by: Mr Dk.

2026 / 05 / 25 16:00

Hangzhou, Zhejiang, China

---

## 背景

Tantivy 是一个用 Rust 实现的全文搜索引擎库。它的架构深受 Apache Lucene 影响——如果你熟悉 Lucene 的概念体系，会发现两者在术语和设计模式上有大量重叠。

全文搜索要解决的核心问题是：给定一组文本文档和一个查询，快速返回最相关的 K 篇文档。为了高效地执行这个检索，需要预先构建索引。Tantivy 默认使用 BM25 作为相关性评分算法，这和 Lucene / Elasticsearch 的默认行为一致。

Tantivy 的设计遵循几个原则：

- 搜索应当是 O(1) 内存的——不管索引多大，搜索时的内存占用恒定
- 索引应当是亚线性内存的——通过定期 flush 控制内存上界
- 搜索应当尽可能快
- 索引更新以批量方式进行，不支持单文档实时更新

这些取舍使得 Tantivy 非常适合构建离线索引、批量写入的搜索场景。本文围绕 segment 这一核心抽象，介绍 Tantivy 的整体架构，以及索引和搜索两条主线的数据流。

## Segment：核心抽象

和 Lucene 一样，Tantivy 的 Index 并不是一个单一的整体数据结构，而是由若干个 **segment** 组成的集合。每个 segment 是一个独立、不可变的数据单元，包含一批文档的完整索引信息。这种设计使得新文档的写入只需要追加新的 segment 而无需修改已有数据，天然支持并发读写。

一个 segment 由 UUID 标识。在磁盘上，每个 segment 由 7 个文件组成，分别承载不同的数据结构。索引目录中还有一个 `meta.json` 文件记录当前有哪些 segment、每个 segment 包含多少文档，以及索引的 schema 定义。每次 commit 时 `meta.json` 被原子更新，这是索引一致性的保障。

```
index_directory/
├── meta.json                         # segment 列表 + schema 定义
│
├── <uuid>.term                       # Term Dictionary (词典)
├── <uuid>.idx                        # Postings (倒排列表)
├── <uuid>.pos                        # Positions (词项位置)
├── <uuid>.fast                       # Fast Fields (列式存储)
├── <uuid>.fieldnorm                  # Field Norms (字段长度)
├── <uuid>.store                      # Store (文档原文)
└── <uuid>.<opstamp>.del              # Alive Bitset (存活位图)
```

在每个 segment 内部，文档由一个从 0 开始的紧凑整数 `DocId`（`u32`）标识。这个紧凑 ID 空间是后续所有数据结构能够高效压缩的关键前提——posting list 的 delta 编码、fast field 的定长数组访问，都依赖于 DocId 从 0 到 N-1 连续分布这一事实。

删除操作不修改 segment 文件（segment 是不可变的），而是在 alive bitset 中将对应 DocId 标记为"已死亡"。被删除的文档在搜索时会被过滤掉，直到后续的 merge 操作将其物理清除。

## 从一篇文档看索引存储

### 评分模型：TF / IDF / BM25

在深入各个文件之前先简单介绍一下评分模型——后面看到的几个数据结构都是为这个评分函数服务的。常用的评分模型有三个核心概念：

- **TF（Term Frequency，词频）**：某个 term 在一篇文档中出现的次数。
- **IDF（Inverse Document Frequency，逆文档频率）**：衡量一个 term 的"信息量"——常见词信息量低，罕见词信息量高。
- **BM25**：在 TF 和 IDF 之上加入文档长度归一化得到最终评分，是 Tantivy 默认采用的算法。

下面依次给出每个模型的公式。

**TF** 直接采用词频计数，直觉是出现次数越多越相关，但这种相关性不是线性的——出现 100 次未必比出现 10 次更相关，因此 BM25 会再对其做一层饱和归一化（详见下文）。

**IDF** 的公式如下：

```
IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5) + 1)
```

其中 `N` 是文档总数，`df(t)` 是包含 term `t` 的文档数。"the" 这种几乎在所有文档里都出现的词 IDF 接近 0，而 "tantivy" 这种只在少数文档里出现的词 IDF 很高。

**BM25** 对于查询 `Q` 和文档 `D`，分数为各 term 贡献之和：

```
                              TF(t,D) * (k1 + 1)
BM25(Q,D) = Σ IDF(t) * ──────────────────────────────────
              t∈Q       TF(t,D) + k1 * (1 - b + b * |D|/avgdl)
```

`k1`（默认 1.2）控制 TF 的饱和速度，`b`（默认 0.75）控制长度归一化的强度；`|D|` 是当前文档长度，`avgdl` 是平均文档长度。直觉上 BM25 在说两件事：

1. 相同 TF 下短文档比长文档更相关。
2. TF 的边际收益随次数递减。

从公式可以反推索引必须存什么：

- `TF(t,D)` → 每个 `(term, doc)` 对的词频 → 存在 postings 里
- `df(t)` → 每个 term 出现在多少篇文档中 → 存在 term dictionary 的 `TermInfo` 里
- `|D|` → 每篇文档每个字段的长度 → 存在 field norms 里
- `avgdl` → 全局统计，从所有 field norms 累加得到

这正是 `.idx`、`.term`、`.fieldnorm` 三个文件各自承载的核心数据。

### 字段选项

Tantivy 在定义 schema 时，可以为每个字段打上若干选项标志，告诉索引该字段需要哪些用途。常用的标志有：

- `TEXT`：建倒排索引，字段值经过分词器拆分为 tokens 并记录位置信息，支持全文检索（包括短语查询）
- `STRING`：建倒排索引，但整个字段值作为单个 token 不分词，适用于 ID、状态等需要精确匹配的关键字字段
- `STORED`：在 `.store` 文件中逐字保留字段的原始值，搜索完成后可取回展示
- `FAST`：在 `.fast` 文件中建列式存储，支持按 `DocId` 随机访问，用于排序、聚合、过滤

这些标志互相独立，可以用 `|` 组合。例如 `TEXT | STORED` 既能搜索又能取回原文；只标 `FAST` 而不标 `STORED` 则不在 `.store` 里保留原值，但仍可从列存里读出。

把"索引"和"保存原文"拆成两件事是有意为之：倒排索引只保留分词后的 token，且经过小写化等处理。例如 "The Old Man and the Sea" 进倒排索引后变成 `[the, old, man, and, the, sea]`，大小写、空格、顺序全部丢失——这些信息够用来检索，但不够展示给用户；`STORED` 字段则把原文逐字保留下来。

### 各文件承载的数据

假设我们的 schema 定义了两个字段：`title`（`TEXT | STORED`）和 `price`（`FAST`）。现在索引一篇文档：

```json
{ "title": "The Old Man and the Sea", "price": 42 }
```

这篇文档被分配了 `DocId = 3`（假设 segment 中已有 3 篇文档）。分词器将 title 拆分为 tokens：`[the, old, man, and, the, sea]`，位置分别为 `[0, 1, 2, 3, 4, 5]`。接下来各数据结构分别存储以下内容：

**Term Dictionary（`.term`）**：存储 term 到元数据的映射。`TermInfo` 中记录了三项信息：

- `doc_freq`：包含该 term 的文档数，用于计算 IDF。将其直接存在这里，可以在计算 IDF 时无需加载整个 posting list
- `postings_range`：posting list 在 `.idx` 文件中的字节范围
- `positions_range`：位置信息在 `.pos` 文件中的字节范围

对于这篇文档涉及的 term：

```
"and" ──▶ TermInfo { doc_freq, postings_range, positions_range }
"man" ──▶ TermInfo { doc_freq, postings_range, positions_range }
"old" ──▶ TermInfo { doc_freq, postings_range, positions_range }
"sea" ──▶ TermInfo { doc_freq, postings_range, positions_range }
"the" ──▶ TermInfo { doc_freq, postings_range, positions_range }
```

**Postings（`.idx`）**：对于每个 term，存储包含该 term 的文档 ID 列表及词频。`DocId` 列表按升序排列，每 128 个为一个 block，block 内使用 delta 编码 + bitpacking 压缩（所有值用相同位宽）；不足 128 个的尾部用 VInt 编码。词频与 `DocId` 分开编码，同样以 128 为一个 block 进行 bitpacking。

```
"the" ──▶ [(DocId=0, tf=1), (DocId=1, tf=3), (DocId=3, tf=2)]
"sea" ──▶ [(DocId=3, tf=1)]
"old" ──▶ [(DocId=2, tf=1), (DocId=3, tf=1)]
...
```

**Positions（`.pos`）**：记录 term 在每篇文档中出现的具体位置，使用与 postings 相同的 delta 编码 + bitpacking 方案（128 个位置为一个 block）。位置信息使短语查询成为可能——搜索 "old man" 时，不仅要求两个 term 都出现在同一篇文档中，还要求 "old" 的位置恰好在 "man" 之前一位。

```
"the" in DocId=3 ──▶ positions: [0, 4]
"sea" in DocId=3 ──▶ positions: [5]
"old" in DocId=3 ──▶ positions: [1]
...
```

**Fast Fields（`.fast`）**：列式存储，按 `DocId` 随机访问。Tantivy 会根据数据特征自动选择最优编码（bitpacked、linear、blockwise-linear 等）；由于 `DocId` 空间连续，访问任意一个值都是 O(1) 的。下面是 `price` 字段的存储，`price[3] = 42` 对应我们刚索引的这篇文档：

```
price[0] = 35
price[1] = 28
price[2] = 99
price[3] = 42
```

**Field Norms（`.fieldnorm`）**：每篇文档的每个 `TEXT` 字段存储一个 token 计数（用于 BM25 评分），每个值通过对数查找表编码为 1 字节（小值无损，大值有精度损失，与 Lucene 方案相同）。BM25 用它来惩罚过长的文档——同样命中了搜索词，短文档的相关性通常高于长文档。下面 `title_norm[3] = 6` 对应 `TEXT` 字段 `title` 中 "The Old Man and the Sea" 的 6 个 token：

```
title_norm[0] = 5
title_norm[1] = 12
title_norm[2] = 3
title_norm[3] = 6
```

**Store（`.store`）**：行式压缩存储，保存标记为 `STORED` 的字段原始值。多篇文档打包为一个 block（默认 16KB），整块使用 LZ4 或 Zstd 压缩；读取单篇文档需要先定位 block，再整块解压。因此 store 只用于搜索完成后取回 top-K 结果的展示，不参与评分过程。

```
DocId=3 ──▶ { "title": "The Old Man and the Sea" }
```

可以看到，同一篇文档的数据被"打散"存储到了不同的文件中。这不是冗余，而是各数据结构各司其职：term dictionary 和 postings 服务于"根据关键词找文档"的检索需求；fast field 服务于"根据文档取数值"的聚合/排序需求；store 服务于"根据文档取原文"的展示需求。搜索引擎的性能正是来源于这种按访问模式拆分存储的设计。

## 索引流程

`IndexWriter` 是用户向索引添加文档的入口。它的内部架构是一个多生产者-多消费者模型：用户线程通过一个有界 channel（容量 10,000 篇文档）将文档分发给若干工作线程（根据 CPU 核心数和内存预算自动决定，最多 8 个）。每个工作线程独立持有一个 `SegmentWriter`，在各自的内存空间中构建 segment 的中间表示。

```
    add_document()
         │
         ▼
    IndexWriter ─── channel ──┬── Thread 1: SegmentWriter ──┐
         │                    ├── Thread 2: SegmentWriter ──┤── flush ──▶ Segment 文件
         │                    └── Thread N: SegmentWriter ──┘
         │
         ▼ commit()
    meta.json (原子更新)
         │
         ▼ background
    SegmentUpdater ──▶ MergePolicy ──▶ Merger
```

对于收到的每篇文档，`SegmentWriter` 做三件事：

1. 构建倒排索引：对文本字段运行分词器，将每个 token 及其位置信息写入内存中的 posting 结构（基于 `tantivy-stacker` 的 arena hashmap）
2. 写入列式存储：将数值型 fast field 的值追加到列式 writer（基于 `tantivy-columnar`）
3. 写入文档存储：将标记为 `STORED` 的字段序列化到 store writer 的压缩块中

每个工作线程有一个内存上限（最少 15MB）。当内存使用接近上限时，线程将当前 segment flush 到磁盘，然后开始构建下一个新的 segment。注意 flush 不等于 commit——flush 产生的文件还不可被搜索到。

只有当用户显式调用 `commit()` 时，所有工作线程才会停止接收新文档、flush 各自正在构建的 segment，最后原子地更新 `meta.json` 将这些新 segment 注册为索引的一部分。此后新获取的 `Searcher` 就能看到这批新文档了。

随着 commit 次数增加，segment 数量会不断增长。过多的 segment 会拖慢搜索性能（每次搜索都需要遍历所有 segment），因此需要后台合并。`LogMergePolicy` 是默认的合并策略——它按文档数量的对数将 segment 分层，当同一层积累了 8 个及以上 segment 时触发合并。合并操作将多个小 segment 读取并合为一个大 segment，同时物理清除已标记删除的文档。合并在独立的线程池中执行，不阻塞索引和搜索。

## 搜索流程

搜索通过 `Searcher` 对象进行。`Searcher` 持有索引某一时刻的快照——一组 `SegmentReader` 的集合。无论后续发生了 commit、merge 还是文件回收，只要持有同一个 `Searcher`，搜索就始终在同一个不可变快照上进行。这是一种 MVCC（多版本并发控制）式的设计，读写之间完全无锁。

`SegmentReader` 是对一个 segment 所有数据结构的只读访问入口，提供对所有存储结构的统一只读访问。由于底层数据几乎全部通过 mmap 映射，`SegmentReader` 的匿名内存占用极低——加载一个索引的速度本质上就是 mmap 这些文件的速度。

### 查询系统抽象

Tantivy 的查询系统分为三层抽象，每一层都有明确的职责：

```
    QueryParser::parse_query("old sea")
         │
         ▼
    Query                           定义匹配逻辑
         │  .weight(searcher)
         ▼
    Weight                          绑定了全局统计信息的查询
         │  .scorer(segment_reader) ← 对每个 segment 分别调用
         ▼
    Scorer                          在具体 segment 上遍历匹配文档
         │
         ▼
    Collector                       收集/聚合结果
```

为什么不从 Query 直接产生结果，而要经过这三层？

- **Query**：纯粹的逻辑描述——"我要找包含 old 或 sea 的文档"。它不关心索引有多少 segment，也不知道 old 这个词在整个索引中出现了多少次。
- **Weight**：在 Query 的基础上绑定了全局统计信息。BM25 评分需要每个 term 的逆文档频率（IDF），而 IDF 的计算需要汇总所有 segment 中该 term 的文档频率。Weight 正是承载这些全局统计的中间层——它被创建一次，随后可以为每个 segment 生成 Scorer。
- **Scorer**：绑定到具体 segment 的迭代器。持有该 segment 中对应 term 的 posting list，能够高效地遍历匹配的 DocId 并计算每篇文档的 BM25 分数。

这个三层结构对应着三个粒度：整个查询级别、整个索引级别、单个 segment 级别。如果要实现一种新的 Query 类型，就需要对应地实现这三个 trait。

### Collector 模式

搜索的最后一环是 Collector，它负责决定如何处理 Scorer 产生的 (DocId, Score) 对。Tantivy 为每个 segment 创建一个 `SegmentCollector`，各自独立收集结果，最后通过 `merge_fruits()` 将各 segment 的局部结果汇总为最终输出。

```
    Segment 0 ──▶ SegmentCollector 0 ──▶ top 10 of segment 0 ─┐
    Segment 1 ──▶ SegmentCollector 1 ──▶ top 10 of segment 1 ─┤── merge ──▶ 全局 top 10
    Segment 2 ──▶ SegmentCollector 2 ──▶ top 10 of segment 2 ─┘
```

内置的 Collector 包括：`TopDocs`（取评分最高的 K 篇文档）、`Count`（统计匹配文档总数）、`FacetCollector`（分面统计）等。因为 Collector 是一个 trait，用户也可以实现自定义的聚合逻辑。

### 一次搜索的完整路径

将上述概念串起来，当用户搜索 "old sea" 时，实际发生的事情是：

1. `QueryParser` 将字符串解析为一个 `BooleanQuery`（`TermQuery("old") OR TermQuery("sea")`）
2. `BooleanQuery` 创建 `BooleanWeight`，过程中从所有 segment 汇总 "old" 和 "sea" 的文档频率以计算 IDF
3. 对于每个 segment，`BooleanWeight` 创建 Scorer：
   - 在 term dictionary 中查找 "old" 和 "sea" → 得到各自的 `TermInfo`（posting list 的偏移范围）
   - 根据 `TermInfo` 定位到 `.idx` 文件中对应的 posting list
   - 两个 posting list 取并集，对每篇匹配文档计算 BM25 分数
4. `TopDocs` collector 在每个 segment 中只保留分数最高的 K 篇文档（内部通过带阈值的缓冲区实现剪枝）
5. 各 segment 的 top-K 结果合并为全局 top-K
6. 用户拿到 `DocAddress`（segment 序号 + DocId）后，可从 store 中取回文档原文用于展示

## 参考资料

- [Tantivy GitHub Repository](https://github.com/quickwit-oss/tantivy)
- [Tantivy ARCHITECTURE.md](https://github.com/quickwit-oss/tantivy/blob/main/ARCHITECTURE.md)
- [Behold, Tantivy (Part 2) - Paul Masurel](https://fulmicoton.com/posts/behold-tantivy-part2/)
- [Quickwit Documentation](https://quickwit.io/docs)
