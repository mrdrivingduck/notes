# InnoDB - Backup

Created by : Mr Dk.

2020 / 10 / 18 23:52

Nanjing, Jiangsu, China

---

## Classification

按照备份的方法，可以分为：

* Hot Backup - 在数据库运行中直接备份，对正在运行的数据操作没有任何影响
* Cold Backup - 在数据库停止的情况下备份
* Warm Backup - 在数据库运行中备份，但对当前数据库操作有影响

按照备份后文件的内容，可分为：

* 逻辑备份 - 备份出的文件内容是可读的，但需要恢复的时间较长
* 裸文件备份 - 直接复制数据库的物理文件，恢复时间短

按照备份数据库的内容来分：

* 完全备份 - 对整个数据库进行完整备份
* 增量备份 - 在上次完整备份的基础上对更改的数据进行备份
* 日志备份 - 对 MySQL 的二进制日志备份并 redo

## Cold Backup

冷备份只需要备份 MySQL 的 frm 文件、共享表空间文件、独立表空间文件、redo log 文件。

* 备份简单，只需要复制文件
* 备份文件可跨平台
* 恢复简单且速度快
* 冷备文件比逻辑文件大很多

## Logical Backup

### mysqldump

备份出的文件内容是表结构和数据，由 SQL 语句表示。

* `--single-transaction` 参数用于备份 InnoDB 存储引擎 - 在备份开始前，执行一次 `START TRANSACTION`，但需要确保没有其它 DDL 语句执行
* `--lock-tables` - 依次锁住每个架构 (存储引擎) 下的所有表，只能保证部分表的一致性
* `--lock-all-tables` - 对所有架构中的所有表上锁，保证所有表的一致性

在恢复时，只需要执行导出的 SQL 语句即可。

> 通过 mysqldump 备份数据库时，并不能导出视图 - 需要手动完成。

### SELECT...INTO OUTFILE

使用 `LOAD DATA INFILE` 导入备份数据。其命令行接口为 mysqlimport 工具。

## Binary Log Backup

MySQL 默认不启用二进制日志，需要通过配置文件开启。另外，还需要启用一些其它参数保证二进制日志的安全记录。通过 mysqlbinlog 工具，可以使用二进制日志恢复数据库。

## Hot Backup

### ibbackup

工作原理：

* 记录备份开始时 redo log 检查点的 LSN
* 复制共享表空间和独立表空间的文件
* 记录复制完毕后 redo log 检查点的 LSN
* 复制两个 LSN 中间的 redo log

数据恢复的步骤：

1. 恢复表空间文件
2. 应用 redo log

优点：

* 在线备份，不阻塞任何 SQL 语句
* 备份性能好，支持压缩，且跨平台支持

### XtraBackup

XtraBackup 能够对 InnoDB 存储引擎实现增量备份：

1. 首先完成一次完全备份，并记录此时 checkpoint 的 LSN
2. 增量备份时，比较表空间中每个页的 LSN 是否大于上次备份的 LSN，如果是，则备份并记录当前检查点 LSN

## Replication

MySQL 数据库提供了高可用高性能的主从模式：

1. 主服务器将数据更改记录到二进制日志中
2. 从服务器将主服务器的二进制日志复制到自身的 relay log 中
3. 从服务器 redo relay log，把更改应用到自身上，保证主从一致性

复制的原理实际上是完全备份 + 二进制日志备份的还原。但是复制并不是完全实时的，而是异步实时，主从服务器之间可能会存在延时。

---

