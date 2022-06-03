# PostgreSQL - Executor: Append

Created by : Mr Dk.

2021 / 07 / 04 15:18

Hangzhou, Zhejiang, China

---

Append 节点包含一个需要被迭代处理的 **一个或多个子计划** 的链表。根据注释说明，Append 节点会从链表中的每个子计划里获取元组，直到没有元组可以获得，然后处理下一个子计划。因此，Append 节点可用于处理 **union** 查询，比如继承表的查询：查询父表时，会生成顺带查询所有继承子表的查询计划，那么查询父表和子表的子计划都会被放到 Append 节点的链表中。

```c
/* INTERFACE ROUTINES
 *      ExecInitAppend  - initialize the append node
 *      ExecAppend      - retrieve the next tuple from the node
 *      ExecEndAppend   - shut down the append node
 *      ExecReScanAppend - rescan the append node
 *
 *   NOTES
 *      Each append node contains a list of one or more subplans which
 *      must be iteratively processed (forwards or backwards).
 *      Tuples are retrieved by executing the 'whichplan'th subplan
 *      until the subplan stops returning tuples, at which point that
 *      plan is shut down and the next started up.
 *
 *      Append nodes don't make use of their left and right
 *      subtrees, rather they maintain a list of subplans so
 *      a typical append node looks like this in the plan tree:
 *
 *                 ...
 *                 /
 *              Append -------+------+------+--- nil
 *              /   \         |      |      |
 *            nil   nil      ...    ...    ...
 *                               subplans
 *
 *      Append nodes are currently used for unions, and to support
 *      inheritance queries, where several relations need to be scanned.
 *      For example, in our standard person/student/employee/student-emp
 *      example, where student and employee inherit from person
 *      and student-emp inherits from student and employee, the
 *      query:
 *
 *              select name from person
 *
 *      generates the plan:
 *
 *                |
 *              Append -------+-------+--------+--------+
 *              /   \         |       |        |        |
 *            nil   nil      Scan    Scan     Scan     Scan
 *                            |       |        |        |
 *                          person employee student student-emp
 */
```

## Plan Node

根据注释里的信息，Append 节点不需要用到 Plan 结构体内带有的左右孩子节点，而是自行扩展了计划节点定义，为所有的子计划维护一个链表 `appendplans`：

```c
/* ----------------
 *   Append node -
 *      Generate the concatenation of the results of sub-plans.
 * ----------------
 */
typedef struct Append
{
    Plan        plan;
    Bitmapset  *apprelids;      /* RTIs of appendrel(s) formed by this node */
    List       *appendplans;
    int         nasyncplans;    /* # of asynchronous plans */

    /*
     * All 'appendplans' preceding this index are non-partial plans. All
     * 'appendplans' from this index onwards are partial plans.
     */
    int         first_partial_plan;

    /* Info for run-time subplan pruning; NULL if we're not doing that */
    struct PartitionPruneInfo *part_prune_info;
} Append;
```

对于 Append 节点对应的 PlanState，其中维护了链表的长度（子计划的个数），以及目前正在执行的子计划的状态信息（哪一个子计划 / 执行是否开始 / 执行是否完成）：

```c
/* ----------------
 *   AppendState information
 *
 *      nplans              how many plans are in the array
 *      whichplan           which synchronous plan is being executed (0 .. n-1)
 *                          or a special negative value. See nodeAppend.c.
 *      prune_state         details required to allow partitions to be
 *                          eliminated from the scan, or NULL if not possible.
 *      valid_subplans      for runtime pruning, valid synchronous appendplans
 *                          indexes to scan.
 * ----------------
 */

struct AppendState;
typedef struct AppendState AppendState;
struct ParallelAppendState;
typedef struct ParallelAppendState ParallelAppendState;
struct PartitionPruneState;

struct AppendState
{
    PlanState   ps;             /* its first field is NodeTag */
    PlanState **appendplans;    /* array of PlanStates for my inputs */
    int         as_nplans;
    int         as_whichplan;
    bool        as_begun;       /* false means need to initialize */
    Bitmapset  *as_asyncplans;  /* asynchronous plans indexes */
    int         as_nasyncplans; /* # of asynchronous plans */
    AsyncRequest **as_asyncrequests;    /* array of AsyncRequests */
    TupleTableSlot **as_asyncresults;   /* unreturned results of async plans */
    int         as_nasyncresults;   /* # of valid entries in as_asyncresults */
    bool        as_syncdone;    /* true if all synchronous plans done in
                                 * asynchronous mode, else false */
    int         as_nasyncremain;    /* # of remaining asynchronous plans */
    Bitmapset  *as_needrequest; /* asynchronous plans needing a new request */
    struct WaitEventSet *as_eventset;   /* WaitEventSet used to configure file
                                         * descriptor wait events */
    int         as_first_partial_plan;  /* Index of 'appendplans' containing
                                         * the first partial plan */
    ParallelAppendState *as_pstate; /* parallel coordination info */
    Size        pstate_len;     /* size of parallel coordination info */
    struct PartitionPruneState *as_prune_state;
    Bitmapset  *as_valid_subplans;
    Bitmapset  *as_valid_asyncplans;    /* valid asynchronous plans indexes */
    bool        (*choose_next_subplan) (AppendState *);
};
```

## Initialization

该函数在 `ExecInitNode()` 生命周期中被调用，完成给 Append 节点构造相应 AppendState 节点的工作。该函数内会为一次性为所有子计划分配好 `PlanState` 结构体的空间，然后为每一个子计划递归调用 `ExecInitNode()`。

> 这里与一般节点有区别。其它节点都是对当前节点的左右孩子递归调用 `ExecInitNode()`；Append 节点没有左右孩子节点，是通过遍历子计划链表，分别调用 `ExecInitNode()` 来完成初始化的。

```c
/* ----------------------------------------------------------------
 *      ExecInitAppend
 *
 *      Begin all of the subscans of the append node.
 *
 *     (This is potentially wasteful, since the entire result of the
 *      append node may not be scanned, but this way all of the
 *      structures get allocated in the executor's top level memory
 *      block instead of that of the call to ExecAppend.)
 * ----------------------------------------------------------------
 */
AppendState *
ExecInitAppend(Append *node, EState *estate, int eflags)
{
    AppendState *appendstate = makeNode(AppendState);
    PlanState **appendplanstates;
    Bitmapset  *validsubplans;
    Bitmapset  *asyncplans;
    int         nplans;
    int         nasyncplans;
    int         firstvalid;
    int         i,
                j;

    /* check for unsupported flags */
    Assert(!(eflags & EXEC_FLAG_MARK));

    /*
     * create new AppendState for our append node
     */
    appendstate->ps.plan = (Plan *) node;
    appendstate->ps.state = estate;
    appendstate->ps.ExecProcNode = ExecAppend;

    /* Let choose_next_subplan_* function handle setting the first subplan */
    appendstate->as_whichplan = INVALID_SUBPLAN_INDEX;
    appendstate->as_syncdone = false;
    appendstate->as_begun = false;

    /* If run-time partition pruning is enabled, then set that up now */
    if (node->part_prune_info != NULL)
    {
        PartitionPruneState *prunestate;

        /* We may need an expression context to evaluate partition exprs */
        ExecAssignExprContext(estate, &appendstate->ps);

        /* Create the working data structure for pruning. */
        prunestate = ExecCreatePartitionPruneState(&appendstate->ps,
                                                   node->part_prune_info);
        appendstate->as_prune_state = prunestate;

        /* Perform an initial partition prune, if required. */
        if (prunestate->do_initial_prune)
        {
            /* Determine which subplans survive initial pruning */
            validsubplans = ExecFindInitialMatchingSubPlans(prunestate,
                                                            list_length(node->appendplans));

            nplans = bms_num_members(validsubplans);
        }
        else
        {
            /* We'll need to initialize all subplans */
            nplans = list_length(node->appendplans);
            Assert(nplans > 0);
            validsubplans = bms_add_range(NULL, 0, nplans - 1);
        }

        /*
         * When no run-time pruning is required and there's at least one
         * subplan, we can fill as_valid_subplans immediately, preventing
         * later calls to ExecFindMatchingSubPlans.
         */
        if (!prunestate->do_exec_prune && nplans > 0)
            appendstate->as_valid_subplans = bms_add_range(NULL, 0, nplans - 1);
    }
    else
    {
        nplans = list_length(node->appendplans);

        /*
         * When run-time partition pruning is not enabled we can just mark all
         * subplans as valid; they must also all be initialized.
         */
        Assert(nplans > 0);
        appendstate->as_valid_subplans = validsubplans =
            bms_add_range(NULL, 0, nplans - 1);
        appendstate->as_prune_state = NULL;
    }

    /*
     * Initialize result tuple type and slot.
     */
    ExecInitResultTupleSlotTL(&appendstate->ps, &TTSOpsVirtual);

    /* node returns slots from each of its subnodes, therefore not fixed */
    appendstate->ps.resultopsset = true;
    appendstate->ps.resultopsfixed = false;

    appendplanstates = (PlanState **) palloc(nplans *
                                             sizeof(PlanState *));

    /*
     * call ExecInitNode on each of the valid plans to be executed and save
     * the results into the appendplanstates array.
     *
     * While at it, find out the first valid partial plan.
     */
    j = 0;
    asyncplans = NULL;
    nasyncplans = 0;
    firstvalid = nplans;
    i = -1;
    while ((i = bms_next_member(validsubplans, i)) >= 0)
    {
        Plan       *initNode = (Plan *) list_nth(node->appendplans, i);

        /*
         * Record async subplans.  When executing EvalPlanQual, we treat them
         * as sync ones; don't do this when initializing an EvalPlanQual plan
         * tree.
         */
        if (initNode->async_capable && estate->es_epq_active == NULL)
        {
            asyncplans = bms_add_member(asyncplans, j);
            nasyncplans++;
        }

        /*
         * Record the lowest appendplans index which is a valid partial plan.
         */
        if (i >= node->first_partial_plan && j < firstvalid)
            firstvalid = j;

        appendplanstates[j++] = ExecInitNode(initNode, estate, eflags);
    }

    appendstate->as_first_partial_plan = firstvalid;
    appendstate->appendplans = appendplanstates;
    appendstate->as_nplans = nplans;

    /* Initialize async state */
    appendstate->as_asyncplans = asyncplans;
    appendstate->as_nasyncplans = nasyncplans;
    appendstate->as_asyncrequests = NULL;
    appendstate->as_asyncresults = (TupleTableSlot **)
        palloc0(nasyncplans * sizeof(TupleTableSlot *));
    appendstate->as_needrequest = NULL;
    appendstate->as_eventset = NULL;

    if (nasyncplans > 0)
    {
        appendstate->as_asyncrequests = (AsyncRequest **)
            palloc0(nplans * sizeof(AsyncRequest *));

        i = -1;
        while ((i = bms_next_member(asyncplans, i)) >= 0)
        {
            AsyncRequest *areq;

            areq = palloc(sizeof(AsyncRequest));
            areq->requestor = (PlanState *) appendstate;
            areq->requestee = appendplanstates[i];
            areq->request_index = i;
            areq->callback_pending = false;
            areq->request_complete = false;
            areq->result = NULL;

            appendstate->as_asyncrequests[i] = areq;
        }
    }

    /*
     * Miscellaneous initialization
     */

    appendstate->ps.ps_ProjInfo = NULL;

    /* For parallel query, this will be overridden later. */
    appendstate->choose_next_subplan = choose_next_subplan_locally;

    return appendstate;
}
```

## Execution

该函数在 `ExecProcNode()` 生命周期中被调用。如果这个函数被第一次调用，那么首先进行一些初始化工作（比如在 `AppendState` 中标记开始执行第一个子计划），然后进入一个死循环。在死循环中，定位到当前子计划并递归调用 `ExecProcNode()` 获取元组并返回；如果返回元组为空，则选择下一个子计划重复上述过程，直到没有更多子计划。

```c
/* ----------------------------------------------------------------
 *     ExecAppend
 *
 *      Handles iteration over multiple subplans.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecAppend(PlanState *pstate)
{
    AppendState *node = castNode(AppendState, pstate);
    TupleTableSlot *result;

    /*
     * If this is the first call after Init or ReScan, we need to do the
     * initialization work.
     */
    if (!node->as_begun)
    {
        Assert(node->as_whichplan == INVALID_SUBPLAN_INDEX);
        Assert(!node->as_syncdone);

        /* Nothing to do if there are no subplans */
        if (node->as_nplans == 0)
            return ExecClearTuple(node->ps.ps_ResultTupleSlot);

        /* If there are any async subplans, begin executing them. */
        if (node->as_nasyncplans > 0)
            ExecAppendAsyncBegin(node);

        /*
         * If no sync subplan has been chosen, we must choose one before
         * proceeding.
         */
        if (!node->choose_next_subplan(node) && node->as_nasyncremain == 0)
            return ExecClearTuple(node->ps.ps_ResultTupleSlot);

        Assert(node->as_syncdone ||
               (node->as_whichplan >= 0 &&
                node->as_whichplan < node->as_nplans));

        /* And we're initialized. */
        node->as_begun = true;
    }

    for (;;)
    {
        PlanState  *subnode;

        CHECK_FOR_INTERRUPTS();

        /*
         * try to get a tuple from an async subplan if any
         */
        if (node->as_syncdone || !bms_is_empty(node->as_needrequest))
        {
            if (ExecAppendAsyncGetNext(node, &result))
                return result;
            Assert(!node->as_syncdone);
            Assert(bms_is_empty(node->as_needrequest));
        }

        /*
         * figure out which sync subplan we are currently processing
         */
        Assert(node->as_whichplan >= 0 && node->as_whichplan < node->as_nplans);
        subnode = node->appendplans[node->as_whichplan];

        /*
         * get a tuple from the subplan
         */
        result = ExecProcNode(subnode);

        if (!TupIsNull(result))
        {
            /*
             * If the subplan gave us something then return it as-is. We do
             * NOT make use of the result slot that was set up in
             * ExecInitAppend; there's no need for it.
             */
            return result;
        }

        /*
         * wait or poll for async events if any. We do this before checking
         * for the end of iteration, because it might drain the remaining
         * async subplans.
         */
        if (node->as_nasyncremain > 0)
            ExecAppendAsyncEventWait(node);

        /* choose new sync subplan; if no sync/async subplans, we're done */
        if (!node->choose_next_subplan(node) && node->as_nasyncremain == 0)
            return ExecClearTuple(node->ps.ps_ResultTupleSlot);
    }
}
```

## Clean Up

清理过程相对简单。与初始化过程类似，无视节点的左右孩子，直接对节点的子计划链表进行遍历，依次对每一个子计划递归调用 `ExecEndNode()` 即可。

```c
/* ----------------------------------------------------------------
 *      ExecEndAppend
 *
 *      Shuts down the subscans of the append node.
 *
 *      Returns nothing of interest.
 * ----------------------------------------------------------------
 */
void
ExecEndAppend(AppendState *node)
{
    PlanState **appendplans;
    int         nplans;
    int         i;

    /*
     * get information from the node
     */
    appendplans = node->appendplans;
    nplans = node->as_nplans;

    /*
     * shut down each of the subscans
     */
    for (i = 0; i < nplans; i++)
        ExecEndNode(appendplans[i]);
}
```

## New Version Kernel

PostgreSQL 14 内核提供了对 Append 节点异步执行的支持，后续有机会再详细了解。
