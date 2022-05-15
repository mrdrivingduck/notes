# PostgreSQL - Executor: Sort

Created by : Mr Dk.

2021 / 07 / 11 21:07

Hangzhou, Zhejiang, China

---

## Tuple Sort

排序节点也是一种物化节点，因为需要把下层节点所有的元组读取出来以后再进行排序。对于元组的保存，使用了 `Tuplesortstate` 结构。该结构在 `Tuplestorestate` 结构的基础上增加了排序的功能：

- 如果内存中放得下，那么直接进行 **快速排序**
- 如果内存中放不下，那么使用临时文件 + 外部 **归并排序**

`Tuplesortstate` 在 B-Tree 索引构建的代码中也有出现过，眼熟。之后单独分析它的功能，目前仅明确其用途：

- `tuplesort_begin_heap()` 初始化元组缓存结构
- `tuplesort_puttupleslot()` 将元组放入缓存结构
- `tuplesort_performsort()` 对缓存结构中的元组进行排序
- `tuplesort_gettupleslot()` 从缓存结构中获取元组
- `tuplesort_end()` 释放缓存结构

## Plan Node

排序节点继承自 `Plan` 结构体，并扩展了与排序相关的字段。主要包含进行排序的列数、进行排序的列索引、排序运算符及 NULL 值处理方式：

```c
/* ----------------
 *      sort node
 * ----------------
 */
typedef struct Sort
{
    Plan        plan;
    int         numCols;        /* number of sort-key columns */
    AttrNumber *sortColIdx;     /* their indexes in the target list */
    Oid        *sortOperators;  /* OIDs of operators to sort them by */
    Oid        *collations;     /* OIDs of collations */
    bool       *nullsFirst;     /* NULLS FIRST/LAST directions */
} Sort;
```

## Plan State

节点 state 继承自 `ScanState`。其中 `ScanState` 继承自 `PlanState`，扩展了与扫描相关的信息；另外 `SortState` 扩展了与 (并行) 排序相关的状态信息：

```c
/* ----------------
 *   SortState information
 * ----------------
 */
typedef struct SortState
{
    ScanState   ss;             /* its first field is NodeTag */
    bool        randomAccess;   /* need random access to sort output? */
    bool        bounded;        /* is the result set bounded? */
    int64       bound;          /* if bounded, how many tuples are needed */
    bool        sort_Done;      /* sort completed yet? */
    bool        bounded_Done;   /* value of bounded we did the sort with */
    int64       bound_Done;     /* value of bound we did the sort with */
    void       *tuplesortstate; /* private state of tuplesort.c */
    bool        am_worker;      /* are we a worker? */
    SharedSortInfo *shared_info;    /* one entry per worker */
} SortState;
```

## Initialization

在 `ExecInitNode()` 生命周期中被调用。构造 `SortState` 节点并初始化，然后递归调用 `ExecInitNode()`。排序状态 `sort_Done` 被初始化为 `false`。

同样，排序节点不需要初始化投影信息。返回的元组不做投影操作，直接返回。

```c
/* ----------------------------------------------------------------
 *      ExecInitSort
 *
 *      Creates the run-time state information for the sort node
 *      produced by the planner and initializes its outer subtree.
 * ----------------------------------------------------------------
 */
SortState *
ExecInitSort(Sort *node, EState *estate, int eflags)
{
    SortState  *sortstate;

    SO1_printf("ExecInitSort: %s\n",
               "initializing sort node");

    /*
     * create state structure
     */
    sortstate = makeNode(SortState);
    sortstate->ss.ps.plan = (Plan *) node;
    sortstate->ss.ps.state = estate;
    sortstate->ss.ps.ExecProcNode = ExecSort;

    /*
     * We must have random access to the sort output to do backward scan or
     * mark/restore.  We also prefer to materialize the sort output if we
     * might be called on to rewind and replay it many times.
     */
    sortstate->randomAccess = (eflags & (EXEC_FLAG_REWIND |
                                         EXEC_FLAG_BACKWARD |
                                         EXEC_FLAG_MARK)) != 0;

    sortstate->bounded = false;
    sortstate->sort_Done = false;
    sortstate->tuplesortstate = NULL;

    /*
     * Miscellaneous initialization
     *
     * Sort nodes don't initialize their ExprContexts because they never call
     * ExecQual or ExecProject.
     */

    /*
     * initialize child nodes
     *
     * We shield the child node from the need to support REWIND, BACKWARD, or
     * MARK/RESTORE.
     */
    eflags &= ~(EXEC_FLAG_REWIND | EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK);

    outerPlanState(sortstate) = ExecInitNode(outerPlan(node), estate, eflags);

    /*
     * Initialize scan slot and type.
     */
    ExecCreateScanSlotFromOuterPlan(estate, &sortstate->ss, &TTSOpsVirtual);

    /*
     * Initialize return slot and type. No need to initialize projection info
     * because this node doesn't do projections.
     */
    ExecInitResultTupleSlotTL(&sortstate->ss.ps, &TTSOpsMinimalTuple);
    sortstate->ss.ps.ps_ProjInfo = NULL;

    SO1_printf("ExecInitSort: %s\n",
               "sort node initialized");

    return sortstate;
}
```

## Execution

在 `ExecProcNode()` 生命周期中被调用。当节点第一次被执行时：

- 调用 `tuplesort_begin_heap()` 初始化缓存排序结构
- 在一个死循环中不断对子节点调用 `ExecProcNode()` 获取元组，调用 `tuplesort_puttupleslot()` 将元组放入缓存排序结构中，直到子节点返回空元组
- 调用 `tuplesort_performsort()` 完成排序
- 将节点的 `sort_Done` 设置为 `true`

之后再进入节点时，只需要调用 `tuplesort_gettupleslot()` 从缓存排序结构中依次获取排序后的元组即可：

```c
/* ----------------------------------------------------------------
 *      ExecSort
 *
 *      Sorts tuples from the outer subtree of the node using tuplesort,
 *      which saves the results in a temporary file or memory. After the
 *      initial call, returns a tuple from the file with each call.
 *
 *      Conditions:
 *        -- none.
 *
 *      Initial States:
 *        -- the outer child is prepared to return the first tuple.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecSort(PlanState *pstate)
{
    SortState  *node = castNode(SortState, pstate);
    EState     *estate;
    ScanDirection dir;
    Tuplesortstate *tuplesortstate;
    TupleTableSlot *slot;

    CHECK_FOR_INTERRUPTS();

    /*
     * get state info from node
     */
    SO1_printf("ExecSort: %s\n",
               "entering routine");

    estate = node->ss.ps.state;
    dir = estate->es_direction;
    tuplesortstate = (Tuplesortstate *) node->tuplesortstate;

    /*
     * If first time through, read all tuples from outer plan and pass them to
     * tuplesort.c. Subsequent calls just fetch tuples from tuplesort.
     */

    if (!node->sort_Done)
    {
        Sort       *plannode = (Sort *) node->ss.ps.plan;
        PlanState  *outerNode;
        TupleDesc   tupDesc;

        SO1_printf("ExecSort: %s\n",
                   "sorting subplan");

        /*
         * Want to scan subplan in the forward direction while creating the
         * sorted data.
         */
        estate->es_direction = ForwardScanDirection;

        /*
         * Initialize tuplesort module.
         */
        SO1_printf("ExecSort: %s\n",
                   "calling tuplesort_begin");

        outerNode = outerPlanState(node);
        tupDesc = ExecGetResultType(outerNode);

        tuplesortstate = tuplesort_begin_heap(tupDesc,
                                              plannode->numCols,
                                              plannode->sortColIdx,
                                              plannode->sortOperators,
                                              plannode->collations,
                                              plannode->nullsFirst,
                                              work_mem,
                                              NULL,
                                              node->randomAccess);
        if (node->bounded)
            tuplesort_set_bound(tuplesortstate, node->bound);
        node->tuplesortstate = (void *) tuplesortstate;

        /*
         * Scan the subplan and feed all the tuples to tuplesort.
         */

        for (;;)
        {
            slot = ExecProcNode(outerNode);

            if (TupIsNull(slot))
                break;

            tuplesort_puttupleslot(tuplesortstate, slot);
        }

        /*
         * Complete the sort.
         */
        tuplesort_performsort(tuplesortstate);

        /*
         * restore to user specified direction
         */
        estate->es_direction = dir;

        /*
         * finally set the sorted flag to true
         */
        node->sort_Done = true;
        node->bounded_Done = node->bounded;
        node->bound_Done = node->bound;
        if (node->shared_info && node->am_worker)
        {
            TuplesortInstrumentation *si;

            Assert(IsParallelWorker());
            Assert(ParallelWorkerNumber <= node->shared_info->num_workers);
            si = &node->shared_info->sinstrument[ParallelWorkerNumber];
            tuplesort_get_stats(tuplesortstate, si);
        }
        SO1_printf("ExecSort: %s\n", "sorting done");
    }

    SO1_printf("ExecSort: %s\n",
               "retrieving tuple from tuplesort");

    /*
     * Get the first or next tuple from tuplesort. Returns NULL if no more
     * tuples.  Note that we only rely on slot tuple remaining valid until the
     * next fetch from the tuplesort.
     */
    slot = node->ss.ps.ps_ResultTupleSlot;
    (void) tuplesort_gettupleslot(tuplesortstate,
                                  ScanDirectionIsForward(dir),
                                  false, slot, NULL);
    return slot;
}
```

## Clean Up

在 `ExecEndNode()` 结构中被调用。其中调用 `tuplesort_end()` 释放缓存排序结构，并递归调用 `ExecEndNode()` 完成清理。

```c
/* ----------------------------------------------------------------
 *      ExecEndSort(node)
 * ----------------------------------------------------------------
 */
void
ExecEndSort(SortState *node)
{
    SO1_printf("ExecEndSort: %s\n",
               "shutting down sort node");

    /*
     * clean out the tuple table
     */
    ExecClearTuple(node->ss.ss_ScanTupleSlot);
    /* must drop pointer to sort result tuple */
    ExecClearTuple(node->ss.ps.ps_ResultTupleSlot);

    /*
     * Release tuplesort resources
     */
    if (node->tuplesortstate != NULL)
        tuplesort_end((Tuplesortstate *) node->tuplesortstate);
    node->tuplesortstate = NULL;

    /*
     * shut down the subplan
     */
    ExecEndNode(outerPlanState(node));

    SO1_printf("ExecEndSort: %s\n",
               "sort node shutdown");
}
```
