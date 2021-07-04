# PostgreSQL - Executor: Result

Created by : Mr Dk.

2021 / 07 / 04 16:41

Hangzhou, Zhejiang, China

---

Result 节点的作用，概括来说用于承载表达式的执行结果。细分有两种用途：

- 承载不需要进行表扫描的 SQL 语句执行结果
- 承载常量选择条件的执行结果，用于优化选择条件为常量的查询

不用进行表扫描的 SQL 语句包括没有 `FROM` 的 `SELECT` 语句，或者带有 `VALUES` 的元组构造语句：

```sql
select 1 * 2;
insert into emp values ('mike', 15000)
```

查询条件为常量的查询。此时，表达式的结果只需要被计算一次：如果计算为假，那么相当于直接进行一次过滤，不再需要查询出每个元组之后再和查询条件进行判断了。

```sql
select * from emp where 2 > 1
```

```c
/*-------------------------------------------------------------------------
 *
 * nodeResult.c
 *    support for constant nodes needing special code.
 *
 * DESCRIPTION
 *
 *      Result nodes are used in queries where no relations are scanned.
 *      Examples of such queries are:
 *
 *              select 1 * 2
 *
 *              insert into emp values ('mike', 15000)
 *
 *      (Remember that in an INSERT or UPDATE, we need a plan tree that
 *      generates the new rows.)
 *
 *      Result nodes are also used to optimise queries with constant
 *      qualifications (ie, quals that do not depend on the scanned data),
 *      such as:
 *
 *              select * from emp where 2 > 1
 *
 *      In this case, the plan generated is
 *
 *                      Result  (with 2 > 1 qual)
 *                      /
 *                 SeqScan (emp.*)
 *
 *      At runtime, the Result node evaluates the constant qual once,
 *      which is shown by EXPLAIN as a One-Time Filter.  If it's
 *      false, we can return an empty result set without running the
 *      controlled plan at all.  If it's true, we run the controlled
 *      plan normally and pass back the results.
 *
 *
 * Portions Copyright (c) 1996-2021, PostgreSQL Global Development Group
 * Portions Copyright (c) 1994, Regents of the University of California
 *
 * IDENTIFICATION
 *    src/backend/executor/nodeResult.c
 *
 *-------------------------------------------------------------------------
 */
```

## Plan Node

Result 的计划节点定义如下。其中，扩展出的 `resconstantqual` 是只需要被计算一次的常量表达式。因为表达式的结果不被 *outer plan* (当前节点的左子树) 影响，所以只需要被计算一次即可。

```c
/* ----------------
 *   Result node -
 *      If no outer plan, evaluate a variable-free targetlist.
 *      If outer plan, return tuples from outer plan (after a level of
 *      projection as shown by targetlist).
 *
 * If resconstantqual isn't NULL, it represents a one-time qualification
 * test (i.e., one that doesn't depend on any variables from the outer plan,
 * so needs to be evaluated only once).
 * ----------------
 */
typedef struct Result
{
    Plan        plan;
    Node       *resconstantqual;
} Result;
```

以下相应的 Plan State 结构体定义。其中扩展的字段包括：

- `resconstantqual`：对常量表达式进行计算的 `ExprState` 结构
- `rs_checkqual`：指示是否需要对常量表达式进行计算
- `rs_done`：指示查询是否完成的标志位

```c
/* ----------------
 *   ResultState information
 * ----------------
 */
typedef struct ResultState
{
    PlanState   ps;             /* its first field is NodeTag */
    ExprState  *resconstantqual;
    bool        rs_done;        /* are we done? */
    bool        rs_checkqual;   /* do we need to check the qual? */
} ResultState;
```

## Initialization

在 `ExecInitNode()` 生命周期中被调用。该函数分配 `ResultState` 结构体，然后填写结构体字段进行初始化。为左孩子节点递归调用 `ExecInitNode()` 进行初始化，右孩子节点必须为空 (优化器保证)。最终，还要对节点级别的选择条件调用 `ExecInitQual()` 分配 `ExprState` 结构。对于一般的节点来说，只需要为 `Plan` 结构中的 `qual` 分配空间就可以了；而对于 Result 节点来说，还需要对 `Result` 结构扩展的只执行一次的表达式 `resconstantqual` 分配 `ExprState`。

```c
/* ----------------------------------------------------------------
 *      ExecInitResult
 *
 *      Creates the run-time state information for the result node
 *      produced by the planner and initializes outer relations
 *      (child nodes).
 * ----------------------------------------------------------------
 */
ResultState *
ExecInitResult(Result *node, EState *estate, int eflags)
{
    ResultState *resstate;

    /* check for unsupported flags */
    Assert(!(eflags & (EXEC_FLAG_MARK | EXEC_FLAG_BACKWARD)) ||
           outerPlan(node) != NULL);

    /*
     * create state structure
     */
    resstate = makeNode(ResultState);
    resstate->ps.plan = (Plan *) node;
    resstate->ps.state = estate;
    resstate->ps.ExecProcNode = ExecResult;

    resstate->rs_done = false;
    resstate->rs_checkqual = (node->resconstantqual == NULL) ? false : true;

    /*
     * Miscellaneous initialization
     *
     * create expression context for node
     */
    ExecAssignExprContext(estate, &resstate->ps);

    /*
     * initialize child nodes
     */
    outerPlanState(resstate) = ExecInitNode(outerPlan(node), estate, eflags);

    /*
     * we don't use inner plan
     */
    Assert(innerPlan(node) == NULL);

    /*
     * Initialize result slot, type and projection.
     */
    ExecInitResultTupleSlotTL(&resstate->ps, &TTSOpsVirtual);
    ExecAssignProjectionInfo(&resstate->ps, NULL);

    /*
     * initialize child expressions
     */
    resstate->ps.qual =
        ExecInitQual(node->plan.qual, (PlanState *) resstate);
    resstate->resconstantqual =
        ExecInitQual((List *) node->resconstantqual, (PlanState *) resstate);

    return resstate;
}
```

## Execution

在 `ExecProcNode()` 生命周期中被调用。首先判断一下 `rs_checkqual` 是否需要对常量表达式进行计算，如果需要，那么调用 `ExecQual()` 进行计算，然后将标志位 reset (下次就不需要重复计算了)。如果表达式的计算结果为 `false`，则直接从该节点结束 plan tree 的遍历：因为孩子节点中返回的元组必然不可能通过常量表达式的选择过滤条件，因此将 `rs_done` 设置为 `true` 然后返回 `NULL`。

如果常量表达式计算为 `true`，那么对左孩子节点递归调用 `ExecProcNode()` 获取元组，然后进行投影处理。直到没有元组可以从左孩子节点获取时，将 `rs_done` 设置为 `true`。

```c
/* ----------------------------------------------------------------
 *      ExecResult(node)
 *
 *      returns the tuples from the outer plan which satisfy the
 *      qualification clause.  Since result nodes with right
 *      subtrees are never planned, we ignore the right subtree
 *      entirely (for now).. -cim 10/7/89
 *
 *      The qualification containing only constant clauses are
 *      checked first before any processing is done. It always returns
 *      'nil' if the constant qualification is not satisfied.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecResult(PlanState *pstate)
{
    ResultState *node = castNode(ResultState, pstate);
    TupleTableSlot *outerTupleSlot;
    PlanState  *outerPlan;
    ExprContext *econtext;

    CHECK_FOR_INTERRUPTS();

    econtext = node->ps.ps_ExprContext;

    /*
     * check constant qualifications like (2 > 1), if not already done
     */
    if (node->rs_checkqual)
    {
        bool        qualResult = ExecQual(node->resconstantqual, econtext);

        node->rs_checkqual = false;
        if (!qualResult)
        {
            node->rs_done = true;
            return NULL;
        }
    }

    /*
     * Reset per-tuple memory context to free any expression evaluation
     * storage allocated in the previous tuple cycle.
     */
    ResetExprContext(econtext);

    /*
     * if rs_done is true then it means that we were asked to return a
     * constant tuple and we already did the last time ExecResult() was
     * called, OR that we failed the constant qual check. Either way, now we
     * are through.
     */
    if (!node->rs_done)
    {
        outerPlan = outerPlanState(node);

        if (outerPlan != NULL)
        {
            /*
             * retrieve tuples from the outer plan until there are no more.
             */
            outerTupleSlot = ExecProcNode(outerPlan);

            if (TupIsNull(outerTupleSlot))
                return NULL;

            /*
             * prepare to compute projection expressions, which will expect to
             * access the input tuples as varno OUTER.
             */
            econtext->ecxt_outertuple = outerTupleSlot;
        }
        else
        {
            /*
             * if we don't have an outer plan, then we are just generating the
             * results from a constant target list.  Do it only once.
             */
            node->rs_done = true;
        }

        /* form the result tuple using ExecProject(), and return it */
        return ExecProject(node->ps.ps_ProjInfo);
    }

    return NULL;
}
```

## End

在 `ExecEndNode()` 生命周期中被调用，主要工作时清理本级 plan state 中的内存，然后对左孩子节点递归调用 `ExecEndNode()`：

```c
/* ----------------------------------------------------------------
 *      ExecEndResult
 *
 *      frees up storage allocated through C routines
 * ----------------------------------------------------------------
 */
void
ExecEndResult(ResultState *node)
{
    /*
     * Free the exprcontext
     */
    ExecFreeExprContext(&node->ps);

    /*
     * clean out the tuple table
     */
    ExecClearTuple(node->ps.ps_ResultTupleSlot);

    /*
     * shut down subplans
     */
    ExecEndNode(outerPlanState(node));
}
```

