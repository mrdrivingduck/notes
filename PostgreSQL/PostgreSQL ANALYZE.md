# PostgreSQL - ANALYZE

Created by : Mr Dk.

2022 / 06 / 20 0:34

Hangzhou, Zhejiang, China

---

## Background

PostgreSQL 在优化器中为一个查询树输出一个执行效率最高的物理计划树。其中，执行效率高低的衡量是通过代价估算实现的。比如通过估算查询返回元组的条数，和元组的宽度，就可以计算出 I/O 开销；也可以根据将要执行的物理操作估算出可能需要消耗的 CPU 代价。优化器通过系统表 `pg_statistic` 获得这些在代价估算过程需要使用到的关键统计信息，而 `pg_statistic` 系统表中的统计信息又是通过自动或手动的 `ANALYZE` 操作（或 `VACUUM`）计算得到的。`ANALYZE` 将会扫描表中的数据并按列进行分析，将得到的诸如每列的数据分布、最常见值、频率等统计信息写入系统表。

本文从源码的角度分析一下 `ANALYZE` 操作的实现机制。源码使用目前 PostgreSQL 最新的稳定版本 PostgreSQL 14。

## Statistics

首先，我们应当搞明白分析操作的输出是什么。所以我们可以看一看 `pg_statistic` 中有哪些列，每个列的含义是什么。这个系统表中的每一行表示其它数据表中 **每一列的统计信息**。

```sql
postgres=# \d+ pg_statistic
                                 Table "pg_catalog.pg_statistic"
   Column    |   Type   | Collation | Nullable | Default | Storage  | Stats target | Description
-------------+----------+-----------+----------+---------+----------+--------------+-------------
 starelid    | oid      |           | not null |         | plain    |              |
 staattnum   | smallint |           | not null |         | plain    |              |
 stainherit  | boolean  |           | not null |         | plain    |              |
 stanullfrac | real     |           | not null |         | plain    |              |
 stawidth    | integer  |           | not null |         | plain    |              |
 stadistinct | real     |           | not null |         | plain    |              |
 stakind1    | smallint |           | not null |         | plain    |              |
 stakind2    | smallint |           | not null |         | plain    |              |
 stakind3    | smallint |           | not null |         | plain    |              |
 stakind4    | smallint |           | not null |         | plain    |              |
 stakind5    | smallint |           | not null |         | plain    |              |
 staop1      | oid      |           | not null |         | plain    |              |
 staop2      | oid      |           | not null |         | plain    |              |
 staop3      | oid      |           | not null |         | plain    |              |
 staop4      | oid      |           | not null |         | plain    |              |
 staop5      | oid      |           | not null |         | plain    |              |
 stanumbers1 | real[]   |           |          |         | extended |              |
 stanumbers2 | real[]   |           |          |         | extended |              |
 stanumbers3 | real[]   |           |          |         | extended |              |
 stanumbers4 | real[]   |           |          |         | extended |              |
 stanumbers5 | real[]   |           |          |         | extended |              |
 stavalues1  | anyarray |           |          |         | extended |              |
 stavalues2  | anyarray |           |          |         | extended |              |
 stavalues3  | anyarray |           |          |         | extended |              |
 stavalues4  | anyarray |           |          |         | extended |              |
 stavalues5  | anyarray |           |          |         | extended |              |
Indexes:
    "pg_statistic_relid_att_inh_index" UNIQUE, btree (starelid, staattnum, stainherit)
```

```c
/* ----------------
 *      pg_statistic definition.  cpp turns this into
 *      typedef struct FormData_pg_statistic
 * ----------------
 */
CATALOG(pg_statistic,2619,StatisticRelationId)
{
    /* These fields form the unique key for the entry: */
    Oid         starelid BKI_LOOKUP(pg_class);  /* relation containing
                                                 * attribute */
    int16       staattnum;      /* attribute (column) stats are for */
    bool        stainherit;     /* true if inheritance children are included */

    /* the fraction of the column's entries that are NULL: */
    float4      stanullfrac;

    /*
     * stawidth is the average width in bytes of non-null entries.  For
     * fixed-width datatypes this is of course the same as the typlen, but for
     * var-width types it is more useful.  Note that this is the average width
     * of the data as actually stored, post-TOASTing (eg, for a
     * moved-out-of-line value, only the size of the pointer object is
     * counted).  This is the appropriate definition for the primary use of
     * the statistic, which is to estimate sizes of in-memory hash tables of
     * tuples.
     */
    int32       stawidth;

    /* ----------------
     * stadistinct indicates the (approximate) number of distinct non-null
     * data values in the column.  The interpretation is:
     *      0       unknown or not computed
     *      > 0     actual number of distinct values
     *      < 0     negative of multiplier for number of rows
     * The special negative case allows us to cope with columns that are
     * unique (stadistinct = -1) or nearly so (for example, a column in which
     * non-null values appear about twice on the average could be represented
     * by stadistinct = -0.5 if there are no nulls, or -0.4 if 20% of the
     * column is nulls).  Because the number-of-rows statistic in pg_class may
     * be updated more frequently than pg_statistic is, it's important to be
     * able to describe such situations as a multiple of the number of rows,
     * rather than a fixed number of distinct values.  But in other cases a
     * fixed number is correct (eg, a boolean column).
     * ----------------
     */
    float4      stadistinct;

    /* ----------------
     * To allow keeping statistics on different kinds of datatypes,
     * we do not hard-wire any particular meaning for the remaining
     * statistical fields.  Instead, we provide several "slots" in which
     * statistical data can be placed.  Each slot includes:
     *      kind            integer code identifying kind of data (see below)
     *      op              OID of associated operator, if needed
     *      coll            OID of relevant collation, or 0 if none
     *      numbers         float4 array (for statistical values)
     *      values          anyarray (for representations of data values)
     * The ID, operator, and collation fields are never NULL; they are zeroes
     * in an unused slot.  The numbers and values fields are NULL in an
     * unused slot, and might also be NULL in a used slot if the slot kind
     * has no need for one or the other.
     * ----------------
     */

    int16       stakind1;
    int16       stakind2;
    int16       stakind3;
    int16       stakind4;
    int16       stakind5;

    Oid         staop1 BKI_LOOKUP_OPT(pg_operator);
    Oid         staop2 BKI_LOOKUP_OPT(pg_operator);
    Oid         staop3 BKI_LOOKUP_OPT(pg_operator);
    Oid         staop4 BKI_LOOKUP_OPT(pg_operator);
    Oid         staop5 BKI_LOOKUP_OPT(pg_operator);

    Oid         stacoll1 BKI_LOOKUP_OPT(pg_collation);
    Oid         stacoll2 BKI_LOOKUP_OPT(pg_collation);
    Oid         stacoll3 BKI_LOOKUP_OPT(pg_collation);
    Oid         stacoll4 BKI_LOOKUP_OPT(pg_collation);
    Oid         stacoll5 BKI_LOOKUP_OPT(pg_collation);

#ifdef CATALOG_VARLEN           /* variable-length fields start here */
    float4      stanumbers1[1];
    float4      stanumbers2[1];
    float4      stanumbers3[1];
    float4      stanumbers4[1];
    float4      stanumbers5[1];

    /*
     * Values in these arrays are values of the column's data type, or of some
     * related type such as an array element type.  We presently have to cheat
     * quite a bit to allow polymorphic arrays of this kind, but perhaps
     * someday it'll be a less bogus facility.
     */
    anyarray    stavalues1;
    anyarray    stavalues2;
    anyarray    stavalues3;
    anyarray    stavalues4;
    anyarray    stavalues5;
#endif
} FormData_pg_statistic;
```

从数据库命令行的角度和内核 C 代码的角度来看，统计信息的内容都是一致的。所有的属性都以 `sta` 开头。其中：

- `starelid` 表示当前列所属的表或索引
- `staattnum` 表示本行统计信息属于上述表或索引中的第几列
- `stainherit` 表示统计信息是否包含子列
- `stanullfrac` 表示该列中值为 NULL 的行数比例
- `stawidth` 表示该列非空值的平均宽度
- `stadistinct` 表示列中非空值的唯一值数量
  - `0` 表示未知或未计算
  - `> 0` 表示唯一值的实际数量
  - `< 0` 表示 _negative of multiplier for number of rows_ ？啥登西 😩

由于不同数据类型所能够被计算的统计信息可能会有一些细微的差别，在接下来的部分中，PostgreSQL 预留了一些存放统计信息的 **槽（slots）**。目前的内核里暂时预留了五个槽：

```c
#define STATISTIC_NUM_SLOTS  5
```

每一种特定的统计信息可以使用一个槽，具体在槽里放什么完全由这种统计信息的定义自由决定。每一个槽的可用空间包含这么几个部分（其中的 `N` 表示槽的编号，取值为 `1` 到 `5`）：

- `stakindN`：标识这种统计信息的整数编号
- `staopN`：用于计算或使用统计信息的运算符 OID
- `stacollN`：排序规则 OID
- `stanumbersN`：浮点数数组
- `stavaluesN`：任意值数组

PostgreSQL 内核中规定，统计信息的编号 `1` 至 `99` 被保留给 PostgreSQL 核心统计信息使用，其它部分的编号安排如内核注释所示：

```c
/*
 * The present allocation of "kind" codes is:
 *
 *  1-99:       reserved for assignment by the core PostgreSQL project
 *              (values in this range will be documented in this file)
 *  100-199:    reserved for assignment by the PostGIS project
 *              (values to be documented in PostGIS documentation)
 *  200-299:    reserved for assignment by the ESRI ST_Geometry project
 *              (values to be documented in ESRI ST_Geometry documentation)
 *  300-9999:   reserved for future public assignments
 *
 * For private use you may choose a "kind" code at random in the range
 * 10000-30000.  However, for code that is to be widely disseminated it is
 * better to obtain a publicly defined "kind" code by request from the
 * PostgreSQL Global Development Group.
 */
```

目前可以在内核代码中看到的 PostgreSQL 核心统计信息有 7 个，编号分别从 `1` 到 `7`。我们可以看看这 7 种统计信息分别如何使用上述的槽。

### Most Common Values (MCV)

```c
/*
 * In a "most common values" slot, staop is the OID of the "=" operator
 * used to decide whether values are the same or not, and stacoll is the
 * collation used (same as column's collation).  stavalues contains
 * the K most common non-null values appearing in the column, and stanumbers
 * contains their frequencies (fractions of total row count).  The values
 * shall be ordered in decreasing frequency.  Note that since the arrays are
 * variable-size, K may be chosen by the statistics collector.  Values should
 * not appear in MCV unless they have been observed to occur more than once;
 * a unique column will have no MCV slot.
 */
#define STATISTIC_KIND_MCV  1
```

对于一个列中的 **最常见值**，在 `staop` 中保存 `=` 运算符来决定一个值是否等于一个最常见值。在 `stavalues` 中保存了该列中最常见的 K 个非空值，`stanumbers` 中分别保存了这 K 个值出现的频率。

### Histogram

```c
/*
 * A "histogram" slot describes the distribution of scalar data.  staop is
 * the OID of the "<" operator that describes the sort ordering, and stacoll
 * is the relevant collation.  (In theory more than one histogram could appear,
 * if a datatype has more than one useful sort operator or we care about more
 * than one collation.  Currently the collation will always be that of the
 * underlying column.)  stavalues contains M (>=2) non-null values that
 * divide the non-null column data values into M-1 bins of approximately equal
 * population.  The first stavalues item is the MIN and the last is the MAX.
 * stanumbers is not used and should be NULL.  IMPORTANT POINT: if an MCV
 * slot is also provided, then the histogram describes the data distribution
 * *after removing the values listed in MCV* (thus, it's a "compressed
 * histogram" in the technical parlance).  This allows a more accurate
 * representation of the distribution of a column with some very-common
 * values.  In a column with only a few distinct values, it's possible that
 * the MCV list describes the entire data population; in this case the
 * histogram reduces to empty and should be omitted.
 */
#define STATISTIC_KIND_HISTOGRAM  2
```

表示一个（数值）列的数据分布直方图。`staop` 保存 `<` 运算符用于决定数据分布的排序顺序。`stavalues` 包含了能够将该列的非空值划分到 M - 1 个容量接近的桶中的 M 个非空值。如果该列中已经有了 MCV 的槽，那么数据分布直方图中将不包含 MCV 中的值，以获得更精确的数据分布。

### Correlation

```c
/*
 * A "correlation" slot describes the correlation between the physical order
 * of table tuples and the ordering of data values of this column, as seen
 * by the "<" operator identified by staop with the collation identified by
 * stacoll.  (As with the histogram, more than one entry could theoretically
 * appear.)  stavalues is not used and should be NULL.  stanumbers contains
 * a single entry, the correlation coefficient between the sequence of data
 * values and the sequence of their actual tuple positions.  The coefficient
 * ranges from +1 to -1.
 */
#define STATISTIC_KIND_CORRELATION  3
```

在 `stanumbers` 中保存数据值和它们的实际元组位置的相关系数。

### Most Common Elements

```c
/*
 * A "most common elements" slot is similar to a "most common values" slot,
 * except that it stores the most common non-null *elements* of the column
 * values.  This is useful when the column datatype is an array or some other
 * type with identifiable elements (for instance, tsvector).  staop contains
 * the equality operator appropriate to the element type, and stacoll
 * contains the collation to use with it.  stavalues contains
 * the most common element values, and stanumbers their frequencies.  Unlike
 * MCV slots, frequencies are measured as the fraction of non-null rows the
 * element value appears in, not the frequency of all rows.  Also unlike
 * MCV slots, the values are sorted into the element type's default order
 * (to support binary search for a particular value).  Since this puts the
 * minimum and maximum frequencies at unpredictable spots in stanumbers,
 * there are two extra members of stanumbers, holding copies of the minimum
 * and maximum frequencies.  Optionally, there can be a third extra member,
 * which holds the frequency of null elements (expressed in the same terms:
 * the fraction of non-null rows that contain at least one null element).  If
 * this member is omitted, the column is presumed to contain no null elements.
 *
 * Note: in current usage for tsvector columns, the stavalues elements are of
 * type text, even though their representation within tsvector is not
 * exactly text.
 */
#define STATISTIC_KIND_MCELEM  4
```

与 MCV 类似，但是保存的是列中的 **最常见元素**，主要用于数组等类型。同样，在 `staop` 中保存了等值运算符用于判断元素出现的频率高低。但与 MCV 不同的是这里的频率计算的分母是非空的行，而不是所有的行。另外，所有的常见元素使用元素对应数据类型的默认顺序进行排序，以便二分查找。

### Distinct Elements Count Histogram

```c
/*
 * A "distinct elements count histogram" slot describes the distribution of
 * the number of distinct element values present in each row of an array-type
 * column.  Only non-null rows are considered, and only non-null elements.
 * staop contains the equality operator appropriate to the element type,
 * and stacoll contains the collation to use with it.
 * stavalues is not used and should be NULL.  The last member of stanumbers is
 * the average count of distinct element values over all non-null rows.  The
 * preceding M (>=2) members form a histogram that divides the population of
 * distinct-elements counts into M-1 bins of approximately equal population.
 * The first of these is the minimum observed count, and the last the maximum.
 */
#define STATISTIC_KIND_DECHIST  5
```

表示列中出现所有数值的频率分布直方图。`stanumbers` 数组的前 M 个元素是将列中所有唯一值的出现次数大致均分到 M - 1 个桶中的边界值。后续跟上一个所有唯一值的平均出现次数。这个统计信息应该会被用于计算 _选择率_。

### Length Histogram

```c
/*
 * A "length histogram" slot describes the distribution of range lengths in
 * rows of a range-type column. stanumbers contains a single entry, the
 * fraction of empty ranges. stavalues is a histogram of non-empty lengths, in
 * a format similar to STATISTIC_KIND_HISTOGRAM: it contains M (>=2) range
 * values that divide the column data values into M-1 bins of approximately
 * equal population. The lengths are stored as float8s, as measured by the
 * range type's subdiff function. Only non-null rows are considered.
 */
#define STATISTIC_KIND_RANGE_LENGTH_HISTOGRAM  6
```

长度直方图描述了一个范围类型的列的范围长度分布。同样也是一个长度为 M 的直方图，保存在 `stanumbers` 中。

### Bounds Histogram

```c
/*
 * A "bounds histogram" slot is similar to STATISTIC_KIND_HISTOGRAM, but for
 * a range-type column.  stavalues contains M (>=2) range values that divide
 * the column data values into M-1 bins of approximately equal population.
 * Unlike a regular scalar histogram, this is actually two histograms combined
 * into a single array, with the lower bounds of each value forming a
 * histogram of lower bounds, and the upper bounds a histogram of upper
 * bounds.  Only non-NULL, non-empty ranges are included.
 */
#define STATISTIC_KIND_BOUNDS_HISTOGRAM  7
```

边界直方图同样也被用于范围类型，与数据分布直方图类似。`stavalues` 中保存了使该列数值大致均分到 M - 1 个桶中的 M 个范围边界值。只考虑非空行。

## Kernel Execution of Analyze

知道 `pg_statistic` 最终需要保存哪些信息以后，再来看看内核如何收集和计算这些信息。让我们进入 PostgreSQL 内核的执行器代码中。对于 `ANALYZE` 这种工具性质的指令，执行器代码通过 `standard_ProcessUtility()` 函数中的 switch case 将每一种指令路由到实现相应功能的函数中。

```c
/*
 * standard_ProcessUtility itself deals only with utility commands for
 * which we do not provide event trigger support.  Commands that do have
 * such support are passed down to ProcessUtilitySlow, which contains the
 * necessary infrastructure for such triggers.
 *
 * This division is not just for performance: it's critical that the
 * event trigger code not be invoked when doing START TRANSACTION for
 * example, because we might need to refresh the event trigger cache,
 * which requires being in a valid transaction.
 */
void
standard_ProcessUtility(PlannedStmt *pstmt,
                        const char *queryString,
                        bool readOnlyTree,
                        ProcessUtilityContext context,
                        ParamListInfo params,
                        QueryEnvironment *queryEnv,
                        DestReceiver *dest,
                        QueryCompletion *qc)
{
    // ...

    switch (nodeTag(parsetree))
    {
        // ...

        case T_VacuumStmt:
            ExecVacuum(pstate, (VacuumStmt *) parsetree, isTopLevel);
            break;

        // ...
    }

    // ...
}
```

`ANALYZE` 的处理逻辑入口和 `VACUUM` 一致，进入 `ExecVacuum()` 函数。

```c
/*
 * Primary entry point for manual VACUUM and ANALYZE commands
 *
 * This is mainly a preparation wrapper for the real operations that will
 * happen in vacuum().
 */
void
ExecVacuum(ParseState *pstate, VacuumStmt *vacstmt, bool isTopLevel)
{
    // ...

    /* Now go through the common routine */
    vacuum(vacstmt->rels, &params, NULL, isTopLevel);
}
```

在 parse 了一大堆 option 之后，进入了 `vacuum()` 函数。在这里，内核代码将会首先明确一下要分析哪些表。因为 `ANALYZE` 命令在使用上可以：

- 分析整个数据库中的所有表
- 分析某几个特定的表
- 分析某个表的某几个特定列

在明确要分析哪些表以后，依次将每一个表传入 `analyze_rel()` 函数：

```c
if (params->options & VACOPT_ANALYZE)
{
    // ...

    analyze_rel(vrel->oid, vrel->relation, params,
                vrel->va_cols, in_outer_xact, vac_strategy);

    // ...
}
```

进入 `analyze_rel()` 函数以后，内核代码将会对将要被分析的表加 `ShareUpdateExclusiveLock` 锁，以防止两个并发进行的 `ANALYZE`。然后根据待分析表的类型来决定具体的处理方式（比如分析一个 FDW 外表就应该直接调用 FDW routine 中提供的 ANALYZE 功能了）。接下来，将这个表传入 `do_analyze_rel()` 函数中。

```c
/*
 *  analyze_rel() -- analyze one relation
 *
 * relid identifies the relation to analyze.  If relation is supplied, use
 * the name therein for reporting any failure to open/lock the rel; do not
 * use it once we've successfully opened the rel, since it might be stale.
 */
void
analyze_rel(Oid relid, RangeVar *relation,
            VacuumParams *params, List *va_cols, bool in_outer_xact,
            BufferAccessStrategy bstrategy)
{
    // ...

    /*
     * Do the normal non-recursive ANALYZE.  We can skip this for partitioned
     * tables, which don't contain any rows.
     */
    if (onerel->rd_rel->relkind != RELKIND_PARTITIONED_TABLE)
        do_analyze_rel(onerel, params, va_cols, acquirefunc,
                       relpages, false, in_outer_xact, elevel);

    // ...
}
```

进入 `do_analyze_rel()` 函数后，内核代码将进一步明确要分析一个表中的哪些列：用户可能指定只分析表中的某几个列——被频繁访问的列才更有被分析的价值。然后还要打开待分析表的所有索引，看看是否有可以被分析的列。

为了得到每一列的统计信息，显然我们需要把每一列的数据从磁盘上读起来再去做计算。这里就有一个比较关键的问题了：到底扫描多少行数据呢？理论上，分析尽可能多的数据，最好是全部的数据，肯定能够得到最精确的统计数据；但是对一张很大的表来说，我们没有办法在内存中放下所有的数据，并且分析的阻塞时间也是不可接受的。所以用户可以指定要采样的最大行数，从而在运行开销和统计信息准确性上达成妥协：

> 通过设置 GUC 参数 [`default_statistics_target`](https://www.postgresql.org/docs/current/runtime-config-query.html#GUC-DEFAULT-STATISTICS-TARGET) 为更大的值，可以全局增大采样的数据量。这会导致 `ANALYZE` 所需要的整体时间变长，但可以得到更准确的统计信息（尤其是对大表）。如果全局设置带来的影响较大，可以通过 [`ALTER TABLE ... ALTER COLUMN ... SET STATISTICS`](https://www.postgresql.org/docs/current/sql-altertable.html) 为某一个列单独设置采样数据量。

```c
/*
 * Determine how many rows we need to sample, using the worst case from
 * all analyzable columns.  We use a lower bound of 100 rows to avoid
 * possible overflow in Vitter's algorithm.  (Note: that will also be the
 * target in the corner case where there are no analyzable columns.)
 */
targrows = 100;
for (i = 0; i < attr_cnt; i++)
{
    if (targrows < vacattrstats[i]->minrows)
        targrows = vacattrstats[i]->minrows;
}
for (ind = 0; ind < nindexes; ind++)
{
    AnlIndexData *thisdata = &indexdata[ind];

    for (i = 0; i < thisdata->attr_cnt; i++)
    {
        if (targrows < thisdata->vacattrstats[i]->minrows)
            targrows = thisdata->vacattrstats[i]->minrows;
    }
}

/*
 * Look at extended statistics objects too, as those may define custom
 * statistics target. So we may need to sample more rows and then build
 * the statistics with enough detail.
 */
minrows = ComputeExtStatisticsRows(onerel, attr_cnt, vacattrstats);

if (targrows < minrows)
    targrows = minrows;
```

在确定需要采样多少行数据后，内核代码分配了一块相应长度的元组数组，然后开始使用 `acquirefunc` 函数指针采样数据：

```c
/*
 * Acquire the sample rows
 */
rows = (HeapTuple *) palloc(targrows * sizeof(HeapTuple));
pgstat_progress_update_param(PROGRESS_ANALYZE_PHASE,
                             inh ? PROGRESS_ANALYZE_PHASE_ACQUIRE_SAMPLE_ROWS_INH :
                             PROGRESS_ANALYZE_PHASE_ACQUIRE_SAMPLE_ROWS);
if (inh)
    numrows = acquire_inherited_sample_rows(onerel, elevel,
                                            rows, targrows,
                                            &totalrows, &totaldeadrows);
else
    numrows = (*acquirefunc) (onerel, elevel,
                              rows, targrows,
                              &totalrows, &totaldeadrows);
```

这个函数指针指向的是 `analyze_rel()` 函数中设置好的 `acquire_sample_rows()` 函数。该函数使用两阶段模式对表中的数据进行采样：

- 阶段 1：随机选择包含目标采样行数的数据块
- 阶段 2：对每一个数据块使用 Vitter 算法按行随机采样数据

两阶段同时进行。在采样完成后，被采样到的元组应该已经被放置在元组数组中了。对这个元组数组按照元组的位置进行快速排序，并使用这些采样到的数据估算整个表中的存活元组与死元组的个数：

```c
/*
 * acquire_sample_rows -- acquire a random sample of rows from the table
 *
 * Selected rows are returned in the caller-allocated array rows[], which
 * must have at least targrows entries.
 * The actual number of rows selected is returned as the function result.
 * We also estimate the total numbers of live and dead rows in the table,
 * and return them into *totalrows and *totaldeadrows, respectively.
 *
 * The returned list of tuples is in order by physical position in the table.
 * (We will rely on this later to derive correlation estimates.)
 *
 * As of May 2004 we use a new two-stage method:  Stage one selects up
 * to targrows random blocks (or all blocks, if there aren't so many).
 * Stage two scans these blocks and uses the Vitter algorithm to create
 * a random sample of targrows rows (or less, if there are less in the
 * sample of blocks).  The two stages are executed simultaneously: each
 * block is processed as soon as stage one returns its number and while
 * the rows are read stage two controls which ones are to be inserted
 * into the sample.
 *
 * Although every row has an equal chance of ending up in the final
 * sample, this sampling method is not perfect: not every possible
 * sample has an equal chance of being selected.  For large relations
 * the number of different blocks represented by the sample tends to be
 * too small.  We can live with that for now.  Improvements are welcome.
 *
 * An important property of this sampling method is that because we do
 * look at a statistically unbiased set of blocks, we should get
 * unbiased estimates of the average numbers of live and dead rows per
 * block.  The previous sampling method put too much credence in the row
 * density near the start of the table.
 */
static int
acquire_sample_rows(Relation onerel, int elevel,
                    HeapTuple *rows, int targrows,
                    double *totalrows, double *totaldeadrows)
{
    // ...

    /* Outer loop over blocks to sample */
    while (BlockSampler_HasMore(&bs))
    {
        bool        block_accepted;
        BlockNumber targblock = BlockSampler_Next(&bs);
        // ...
    }

    // ...

    /*
     * If we didn't find as many tuples as we wanted then we're done. No sort
     * is needed, since they're already in order.
     *
     * Otherwise we need to sort the collected tuples by position
     * (itempointer). It's not worth worrying about corner cases where the
     * tuples are already sorted.
     */
    if (numrows == targrows)
        qsort((void *) rows, numrows, sizeof(HeapTuple), compare_rows);

    /*
     * Estimate total numbers of live and dead rows in relation, extrapolating
     * on the assumption that the average tuple density in pages we didn't
     * scan is the same as in the pages we did scan.  Since what we scanned is
     * a random sample of the pages in the relation, this should be a good
     * assumption.
     */
    if (bs.m > 0)
    {
        *totalrows = floor((liverows / bs.m) * totalblocks + 0.5);
        *totaldeadrows = floor((deadrows / bs.m) * totalblocks + 0.5);
    }
    else
    {
        *totalrows = 0.0;
        *totaldeadrows = 0.0;
    }

    // ...
}
```

回到 `do_analyze_rel()` 函数。采样到数据以后，对于要分析的每一个列，分别计算统计数据，然后更新 `pg_statistic` 系统表：

```c
/*
 * Compute the statistics.  Temporary results during the calculations for
 * each column are stored in a child context.  The calc routines are
 * responsible to make sure that whatever they store into the VacAttrStats
 * structure is allocated in anl_context.
 */
if (numrows > 0)
{
    // ...

    for (i = 0; i < attr_cnt; i++)
    {
        VacAttrStats *stats = vacattrstats[i];
        AttributeOpts *aopt;

        stats->rows = rows;
        stats->tupDesc = onerel->rd_att;
        stats->compute_stats(stats,
                             std_fetch_func,
                             numrows,
                             totalrows);

        // ...
    }

    // ...

    /*
     * Emit the completed stats rows into pg_statistic, replacing any
     * previous statistics for the target columns.  (If there are stats in
     * pg_statistic for columns we didn't process, we leave them alone.)
     */
    update_attstats(RelationGetRelid(onerel), inh,
                    attr_cnt, vacattrstats);

    // ...
}
```

显然，对于不同类型的列，其 `compute_stats` 函数指针指向的计算函数肯定不太一样。所以我们不妨看看给这个函数指针赋值的地方：

```c
/*
 * std_typanalyze -- the default type-specific typanalyze function
 */
bool
std_typanalyze(VacAttrStats *stats)
{
    // ...

    /*
     * Determine which standard statistics algorithm to use
     */
    if (OidIsValid(eqopr) && OidIsValid(ltopr))
    {
        /* Seems to be a scalar datatype */
        stats->compute_stats = compute_scalar_stats;
        /*--------------------
         * The following choice of minrows is based on the paper
         * "Random sampling for histogram construction: how much is enough?"
         * by Surajit Chaudhuri, Rajeev Motwani and Vivek Narasayya, in
         * Proceedings of ACM SIGMOD International Conference on Management
         * of Data, 1998, Pages 436-447.  Their Corollary 1 to Theorem 5
         * says that for table size n, histogram size k, maximum relative
         * error in bin size f, and error probability gamma, the minimum
         * random sample size is
         *      r = 4 * k * ln(2*n/gamma) / f^2
         * Taking f = 0.5, gamma = 0.01, n = 10^6 rows, we obtain
         *      r = 305.82 * k
         * Note that because of the log function, the dependence on n is
         * quite weak; even at n = 10^12, a 300*k sample gives <= 0.66
         * bin size error with probability 0.99.  So there's no real need to
         * scale for n, which is a good thing because we don't necessarily
         * know it at this point.
         *--------------------
         */
        stats->minrows = 300 * attr->attstattarget;
    }
    else if (OidIsValid(eqopr))
    {
        /* We can still recognize distinct values */
        stats->compute_stats = compute_distinct_stats;
        /* Might as well use the same minrows as above */
        stats->minrows = 300 * attr->attstattarget;
    }
    else
    {
        /* Can't do much but the trivial stuff */
        stats->compute_stats = compute_trivial_stats;
        /* Might as well use the same minrows as above */
        stats->minrows = 300 * attr->attstattarget;
    }

    // ...
}
```

这个条件判断语句可以被解读为：

- 如果说一个列的数据类型支持默认的 `=`（`eqopr`：equals operator）和 `<`（`ltopr`：less than operator），那么这个列应该是一个数值类型，可以使用 `compute_scalar_stats()` 函数进行分析
- 如果列的数据类型只支持 `=` 运算符，那么依旧还可以使用 `compute_distinct_stats` 进行唯一值的统计分析
- 如果都不行，那么这个列只能使用 `compute_trivial_stats` 进行一些简单的分析

我们可以分别看看这三个分析函数里做了啥，但我不准备深入每一个分析函数解读其中的逻辑了。因为其中的思想基于一些很古早的统计学论文，古早到连 PDF 上的字母都快看不清了...😱 咱数学不好，偷个懒。在代码上没有特别大的可读性，因为基本是参照论文中的公式实现的，不看论文根本没法理解变量和公式的含义。

### compute_trivial_stats

如果某个列的数据类型不支持等值运算符和比较运算符，那么就只能进行一些简单的分析，比如：

- 非空行的比例
- 列中元组的平均宽度

这些可以通过对采样后的元组数组进行循环遍历后轻松得到。

```c
/*
 *  compute_trivial_stats() -- compute very basic column statistics
 *
 *  We use this when we cannot find a hash "=" operator for the datatype.
 *
 *  We determine the fraction of non-null rows and the average datum width.
 */
static void
compute_trivial_stats(VacAttrStatsP stats,
                      AnalyzeAttrFetchFunc fetchfunc,
                      int samplerows,
                      double totalrows)
{}
```

### compute_distinct_stats

如果某个列只支持等值运算符，也就是说我们只能知道一个数值 **是什么**，但不能和其它数值比大小。所以无法分析数值在大小范围上的分布，只能分析数值在出现频率上的分布。所以该函数分析的统计数据包含：

- 非空行的比例
- 列中元组的平均宽度
- 最频繁出现的值（MCV）
- （估算的）唯一值个数

```c
/*
 *  compute_distinct_stats() -- compute column statistics including ndistinct
 *
 *  We use this when we can find only an "=" operator for the datatype.
 *
 *  We determine the fraction of non-null rows, the average width, the
 *  most common values, and the (estimated) number of distinct values.
 *
 *  The most common values are determined by brute force: we keep a list
 *  of previously seen values, ordered by number of times seen, as we scan
 *  the samples.  A newly seen value is inserted just after the last
 *  multiply-seen value, causing the bottommost (oldest) singly-seen value
 *  to drop off the list.  The accuracy of this method, and also its cost,
 *  depend mainly on the length of the list we are willing to keep.
 */
static void
compute_distinct_stats(VacAttrStatsP stats,
                       AnalyzeAttrFetchFunc fetchfunc,
                       int samplerows,
                       double totalrows)
{}
```

### compute_scalar_stats

如果一个列的数据类型支持等值运算符和比较运算符，那么可以进行最详尽的分析。分析目标包含：

- 非空行的比例
- 列中元组的平均宽度
- 最频繁出现的值（MCV）
- （估算的）唯一值个数
- 数据分布直方图
- 物理和逻辑位置的相关性（这个是用来干啥的？？？😥）

```c
/*
 *  compute_distinct_stats() -- compute column statistics including ndistinct
 *
 *  We use this when we can find only an "=" operator for the datatype.
 *
 *  We determine the fraction of non-null rows, the average width, the
 *  most common values, and the (estimated) number of distinct values.
 *
 *  The most common values are determined by brute force: we keep a list
 *  of previously seen values, ordered by number of times seen, as we scan
 *  the samples.  A newly seen value is inserted just after the last
 *  multiply-seen value, causing the bottommost (oldest) singly-seen value
 *  to drop off the list.  The accuracy of this method, and also its cost,
 *  depend mainly on the length of the list we are willing to keep.
 */
static void
compute_distinct_stats(VacAttrStatsP stats,
                       AnalyzeAttrFetchFunc fetchfunc,
                       int samplerows,
                       double totalrows)
{}
```

## Summary

以 PostgreSQL 优化器需要的统计信息为切入点，分析了 `ANALYZE` 命令的大致执行流程。出于简洁性，在流程分析上没有覆盖各种 corner case 和相关的处理逻辑。同时避开了所有和数学相关的细节 🤪。

## References

[PostgreSQL 14 Documentation: ANALYZE](https://www.postgresql.org/docs/current/sql-analyze.html)

[PostgreSQL 14 Documentation: 25.1. Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html#VACUUM-FOR-STATISTICS)

[PostgreSQL 14 Documentation: 14.2. Statistics Used by the Planner](https://www.postgresql.org/docs/current/planner-stats.html)

[PostgreSQL 14 Documentation: 52.49. pg_statistic](https://www.postgresql.org/docs/current/catalog-pg-statistic.html)

[阿里云数据库内核月报 2016/05：PostgreSQL 特性分析 统计信息计算方法](http://mysql.taobao.org/monthly/2016/05/09/)
