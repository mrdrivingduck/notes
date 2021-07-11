# PostgreSQL - Executor: Unique

Created by : Mr Dk.

2021 / 07 / 11 21:44

Hangzhou, Zhejiang, China

---

`Unique` 计划节点用于元组的去重。众所周知，去重操作基于一个很重要的前提：**输入数据有序**。如果已知输入数据有序，那么去重的实现方式将非常直截了当：缓存前一个元组，如果当前元组与前一个元组相同，就丢弃这个重复元组。可以得知，`Unique` 节点会被放在一个 `Sort` 节点的上层。

这也是一个很简单的节点，不对元组做选择和投影操作。

## Plan Node

`Unique` 节点继承自 `Plan` 结构体，同时扩展了去重相关的信息。由于判断去重实际上是判断是否相等，因此去重信息主要包含用于比较的列信息，以及比较操作的信息：

```c
/* ----------------
 *      unique node
 * ----------------
 */
typedef struct Unique
{
    Plan        plan;
    int         numCols;        /* number of columns to check for uniqueness */
    AttrNumber *uniqColIdx;     /* their indexes in the target list */
    Oid        *uniqOperators;  /* equality operators to compare with */
    Oid        *uniqCollations; /* collations for equality comparisons */
} Unique;
```

## Plan State

`UniqueState` 继承自 `PlanState` 结构，同时扩展了用于判断是否相等的 `ExprState *`：

```c
/* ----------------
 *   UniqueState information
 *
 *      Unique nodes are used "on top of" sort nodes to discard
 *      duplicate tuples returned from the sort phase.  Basically
 *      all it does is compare the current tuple from the subplan
 *      with the previously fetched tuple (stored in its result slot).
 *      If the two are identical in all interesting fields, then
 *      we just fetch another tuple from the sort and try again.
 * ----------------
 */
typedef struct UniqueState
{
    PlanState   ps;             /* its first field is NodeTag */
    ExprState  *eqfunction;     /* tuple equality qual */
} UniqueState;
```

## Initialization

在 `ExecInitNode()` 生命周期中被调用，主要工作包括分配 `UniqueState` 节点并初始化，然后递归调用 `ExecInitNode()`。将 `Unique` 节点中与比较相关的信息传递给 `execTuplesMatchPrepare()` 函数，返回 `ExprState` 结构并将指针设置到 `UniqueState` 中。

```c
/* ----------------------------------------------------------------
 *      ExecInitUnique
 *
 *      This initializes the unique node state structures and
 *      the node's subplan.
 * ----------------------------------------------------------------
 */
UniqueState *
ExecInitUnique(Unique *node, EState *estate, int eflags)
{
    UniqueState *uniquestate;

    /* check for unsupported flags */
    Assert(!(eflags & (EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK)));

    /*
     * create state structure
     */
    uniquestate = makeNode(UniqueState);
    uniquestate->ps.plan = (Plan *) node;
    uniquestate->ps.state = estate;
    uniquestate->ps.ExecProcNode = ExecUnique;

    /*
     * create expression context
     */
    ExecAssignExprContext(estate, &uniquestate->ps);

    /*
     * then initialize outer plan
     */
    outerPlanState(uniquestate) = ExecInitNode(outerPlan(node), estate, eflags);

    /*
     * Initialize result slot and type. Unique nodes do no projections, so
     * initialize projection info for this node appropriately.
     */
    ExecInitResultTupleSlotTL(&uniquestate->ps, &TTSOpsMinimalTuple);
    uniquestate->ps.ps_ProjInfo = NULL;

    /*
     * Precompute fmgr lookup data for inner loop
     */
    uniquestate->eqfunction =
        execTuplesMatchPrepare(ExecGetResultType(outerPlanState(uniquestate)),
                               node->numCols,
                               node->uniqColIdx,
                               node->uniqOperators,
                               node->uniqCollations,
                               &uniquestate->ps);

    return uniquestate;
}
```

## Execution

在 `ExecProcNode()` 生命周期中被调用。`UniqueState` 节点的 `ps_ResultTupleSlot` 保存了上一个返回给上层节点的元组。在死循环中不断对子节点递归调用 `ExecProcNode()` 获取一个元组，然后利用之前初始化好的比较函数将当前元组与 `ps_ResultTupleSlot` 元组进行比较。

- 如果相同，那么说明元组重复，直接忽略当前元组并扫描下一个
- 如果不同，那么说明元组从未出现过，那么将当前元组拷贝到 `ps_ResultTupleSlot` 中 (并返回给上层节点)

直到子节点返回空元组。

```c
/* ----------------------------------------------------------------
 *      ExecUnique
 * ----------------------------------------------------------------
 */
static TupleTableSlot *         /* return: a tuple or NULL */
ExecUnique(PlanState *pstate)
{
    UniqueState *node = castNode(UniqueState, pstate);
    ExprContext *econtext = node->ps.ps_ExprContext;
    TupleTableSlot *resultTupleSlot;
    TupleTableSlot *slot;
    PlanState  *outerPlan;

    CHECK_FOR_INTERRUPTS();

    /*
     * get information from the node
     */
    outerPlan = outerPlanState(node);
    resultTupleSlot = node->ps.ps_ResultTupleSlot;

    /*
     * now loop, returning only non-duplicate tuples. We assume that the
     * tuples arrive in sorted order so we can detect duplicates easily. The
     * first tuple of each group is returned.
     */
    for (;;)
    {
        /*
         * fetch a tuple from the outer subplan
         */
        slot = ExecProcNode(outerPlan);
        if (TupIsNull(slot))
        {
            /* end of subplan, so we're done */
            ExecClearTuple(resultTupleSlot);
            return NULL;
        }

        /*
         * Always return the first tuple from the subplan.
         */
        if (TupIsNull(resultTupleSlot))
            break;

        /*
         * Else test if the new tuple and the previously returned tuple match.
         * If so then we loop back and fetch another new tuple from the
         * subplan.
         */
        econtext->ecxt_innertuple = slot;
        econtext->ecxt_outertuple = resultTupleSlot;
        if (!ExecQualAndReset(node->eqfunction, econtext))
            break;
    }

    /*
     * We have a new tuple different from the previous saved tuple (if any).
     * Save it and return it.  We must copy it because the source subplan
     * won't guarantee that this source tuple is still accessible after
     * fetching the next source tuple.
     */
    return ExecCopySlot(resultTupleSlot, slot);
}
```

## Clean Up

在 `ExecEndNode()` 生命周期函数中被调用。

```c
/* ----------------------------------------------------------------
 *      ExecEndUnique
 *
 *      This shuts down the subplan and frees resources allocated
 *      to this node.
 * ----------------------------------------------------------------
 */
void
ExecEndUnique(UniqueState *node)
{
    /* clean up tuple table */
    ExecClearTuple(node->ps.ps_ResultTupleSlot);

    ExecFreeExprContext(&node->ps);

    ExecEndNode(outerPlanState(node));
}
```

