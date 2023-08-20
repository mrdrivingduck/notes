# PostgreSQL - COPY TO

Created by : Mr Dk.

2023 / 08 / 20 13:20

Hangzhou, Zhejiang, China

---

## Background

在 PostgreSQL 中，`COPY TO` 语法被用于将表数据导出到文件中。导出到 _文件_ 是 PG 官方文档的说法，我个人认为实际上是导出到各式各样的 **流** 中。因为导出的目标端可以是文件，也可以是标准输出，还可以是另一个进程（这意味着使用了管道）。在这个过程中，需要处理查询优化与执行、输出格式序列化、编码等很多复杂的问题。本文基于当前 PostgreSQL 主干开发分支源码（PostgreSQL 16 under devel）对这个过程进行分析：

```
commit a2a6249cf1a4210caac534e8454a1614d0dd081a
Author: Andres Freund <andres@anarazel.de>
Date:   Sat Aug 19 12:40:45 2023 -0700

    ci: macos: use cached macports install

    A significant chunk of the time on the macos CI task is spent installing
    packages using homebrew. The downloads of the packages are cached, but the
    installation needs to happen every time. We can't cache the whole homebrew
    installation, because it is too large due to pre-installed packages.

    Speed this up by installing packages using macports and caching the
    installation as .dmg. That's a lot faster than unpacking a tarball.

    In addition, don't install llvm - it wasn't enabled when building, so it's
    just a waste of time/space.

    This substantially speeds up the mac CI time, both in the cold cache and in
    the warm cache case (the latter from ~1m20s to ~5s).

    It doesn't seem great to have diverging sources of packages for CI between
    branches, so backpatch to 15 (where CI was added).

    Discussion: https://postgr.es/m/20230805202539.r3umyamsnctysdc7@awork3.anarazel.de
    Backpatch: 15-, where CI was added
```

## Copy Statement

从定义上来说，`COPY` 语法算是一种 DDL。所以是由执行器的 `standard_ProcessUtility` 函数进行处理的：

```c
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
    /* ... */

    switch (nodeTag(parsetree))
    {
        /* ... */

        case T_CopyStmt:
            {
                uint64      processed;

                DoCopy(pstate, (CopyStmt *) parsetree,
                       pstmt->stmt_location, pstmt->stmt_len,
                       &processed);
                if (qc)
                    SetQueryCompletion(qc, CMDTAG_COPY, processed);
            }
            break;

        /* ... */
    }

    /* ... */
}
```

在执行器开始处理之前，语法解析器已经把与 `COPY` 相关的参数设置在 `CopyStmt` 结构中了。其中：

- `relation`：将要被导出的表
- `query`：导出数据所用的查询（`COPY` 也支持通过查询导出数据）
- `attlist`：将要导出的列名列表
- `is_from`：当前执行的是 `COPY TO` 还是 `COPY FROM`
- `is_program`：导出的目标端是否是一个进程（管道）
- `filename`：导出目标端的文件名/程序名（为 `NULL` 意味着导出至 `STDOUT`）
- `options`：保存导出过程中的选项

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

进入到 `DoCopy` 函数后，需要进行初步的权限检查。首先需要做判断的是导出到文件/进程的情况。如果是导出到文件，那么当前用户需要有写文件的权限；如果是导出到程序，那么当前用户需要有执行程序的权限：

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

下一步是对将要导出的数据来源进行准备：

1. 如果数据的来源是表，那么需要对表上锁；对于 `COPY TO` 来说，`AccessShareLock` 已经足够；接着检查列权限和行安全策略权限
2. 如果数据的来源是查询，那么将查询构造为语法树节点以备后续使用

上述所有逻辑是 `COPY TO` 和 `COPY FROM` 两种语法共用的。接下来，执行器逻辑开始对这两种语法做区分处理了。对于 `COPY TO` 来说，`BeginCopyTo` / `DoCopyTo` / `EndCopyTo` 三个函数分别对应了三个执行阶段：

1. 准备
2. 执行
3. 结束

```c
if (is_from)
{
    /* COPY FROM */
}
else
{
    CopyToState cstate;

    cstate = BeginCopyTo(pstate, rel, query, relid,
                         stmt->filename, stmt->is_program,
                         NULL, stmt->attlist, stmt->options);
    *processed = DoCopyTo(cstate);  /* copy from database to file */
    EndCopyTo(cstate);
}
```

## COPY TO 准备阶段

整个 `BeginCopyTo` 函数实际上都是在初始化一个 `CopyToState` 结构。该结构保存了后续 `COPY TO` 执行阶段所需要用到的所有东西：

- 用于导出数据的文件描述符
- 每行数据的序列化缓冲区
- 编码相关信息
- 每个列的序列化函数
- 内存上下文
- 统计信息

```c
/*
 * This struct contains all the state variables used throughout a COPY TO
 * operation.
 *
 * Multi-byte encodings: all supported client-side encodings encode multi-byte
 * characters by having the first byte's high bit set. Subsequent bytes of the
 * character can have the high bit not set. When scanning data in such an
 * encoding to look for a match to a single-byte (ie ASCII) character, we must
 * use the full pg_encoding_mblen() machinery to skip over multibyte
 * characters, else we might find a false match to a trailing byte. In
 * supported server encodings, there is no possibility of a false match, and
 * it's faster to make useless comparisons to trailing bytes than it is to
 * invoke pg_encoding_mblen() to skip over them. encoding_embeds_ascii is true
 * when we have to do it the hard way.
 */
typedef struct CopyToStateData
{
    /* low-level state data */
    CopyDest    copy_dest;      /* type of copy source/destination */
    FILE       *copy_file;      /* used if copy_dest == COPY_FILE */
    StringInfo  fe_msgbuf;      /* used for all dests during COPY TO */

    int         file_encoding;  /* file or remote side's character encoding */
    bool        need_transcoding;   /* file encoding diff from server? */
    bool        encoding_embeds_ascii;  /* ASCII can be non-first byte? */

    /* parameters from the COPY command */
    Relation    rel;            /* relation to copy to */
    QueryDesc  *queryDesc;      /* executable query to copy from */
    List       *attnumlist;     /* integer list of attnums to copy */
    char       *filename;       /* filename, or NULL for STDOUT */
    bool        is_program;     /* is 'filename' a program to popen? */
    copy_data_dest_cb data_dest_cb; /* function for writing data */

    CopyFormatOptions opts;
    Node       *whereClause;    /* WHERE condition (or NULL) */

    /*
     * Working state
     */
    MemoryContext copycontext;  /* per-copy execution context */

    FmgrInfo   *out_functions;  /* lookup info for output functions */
    MemoryContext rowcontext;   /* per-row evaluation context */
    uint64      bytes_processed;    /* number of bytes processed so far */
} CopyToStateData;
```

首先，拒绝掉除普通表以外的所有对象类型的 **直接导出**。诸如分区表、视图等其它类型的对象只能通过查询进行导出：

```c
if (rel != NULL && rel->rd_rel->relkind != RELKIND_RELATION)
{
    if (rel->rd_rel->relkind == RELKIND_VIEW)
        ereport(ERROR,
                (errcode(ERRCODE_WRONG_OBJECT_TYPE),
                 errmsg("cannot copy from view \"%s\"",
                        RelationGetRelationName(rel)),
                 errhint("Try the COPY (SELECT ...) TO variant.")));
    /* ... */
}
```

然后分配好 `CopyToState` 的内存及其相关的内存上下文，开始初始化。通过 `ProcessCopyOptions` 函数解析所有的导出选项：

- 导出格式：`text` / `csv` / `binary`
- 是否允许 `NULL` 值、转义字符、默认值、分隔符
- 编码

```c
/* Allocate workspace and zero all fields */
cstate = (CopyToStateData *) palloc0(sizeof(CopyToStateData));

/*
 * We allocate everything used by a cstate in a new memory context. This
 * avoids memory leaks during repeated use of COPY in a query.
 */
cstate->copycontext = AllocSetContextCreate(CurrentMemoryContext,
                                            "COPY",
                                            ALLOCSET_DEFAULT_SIZES);

oldcontext = MemoryContextSwitchTo(cstate->copycontext);

/* Extract options from the statement node tree */
ProcessCopyOptions(pstate, &cstate->opts, false /* is_from */ , options);
```

如果导出的数据来源不是表而是查询，那么需要解析并重写这条查询，然后把这条查询输入优化器得到执行计划，把执行计划输入执行器，完成执行器初始化。查询只允许 `SELECT` 语句，或带有 `RETURNING` 子句的 DML。（不然你还导出个啥？）

```c
/* Process the source/target relation or query */
if (rel)
{
    Assert(!raw_query);

    cstate->rel = rel;

    tupDesc = RelationGetDescr(cstate->rel);
}
else
{
    /* ... */

    /*
     * Run parse analysis and rewrite.  Note this also acquires sufficient
     * locks on the source table(s).
     */
    rewritten = pg_analyze_and_rewrite_fixedparams(raw_query,
                                                   pstate->p_sourcetext, NULL, 0,
                                                   NULL);

    /* check that we got back something we can work with */
    if (rewritten == NIL)
    {
        ereport(ERROR,
                (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                 errmsg("DO INSTEAD NOTHING rules are not supported for COPY")));
    }
    else if (list_length(rewritten) > 1)
    {
        ListCell   *lc;

        /* examine queries to determine which error message to issue */
        foreach(lc, rewritten)
        {
            Query      *q = lfirst_node(Query, lc);

            if (q->querySource == QSRC_QUAL_INSTEAD_RULE)
                ereport(ERROR,
                        (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                         errmsg("conditional DO INSTEAD rules are not supported for COPY")));
            if (q->querySource == QSRC_NON_INSTEAD_RULE)
                ereport(ERROR,
                        (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                         errmsg("DO ALSO rules are not supported for the COPY")));
        }

        ereport(ERROR,
                (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                 errmsg("multi-statement DO INSTEAD rules are not supported for COPY")));
    }

    query = linitial_node(Query, rewritten);

    /* The grammar allows SELECT INTO, but we don't support that */
    if (query->utilityStmt != NULL &&
        IsA(query->utilityStmt, CreateTableAsStmt))
        ereport(ERROR,
                (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                 errmsg("COPY (SELECT INTO) is not supported")));

    Assert(query->utilityStmt == NULL);

    /*
     * Similarly the grammar doesn't enforce the presence of a RETURNING
     * clause, but this is required here.
     */
    if (query->commandType != CMD_SELECT &&
        query->returningList == NIL)
    {
        Assert(query->commandType == CMD_INSERT ||
               query->commandType == CMD_UPDATE ||
               query->commandType == CMD_DELETE);

        ereport(ERROR,
                (errcode(ERRCODE_FEATURE_NOT_SUPPORTED),
                 errmsg("COPY query must have a RETURNING clause")));
    }

    /* plan the query */
    plan = pg_plan_query(query, pstate->p_sourcetext,
                         CURSOR_OPT_PARALLEL_OK, NULL);

    /* ... */

    /*
     * Use a snapshot with an updated command ID to ensure this query sees
     * results of any previously executed queries.
     */
    PushCopiedSnapshot(GetActiveSnapshot());
    UpdateActiveSnapshotCommandId();

    /* Create dest receiver for COPY OUT */
    dest = CreateDestReceiver(DestCopyOut);
    ((DR_copy *) dest)->cstate = cstate;

    /* Create a QueryDesc requesting no output */
    cstate->queryDesc = CreateQueryDesc(plan, pstate->p_sourcetext,
                                        GetActiveSnapshot(),
                                        InvalidSnapshot,
                                        dest, NULL, NULL, 0);

    /*
     * Call ExecutorStart to prepare the plan for execution.
     *
     * ExecutorStart computes a result tupdesc for us
     */
    ExecutorStart(cstate->queryDesc, 0);

    tupDesc = cstate->queryDesc->tupDesc;
}
```

在调用优化器的入口函数时，传入了 `CURSOR_OPT_PARALLEL_OK` 参数。这意味着在条件允许的情况下，优化器可以生成并行执行计划加速扫描。

另外，上述代码通过 `CreateDestReceiver` 调用 `CreateCopyDestReceiver` 注册好 `COPY TO` 专用的执行器回调函数。这会被后续的执行阶段使用到：

```c
/*
 * CreateCopyDestReceiver -- create a suitable DestReceiver object
 */
DestReceiver *
CreateCopyDestReceiver(void)
{
    DR_copy    *self = (DR_copy *) palloc(sizeof(DR_copy));

    self->pub.receiveSlot = copy_dest_receive;
    self->pub.rStartup = copy_dest_startup;
    self->pub.rShutdown = copy_dest_shutdown;
    self->pub.rDestroy = copy_dest_destroy;
    self->pub.mydest = DestCopyOut;

    self->cstate = NULL;        /* will be set later */
    self->processed = 0;

    return (DestReceiver *) self;
}
```

接下来，根据要导出的列，处理每一个列的转义、编码等信息。最后，根据要导出的目标端做相应的准备：

- 如果导出到一个回调函数，那么准备好这个回调函数
- 如果导出到 `STDOUT`，那么就设置好相应的文件描述符
- 如果导出到一个程序，那么通过 `popen` 启动相应的程序，并创建好 I/O 管道
- 如果导出到一个文件，那么通过 `fopen` 打开文件，并通过 `fstat` 确认文件的合法性

```c
if (data_dest_cb)
{
    progress_vals[1] = PROGRESS_COPY_TYPE_CALLBACK;
    cstate->copy_dest = COPY_CALLBACK;
    cstate->data_dest_cb = data_dest_cb;
}
else if (pipe)
{
    progress_vals[1] = PROGRESS_COPY_TYPE_PIPE;

    Assert(!is_program);    /* the grammar does not allow this */
    if (whereToSendOutput != DestRemote)
        cstate->copy_file = stdout;
}
else
{
    cstate->filename = pstrdup(filename);
    cstate->is_program = is_program;

    if (is_program)
    {
        progress_vals[1] = PROGRESS_COPY_TYPE_PROGRAM;
        cstate->copy_file = OpenPipeStream(cstate->filename, PG_BINARY_W);
        if (cstate->copy_file == NULL)
            ereport(ERROR,
                    (errcode_for_file_access(),
                     errmsg("could not execute command \"%s\": %m",
                            cstate->filename)));
    }
    else
    {
        mode_t      oumask; /* Pre-existing umask value */
        struct stat st;

        progress_vals[1] = PROGRESS_COPY_TYPE_FILE;

        /*
         * Prevent write to relative path ... too easy to shoot oneself in
         * the foot by overwriting a database file ...
         */
        if (!is_absolute_path(filename))
            ereport(ERROR,
                    (errcode(ERRCODE_INVALID_NAME),
                     errmsg("relative path not allowed for COPY to file")));

        oumask = umask(S_IWGRP | S_IWOTH);
        PG_TRY();
        {
            cstate->copy_file = AllocateFile(cstate->filename, PG_BINARY_W);
        }
        PG_FINALLY();
        {
            umask(oumask);
        }
        PG_END_TRY();
        if (cstate->copy_file == NULL)
        {
            /* copy errno because ereport subfunctions might change it */
            int         save_errno = errno;

            ereport(ERROR,
                    (errcode_for_file_access(),
                     errmsg("could not open file \"%s\" for writing: %m",
                            cstate->filename),
                     (save_errno == ENOENT || save_errno == EACCES) ?
                     errhint("COPY TO instructs the PostgreSQL server process to write a file. "
                             "You may want a client-side facility such as psql's \\copy.") : 0));
        }

        if (fstat(fileno(cstate->copy_file), &st))
            ereport(ERROR,
                    (errcode_for_file_access(),
                     errmsg("could not stat file \"%s\": %m",
                            cstate->filename)));

        if (S_ISDIR(st.st_mode))
            ereport(ERROR,
                    (errcode(ERRCODE_WRONG_OBJECT_TYPE),
                     errmsg("\"%s\" is a directory", cstate->filename)));
    }
}
```

## COPY TO 执行阶段

`DoCopyTo` 函数不断从数据源取出数据，并写出到已经初始化完毕的目标端中。

首先，对于导出到 `STDOUT` 的情况，PostgreSQL 会直接认为接收端是一个实现了 [pq 协议](https://www.postgresql.org/docs/current/protocol.html) 的前端。根据协议，首先需要发送 `COPY` 开始的消息：

```c
bool        pipe = (cstate->filename == NULL && cstate->data_dest_cb == NULL);
bool        fe_copy = (pipe && whereToSendOutput == DestRemote);

if (fe_copy)
    SendCopyBegin(cstate);
```

接下来，获取要导出的每一个列，初始化每一个列的序列化函数。根据要导出的格式，选择使用二进制序列化函数还是字符串序列化函数：

```c
if (cstate->rel)
    tupDesc = RelationGetDescr(cstate->rel);
else
    tupDesc = cstate->queryDesc->tupDesc;
num_phys_attrs = tupDesc->natts;
cstate->opts.null_print_client = cstate->opts.null_print;   /* default */

/* We use fe_msgbuf as a per-row buffer regardless of copy_dest */
cstate->fe_msgbuf = makeStringInfo();

/* Get info about the columns we need to process. */
cstate->out_functions = (FmgrInfo *) palloc(num_phys_attrs * sizeof(FmgrInfo));
foreach(cur, cstate->attnumlist)
{
    int         attnum = lfirst_int(cur);
    Oid         out_func_oid;
    bool        isvarlena;
    Form_pg_attribute attr = TupleDescAttr(tupDesc, attnum - 1);

    if (cstate->opts.binary)
        getTypeBinaryOutputInfo(attr->atttypid,
                                &out_func_oid,
                                &isvarlena);
    else
        getTypeOutputInfo(attr->atttypid,
                          &out_func_oid,
                          &isvarlena);
    fmgr_info(out_func_oid, &cstate->out_functions[attnum - 1]);
}
```

如果导出格式为二进制，那么需要向输出流中写入签名、标志位等信息；如果导出格式为字符串，那么根据导出的是 `text` 格式还是 `csv` 格式，可选地向输出流中写入 header 等信息：

```c
if (cstate->opts.binary)
{
    /* Generate header for a binary copy */
    int32       tmp;

    /* Signature */
    CopySendData(cstate, BinarySignature, 11);
    /* Flags field */
    tmp = 0;
    CopySendInt32(cstate, tmp);
    /* No header extension */
    tmp = 0;
    CopySendInt32(cstate, tmp);
}
else
{
    /*
     * For non-binary copy, we need to convert null_print to file
     * encoding, because it will be sent directly with CopySendString.
     */
    if (cstate->need_transcoding)
        cstate->opts.null_print_client = pg_server_to_any(cstate->opts.null_print,
                                                          cstate->opts.null_print_len,
                                                          cstate->file_encoding);

    /* if a header has been requested send the line */
    if (cstate->opts.header_line)
    {
        bool        hdr_delim = false;

        foreach(cur, cstate->attnumlist)
        {
            int         attnum = lfirst_int(cur);
            char       *colname;

            if (hdr_delim)
                CopySendChar(cstate, cstate->opts.delim[0]);
            hdr_delim = true;

            colname = NameStr(TupleDescAttr(tupDesc, attnum - 1)->attname);

            if (cstate->opts.csv_mode)
                CopyAttributeOutCSV(cstate, colname, false,
                                    list_length(cstate->attnumlist) == 1);
            else
                CopyAttributeOutText(cstate, colname);
        }

        CopySendEndOfRow(cstate);
    }
}
```

如果导出的来源是裸表，那么调用表的 Access Method 接口不断从表中取出一行数据，序列化并发送；如果导出的来源是查询，那么直接让执行器进入执行阶段。

```c
if (cstate->rel)
{
    TupleTableSlot *slot;
    TableScanDesc scandesc;

    scandesc = table_beginscan(cstate->rel, GetActiveSnapshot(), 0, NULL);
    slot = table_slot_create(cstate->rel, NULL);

    processed = 0;
    while (table_scan_getnextslot(scandesc, ForwardScanDirection, slot))
    {
        CHECK_FOR_INTERRUPTS();

        /* Deconstruct the tuple ... */
        slot_getallattrs(slot);

        /* Format and send the data */
        CopyOneRowTo(cstate, slot);

        /*
         * Increment the number of processed tuples, and report the
         * progress.
         */
        pgstat_progress_update_param(PROGRESS_COPY_TUPLES_PROCESSED,
                                        ++processed);
    }

    ExecDropSingleTupleTableSlot(slot);
    table_endscan(scandesc);
}
else
{
    /* run the plan --- the dest receiver will send tuples */
    ExecutorRun(cstate->queryDesc, ForwardScanDirection, 0, true);
    processed = ((DR_copy *) cstate->queryDesc->dest)->processed;
}
```

执行器在执行阶段会通过回调 `copy_dest_receive` 函数完成每一行数据的序列化和发送：

```c
/*
 * copy_dest_receive --- receive one tuple
 */
static bool
copy_dest_receive(TupleTableSlot *slot, DestReceiver *self)
{
    DR_copy    *myState = (DR_copy *) self;
    CopyToState cstate = myState->cstate;

    /* Send the data */
    CopyOneRowTo(cstate, slot);

    /* Increment the number of processed tuples, and report the progress */
    pgstat_progress_update_param(PROGRESS_COPY_TUPLES_PROCESSED,
                                 ++myState->processed);

    return true;
}
```

所有数据行都写出后，如果导出格式为二进制，那么还需要额外写入尾部消息：

```c
if (cstate->opts.binary)
{
    /* Generate trailer for a binary copy */
    CopySendInt16(cstate, -1);
    /* Need to flush out the trailer */
    CopySendEndOfRow(cstate);
}
```

如果导出的目标端是 `STDOUT`，那么根据 pq 协议还需要写入结束消息：

```c
if (fe_copy)
    SendCopyEnd(cstate);
```

至此，`COPY` 执行阶段结束，返回导出的数据行数。

### COPY TO 结束阶段

结束阶段相对来说简单直接一些。如果使用了执行器，那就让执行器进入清理和结束阶段；如果导出到程序，则关闭管道；如果导出到文件，则关闭文件：

```c
/*
 * Clean up storage and release resources for COPY TO.
 */
void
EndCopyTo(CopyToState cstate)
{
    if (cstate->queryDesc != NULL)
    {
        /* Close down the query and free resources. */
        ExecutorFinish(cstate->queryDesc);
        ExecutorEnd(cstate->queryDesc);
        FreeQueryDesc(cstate->queryDesc);
        PopActiveSnapshot();
    }

    /* Clean up storage */
    EndCopy(cstate);
}

/*
 * Release resources allocated in a cstate for COPY TO/FROM.
 */
static void
EndCopy(CopyToState cstate)
{
    if (cstate->is_program)
    {
        ClosePipeToProgram(cstate);
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
