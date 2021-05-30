# InnoDB - Critical Features

Created by : Mr Dk.

2020 / 10 / 10 14:17

Nanjing, Jiangsu, China

---

InnoDB 的关键特性包含：

* Insert Buffer
* 两次写 (Double Write)
* 自适应哈希索引 (Adaptive Hash Index)
* 异步 I/O (Async I/O)
* 刷新邻接页 (Flush Neighbor Page)

## Double Write

Insert Buffer 为 InnoDB 带来性能上的提升，而 Double Write 则保证了数据页的 **可靠性**。

如果数据库在对一个页进行写入时，数据库突然 crash，那么会出现 *部分写失效*。虽然可以用 redo log 对页进行恢复，但是页本身已经发生损坏，redo 没有意义 - redo 总该基于一个原本完整的页进行。因此，在应用 redo log 前，用户需要页原有状态的副本，基于这个副本来应用 redo log。

InnoDB 中的 Double Write 包含两个部分：

* 内存中的 Double Write Buffer (2MB)
* 磁盘上共享表空间中的连续 128 个页 (2MB)

数据库在对脏页进行写回操作时，首先通过 `memcpy()` 将脏页复制到内存中的 Double Write Buffer 中。由 Double Write Buffer 分两次 **顺序地** 写入磁盘共享表空间中，然后立刻调用 `fsync()` 落盘 (保证脏页全部落到磁盘上)。这一步由于内存和磁盘中空间的连续性，开销不是很大。之后再将 Double Write Buffer 中的页离散地写入各个独立表空间中。

如果在将页写入磁盘的过程中发生了崩溃，在恢复过程中，InnoDB 存储索引可以从共享表空间中找到该页的一个副本，然后再应用 redo log 进行恢复。

## Adaptive Hash Index

Hash 查找速度的理论复杂度只有 `O(1)`，而 B+ 树的查找复杂度则取决于 B+ 树的高度，一般来说需要三到四次的查询。InnoDB 存储索引会监控对表上各索引页的查询，自动根据访问的频率和模式为某些热点页建立 hash 索引。AHI 的要求以相同的模式访问数据时才会被触发。

Hash 索引只能用来搜索等值查询。

## Asynchronous I/O

与 AIO 对应的是同步 I/O，也就是进行 I/O 操作时，等待此次操作结束之后才能继续接下来的操作。如果一条 SQL 查询语句需要扫描多个索引页，依次等待多个 I/O 操作是没有必要的，完全可以一次性发出所有的 I/O 请求，然后等待所有 I/O 操作的完成。AIO 的另一个优势是可以进行 I/O Merge 操作，将多次 I/O 合并为一次。

InnoDB 1.1.x 之前的 AIO 都是 InnoDB 存储引擎的代码 **模拟** 实现的，而之后的版本提供了 **内核级别** 的 AIO 支持。而内核级别的 AIO 需要 OS 的支持 - Windows 和 Linux 都提供了相应的支持，OSX 则需要继续模拟。

## Flush Neighbor Page

将一个脏页写回磁盘时，InnoDB 存储引擎会检测该页所在区的所有页，如果是脏页，那么一起刷新。通过 AIO 可以将多个 I/O 操作合并为一个 I/O 操作，在传统 **机械硬盘** 下有着显著优势。可以通过参数 `innodb_flush_neighbors` 来控制是否启动这一特性。

## InnoDB 的启动、关闭和恢复

在 InnoDB 关闭时，参数 `innodb_fast_shutdown` 影响了以 InnoDB 为存储引擎的表的行为。取值范围为 0、1、2，默认为 1：

* `0` 表示 MySQL 关闭时，InnoDB 需要完成所有的 full purge 和 merge insert buffer，并将所有脏页写回磁盘 (耗时)
* `1` 表示不需要完成 full purge 和 merge insert buffer，但一些脏页还是会写回磁盘
* `2` 表示不完成 full purge 和 merge insert buffer，也不将脏页写回磁盘，只将日志都写入日志文件 (下次启动时需要恢复)

当使用 `kill` 命令关闭数据库，或上述选项为 `2` 时，下次启动 MySQL 时都会对 InnoDB 存储引擎管理的表进行恢复操作。

---

