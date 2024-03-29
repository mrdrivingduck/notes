# InnoDB - Table Storage

Created by : Mr Dk.

2020 / 10 / 14 10:55

Nanjing, Jiangsu, China

---

## Table Organization

InnoDB 中表以 **主键顺序** 组织存放，这种存储方式的表成为 _索引组织表 (Index Organized Table)_。如果在创建表时没有定义主键：

- 如果表中有非空的唯一索引 (Unique NOT NULL) 的列，如果有，则使用第一个定义这种索引的列
- 如果没有，那么 InnoDB 存储引擎自动创建一个 6B 大小的指针

## Logical Structure

### Table Space

InnoDB 存储引擎中，所有数据都被存放在称为 _表空间 (Table Space)_ 的逻辑存储结构中。默认情况下，所有表的数据都存放在一个名为 `ibdata1` 的共享表空间中。在开启 `innodb_file_per_table` 后，每张表的数据、索引、插入缓冲 bitmap 会被存放到独立的表空间中；undo 信息、插入缓冲索引、事务信息、二次写缓冲还会被存放在共享表空间中。

### Segment

表空间由各个段组成，段的类型各有不同 - 数据段、索引段、回滚段等。InnoDB 存储引擎的表是由 B+ 树索引组织的，因此数据段就是 B+ 树的叶子结点，索引段就是 B+ 树的非叶子结点。对段的管理由引擎自身完成。

### Extent

**区** 由连续的页组成，一般来说一个区由 64 个连续的页组成。

### Page

页 (块) 时 InnoDB 存储引擎对磁盘进行管理的最小单位，根据用途，分为很多不同类型的页。

### Row

InnoDB 存储引擎是 _面向列 (Row-Oriented)_ 的，数据按 **行** 为单位进行存放，每页最多允许存放 16KB / 2-200 行记录。面向列的数据库有利于分析类 SQL 的执行以及数据压缩。在 InnoDB 1.0.x 版本之前，提供 Compact 和 Redundant 两种格式存放行记录。

## Row Record Format

### Compact 行记录格式

Compact 格式在 MySQL 5.0 中引入，包含：

- 变长字段长度列表 - **逆序** 存放所有 _变长列_ 的长度 (列 n 长度，列 n-1 长度，...)
  - 若列长度 < 255B，则用 1B 表示长度
  - 若列长度 > 255B，则用 2B 表示长度 (可见列长度最大限制为 65535)
- NULL 标志位 - 指示该行数据中是否有 NULL 值
- 记录头 (Record Header) - 包含记录的信息，以及下一个记录的偏移量；页内部通过链表串联行记录
- 行中每列的数据 (NULL 不占任何空间)

每行除了用户定义的列，还会有两个隐藏列：

- 事务 ID 列
- 回滚指针列

如果 InnoDB 表没有定义主键，每行还会增加一个 6B 的 rowid 列。

### Redundant 行记录格式

MySQL 5.0 前 InnoDB 存储引擎的存储方式：

- 字段长度偏移列表 (当前偏移减去前一个偏移才能得到长度)，同样以逆序存放
- 记录头 (Record Header) - 包含一行中列的数量
- 行中每列数据

对于 VARCHAR 类型的 NULL 值不占空间，而 CHAR 类型的 NULL 值需要占用空间。

### 行溢出数据

InnoDB 存储引擎可以将一些数据存储在真正的数据页面之外。一般情况下，InnoDB 存储引擎的数据都是存放在类型为 _B-tree node_ 的页中；但发生行溢出时，数据会被存放到类型为 _Uncompress BLOB_ 的页中。由于 InnoDB 存储引擎的表由 B+ 树索引组织，那么每个页中应当至少有两条行记录 - 如果每页中只能放得下一条行记录，那么 InnoDB 存储索引会自动将 (768B 后的) 行数据存放到溢出页中，保证一个数据页内至少有两条行记录。如果一个页中能够存放至少两行数据，那么行数据就不会存放到 BLOB 页中。

### Compressed 和 Dynamic 行记录格式

这两种新的格式对于存放 BLOB 数据采用 **完全行溢出** 的方式 - 数据页中只存放 20B 的指针，实际的数据存放在 _Off Page_ 中。另外，存储的行数据会以 zlib 的算法进行压缩存储。

## Data Page Format

页是 InnoDB 存储引擎管理数据库的最小磁盘单位。其中，页类型为 B-tree node 的页存放的就是实际的行数据，即数据页。数据页包含以下七个部分：

- File Header - 记录页的所属表空间，所在表空间中的位置，校验和等
- Page Header - 记录当前页的状态信息
- Infimum + Supremum Records - 虚拟行记录，限定记录的边界 (最小值 + 最大值)，不会被删除
- User Records - 实际存储的行记录
- Free Space - 空闲空间 (链表)
- Page Directory - 存放当前页中记录的相对位置，是一个稀疏的 (哈希表?)，按主键值顺序存放
- File Trailer - 用于检测页是否被完整地写入磁盘

B+ 树索引只能找到一条记录所在的页，数据库将该页载入内存后，再通过 Page Directory 进行二分查找 (因为是顺序存放) 得到一个粗略的结果 (一个 hash slot 中对应多条记录)，还要通过每条记录 Record Header 中的 `next_record` 继续查找，直到得到具体的某条记录。由于二分查找的复杂度低，并且在内存中完成，因此这部分开销通常被忽略。

在默认配置下，InnoDB 存储引擎每次从磁盘中读取一个页就会检测页的完整性，会带来一定开销，通过 `innodb_checksums` 可以开启或关闭完整性检查。

---
