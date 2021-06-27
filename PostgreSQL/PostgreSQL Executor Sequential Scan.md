# PostgreSQL - Executor: Sequential Scan

Created by : Mr Dk.

2021 / 06 / 27 23:42

Hangzhou, Zhejiang, China

---

对 PostgreSQL 执行器的执行流程进行分析后，看看最简单的顺序扫描算子是如何实现的。

## Plan Node

优化器输出的查询计划树是二叉树的形式。二叉树的节点有着最基本的结构定义，并根据不同类型的操作实现继承关系。最基本的计划树节点的结构定义如下。其中，由 `type` 来指定计划节点的类型。

```c
/* ----------------
 *      Plan node
 *
 * All plan nodes "derive" from the Plan structure by having the
 * Plan structure as the first field.  This ensures that everything works
 * when nodes are cast to Plan's.  (node pointers are frequently cast to Plan*
 * when passed around generically in the executor)
 *
 * We never actually instantiate any Plan nodes; this is just the common
 * abstract superclass for all Plan-type nodes.
 * ----------------
 */
typedef struct Plan
{
    NodeTag     type;

    /*
     * estimated execution costs for plan (see costsize.c for more info)
     */
    Cost        startup_cost;   /* cost expended before fetching any tuples */
    Cost        total_cost;     /* total cost (assuming all tuples fetched) */

    /*
     * planner's estimate of result size of this plan step
     */
    double      plan_rows;      /* number of rows plan is expected to emit */
    int         plan_width;     /* average row width in bytes */

    /*
     * information needed for parallel query
     */
    bool        parallel_aware; /* engage parallel-aware logic? */
    bool        parallel_safe;  /* OK to use as part of parallel plan? */

    /*
     * information needed for asynchronous execution
     */
    bool        async_capable;  /* engage asynchronous-capable logic? */

    /*
     * Common structural data for all Plan types.
     */
    int         plan_node_id;   /* unique across entire final plan tree */
    List       *targetlist;     /* target list to be computed at this node */
    List       *qual;           /* implicitly-ANDed qual conditions */
    struct Plan *lefttree;      /* input plan tree(s) */
    struct Plan *righttree;
    List       *initPlan;       /* Init Plan nodes (un-correlated expr
                                 * subselects) */

    /*
     * Information for management of parameter-change-driven rescanning
     *
     * extParam includes the paramIDs of all external PARAM_EXEC params
     * affecting this plan node or its children.  setParam params from the
     * node's initPlans are not included, but their extParams are.
     *
     * allParam includes all the extParam paramIDs, plus the IDs of local
     * params that affect the node (i.e., the setParams of its initplans).
     * These are _all_ the PARAM_EXEC params that affect this node.
     */
    Bitmapset  *extParam;
    Bitmapset  *allParam;
} Plan;
```

任何类型计划节点都要继承自这个最基本的 `Plan` 结构，并在其结构体中将 `Plan` 作为第一个成员变量，使得将子类型的计划节点指针强制转换为 `Plan *` 时能够直接引用到 `Plan` 结构体内的变量。这和 C++ 的对象继承行为一致。这里以扫描计划节点为例：

```c
/*
 * ==========
 * Scan nodes
 * ==========
 */
typedef struct Scan
{
    Plan        plan;
    Index       scanrelid;      /* relid is index into the range table */
} Scan;
```

这也是所有扫描节点的父类。任何扫描计划节点都要继承自这个结构体，并将 `Scan` 作为第一个成员变量。以最简单的顺序扫描 (sequential scan) 节点为例：

```c
/* ----------------
 *      sequential scan node
 * ----------------
 */
typedef Scan SeqScan;

/* ----------------
 *      table sample scan node
 * ----------------
 */
typedef struct SampleScan
{
    Scan        scan;
    /* use struct pointer to avoid including parsenodes.h here */
    struct TableSampleClause *tablesample;
} SampleScan;
```

好吧，由于顺序扫描过于简单，除了 `Scan` 的变量以外没有任何扩展变量了；对于 `SampleScan`，除了第一个成员变量 `scan` 外，还有完成其对应功能的其它成员变量。

## Initialization

之前已经分析过，在执行器的 `ExecInitNode()` 函数中有一个 `switch` 语句，根据查询计划节点的类型 (`NodeTag`) 调用相应的 `ExecInitXXX()`。对于顺序扫描节点，自然是调用 `ExecInitSeqScan()`。传入参数为顺序扫描的计划节点，以及计划执行的全局状态：

```c
/* ----------------------------------------------------------------
 *      ExecInitSeqScan
 * ----------------------------------------------------------------
 */
SeqScanState *
ExecInitSeqScan(SeqScan *node, EState *estate, int eflags)
{
    SeqScanState *scanstate;

    /*
     * Once upon a time it was possible to have an outerPlan of a SeqScan, but
     * not any more.
     */
    Assert(outerPlan(node) == NULL);
    Assert(innerPlan(node) == NULL);

    /*
     * create state structure
     */
    scanstate = makeNode(SeqScanState);
    scanstate->ss.ps.plan = (Plan *) node;
    scanstate->ss.ps.state = estate;
    scanstate->ss.ps.ExecProcNode = ExecSeqScan;

    /*
     * Miscellaneous initialization
     *
     * create expression context for node
     */
    ExecAssignExprContext(estate, &scanstate->ss.ps);

    /*
     * open the scan relation
     */
    scanstate->ss.ss_currentRelation =
        ExecOpenScanRelation(estate,
                             node->scanrelid,
                             eflags);

    /* and create slot with the appropriate rowtype */
    ExecInitScanTupleSlot(estate, &scanstate->ss,
                          RelationGetDescr(scanstate->ss.ss_currentRelation),
                          table_slot_callbacks(scanstate->ss.ss_currentRelation));

    /*
     * Initialize result type and projection.
     */
    ExecInitResultTypeTL(&scanstate->ss.ps);
    ExecAssignScanProjectionInfo(&scanstate->ss);

    /*
     * initialize child expressions
     */
    scanstate->ss.ps.qual =
        ExecInitQual(node->plan.qual, (PlanState *) scanstate);

    return scanstate;
}
```

可以看到，顺序扫描节点不再允许有任何左右孩子节点了，必须是计划树的叶子节点。然后根据当前的计划节点构造相对应的 `PlanState` 节点：`SeqScanState`。然后将计划执行阶段的节点回调函数 `ExecProcNode` 函数指针设置为函数 `ExecSeqScan()`。值得一提的是，`PlanState` 也满足类似 `Plan` 的继承关系：

```c
/* ----------------------------------------------------------------
 *               Scan State Information
 * ----------------------------------------------------------------
 */

/* ----------------
 *   ScanState information
 *
 *      ScanState extends PlanState for node types that represent
 *      scans of an underlying relation.  It can also be used for nodes
 *      that scan the output of an underlying plan node --- in that case,
 *      only ScanTupleSlot is actually useful, and it refers to the tuple
 *      retrieved from the subplan.
 *
 *      currentRelation    relation being scanned (NULL if none)
 *      currentScanDesc    current scan descriptor for scan (NULL if none)
 *      ScanTupleSlot      pointer to slot in tuple table holding scan tuple
 * ----------------
 */
typedef struct ScanState
{
    PlanState   ps;             /* its first field is NodeTag */
    Relation    ss_currentRelation;
    struct TableScanDescData *ss_currentScanDesc;
    TupleTableSlot *ss_ScanTupleSlot;
} ScanState;

/* ----------------
 *   SeqScanState information
 * ----------------
 */
typedef struct SeqScanState
{
    ScanState   ss;             /* its first field is NodeTag */
    Size        pscan_len;      /* size of parallel heap scan descriptor */
} SeqScanState;
```

## Sequential Scan Execution

如上所述，顺序扫描计划节点的执行回调函数被设置为 `ExecSeqScan()`：

```c
/* ----------------------------------------------------------------
 *      ExecSeqScan(node)
 *
 *      Scans the relation sequentially and returns the next qualifying
 *      tuple.
 *      We call the ExecScan() routine and pass it the appropriate
 *      access method functions.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecSeqScan(PlanState *pstate)
{
    SeqScanState *node = castNode(SeqScanState, pstate);

    return ExecScan(&node->ss,
                    (ExecScanAccessMtd) SeqNext,
                    (ExecScanRecheckMtd) SeqRecheck);
}
```

这里，所有与扫描相关的操作又被抽象到了 `ExecScan()` 函数中，被各种扫描操作复用。每种扫描操作需要提供 `accessMtd` 和 `recheckMtd` 两个回调函数指针。

```c
/*
 * prototypes from functions in execScan.c
 */
typedef TupleTableSlot *(*ExecScanAccessMtd) (ScanState *node);
typedef bool (*ExecScanRecheckMtd) (ScanState *node, TupleTableSlot *slot);
```

其中，`accessMtd` 用于使用特定的扫描方式 **返回下一个元组**。对于顺序扫描来说，上述调用指定 `SeqNext()` 函数顺序扫描下一个元组并返回：

- 如果扫描描述符为空，那么立刻初始化一个，并维护在 `SeqScanState` 中
- 调用 `table_scan_getnextslot()` 获取下一个元组

```c
/* ----------------------------------------------------------------
 *                      Scan Support
 * ----------------------------------------------------------------
 */

/* ----------------------------------------------------------------
 *      SeqNext
 *
 *      This is a workhorse for ExecSeqScan
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
SeqNext(SeqScanState *node)
{
    TableScanDesc scandesc;
    EState     *estate;
    ScanDirection direction;
    TupleTableSlot *slot;

    /*
     * get information from the estate and scan state
     */
    scandesc = node->ss.ss_currentScanDesc;
    estate = node->ss.ps.state;
    direction = estate->es_direction;
    slot = node->ss.ss_ScanTupleSlot;

    if (scandesc == NULL)
    {
        /*
         * We reach here if the scan is not parallel, or if we're serially
         * executing a scan that was planned to be parallel.
         */
        scandesc = table_beginscan(node->ss.ss_currentRelation,
                                   estate->es_snapshot,
                                   0, NULL);
        node->ss.ss_currentScanDesc = scandesc;
    }

    /*
     * get the next tuple from the table
     */
    if (table_scan_getnextslot(scandesc, direction, slot))
        return slot;
    return NULL;
}

/*
 * SeqRecheck -- access method routine to recheck a tuple in EvalPlanQual
 */
static bool
SeqRecheck(SeqScanState *node, TupleTableSlot *slot)
{
    /*
     * Note that unlike IndexScan, SeqScan never use keys in heap_beginscan
     * (and this is very bad) - so, here we do not check are keys ok or not.
     */
    return true;
}
```

再来看看 `ExecScan()` 中的通用扫描动作，以及如何调用上述两个回调函数。其中有一个核心死循环，用于不同获取元组：

```c
/* ----------------------------------------------------------------
 *      ExecScan
 *
 *      Scans the relation using the 'access method' indicated and
 *      returns the next qualifying tuple.
 *      The access method returns the next tuple and ExecScan() is
 *      responsible for checking the tuple returned against the qual-clause.
 *
 *      A 'recheck method' must also be provided that can check an
 *      arbitrary tuple of the relation against any qual conditions
 *      that are implemented internal to the access method.
 *
 *      Conditions:
 *        -- the "cursor" maintained by the AMI is positioned at the tuple
 *           returned previously.
 *
 *      Initial States:
 *        -- the relation indicated is opened for scanning so that the
 *           "cursor" is positioned before the first qualifying tuple.
 * ----------------------------------------------------------------
 */
TupleTableSlot *
ExecScan(ScanState *node,
         ExecScanAccessMtd accessMtd,   /* function returning a tuple */
         ExecScanRecheckMtd recheckMtd)
{
    ExprContext *econtext;
    ExprState  *qual;
    ProjectionInfo *projInfo;

    /*
     * Fetch data from node
     */
    qual = node->ps.qual;
    projInfo = node->ps.ps_ProjInfo;
    econtext = node->ps.ps_ExprContext;

    /* interrupt checks are in ExecScanFetch */

    /*
     * If we have neither a qual to check nor a projection to do, just skip
     * all the overhead and return the raw scan tuple.
     */
    if (!qual && !projInfo)
    {
        ResetExprContext(econtext);
        return ExecScanFetch(node, accessMtd, recheckMtd);
    }

    /*
     * Reset per-tuple memory context to free any expression evaluation
     * storage allocated in the previous tuple cycle.
     */
    ResetExprContext(econtext);

    /*
     * get a tuple from the access method.  Loop until we obtain a tuple that
     * passes the qualification.
     */
    for (;;)
    {
        TupleTableSlot *slot;

        slot = ExecScanFetch(node, accessMtd, recheckMtd);

        /*
         * if the slot returned by the accessMtd contains NULL, then it means
         * there is nothing more to scan so we just return an empty slot,
         * being careful to use the projection result slot so it has correct
         * tupleDesc.
         */
        if (TupIsNull(slot))
        {
            if (projInfo)
                return ExecClearTuple(projInfo->pi_state.resultslot);
            else
                return slot;
        }

        /*
         * place the current tuple into the expr context
         */
        econtext->ecxt_scantuple = slot;

        /*
         * check that the current tuple satisfies the qual-clause
         *
         * check for non-null qual here to avoid a function call to ExecQual()
         * when the qual is null ... saves only a few cycles, but they add up
         * ...
         */
        if (qual == NULL || ExecQual(qual, econtext))
        {
            /*
             * Found a satisfactory scan tuple.
             */
            if (projInfo)
            {
                /*
                 * Form a projection tuple, store it in the result tuple slot
                 * and return it.
                 */
                return ExecProject(projInfo);
            }
            else
            {
                /*
                 * Here, we aren't projecting, so just return scan tuple.
                 */
                return slot;
            }
        }
        else
            InstrCountFiltered1(node, 1);

        /*
         * Tuple fails qual, so free per-tuple memory and try again.
         */
        ResetExprContext(econtext);
    }
}
```

在死循环中，调用 `ExecScanFetch()` 并传入两个回调函数指针获取元组。在这个函数中折腾了一大堆，在函数返回前调用了 `accessMtd` 函数指针：

```c
/*
 * Run the node-type-specific access method function to get the next tuple
 */
return (*accessMtd) (node);
```

## Ending

执行结束时，调用 `ExecEndNode()`。与初始化类似，其中也有一个核心的 `switch` 函数，根据计划节点的类型，调用相应的 `ExecEndXXX()`。这里显然将会调用 `ExecEndSeqScan()`，完成所有的清理工作：

```c
/* ----------------------------------------------------------------
 *      ExecEndSeqScan
 *
 *      frees any storage allocated through C routines.
 * ----------------------------------------------------------------
 */
void
ExecEndSeqScan(SeqScanState *node)
{
    TableScanDesc scanDesc;

    /*
     * get information from node
     */
    scanDesc = node->ss.ss_currentScanDesc;

    /*
     * Free the exprcontext
     */
    ExecFreeExprContext(&node->ss.ps);

    /*
     * clean out the tuple table
     */
    if (node->ss.ps.ps_ResultTupleSlot)
        ExecClearTuple(node->ss.ps.ps_ResultTupleSlot);
    ExecClearTuple(node->ss.ss_ScanTupleSlot);

    /*
     * close heap scan
     */
    if (scanDesc != NULL)
        table_endscan(scanDesc);
}
```

顺序扫描已经是最简单的扫描算子了，后续考虑看一下索引扫描算子，看看实现上有什么特别的地方。暂时没有向下研究至存储级别的实现：heap 表似乎定义了自己的 access method，与具体扫描操作的实现解耦。

