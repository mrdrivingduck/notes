# DuckDB - duckdb-paimon

Created by: Mr Dk.

Co-authored by: Claude Sonnet 4.6

2026 / 03 / 21 22:10

Hangzhou, Zhejiang, China

---

## 背景

如果你正在用 Flink 做实时数仓，大概率遇到过这样的场景：一条 Flink CDC 链路把业务数据库的订单表实时同步到了 Paimon 数据湖里，运营同事过来问你「昨天华东区的退单率是不是异常了？帮忙跑个数看看」。这本来是一个很简单的聚合查询，但你要先启动 Flink SQL Client 或者 Spark Shell——等三十秒，JVM 慢悠悠地起来，吃掉两个 G 的内存，然后你才能敲下那条 SQL。

就为了跑一条临时 SQL，这也太重了。

这篇文章将介绍我们最近新开源的项目 [duckdb-paimon](https://github.com/polardb/duckdb-paimon)。它是 DuckDB 的一个扩展插件，让你可以用一个几 MB 大小的嵌入式数据库，直接读取本地或对象存储上的 Paimon 表，不需要 Flink，不需要 Spark，不需要任何 JVM。目前这个插件已经被 DuckDB 官方收录到 [Community Extensions](https://duckdb.org/community_extensions/list_of_extensions) 列表中。

## Paimon：实时湖仓的新选择

先简单聊聊 [Apache Paimon](https://paimon.apache.org/)。

传统的数据湖格式，不管是 Hudi、Iceberg 还是 Delta Lake，本质上都是在解决「如何在对象存储上高效管理表数据」这个问题。Paimon 的独特之处在于把 LSM-Tree 的思想引入了湖仓格式。这意味着它天然支持高频的实时写入——你可以用 Flink CDC 把上游数据库的变更流式地写入 Paimon，数据分钟级可见，而且主键表原生支持 Upsert 语义，不需要额外的合并逻辑。

在国内的实时数仓场景中，Paimon 正在被越来越多的团队采用。典型的架构是：MySQL 的 binlog 通过 Flink CDC 实时写入 Paimon，下游通过 Flink SQL 或 Spark 做批流一体的查询。这套架构解决了实时性的问题，但也带来了一个日常痛点：想对 Paimon 里的数据做个即席分析，动静太大了。不管是 Flink SQL Client 还是 Spark Shell，都需要启动 JVM、占用集群资源，而且它们的 SQL 能力往往受限——比如 Flink SQL 对窗口函数、复杂子查询的支持就不如传统 OLAP 引擎完善。更尴尬的是，如果你想把 Paimon 表和一份本地的 CSV 维表或者另一个 Parquet 文件 JOIN 起来做交叉分析，在 Flink/Spark 体系里这几乎意味着要先把数据搬到同一个系统中。

## DuckDB：嵌入式的分析利器

DuckDB 这两年在数据分析社区的热度很高，核心原因在于它把嵌入式数据库的轻量和分析引擎的高性能结合到了一起。

跟 SQLite 一样，DuckDB 是嵌入式的，整个数据库就是一个进程，没有服务端、没有集群、没有任何外部依赖。但它的内核是专门为分析型查询（OLAP）设计的——列式存储、向量化执行、自动并行，在单机上跑分析查询的性能非常强悍。

更重要的是 DuckDB 的生态。它原生支持读取 Parquet、CSV、JSON，还有官方的 Iceberg 插件。这意味着你可以在一个轻量级的本地环境里，用标准 SQL 查询各种格式的数据，甚至可以把不同格式的数据 JOIN 在一起，完全不需要搬运数据。

那么问题来了：DuckDB 能不能直接读 Paimon？

## duckdb-paimon：桥接两个世界

这就是 duckdb-paimon 要做的事情。

从架构上看，这个插件的设计很直接，分为三层：

```
┌──────────────────────────────────┐
│        DuckDB SQL Engine         │  ← SQL query
├──────────────────────────────────┤
│     duckdb-paimon extension      │  ← Bridge layer
│     (Catalog + TableFunction)    │
├──────────────────────────────────┤
│          paimon-cpp              │  ← C++ Paimon reader
│      (Pure C++, No JVM)          │
└──────────────────────────────────┘
              ↓ Read
    Paimon Table Files (Local / OSS)
```

最上面一层是 DuckDB 自身的 SQL 引擎，用户写的 SQL 在这里被解析和执行。最下面一层是 [paimon-cpp](https://github.com/alibaba/paimon-cpp)，这是阿里巴巴近期开源的一个 C++ 库，它用纯 C++ 实现了 Paimon 表的读写能力，包括解析 Snapshot、Manifest、以及读取 Parquet/ORC 数据文件。这个库的意义在于，它第一次把 Paimon 的读写能力从 JVM 生态中解放出来了。

而 duckdb-paimon 插件本身是中间的桥接层。它做的事情不复杂：在 DuckDB 这边注册一个 `paimon_scan` 表函数和一个 Paimon Catalog，把 DuckDB 的查询请求翻译成 paimon-cpp 能理解的调用，再把 paimon-cpp 返回的数据喂回给 DuckDB。

听起来简单，但要做到高效，中间有不少值得聊的工程细节。

## 查询是怎么跑起来的

我们以一条具体的查询为例来看看整个执行过程：

```sql
SELECT f0, f1 FROM paimon_scan('oss://bucket/warehouse/mydb.db/orders') WHERE f1 = 42;
```

Paimon 表的数据是 [分层组织](https://paimon.apache.org/docs/master/concepts/basic-concepts/) 的。最顶层是 Snapshot，每次提交生成一个新的 Snapshot 文件，代表表在该时刻的一致性视图。每个 Snapshot 引用若干 ManifestList 文件（分别对应全量变更、本次增量变更和 changelog），ManifestList 记录了各个 Manifest 文件的元信息及分区级别的统计数据，可用于在查询时跳过无关的 Manifest 文件。Manifest 文件则记录了具体的数据文件列表，以及每个数据文件中各列的最小值、最大值等统计信息，供查询时进一步跳过不相关的数据文件。数据文件本身通常是 Parquet 或 ORC 格式。

当这条查询到达插件时，首先要做的是加载表的 Schema。paimon-cpp 返回的 Schema 是 [Apache Arrow](https://arrow.apache.org/) 格式的，插件通过 DuckDB 内置的 Arrow 转换机制直接映射成 DuckDB 的类型系统，Arrow 在这里充当了类型桥梁。

Schema 确定之后，插件通过 paimon-cpp 读取元数据，规划出一组 Split——每个 Split 代表一个可以独立读取的数据单元，通常对应一个 bucket 下的一组数据文件。然后 DuckDB 启动多个扫描线程，每个线程无锁地认领 Split，创建独立的读取器，循环读取 Arrow 格式的数据批次并转换为 DuckDB 的内部向量格式。一个 Split 读完后，线程自动去认领下一个，直到所有数据读取完毕。

整个流程下来，查询的并行度等于 Split 的数量，充分利用多核 CPU。

## 几个关键优化

光是能跑起来还不够，要想让查询体验真正做到"即开即用"，还需要在数据读取的路径上减少无用功。duckdb-paimon 目前做了几个方向的优化。

### 零 JVM，启动即查

这是最直观的一个优势。传统方式下，不管你用 Flink、Spark 还是 Hive，读 Paimon 表都绕不开 JVM。JVM 的启动本身就需要数秒甚至数十秒，还要加载一堆类、初始化各种框架组件，实际开始执行查询之前已经过去了很长时间。

duckdb-paimon 通过 paimon-cpp 完全绕过了 JVM。整个链路从 DuckDB 进程启动到拿到查询结果，通常在一秒以内。内存占用也从 JVM 动辄 GB 级别降到了百 MB 级别。对于需要在实时湖仓上做轻量分析的场景，这个差距是质变级的。

### Arrow 零拷贝：数据不搬家

paimon-cpp 输出的数据格式是 Apache Arrow，DuckDB 内部的执行引擎也是列式的。这意味着数据从 paimon-cpp 传递到 DuckDB 时，不需要经过序列化和反序列化的过程——通过 Arrow C Data Interface，两边共享同一块内存，只是传递了一个指针。

我们还做了一个对齐优化：paimon-cpp 每次输出的 Arrow 批次大小被设置为与 DuckDB 内部的向量大小一致（默认 2048 行）。这样每个 Arrow 批次恰好填满一个 DuckDB 向量，避免了批次拆分或合并带来的额外拷贝。

### 投影下推：只读你要的列

当你写 `SELECT f0, f1 FROM ...` 的时候，表里可能有几十个列，但你只需要两个。如果把所有列的数据都从数据湖查回，在 DuckDB 中做投影后再丢弃不需要的列，那就浪费了大量的 I/O 和内存带宽。

duckdb-paimon 启用了 DuckDB 的投影下推机制。DuckDB 在查询规划阶段会分析 SELECT 子句，确定实际需要读取的列集合，以列索引列表的形式传递给插件。插件再将这组列索引传递给 paimon-cpp，使其在解码数据文件时只读取对应的列，跳过其余列的 I/O。对于动辄几十列的宽表，只查其中两三列时，I/O 量和内存消耗都能大幅降低。

### 谓词下推：跳过不相关的文件

```sql
WHERE f1 = 42
```

这个 WHERE 条件不仅仅在 DuckDB 引擎层面做行级过滤，还会被下推到 paimon-cpp。具体来说，插件会遍历 DuckDB 的谓词表达式树，对每个比较节点做结构映射和数据类型转换——将 DuckDB 的列引用映射到 Paimon 的字段索引，将 DuckDB 的常量值转换为 Paimon 的字面量类型——从而构造出一棵等价的 paimon-cpp 谓词树。如果 WHERE 中有多个条件，它们会被组合成一棵 AND 谓词树，整体传递给 paimon-cpp。paimon-cpp 拿到这棵谓词树后，在读取 Manifest 文件时，会利用其中记录的列统计信息（min/max），跳过那些肯定不包含匹配数据的整个数据文件。

这里有一个值得展开讲的设计决策：**下推但不信任**。

虽然谓词被下推了，但插件并不会把对应的 filter 从 DuckDB 的执行计划中移除。原因是 paimon-cpp 的谓词下推是 best-effort 的——它只在文件级别做过滤（根据统计信息跳过整个文件），并不保证返回的每一行都满足条件。所以 DuckDB 侧必须保留 filter，对 paimon-cpp 返回的数据做二次精确过滤，确保结果的正确性。

这是一种在性能和正确性之间很常见的权衡模式：底层尽力减少数据量，上层兜底保证语义正确。

目前谓词下推支持的是等值比较（`=`），后续会逐步扩展到大于、小于、IN 等更多比较类型。

值得一提的是，投影下推和谓词下推同时存在时会有一个微妙的问题：谓词树是基于全表 Schema 构建的，但投影后实际读取的列集合变窄了，列的索引也随之改变。插件在查询执行的初始化阶段会对谓词树中的列索引做一次重映射，从全表索引转换为投影后的索引，确保 paimon-cpp 能正确地将谓词应用到对应的列上。

### 多线程并行：无锁分发 Split

前面提到，Paimon 表的数据天然按 Split 划分。duckdb-paimon 利用这个特性实现了多线程并行扫描。

并行的核心机制很简单：全局状态持有所有 Split，配合一个原子计数器。每个工作线程通过原子操作无锁地获取下一个 Split 的索引，然后基于这个 Split 创建自己独立的 Reader。整个过程没有互斥锁，没有条件变量，线程之间完全独立。

当一个线程读完了自己认领的 Split，它不会闲着——它会继续通过原子操作去认领下一个还没被处理的 Split。这实际上是一种简化版的工作窃取（work stealing）机制，确保在 Split 大小不均匀的情况下，快的线程能主动分担更多工作，避免尾部延迟。

## 后续规划

duckdb-paimon 目前还处于早期阶段，有不少能力暂未实现：

- **更全面的谓词下推**：目前只支持等值比较，范围比较（`>`, `<`, `>=`, `<=`）和 IN 列表还没有实现。
- **分区裁剪**：还没有做，对于分区表目前还是会扫描所有分区的数据。
- **时间旅行**：暂时缺席，目前只能查询最新的 Snapshot——不过 paimon-cpp 本身已经具备了读取历史 Snapshot 的能力，插件层面实现起来应该并不困难。
- **写入支持**：暂不支持，目前是一个纯只读的插件。

但核心的读取链路已经打通，几个关键的性能优化也都已经落地。如果你也在用 Paimon 做实时湖仓，欢迎试用；如果你对上面这些 TO DO 项感兴趣，也欢迎贡献 [duckdb-paimon](https://github.com/polardb/duckdb-paimon)。
