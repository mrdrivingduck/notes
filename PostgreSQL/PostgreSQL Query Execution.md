# PostgreSQL - Query Execution

Created by : Mr Dk.

2021 / 06 / 20 22:12

Hangzhou, Zhejiang, China

---

周日，带着电脑去了公司。从流程和数据结构的角度分析一下 PostgreSQL 执行器的大致工作过程。查询计划的具体物理执行留作后续分析。

## Portal

经过查询编译器的工作，用户提交的 SQL 语句已经成为 **查询计划**。接下来，由执行器根据计划对数据进行提取、处理、存储等。在函数 `exec_simple_query()` 中，在 SQL 被编译为 parse tree 后，依次调用以下几个函数完成 SQL 语句的 **执行**：

- `CreatePortal()`：创建一个干净的 `Portal`，初始化内存上下文
- `PortalDefineQuery()`：将查询编译器输出的查询计划初始化到 `Portal` 中
- `PortalStart()`：为 `Portal` 选择执行策略，并进行与执行策略相关的初始化 (描述符)
- `PortalRun()`：根据执行策略调用执行部件，执行计划
- `PortalDrop()`：清理/释放资源

其中，`Portal` 是核心的数据结构。定义如下：

```c
typedef struct PortalData *Portal;

typedef struct PortalData
{
    /* Bookkeeping data */
    const char *name;           /* portal's name */
    const char *prepStmtName;   /* source prepared statement (NULL if none) */
    MemoryContext portalContext;    /* subsidiary memory for portal */
    ResourceOwner resowner;     /* resources owned by portal */
    void        (*cleanup) (Portal portal); /* cleanup hook */

    /*
     * State data for remembering which subtransaction(s) the portal was
     * created or used in.  If the portal is held over from a previous
     * transaction, both subxids are InvalidSubTransactionId.  Otherwise,
     * createSubid is the creating subxact and activeSubid is the last subxact
     * in which we ran the portal.
     */
    SubTransactionId createSubid;   /* the creating subxact */
    SubTransactionId activeSubid;   /* the last subxact with activity */

    /* The query or queries the portal will execute */
    const char *sourceText;     /* text of query (as of 8.4, never NULL) */
    CommandTag  commandTag;     /* command tag for original query */
    QueryCompletion qc;         /* command completion data for executed query */
    List       *stmts;          /* list of PlannedStmts */
    CachedPlan *cplan;          /* CachedPlan, if stmts are from one */

    ParamListInfo portalParams; /* params to pass to query */
    QueryEnvironment *queryEnv; /* environment for query */

    /* Features/options */
    PortalStrategy strategy;    /* see above */
    int         cursorOptions;  /* DECLARE CURSOR option bits */
    bool        run_once;       /* portal will only be run once */

    /* Status data */
    PortalStatus status;        /* see above */
    bool        portalPinned;   /* a pinned portal can't be dropped */
    bool        autoHeld;       /* was automatically converted from pinned to
                                 * held (see HoldPinnedPortals()) */

    /* If not NULL, Executor is active; call ExecutorEnd eventually: */
    QueryDesc  *queryDesc;      /* info needed for executor invocation */

    /* If portal returns tuples, this is their tupdesc: */
    TupleDesc   tupDesc;        /* descriptor for result tuples */
    /* and these are the format codes to use for the columns: */
    int16      *formats;        /* a format code for each column */

    /*
     * Outermost ActiveSnapshot for execution of the portal's queries.  For
     * all but a few utility commands, we require such a snapshot to exist.
     * This ensures that TOAST references in query results can be detoasted,
     * and helps to reduce thrashing of the process's exposed xmin.
     */
    Snapshot    portalSnapshot; /* active snapshot, or NULL if none */

    /*
     * Where we store tuples for a held cursor or a PORTAL_ONE_RETURNING or
     * PORTAL_UTIL_SELECT query.  (A cursor held past the end of its
     * transaction no longer has any active executor state.)
     */
    Tuplestorestate *holdStore; /* store for holdable cursors */
    MemoryContext holdContext;  /* memory containing holdStore */

    /*
     * Snapshot under which tuples in the holdStore were read.  We must keep a
     * reference to this snapshot if there is any possibility that the tuples
     * contain TOAST references, because releasing the snapshot could allow
     * recently-dead rows to be vacuumed away, along with any toast data
     * belonging to them.  In the case of a held cursor, we avoid needing to
     * keep such a snapshot by forcibly detoasting the data.
     */
    Snapshot    holdSnapshot;   /* registered snapshot, or NULL if none */

    /*
     * atStart, atEnd and portalPos indicate the current cursor position.
     * portalPos is zero before the first row, N after fetching N'th row of
     * query.  After we run off the end, portalPos = # of rows in query, and
     * atEnd is true.  Note that atStart implies portalPos == 0, but not the
     * reverse: we might have backed up only as far as the first row, not to
     * the start.  Also note that various code inspects atStart and atEnd, but
     * only the portal movement routines should touch portalPos.
     */
    bool        atStart;
    bool        atEnd;
    uint64      portalPos;

    /* Presentation data, primarily used by the pg_cursors system view */
    TimestampTz creation_time;  /* time at which this portal was defined */
    bool        visible;        /* include this portal in pg_cursors? */
}           PortalData;
```

其中很重要的是 `List *stmts`，这是查询编译器输出的 **原子操作节点** 的链表，链表的每个节点保存了 (可能包含查询计划树在内的) 操作。其中，可能带有查询计划树的原子操作节点只有 `PlannedStmt` 和 `Query` 两类节点。这两类节点中通过 `CmdType` 字段指示了当前原子操作对应的命令类型：

```c
/*
 * CmdType -
 *    enums for type of operation represented by a Query or PlannedStmt
 *
 * This is needed in both parsenodes.h and plannodes.h, so put it here...
 */
typedef enum CmdType
{
    CMD_UNKNOWN,
    CMD_SELECT,                 /* select stmt */
    CMD_UPDATE,                 /* update stmt */
    CMD_INSERT,                 /* insert stmt */
    CMD_DELETE,
    CMD_UTILITY,                /* cmds like create, destroy, copy, vacuum,
                                 * etc. */
    CMD_NOTHING                 /* dummy command for instead nothing rules
                                 * with qual */
} CmdType;
```

## Execution Strategy

对于一个刚被创建好的 `Portal`，经过一定的初始化后，查询编译器输出的原子操作链表将会被设置到 `Portal` 中。在 `PortalStart()` 函数里，对 `Portal` 进行执行前的最后一步初始化：根据操作的类型选择 **执行策略** (实现于函数 `ChoosePortalStrategy()`)：

```c
/*
 * We have several execution strategies for Portals, depending on what
 * query or queries are to be executed.  (Note: in all cases, a Portal
 * executes just a single source-SQL query, and thus produces just a
 * single result from the user's viewpoint.  However, the rule rewriter
 * may expand the single source query to zero or many actual queries.)
 *
 * PORTAL_ONE_SELECT: the portal contains one single SELECT query.  We run
 * the Executor incrementally as results are demanded.  This strategy also
 * supports holdable cursors (the Executor results can be dumped into a
 * tuplestore for access after transaction completion).
 *
 * PORTAL_ONE_RETURNING: the portal contains a single INSERT/UPDATE/DELETE
 * query with a RETURNING clause (plus possibly auxiliary queries added by
 * rule rewriting).  On first execution, we run the portal to completion
 * and dump the primary query's results into the portal tuplestore; the
 * results are then returned to the client as demanded.  (We can't support
 * suspension of the query partway through, because the AFTER TRIGGER code
 * can't cope, and also because we don't want to risk failing to execute
 * all the auxiliary queries.)
 *
 * PORTAL_ONE_MOD_WITH: the portal contains one single SELECT query, but
 * it has data-modifying CTEs.  This is currently treated the same as the
 * PORTAL_ONE_RETURNING case because of the possibility of needing to fire
 * triggers.  It may act more like PORTAL_ONE_SELECT in future.
 *
 * PORTAL_UTIL_SELECT: the portal contains a utility statement that returns
 * a SELECT-like result (for example, EXPLAIN or SHOW).  On first execution,
 * we run the statement and dump its results into the portal tuplestore;
 * the results are then returned to the client as demanded.
 *
 * PORTAL_MULTI_QUERY: all other cases.  Here, we do not support partial
 * execution: the portal's queries will be run to completion on first call.
 */
typedef enum PortalStrategy
{
    PORTAL_ONE_SELECT,
    PORTAL_ONE_RETURNING,
    PORTAL_ONE_MOD_WITH,
    PORTAL_UTIL_SELECT,
    PORTAL_MULTI_QUERY
} PortalStrategy;
```

- `PORTAL_ONE_SELECT` 处理仅包含一个原子操作的情况 (`SELECT` 查询)
- `PORTAL_ONE_RETURNING` 处理带有 `RETURNING` 子句的 DML 操作：先对元组进行修改，然后返回结果
- `PORTAL_UTIL_SELECT` 处理 DDL，返回结果
- `PORTAL_MULTI_QUERY` 处理上述三种操作以外的情况，能处理一个或多个原子操作

PostgreSQL 执行器中提供两个子模块处理不同类型的操作：

- Executor 模块执行前两类策略 (DQL + DML)，统称为 _可优化语句_，查询编译器会为这类操作生成计划树
- ProcessUtility 模块执行后两类策略 (DDL 及其它)，主要是一些功能性操作

## DDL Execution

DDL 的执行比较简单。执行流程进入 ProcessUtility 模块后，通过判断操作的类型，直接分发进入不同操作的处理函数中。核心逻辑是一个 `switch` 语句：

```c
switch (nodeTag(parsetree))
{
        /*
         * ******************** transactions ********************
         */
    case T_TransactionStmt:
        {
        }
        break;

        /*
         * Portal (cursor) manipulation
         */
    case T_DeclareCursorStmt:
        break;

    case T_ClosePortalStmt:
        {
        }
        break;

    case T_FetchStmt:
        PerformPortalFetch((FetchStmt *) parsetree, dest, qc);
        break;

    case T_DoStmt:
        ExecuteDoStmt((DoStmt *) parsetree, isAtomicContext);
        break;

    /* ... */

    default:
        /* All other statement types have event trigger support */
        ProcessUtilitySlow(pstate, pstmt, queryString,
                            context, params, queryEnv,
                            dest, qc);
        break;
}
```

## Optimizable Statement Execution

可优化语句由 Executor 模块处理。对查询计划树的处理，最终转换为 **对查询计划树上每一个节点** 的处理。每一种节点对应一种 _物理代数_ 操作 (我理解的是每一种节点都对应一个算子：扫描算子/排序算子/连接算子等)，计划节点以二叉树的形式构成计划树。父节点从 (左右) 孩子节点获取元组作为输入，经过本节点的算子操作后，返回给更上层的节点。因此，实际执行将会从根节点开始层层向下递归，直到叶子节点。对计划树的遍历完成，也就意味着一次查询执行的完成。

Executor 模块的核心数据结构为 `QueryDesc`，是所有 Executor 模块接口函数的输入参数。它是在 `PortalStart()` 函数中通过 `CreateQueryDesc()` 创建出来的，该函数主要工作是将 `Portal` 结构中的 `stmts` 设置到了 `QueryDesc` 中。其结构定义如下：

```c
/* ----------------
 *      query descriptor:
 *
 *  a QueryDesc encapsulates everything that the executor
 *  needs to execute the query.
 *
 *  For the convenience of SQL-language functions, we also support QueryDescs
 *  containing utility statements; these must not be passed to the executor
 *  however.
 * ---------------------
 */
typedef struct QueryDesc
{
    /* These fields are provided by CreateQueryDesc */
    CmdType     operation;      /* CMD_SELECT, CMD_UPDATE, etc. */
    PlannedStmt *plannedstmt;   /* planner's output (could be utility, too) */
    const char *sourceText;     /* source text of the query */
    Snapshot    snapshot;       /* snapshot to use for query */
    Snapshot    crosscheck_snapshot;    /* crosscheck for RI update/delete */
    DestReceiver *dest;         /* the destination for tuple output */
    ParamListInfo params;       /* param values being passed in */
    QueryEnvironment *queryEnv; /* query environment passed in */
    int         instrument_options; /* OR of InstrumentOption flags */

    /* These fields are set by ExecutorStart */
    TupleDesc   tupDesc;        /* descriptor for result tuples */
    EState     *estate;         /* executor's query-wide state */
    PlanState  *planstate;      /* tree of per-plan-node state */

    /* This field is set by ExecutorRun */
    bool        already_executed;   /* true if previously executed */

    /* This is always set NULL by the core system, but plugins can change it */
    struct Instrumentation *totaltime;  /* total time spent in ExecutorRun */
} QueryDesc;
```

Executor 模块的三个核心入口分别在以下三个函数中被调用，是否被调用的依据是 `Portal` 结构体中的 `PortalStrategy`：

- `ExecutorStart()`：从 `PortalStart()` 中对可优化语句调用
  - 初始化执行器当前执行任务时的全局状态 `EState`，并设置到 `QueryDesc` 中
  - 调用 `InitPlan()`，内部调用 `ExecInitNode()` 从根节点开始递归创建每个计划节点对应的状态 `PlanState`
- `ExecutorRun()`：从 `PortalRun()` 中对可优化语句调用
  - 调用 `ExecutePlan()`，内部调用 `ExecProcNode()` 从根节点开始递归执行计划
- `ExecutorEnd()`：从 `PortalEnd()` 中对可优化语句调用
  - 调用 `ExecEndPlan()`，内部调用 `ExecEndNode()` 从根节点开始递归清理每个计划节点对应的 `PlanState`
  - 释放全局状态 `EState`

### Plan State

`ExecInitNode()` 函数根据计划节点的类型调用相应的 `ExecInitXXX()` 函数，并返回指向该计划节点对应 `PlanState` 结构的指针。其核心也是一个 `switch` 语句：

```c
switch (nodeTag(node))
{
        /*
         * control nodes
         */
    case T_Result:
        result = (PlanState *) ExecInitResult((Result *) node,
                                                estate, eflags);
        break;

    case T_ProjectSet:
        result = (PlanState *) ExecInitProjectSet((ProjectSet *) node,
                                                    estate, eflags);
        break;

    case T_ModifyTable:
        result = (PlanState *) ExecInitModifyTable((ModifyTable *) node,
                                                    estate, eflags);
        break;

    case T_Append:
        result = (PlanState *) ExecInitAppend((Append *) node,
                                                estate, eflags);
        break;

    /* ... */

    default:
        elog(ERROR, "unrecognized node type: %d", (int) nodeTag(node));
        result = NULL;      /* keep compiler quiet */
        break;
}
```

在每一种计划节点对应的 `ExecInitXXX()` 函数中，又会递归调用 `ExecInitNode()` 函数构造子节点的 `PlanState`，然后设置到当前节点 `PlanState` 的左右孩子指针上，再返回上层。看看 `PlanState` 的结构定义吧：

```c
/* ----------------
 *      PlanState node
 *
 * We never actually instantiate any PlanState nodes; this is just the common
 * abstract superclass for all PlanState-type nodes.
 * ----------------
 */
typedef struct PlanState
{
    NodeTag        type;

    Plan       *plan;           /* associated Plan node */

    EState     *state;          /* at execution time, states of individual
                                 * nodes point to one EState for the whole
                                 * top-level plan */

    ExecProcNodeMtd ExecProcNode;   /* function to return next tuple */
    ExecProcNodeMtd ExecProcNodeReal;   /* actual function, if above is a
                                         * wrapper */

    /* ... */

     * Common structural data for all Plan types.  These links to subsidiary
     * state trees parallel links in the associated plan tree (except for the
     * subPlan list, which does not exist in the plan tree).
     */
    ExprState  *qual;           /* boolean qual condition */
    struct PlanState *lefttree; /* input plan tree(s) */
    struct PlanState *righttree;

    /* ... */

} PlanState;
```

其中 `plan` 指针指向对应的计划树节点，`state` 指向执行器的全局状态。`lefttree` 和 `righttree` 指针分别指向左右孩子节点的 `PlanState`。与查询计划树类似，`PlanState` 也构成了一棵结构相同的二叉树。

### Execution

在 `ExecutorRun()` 中，对根计划节点调用 `ExecProcNode()` 开始递归执行查询。该函数以函数指针的形式，设置在了计划节点对应的 `PlanState` 中。显然，每类不同的计划节点有着不同的 `ExecProcXXX()` 实现。但是思想上肯定还是递归的：

- 对孩子节点递归调用 `ExecProcNode()` 获取输入数据 (一般是元组)
- 在当前节点层次中完成对元组的处理，并进行选择运算 + 投影运算
- 向上层节点返回处理后的元组指针

一般来说，叶子计划节点的类型都是扫描节点 (顺序扫描 / 索引扫描)，能向上层节点提供元组。

当 `ExecutePlan()` 对根计划节点调用 `ExecProcNode()` 并最终返回一条元组后，根据整个语句的操作类型，进行最终处理。(？)

> 这里源码和书对不上了，代码应该是重构过了。

### Clean Up

`ExecEndPlan()` 与前面思想类似：对根节点调用 `ExecEndNode()`。该函数中根据计划节点的 `nodeTag` 做了一个 `switch`，分别进入各个类型计划节点的 `ExecEndXXX()` 中。

## More

后续具体看看每种类型计划节点的结构定义 (以及其中继承关系)，以及各类节点分别如何实现 `ExecInitNode()` / `ExecProcNode()` / `ExecEndNode()`。
