# PostgreSQL - COPY FROM

Created by: Mr Dk.

2023 / 09 / 28 00:04

Qingdao, Shandong, China

---

## Background

PostgreSQL 的 `COPY FROM` 语法用于将来自外部 _文件_（磁盘文件 / 网络管道 / IPC 管道）的数据导入到数据库的表中。`COPY FROM` 支持只导入指定的部分列，其它列被填充为默认值。`COPY FROM` 还支持带有 `WHERE` 子句，只允许满足条件的行被导入到表中。

`COPY FROM` 的实现逻辑比 `COPY TO` 相对复杂一些。其原因在于，`COPY TO` 是要把数据库中的数据导出到外部，其中获取数据这一步及其并行优化，很大程度上借助了优化器和执行器的能力，复用了很多代码；而 `COPY FROM` 是要把外部数据导入数据库，其中写入数据库的行为因需要更高效的定制实现，而不能复用 `INSERT` 相关的执行器代码了。

本文基于当前 PostgreSQL 主干开发分支（PostgreSQL 17 under devel）源代码对这个过程进行分析。分析过程中发现 `COPY FROM` 的代码存在一些小小的问题（真的是很小的问题..），于是误打误撞地向 PostgreSQL 社区贡献了自己的第一个 patch：

```
commit e434e21e114b423e919324ad6ce1f3f079ca2a03
Author: Michael Paquier <michael@paquier.xyz>
Date:   Sat Sep 9 21:12:41 2023 +0900

    Remove redundant assignments in copyfrom.c

    The tuple descriptor and the number of attributes are assigned twice to
    the same values in BeginCopyFrom(), for what looks like a small thinko
    coming from the refactoring done in c532d15dddff1.

    Author: Jingtang Zhang
    Discussion: https://postgr.es/m/CAPsk3_CrYeXUVHEiaWAYxY9BKiGvGT3AoXo_+Jm0xP_s_VmXCA@mail.gmail.com
```

## COPY Statement

如对 `COPY TO` 的分析所述，此类语法被视为一种 DDL。在执行器开始处理之前，语法解析器已经把与 `COPY` 相关的参数设置在 `CopyStmt` 结构中了。其中：

- `relation`：将要被导入的表
- `attlist`：将要导入的列名列表
- `is_from`：当前执行的是 `COPY TO` 还是 `COPY FROM`
- `is_program`：导入的来源端是否是一个进程（管道）
- `filename`：导入来源端的文件名/程序名（为 `NULL` 意味着从 `STDIN` 导入）
- `options`：导入选项

```c
/* ----------------------
 *      Copy Statement
 *
 * We support "COPY relation FROM file", "COPY relation TO file", and
 * "COPY (query) TO file".  In any given CopyStmt, exactly one of "relation"
 * and "query" must be non-NULL.
 * ----------------------
 */
typedef struct CopyStmt
{
    NodeTag     type;
    RangeVar   *relation;       /* the relation to copy */
    Node       *query;          /* the query (SELECT or DML statement with
                                 * RETURNING) to copy, as a raw parse tree */
    List       *attlist;        /* List of column names (as Strings), or NIL
                                 * for all columns */
    bool        is_from;        /* TO or FROM */
    bool        is_program;     /* is 'filename' a program to popen? */
    char       *filename;       /* filename, or NULL for STDIN/STDOUT */
    List       *options;        /* List of DefElem nodes */
    Node       *whereClause;    /* WHERE condition (or NULL) */
} CopyStmt;
```

## 权限检查

进入到 `DoCopy` 函数后，需要进行初步的权限检查。首先需要做判断的是从文件/进程导入的场景：如果是从文件导入，那么当前用户需要有读文件的权限；如果是从程序导入，那么当前用户需要有执行程序的权限：

```c
bool        pipe = (stmt->filename == NULL);

/*
 * Disallow COPY to/from file or program except to users with the
 * appropriate role.
 */
if (!pipe)
{
    if (stmt->is_program)
    {
        if (!has_privs_of_role(GetUserId(), ROLE_PG_EXECUTE_SERVER_PROGRAM))
            ereport(ERROR,
                    (errcode(ERRCODE_INSUFFICIENT_PRIVILEGE),
                     errmsg("permission denied to COPY to or from an external program"),
                     errdetail("Only roles with privileges of the \"%s\" role may COPY to or from an external program.",
                               "pg_execute_server_program"),
                     errhint("Anyone can COPY to stdout or from stdin. "
                             "psql's \\copy command also works for anyone.")));
    }
    else
    {
        if (is_from && !has_privs_of_role(GetUserId(), ROLE_PG_READ_SERVER_FILES))
            ereport(ERROR,
                    (errcode(ERRCODE_INSUFFICIENT_PRIVILEGE),
                     errmsg("permission denied to COPY from a file"),
                     errdetail("Only roles with privileges of the \"%s\" role may COPY from a file.",
                               "pg_read_server_files"),
                     errhint("Anyone can COPY to stdout or from stdin. "
                             "psql's \\copy command also works for anyone.")));

        if (!is_from && !has_privs_of_role(GetUserId(), ROLE_PG_WRITE_SERVER_FILES))
            ereport(ERROR,
                    (errcode(ERRCODE_INSUFFICIENT_PRIVILEGE),
                     errmsg("permission denied to COPY to a file"),
                     errdetail("Only roles with privileges of the \"%s\" role may COPY to a file.",
                               "pg_write_server_files"),
                     errhint("Anyone can COPY to stdout or from stdin. "
                             "psql's \\copy command also works for anyone.")));
    }
}
```

下一步是对将要导入的数据库表进行准备。对于 `COPY FROM` 来说，需要对表施加 `RowExclusiveLock` 级别的锁。这个级别与其它 DML 所施加的锁等级一致：

```c
LOCKMODE    lockmode = is_from ? RowExclusiveLock : AccessShareLock;

/* Open and lock the relation, using the appropriate lock type. */
rel = table_openrv(stmt->relation, lockmode);
```

如果指定了 `WHERE` 子句，那么还需要将其处理为布尔表达式：

```c
if (stmt->whereClause)
{
    /* add nsitem to query namespace */
    addNSItemToQuery(pstate, nsitem, false, true, true);

    /* Transform the raw expression tree */
    whereClause = transformExpr(pstate, stmt->whereClause, EXPR_KIND_COPY_WHERE);

    /* Make sure it yields a boolean result. */
    whereClause = coerce_to_boolean(pstate, whereClause, "WHERE");

    /* we have to fix its collations too */
    assign_expr_collations(pstate, whereClause);

    whereClause = eval_const_expressions(NULL, whereClause);

    whereClause = (Node *) canonicalize_qual((Expr *) whereClause, false);
    whereClause = (Node *) make_ands_implicit((Expr *) whereClause);
}
```

对于 `COPY FROM` 来说，需要确保对被导入的列具有插入权限。此外，不支持行级别安全策略：

```c
perminfo = nsitem->p_perminfo;
perminfo->requiredPerms = (is_from ? ACL_INSERT : ACL_SELECT);

tupDesc = RelationGetDescr(rel);
attnums = CopyGetAttnums(tupDesc, rel, stmt->attlist);
foreach(cur, attnums)
{
    int         attno;
    Bitmapset **bms;

    attno = lfirst_int(cur) - FirstLowInvalidHeapAttributeNumber;
    bms = is_from ? &perminfo->insertedCols : &perminfo->selectedCols;

    *bms = bms_add_member(*bms, attno);
}
ExecCheckPermissions(pstate->p_rtable, list_make1(perminfo), true);
```

接下来，执行器逻辑开始处理 `COPY FROM` 的具体事宜。与 `COPY TO` 类似，`BeginCopyFrom` / `CopyFrom` / `EndCopyFrom` 三个函数分别对应了三个执行阶段：

1. 准备
2. 执行
3. 结束

```c
if (is_from)
{
    CopyFromState cstate;

    Assert(rel);

    /* check read-only transaction and parallel mode */
    if (XactReadOnly && !rel->rd_islocaltemp)
        PreventCommandIfReadOnly("COPY FROM");

    cstate = BeginCopyFrom(pstate, rel, whereClause,
                           stmt->filename, stmt->is_program,
                           NULL, stmt->attlist, stmt->options);
    *processed = CopyFrom(cstate);  /* copy from file to database */
    EndCopyFrom(cstate);
}
else
{
    /* COPY TO */
}
```

## COPY FROM 准备阶段

`BeginCopyFrom` 完成 `COPY FROM` 的准备工作，主要是初始化一个 `CopyFromState` 结构：

```c
/*
 * This struct contains all the state variables used throughout a COPY FROM
 * operation.
 */
typedef struct CopyFromStateData
{
    /* low-level state data */
    CopySource  copy_src;       /* type of copy source */
    FILE       *copy_file;      /* used if copy_src == COPY_FILE */
    StringInfo  fe_msgbuf;      /* used if copy_src == COPY_FRONTEND */

    EolType     eol_type;       /* EOL type of input */
    int         file_encoding;  /* file or remote side's character encoding */
    bool        need_transcoding;   /* file encoding diff from server? */
    Oid         conversion_proc;    /* encoding conversion function */

    /* parameters from the COPY command */
    Relation    rel;            /* relation to copy from */
    List       *attnumlist;     /* integer list of attnums to copy */
    char       *filename;       /* filename, or NULL for STDIN */
    bool        is_program;     /* is 'filename' a program to popen? */
    copy_data_source_cb data_source_cb; /* function for reading data */

    CopyFormatOptions opts;
    bool       *convert_select_flags;   /* per-column CSV/TEXT CS flags */
    Node       *whereClause;    /* WHERE condition (or NULL) */

    /* these are just for error messages, see CopyFromErrorCallback */
    const char *cur_relname;    /* table name for error messages */
    uint64      cur_lineno;     /* line number for error messages */
    const char *cur_attname;    /* current att for error messages */
    const char *cur_attval;     /* current att value for error messages */
    bool        relname_only;   /* don't output line number, att, etc. */

    /*
     * Working state
     */
    MemoryContext copycontext;  /* per-copy execution context */

    AttrNumber  num_defaults;   /* count of att that are missing and have
                                 * default value */
    FmgrInfo   *in_functions;   /* array of input functions for each attrs */
    Oid        *typioparams;    /* array of element types for in_functions */
    int        *defmap;         /* array of default att numbers related to
                                 * missing att */
    ExprState **defexprs;       /* array of default att expressions for all
                                 * att */
    bool       *defaults;       /* if DEFAULT marker was found for
                                 * corresponding att */
    bool        volatile_defexprs;  /* is any of defexprs volatile? */
    List       *range_table;    /* single element list of RangeTblEntry */
    List       *rteperminfos;   /* single element list of RTEPermissionInfo */
    ExprState  *qualexpr;

    TransitionCaptureState *transition_capture;

    /*
     * These variables are used to reduce overhead in COPY FROM.
     *
     * attribute_buf holds the separated, de-escaped text for each field of
     * the current line.  The CopyReadAttributes functions return arrays of
     * pointers into this buffer.  We avoid palloc/pfree overhead by re-using
     * the buffer on each cycle.
     *
     * In binary COPY FROM, attribute_buf holds the binary data for the
     * current field, but the usage is otherwise similar.
     */
    StringInfoData attribute_buf;

    /* field raw data pointers found by COPY FROM */

    int         max_fields;
    char      **raw_fields;

    /*
     * Similarly, line_buf holds the whole input line being processed. The
     * input cycle is first to read the whole line into line_buf, and then
     * extract the individual attribute fields into attribute_buf.  line_buf
     * is preserved unmodified so that we can display it in error messages if
     * appropriate.  (In binary mode, line_buf is not used.)
     */
    StringInfoData line_buf;
    bool        line_buf_valid; /* contains the row being processed? */

    /*
     * input_buf holds input data, already converted to database encoding.
     *
     * In text mode, CopyReadLine parses this data sufficiently to locate line
     * boundaries, then transfers the data to line_buf. We guarantee that
     * there is a \0 at input_buf[input_buf_len] at all times.  (In binary
     * mode, input_buf is not used.)
     *
     * If encoding conversion is not required, input_buf is not a separate
     * buffer but points directly to raw_buf.  In that case, input_buf_len
     * tracks the number of bytes that have been verified as valid in the
     * database encoding, and raw_buf_len is the total number of bytes stored
     * in the buffer.
     */
#define INPUT_BUF_SIZE 65536    /* we palloc INPUT_BUF_SIZE+1 bytes */
    char       *input_buf;
    int         input_buf_index;    /* next byte to process */
    int         input_buf_len;  /* total # of bytes stored */
    bool        input_reached_eof;  /* true if we reached EOF */
    bool        input_reached_error;    /* true if a conversion error happened */
    /* Shorthand for number of unconsumed bytes available in input_buf */
#define INPUT_BUF_BYTES(cstate) ((cstate)->input_buf_len - (cstate)->input_buf_index)

    /*
     * raw_buf holds raw input data read from the data source (file or client
     * connection), not yet converted to the database encoding.  Like with
     * 'input_buf', we guarantee that there is a \0 at raw_buf[raw_buf_len].
     */
#define RAW_BUF_SIZE 65536      /* we palloc RAW_BUF_SIZE+1 bytes */
    char       *raw_buf;
    int         raw_buf_index;  /* next byte to process */
    int         raw_buf_len;    /* total # of bytes stored */
    bool        raw_reached_eof;    /* true if we reached EOF */

    /* Shorthand for number of unconsumed bytes available in raw_buf */
#define RAW_BUF_BYTES(cstate) ((cstate)->raw_buf_len - (cstate)->raw_buf_index)

    uint64      bytes_processed;    /* number of bytes processed so far */
} CopyFromStateData;

typedef struct CopyFromStateData *CopyFromState;
```

其中具体需要被初始化的结构包括：

- 执行器内存上下文
- 将要被处理的列编号
- 输入格式解析选项
- 输入端的编码格式，已经是否需要转换编码，编码转换函数指针
- 执行状态
- 输入缓冲区及其指针和标志位
  - `raw_buf`：存放从输入端接收到的裸字节
  - `input_buf`：（文本模式下）存放从裸字节经过编码转换以后的字符
  - `line_buf`：（文本模式下）存放一行数据的完整字符
  - `attribute_buf`：存放当前一行数据解除转义以后按列分隔的内容
- 每个列的输入转换函数（将字符串格式转为内部格式）和默认值
- 输入文件描述符
  - 如果来自于客户端，那么向对方发送 `G` 协议，表明要接收的列和格式
  - 如果来自于程序，那么 `popen` 启动程序
  - 如果来自于文件，那么 `open` 打开文件，并 `fstat` 确认文件存在且不是目录

## COPY FROM 执行阶段

`CopyFrom` 函数完成每一行数据的收集和写入，最终返回处理数据的总行数。

### 表类型检查

首先进行的是表类型检查。只有普通表、外部表、分区表，或其它带有 `INSTEAD OF INSERT` 行触发器的目标才可以进行 `COPY FROM`：

```c
/*
 * The target must be a plain, foreign, or partitioned relation, or have
 * an INSTEAD OF INSERT row trigger.  (Currently, such triggers are only
 * allowed on views, so we only hint about them in the view case.)
 */
if (cstate->rel->rd_rel->relkind != RELKIND_RELATION &&
    cstate->rel->rd_rel->relkind != RELKIND_FOREIGN_TABLE &&
    cstate->rel->rd_rel->relkind != RELKIND_PARTITIONED_TABLE &&
    !(cstate->rel->trigdesc &&
      cstate->rel->trigdesc->trig_insert_instead_row))
{
    if (cstate->rel->rd_rel->relkind == RELKIND_VIEW)
        ereport(ERROR,
                (errcode(ERRCODE_WRONG_OBJECT_TYPE),
                 errmsg("cannot copy to view \"%s\"",
                        RelationGetRelationName(cstate->rel)),
                 errhint("To enable copying to a view, provide an INSTEAD OF INSERT trigger.")));
    else if (cstate->rel->rd_rel->relkind == RELKIND_MATVIEW)
        ereport(ERROR,
                (errcode(ERRCODE_WRONG_OBJECT_TYPE),
                 errmsg("cannot copy to materialized view \"%s\"",
                        RelationGetRelationName(cstate->rel))));
    else if (cstate->rel->rd_rel->relkind == RELKIND_SEQUENCE)
        ereport(ERROR,
                (errcode(ERRCODE_WRONG_OBJECT_TYPE),
                 errmsg("cannot copy to sequence \"%s\"",
                        RelationGetRelationName(cstate->rel))));
    else
        ereport(ERROR,
                (errcode(ERRCODE_WRONG_OBJECT_TYPE),
                 errmsg("cannot copy to non-table relation \"%s\"",
                        RelationGetRelationName(cstate->rel))));
}
```

### 元组可见性优化

接下来是对 `INSERT` 标志位的优化。如果被 `COPY FROM` 的目标是当前事务中新建的，那么加上 `TABLE_INSERT_SKIP_FSM`，插入时就不必检查并重用空闲空间了；如果目标是当前子事务中新建的，加上 `TABLE_INSERT_FROZEN` 使插入的行立刻冻结。

### 初始化执行器状态

如果 `COPY FROM` 的目标是一个外表，那么调用 FDW API 的 `BeginForeignInsert` 使外表准备好被插入；如果外表支持批量插入，那么通过 FDW API 的 `GetForeignModifyBatchSize` 获取批量插入的大小，否则默认每次插入一行：

```c
if (resultRelInfo->ri_FdwRoutine != NULL &&
    resultRelInfo->ri_FdwRoutine->BeginForeignInsert != NULL)
    resultRelInfo->ri_FdwRoutine->BeginForeignInsert(mtstate,
                                                     resultRelInfo);

/*
 * Also, if the named relation is a foreign table, determine if the FDW
 * supports batch insert and determine the batch size (a FDW may support
 * batching, but it may be disabled for the server/table).
 *
 * If the FDW does not support batching, we set the batch size to 1.
 */
if (resultRelInfo->ri_FdwRoutine != NULL &&
    resultRelInfo->ri_FdwRoutine->GetForeignModifyBatchSize &&
    resultRelInfo->ri_FdwRoutine->ExecForeignBatchInsert)
    resultRelInfo->ri_BatchSize =
        resultRelInfo->ri_FdwRoutine->GetForeignModifyBatchSize(resultRelInfo);
else
    resultRelInfo->ri_BatchSize = 1;

Assert(resultRelInfo->ri_BatchSize >= 1);
```

### 初始化分区路由

如果 `COPY FROM` 的目标是分区表，那么初始化分区表的元组路由：

```c
/*
 * If the named relation is a partitioned table, initialize state for
 * CopyFrom tuple routing.
 */
if (cstate->rel->rd_rel->relkind == RELKIND_PARTITIONED_TABLE)
    proute = ExecSetupPartitionTupleRouting(estate, cstate->rel);
```

### 初始化过滤条件

如果 `COPY FROM` 指定了 `WHERE` 子句，那么初始化过滤条件：

```c
if (cstate->whereClause)
    cstate->qualexpr = ExecInitQual(castNode(List, cstate->whereClause),
                                    &mtstate->ps);
```

### 批量写入准备

接下来是 **批量写入** 的优化。对于数据库表和外部表的写入，具有两种 AM 接口：

- 单行写入：`table_tuple_insert()` / `ExecForeignInsert`
- 批量写入：`table_multi_insert()` / `ExecForeignBatchInsert`

通常来说，批量写入是更高效的，因为页面锁定频率和 WAL 记录数都更少了。

> 如果表上有索引，那么堆表元组是批量写入的，而索引元组的写入依旧是随机的。这可能会成为影响性能的因素。

不是所有场景下都能安全使用批量写入的，所以接下来要把无法安全使用的场景挑出来：

- 表上有 `BEFORE` 或 `INSTEAD OF` 触发器：因为在插入时会顺带查询表，攒批会导致本应该能查询到的行还未被写入
- 是一个外表，但不支持批量写入，或强制不使用批量写入
- 是一个分区表，并且具有 `INSERT` 触发器
- 表上具有 `VOLATILE` 的默认值表达式：因为该表达式也有可能去查询表
- `WHERE` 子句中带有 `VOLATILE` 函数
- 是一个分区表，但分区中具有不支持批量插入的外部表

对于可以进行批量写入的场景，初始化批量写入需要用到的内存缓冲区和相关指针；否则，初始化单行写入需要用到的结构。

```c
/*
 * It's generally more efficient to prepare a bunch of tuples for
 * insertion, and insert them in one
 * table_multi_insert()/ExecForeignBatchInsert() call, than call
 * table_tuple_insert()/ExecForeignInsert() separately for every tuple.
 * However, there are a number of reasons why we might not be able to do
 * this.  These are explained below.
 */
if (resultRelInfo->ri_TrigDesc != NULL &&
    (resultRelInfo->ri_TrigDesc->trig_insert_before_row ||
     resultRelInfo->ri_TrigDesc->trig_insert_instead_row))
{
    /*
     * Can't support multi-inserts when there are any BEFORE/INSTEAD OF
     * triggers on the table. Such triggers might query the table we're
     * inserting into and act differently if the tuples that have already
     * been processed and prepared for insertion are not there.
     */
    insertMethod = CIM_SINGLE;
}
else if (resultRelInfo->ri_FdwRoutine != NULL &&
         resultRelInfo->ri_BatchSize == 1)
{
    /*
     * Can't support multi-inserts to a foreign table if the FDW does not
     * support batching, or it's disabled for the server or foreign table.
     */
    insertMethod = CIM_SINGLE;
}
else if (proute != NULL && resultRelInfo->ri_TrigDesc != NULL &&
         resultRelInfo->ri_TrigDesc->trig_insert_new_table)
{
    /*
     * For partitioned tables we can't support multi-inserts when there
     * are any statement level insert triggers. It might be possible to
     * allow partitioned tables with such triggers in the future, but for
     * now, CopyMultiInsertInfoFlush expects that any after row insert and
     * statement level insert triggers are on the same relation.
     */
    insertMethod = CIM_SINGLE;
}
else if (cstate->volatile_defexprs)
{
    /*
     * Can't support multi-inserts if there are any volatile default
     * expressions in the table.  Similarly to the trigger case above,
     * such expressions may query the table we're inserting into.
     *
     * Note: It does not matter if any partitions have any volatile
     * default expressions as we use the defaults from the target of the
     * COPY command.
     */
    insertMethod = CIM_SINGLE;
}
else if (contain_volatile_functions(cstate->whereClause))
{
    /*
     * Can't support multi-inserts if there are any volatile function
     * expressions in WHERE clause.  Similarly to the trigger case above,
     * such expressions may query the table we're inserting into.
     */
    insertMethod = CIM_SINGLE;
}
else
{
    /*
     * For partitioned tables, we may still be able to perform bulk
     * inserts.  However, the possibility of this depends on which types
     * of triggers exist on the partition.  We must disable bulk inserts
     * if the partition is a foreign table that can't use batching or it
     * has any before row insert or insert instead triggers (same as we
     * checked above for the parent table).  Since the partition's
     * resultRelInfos are initialized only when we actually need to insert
     * the first tuple into them, we must have the intermediate insert
     * method of CIM_MULTI_CONDITIONAL to flag that we must later
     * determine if we can use bulk-inserts for the partition being
     * inserted into.
     */
    if (proute)
        insertMethod = CIM_MULTI_CONDITIONAL;
    else
        insertMethod = CIM_MULTI;

    CopyMultiInsertInfoInit(&multiInsertInfo, resultRelInfo, cstate,
                            estate, mycid, ti_options);
}

/*
 * If not using batch mode (which allocates slots as needed) set up a
 * tuple slot too. When inserting into a partitioned table, we also need
 * one, even if we might batch insert, to read the tuple in the root
 * partition's form.
 */
if (insertMethod == CIM_SINGLE || insertMethod == CIM_MULTI_CONDITIONAL)
{
    singleslot = table_slot_create(resultRelInfo->ri_RelationDesc,
                                   &estate->es_tupleTable);
    bistate = GetBulkInsertState();
}
```

### 处理每一行输入数据

接下来是处理每一行数据的大循环，循环将会在没有任何数据输入时退出。

首先，不管是单行写入模式还是批量写入模式，都要获取一个用于保存当前元组的槽位。如果是单行写入，那么直接使用刚才调用 `table_slot_create` 创建出来的槽位就可以了，并且后面的每一行也都一直复用这个槽位；如果是批量写入，那么从内存缓冲区里获取一个槽位：

```c
/* select slot to (initially) load row into */
if (insertMethod == CIM_SINGLE || proute)
{
    myslot = singleslot;
    Assert(myslot != NULL);
}
else
{
    Assert(resultRelInfo == target_resultRelInfo);
    Assert(insertMethod == CIM_MULTI);

    myslot = CopyMultiInsertInfoNextFreeSlot(&multiInsertInfo,
                                             resultRelInfo);
}
```

从输入文件描述符中获取一行数据，根据其格式，通过初始化阶段中准备好的转换函数和默认值表达式，转换为数据库内部的元组表示形式（此处省略内部细节），并存储在槽位中：

```c
/* Directly store the values/nulls array in the slot */
if (!NextCopyFrom(cstate, econtext, myslot->tts_values, myslot->tts_isnull))
    break;

ExecStoreVirtualTuple(myslot);

/*
 * Constraints and where clause might reference the tableoid column,
 * so (re-)initialize tts_tableOid before evaluating them.
 */
myslot->tts_tableOid = RelationGetRelid(target_resultRelInfo->ri_RelationDesc);
```

如果指定了 `WHERE` 子句，那么将这行数据根据过滤条件进行判断，略过不符合条件的行，直接进行下轮循环：

```c
if (cstate->whereClause)
{
    econtext->ecxt_scantuple = myslot;
    /* Skip items that don't match COPY's WHERE clause */
    if (!ExecQual(cstate->qualexpr, econtext))
    {
        /*
         * Report that this tuple was filtered out by the WHERE
         * clause.
         */
        pgstat_progress_update_param(PROGRESS_COPY_TUPLES_EXCLUDED,
                                     ++excluded);
        continue;
    }
}
```

如果 `COPY FROM` 的目标是一个分区表，那么接下来需要确认当前元组真正将会被插入的子分区，并确认这个子分区是否可以使用批量写入。如果可以批量写入，而本次要写入的子分区与上一个子分区不同时，需要先把上一个子分区攒批的缓存元组刷入磁盘，然后将当前元组写入槽位。由于子分区和父分区的列编号可能是不一致的，所以需要获取一个 `TupleConversionMap` 结构，该结构能够根据列名称，将子分区和父分区对应同一个列的编号相互映射。在写入槽位时，需要以该映射作为参数，保证数据的正确性。

```c
/* Determine the partition to insert the tuple into */
if (proute)
{
    TupleConversionMap *map;

    /*
     * Attempt to find a partition suitable for this tuple.
     * ExecFindPartition() will raise an error if none can be found or
     * if the found partition is not suitable for INSERTs.
     */
    resultRelInfo = ExecFindPartition(mtstate, target_resultRelInfo,
                                      proute, myslot, estate);

    if (prevResultRelInfo != resultRelInfo)
    {
        /* Determine which triggers exist on this partition */
        has_before_insert_row_trig = (resultRelInfo->ri_TrigDesc &&
                                      resultRelInfo->ri_TrigDesc->trig_insert_before_row);

        has_instead_insert_row_trig = (resultRelInfo->ri_TrigDesc &&
                                       resultRelInfo->ri_TrigDesc->trig_insert_instead_row);

        /*
         * Disable multi-inserts when the partition has BEFORE/INSTEAD
         * OF triggers, or if the partition is a foreign table that
         * can't use batching.
         */
        leafpart_use_multi_insert = insertMethod == CIM_MULTI_CONDITIONAL &&
            !has_before_insert_row_trig &&
            !has_instead_insert_row_trig &&
            (resultRelInfo->ri_FdwRoutine == NULL ||
             resultRelInfo->ri_BatchSize > 1);

        /* Set the multi-insert buffer to use for this partition. */
        if (leafpart_use_multi_insert)
        {
            if (resultRelInfo->ri_CopyMultiInsertBuffer == NULL)
                CopyMultiInsertInfoSetupBuffer(&multiInsertInfo,
                                               resultRelInfo);
        }
        else if (insertMethod == CIM_MULTI_CONDITIONAL &&
                 !CopyMultiInsertInfoIsEmpty(&multiInsertInfo))
        {
            /*
             * Flush pending inserts if this partition can't use
             * batching, so rows are visible to triggers etc.
             */
            CopyMultiInsertInfoFlush(&multiInsertInfo,
                                     resultRelInfo,
                                     &processed);
        }

        if (bistate != NULL)
            ReleaseBulkInsertStatePin(bistate);
        prevResultRelInfo = resultRelInfo;
    }

    /*
     * If we're capturing transition tuples, we might need to convert
     * from the partition rowtype to root rowtype. But if there are no
     * BEFORE triggers on the partition that could change the tuple,
     * we can just remember the original unconverted tuple to avoid a
     * needless round trip conversion.
     */
    if (cstate->transition_capture != NULL)
        cstate->transition_capture->tcs_original_insert_tuple =
            !has_before_insert_row_trig ? myslot : NULL;

    /*
     * We might need to convert from the root rowtype to the partition
     * rowtype.
     */
    map = ExecGetRootToChildMap(resultRelInfo, estate);
    if (insertMethod == CIM_SINGLE || !leafpart_use_multi_insert)
    {
        /* non batch insert */
        if (map != NULL)
        {
            TupleTableSlot *new_slot;

            new_slot = resultRelInfo->ri_PartitionTupleSlot;
            myslot = execute_attr_map_slot(map->attrMap, myslot, new_slot);
        }
    }
    else
    {
        /*
         * Prepare to queue up tuple for later batch insert into
         * current partition.
         */
        TupleTableSlot *batchslot;

        /* no other path available for partitioned table */
        Assert(insertMethod == CIM_MULTI_CONDITIONAL);

        batchslot = CopyMultiInsertInfoNextFreeSlot(&multiInsertInfo,
                                                    resultRelInfo);

        if (map != NULL)
            myslot = execute_attr_map_slot(map->attrMap, myslot,
                                           batchslot);
        else
        {
            /*
             * This looks more expensive than it is (Believe me, I
             * optimized it away. Twice.). The input is in virtual
             * form, and we'll materialize the slot below - for most
             * slot types the copy performs the work materialization
             * would later require anyway.
             */
            ExecCopySlot(batchslot, myslot);
            myslot = batchslot;
        }
    }

    /* ensure that triggers etc see the right relation  */
    myslot->tts_tableOid = RelationGetRelid(resultRelInfo->ri_RelationDesc);
}
```

最后终于到了完成写入的环节：

- 如果表上有 `BEFORE ROW INSERT` 触发器，那么先执行一遍，如果执行的结果是 do nothing，就直接跳过写入
- 如果表上有 `INSTEAD OF INSERT ROW` 触发器，那么把这个元组交给触发器处理

然后进行一些写入前检查：

- 计算生成列的列值
- 检查元组是否符合表上的约束
- 检查元组是否符合分区约束

根据当前元组是单行写入还是批量写入，将元组写入 AM 或内存缓冲区中。如果表上有索引，还需要创建并插入相应的索引元组。最后调用 `AFTER ROW INSERT` 触发器。

```c
skip_tuple = false;

/* BEFORE ROW INSERT Triggers */
if (has_before_insert_row_trig)
{
    if (!ExecBRInsertTriggers(estate, resultRelInfo, myslot))
        skip_tuple = true;  /* "do nothing" */
}

if (!skip_tuple)
{
    /*
     * If there is an INSTEAD OF INSERT ROW trigger, let it handle the
     * tuple.  Otherwise, proceed with inserting the tuple into the
     * table or foreign table.
     */
    if (has_instead_insert_row_trig)
    {
        ExecIRInsertTriggers(estate, resultRelInfo, myslot);
    }
    else
    {
        /* Compute stored generated columns */
        if (resultRelInfo->ri_RelationDesc->rd_att->constr &&
            resultRelInfo->ri_RelationDesc->rd_att->constr->has_generated_stored)
            ExecComputeStoredGenerated(resultRelInfo, estate, myslot,
                                       CMD_INSERT);

        /*
         * If the target is a plain table, check the constraints of
         * the tuple.
         */
        if (resultRelInfo->ri_FdwRoutine == NULL &&
            resultRelInfo->ri_RelationDesc->rd_att->constr)
            ExecConstraints(resultRelInfo, myslot, estate);

        /*
         * Also check the tuple against the partition constraint, if
         * there is one; except that if we got here via tuple-routing,
         * we don't need to if there's no BR trigger defined on the
         * partition.
         */
        if (resultRelInfo->ri_RelationDesc->rd_rel->relispartition &&
            (proute == NULL || has_before_insert_row_trig))
            ExecPartitionCheck(resultRelInfo, myslot, estate, true);

        /* Store the slot in the multi-insert buffer, when enabled. */
        if (insertMethod == CIM_MULTI || leafpart_use_multi_insert)
        {
            /*
             * The slot previously might point into the per-tuple
             * context. For batching it needs to be longer lived.
             */
            ExecMaterializeSlot(myslot);

            /* Add this tuple to the tuple buffer */
            CopyMultiInsertInfoStore(&multiInsertInfo,
                                     resultRelInfo, myslot,
                                     cstate->line_buf.len,
                                     cstate->cur_lineno);

            /*
             * If enough inserts have queued up, then flush all
             * buffers out to their tables.
             */
            if (CopyMultiInsertInfoIsFull(&multiInsertInfo))
                CopyMultiInsertInfoFlush(&multiInsertInfo,
                                         resultRelInfo,
                                         &processed);

            /*
             * We delay updating the row counter and progress of the
             * COPY command until after writing the tuples stored in
             * the buffer out to the table, as in single insert mode.
             * See CopyMultiInsertBufferFlush().
             */
            continue;   /* next tuple please */
        }
        else
        {
            List       *recheckIndexes = NIL;

            /* OK, store the tuple */
            if (resultRelInfo->ri_FdwRoutine != NULL)
            {
                myslot = resultRelInfo->ri_FdwRoutine->ExecForeignInsert(estate,
                                                                         resultRelInfo,
                                                                         myslot,
                                                                         NULL);

                if (myslot == NULL) /* "do nothing" */
                    continue;   /* next tuple please */

                /*
                 * AFTER ROW Triggers might reference the tableoid
                 * column, so (re-)initialize tts_tableOid before
                 * evaluating them.
                 */
                myslot->tts_tableOid = RelationGetRelid(resultRelInfo->ri_RelationDesc);
            }
            else
            {
                /* OK, store the tuple and create index entries for it */
                table_tuple_insert(resultRelInfo->ri_RelationDesc,
                                   myslot, mycid, ti_options, bistate);

                if (resultRelInfo->ri_NumIndices > 0)
                    recheckIndexes = ExecInsertIndexTuples(resultRelInfo,
                                                           myslot,
                                                           estate,
                                                           false,
                                                           false,
                                                           NULL,
                                                           NIL,
                                                           false);
            }

            /* AFTER ROW INSERT Triggers */
            ExecARInsertTriggers(estate, resultRelInfo, myslot,
                                 recheckIndexes, cstate->transition_capture);

            list_free(recheckIndexes);
        }
    }

    /*
     * We count only tuples not suppressed by a BEFORE INSERT trigger
     * or FDW; this is the same definition used by nodeModifyTable.c
     * for counting tuples inserted by an INSERT command.  Update
     * progress of the COPY command as well.
     */
    pgstat_progress_update_param(PROGRESS_COPY_TUPLES_PROCESSED,
                                 ++processed);
}
```

### 后处理

此时大循环的执行已经结束，这意味着所有的元组已经被处理。接下来进行一些后处理，最重要的是将最后一批在内存中缓存的元组刷下去：

```c
/* Flush any remaining buffered tuples */
if (insertMethod != CIM_SINGLE)
{
    if (!CopyMultiInsertInfoIsEmpty(&multiInsertInfo))
        CopyMultiInsertInfoFlush(&multiInsertInfo, NULL, &processed);
}
```

## COPY FROM 结束阶段

`EndCopyFrom` 完成 `COPY FROM` 的收尾清理工作。主要是关闭文件描述符，并销毁内存上下文：

```c
/*
 * Clean up storage and release resources for COPY FROM.
 */
void
EndCopyFrom(CopyFromState cstate)
{
    /* No COPY FROM related resources except memory. */
    if (cstate->is_program)
    {
        ClosePipeFromProgram(cstate);
    }
    else
    {
        if (cstate->filename != NULL && FreeFile(cstate->copy_file))
            ereport(ERROR,
                    (errcode_for_file_access(),
                     errmsg("could not close file \"%s\": %m",
                            cstate->filename)));
    }

    pgstat_progress_end_command();

    MemoryContextDelete(cstate->copycontext);
    pfree(cstate);
}
```

## References

[PostgreSQL Documentation: COPY](https://www.postgresql.org/docs/current/sql-copy.html)
