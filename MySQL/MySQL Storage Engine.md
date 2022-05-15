# MySQL - Storage Engine

Created by : Mr Dk.

2020 / 10 / 20 15:33

Nanjing, Jiangsu, China

---

## MyISAM

在 MySQL 5.5.8 之前是 MySQL 的默认存储引擎，主要面向一些 OLAP 应用。

- 不支持事务
- 支持表级锁
- 支持全文索引
- 缓冲池只缓存索引，数据的缓存由 OS 本身完成 (不使用 LRU)

## InnoDB

MySQL 5.5.8 之后成为默认的存储引擎，主要面向 OLTP 应用。

- 支持行锁
- 支持外键
- 通过 MVCC 获得高并发性
- 支持事务，实现了 SQL 标准的四种事务隔离级别
- 按主键顺序存放，主键是聚簇索引

新特性：

- 插入缓冲 (Insert Buffer)
- 二次写 (Double Write)
- 自适应哈希索引 (Adaptive Hash Index)
- 预读 (Read Ahead)

## NDB

是一个高可用、高性能的集群存储引擎，数据全部存放在内存中。因此主键查找的速度极快。NDB 的 JOIN 操作是在 MySQL 数据库层面完成的，而不是在存储引擎层面完成，因此连接操作需要大量网络开销，速度较慢。

## Memory

将表中的数据存储在内存中，如果数据库重启或发生崩溃，表中的数据都将丢失。比较适合用于存储临时数据。

如果中间结果集合大于 Memory 存储引擎的容量限制，那么 MySQL 会将其转换为 MyISAM 存储引擎的表并落盘，而 MyISAM 不缓存数据文件，从而引发性能下降。

## Archive

只支持 INSERT 和 SELECT 操作，使用 zlib 算法对数据行进行压缩后再存储。比较适合存放归档数据。使用行锁来实现高并发的插入操作。

## Federated

本身不存放数据，指向一台远程 MySQL 数据库服务器上的表。

## Maria

目标是取代原有的 MyISAM 存储引擎。

---
