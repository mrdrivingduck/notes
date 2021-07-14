# PostgreSQL - Executor: Group

Created by : Mr Dk.

2021 / 07 / 15 0:37

Hangzhou, Zhejiang, China

---

`Group` 算子用于支持 SQL 中的 `GROUP BY` 子句。该子句的作用是把 **指定列值相等的所有元组** 合并为一个元组并返回上层。显然，为了每次能够返回一个合并后的元组，列值相等的元组应当排列在一起。所以 `Group` 节点的子节点应当是根据 `GROUP BY` 的列排序的。

## Plan Node

`Group` 的计划节点继承自 `Plan`，同时扩展了多个字段，主要与分组列有关：指明被用于分组的列数、哪几个列被用于分组，以及被用于比较列值是否相等的运算符：

```c
/* ---------------
 *   group node -
 *      Used for queries with GROUP BY (but no aggregates) specified.
 *      The input must be presorted according to the grouping columns.
 * ---------------
 */
typedef struct Group
{
    Plan        plan;
    int         numCols;        /* number of grouping columns */
    AttrNumber *grpColIdx;      /* their indexes in the target list */
    Oid        *grpOperators;   /* equality operators to compare with */
    Oid        *grpCollations;
} Group;
```

## Plan State

`GroupState` 继承了 `ScanState` 结构，从而也就继承了 `ScanState` 中与被扫描的关系相关的结构。另外扩展了用于计算分组列是否相等的 `ExprState *` 空间，以及 group scan 是否完成的标志位。

```c
/* ---------------------
 *  GroupState information
 * ---------------------
 */
typedef struct GroupState
{
    ScanState   ss;             /* its first field is NodeTag */
    ExprState  *eqfunction;     /* equality function */
    bool        grp_done;       /* indicates completion of Group scan */
} GroupState;
```

## Initialization

在 `ExecInitNode()` 生命周期中被调用。构造并初始化 `GroupState` 节点，然后对左孩子递归调用 `ExecInitNode()`。将分组列和每个列的相等运算符初始化为用于之后比较的 `ExprState *`。

```c
/* -----------------
 * ExecInitGroup
 *
 *  Creates the run-time information for the group node produced by the
 *  planner and initializes its outer subtree
 * -----------------
 */
GroupState *
ExecInitGroup(Group *node, EState *estate, int eflags)
{
    GroupState *grpstate;
    const TupleTableSlotOps *tts_ops;

    /* check for unsupported flags */
    Assert(!(eflags & (EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK)));

    /*
     * create state structure
     */
    grpstate = makeNode(GroupState);
    grpstate->ss.ps.plan = (Plan *) node;
    grpstate->ss.ps.state = estate;
    grpstate->ss.ps.ExecProcNode = ExecGroup;
    grpstate->grp_done = false;

    /*
     * create expression context
     */
    ExecAssignExprContext(estate, &grpstate->ss.ps);

    /*
     * initialize child nodes
     */
    outerPlanState(grpstate) = ExecInitNode(outerPlan(node), estate, eflags);

    /*
     * Initialize scan slot and type.
     */
    tts_ops = ExecGetResultSlotOps(outerPlanState(&grpstate->ss), NULL);
    ExecCreateScanSlotFromOuterPlan(estate, &grpstate->ss, tts_ops);

    /*
     * Initialize result slot, type and projection.
     */
    ExecInitResultTupleSlotTL(&grpstate->ss.ps, &TTSOpsVirtual);
    ExecAssignProjectionInfo(&grpstate->ss.ps, NULL);

    /*
     * initialize child expressions
     */
    grpstate->ss.ps.qual =
        ExecInitQual(node->plan.qual, (PlanState *) grpstate);

    /*
     * Precompute fmgr lookup data for inner loop
     */
    grpstate->eqfunction =
        execTuplesMatchPrepare(ExecGetResultType(outerPlanState(grpstate)),
                               node->numCols,
                               node->grpColIdx,
                               node->grpOperators,
                               node->grpCollations,
                               &grpstate->ss.ps);

    return grpstate;
}
```

## Execution

在 `ExecProcNode()` 生命周期中被调用。函数内维护一个元组槽，用于存放 **每组** 的第一个元组。一开始元组槽为空，那么对子节点递归调用 `ExecProcNode()` 获取一个元组，填充到槽中，做完选择和投影之后返回。

接下来是一个死循环，在死循环中不断对子节点递归调用 `ExecProcNode()` 获取元组，并使用分组列比较函数来判断是否与元组槽中的元组同属一个组：

- 如果孩子节点没有更多元组了，那么将 `GroupState` 中的 `grp_done` 设置为 `true` 后返回空元组 (扫描结束)
- 如果相等，由于本组第一个元组已经被返回了，因此忽略本条元组，继续扫描下一个元组
- 如果不相等，说明这条元组属于一个新的分组，那么将这条元组拷贝到元组槽中，做完选择和投影之后返回

```c
/*
 *   ExecGroup -
 *
 *      Return one tuple for each group of matching input tuples.
 */
static TupleTableSlot *
ExecGroup(PlanState *pstate)
{
    GroupState *node = castNode(GroupState, pstate);
    ExprContext *econtext;
    TupleTableSlot *firsttupleslot;
    TupleTableSlot *outerslot;

    CHECK_FOR_INTERRUPTS();

    /*
     * get state info from node
     */
    if (node->grp_done)
        return NULL;
    econtext = node->ss.ps.ps_ExprContext;

    /*
     * The ScanTupleSlot holds the (copied) first tuple of each group.
     */
    firsttupleslot = node->ss.ss_ScanTupleSlot;

    /*
     * We need not call ResetExprContext here because ExecQualAndReset() will
     * reset the per-tuple memory context once per input tuple.
     */

    /*
     * If first time through, acquire first input tuple and determine whether
     * to return it or not.
     */
    if (TupIsNull(firsttupleslot))
    {
        outerslot = ExecProcNode(outerPlanState(node));
        if (TupIsNull(outerslot))
        {
            /* empty input, so return nothing */
            node->grp_done = true;
            return NULL;
        }
        /* Copy tuple into firsttupleslot */
        ExecCopySlot(firsttupleslot, outerslot);

        /*
         * Set it up as input for qual test and projection.  The expressions
         * will access the input tuple as varno OUTER.
         */
        econtext->ecxt_outertuple = firsttupleslot;

        /*
         * Check the qual (HAVING clause); if the group does not match, ignore
         * it and fall into scan loop.
         */
        if (ExecQual(node->ss.ps.qual, econtext))
        {
            /*
             * Form and return a projection tuple using the first input tuple.
             */
            return ExecProject(node->ss.ps.ps_ProjInfo);
        }
        else
            InstrCountFiltered1(node, 1);
    }

    /*
     * This loop iterates once per input tuple group.  At the head of the
     * loop, we have finished processing the first tuple of the group and now
     * need to scan over all the other group members.
     */
    for (;;)
    {
        /*
         * Scan over all remaining tuples that belong to this group
         */
        for (;;)
        {
            outerslot = ExecProcNode(outerPlanState(node));
            if (TupIsNull(outerslot))
            {
                /* no more groups, so we're done */
                node->grp_done = true;
                return NULL;
            }

            /*
             * Compare with first tuple and see if this tuple is of the same
             * group.  If so, ignore it and keep scanning.
             */
            econtext->ecxt_innertuple = firsttupleslot;
            econtext->ecxt_outertuple = outerslot;
            if (!ExecQualAndReset(node->eqfunction, econtext))
                break;
        }

        /*
         * We have the first tuple of the next input group.  See if we want to
         * return it.
         */
        /* Copy tuple, set up as input for qual test and projection */
        ExecCopySlot(firsttupleslot, outerslot);
        econtext->ecxt_outertuple = firsttupleslot;

        /*
         * Check the qual (HAVING clause); if the group does not match, ignore
         * it and loop back to scan the rest of the group.
         */
        if (ExecQual(node->ss.ps.qual, econtext))
        {
            /*
             * Form and return a projection tuple using the first input tuple.
             */
            return ExecProject(node->ss.ps.ps_ProjInfo);
        }
        else
            InstrCountFiltered1(node, 1);
    }
}
```

## End Node

在 `ExecEndNode()` 生命周期中被调用：

1. 释放判断列值相等的表达式计算空间
2. 清理放置每组第一个元组的元组槽
3. 对左孩子节点递归调用 `ExecEndNode()`

```c
/* ------------------------
 *      ExecEndGroup(node)
 *
 * -----------------------
 */
void
ExecEndGroup(GroupState *node)
{
    PlanState  *outerPlan;

    ExecFreeExprContext(&node->ss.ps);

    /* clean up tuple table */
    ExecClearTuple(node->ss.ss_ScanTupleSlot);

    outerPlan = outerPlanState(node);
    ExecEndNode(outerPlan);
}
```

