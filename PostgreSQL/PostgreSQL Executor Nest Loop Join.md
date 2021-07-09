# PostgreSQL - Executor: Nest Loop Join

Created by : Mr Dk.

2021 / 07 / 09 22:25

Hangzhou, Zhejiang, China

---

实现关系代数中的连接操作。连接分为逻辑上的和物理上的，逻辑上的连接可以由物理上的连接来实现，每种物理连接都有其可以实现的逻辑连接类型。

## 逻辑连接

PostgreSQL 中已经定义了如下几种逻辑 join 类型：

```c
/*
 * JoinType -
 *    enums for types of relation joins
 *
 * JoinType determines the exact semantics of joining two relations using
 * a matching qualification.  For example, it tells what to do with a tuple
 * that has no match in the other relation.
 *
 * This is needed in both parsenodes.h and plannodes.h, so put it here...
 */
typedef enum JoinType
{
    /*
     * The canonical kinds of joins according to the SQL JOIN syntax. Only
     * these codes can appear in parser output (e.g., JoinExpr nodes).
     */
    JOIN_INNER,                 /* matching tuple pairs only */
    JOIN_LEFT,                  /* pairs + unmatched LHS tuples */
    JOIN_FULL,                  /* pairs + unmatched LHS + unmatched RHS */
    JOIN_RIGHT,                 /* pairs + unmatched RHS tuples */

    /*
     * Semijoins and anti-semijoins (as defined in relational theory) do not
     * appear in the SQL JOIN syntax, but there are standard idioms for
     * representing them (e.g., using EXISTS).  The planner recognizes these
     * cases and converts them to joins.  So the planner and executor must
     * support these codes.  NOTE: in JOIN_SEMI output, it is unspecified
     * which matching RHS row is joined to.  In JOIN_ANTI output, the row is
     * guaranteed to be null-extended.
     */
    JOIN_SEMI,                  /* 1 copy of each LHS row that has match(es) */
    JOIN_ANTI,                  /* 1 copy of each LHS row that has no match */

    /*
     * These codes are used internally in the planner, but are not supported
     * by the executor (nor, indeed, by most of the planner).
     */
    JOIN_UNIQUE_OUTER,          /* LHS path must be made unique */
    JOIN_UNIQUE_INNER           /* RHS path must be made unique */

    /*
     * We might need additional join types someday.
     */
} JoinType;
```

以 T1 JOIN T2 为例 (T1 为左，T2 为右)：

- Inner join：内连接，T1 中所有元组与 T2 中 **满足条件的元组** 连接
- Left (outer) join：在内连接基础上，为找不到可连接 T2 元组的 T1 元组，用一个空元组连接
- Right (outer) join：在内连接基础上，为找不到可连接 T1 元组的 T2 元组，用一个空元组连接
- Full (outer) join：在内连接基础上，为找不到可连接的 T1/T2 元组，用一个空元组连接
- Semi join：当 T1 元组能够在 T2 中找到一个满足连接条件的元组时，返回 T1 元组，不连接，用于实现 `EXISTS`
- Anti join：当 T1 元组不能在 T2 中找到一个满足连接条件的元组时，返回 T1 元组与空元组的连接，用于实现 `NOT EXISTS`

## 物理连接

在 PostgreSQL 中，实现了以下三种物理 join 操作：

- Nest loop join：嵌套循环连接
- Merge join：归并连接，能够实现上述所有逻辑连接
- Hash join：哈希连接

除了归并连接，其它连接只能实现内连接、左外连接、半连接和反连接。

## Super Plan Node

Join 也对应一个计划节点，继承自 `Plan` 结构体。由于 join 操作涉及两个关系，显然节点的左右孩子都会被使用到。`Join` 节点的结构体定义如下：

```c
/* ----------------
 *      Join node
 *
 * jointype:    rule for joining tuples from left and right subtrees
 * inner_unique each outer tuple can match to no more than one inner tuple
 * joinqual:    qual conditions that came from JOIN/ON or JOIN/USING
 *              (plan.qual contains conditions that came from WHERE)
 *
 * When jointype is INNER, joinqual and plan.qual are semantically
 * interchangeable.  For OUTER jointypes, the two are *not* interchangeable;
 * only joinqual is used to determine whether a match has been found for
 * the purpose of deciding whether to generate null-extended tuples.
 * (But plan.qual is still applied before actually returning a tuple.)
 * For an outer join, only joinquals are allowed to be used as the merge
 * or hash condition of a merge or hash join.
 *
 * inner_unique is set if the joinquals are such that no more than one inner
 * tuple could match any given outer tuple.  This allows the executor to
 * skip searching for additional matches.  (This must be provable from just
 * the joinquals, ignoring plan.qual, due to where the executor tests it.)
 * ----------------
 */
typedef struct Join
{
    Plan        plan;
    JoinType    jointype;
    bool        inner_unique;
    List       *joinqual;       /* JOIN quals (in addition to plan.qual) */
} Join;
```

其中：

- `jointype` 指示连接类型
- `inner_unique` 指示只有一个内元组会和外元组匹配 (执行器可以根据这个标志快速结束一轮内循环)
- `joinqual` 是除了计划节点的选择条件以外的选择条件，主要在外连接中被用到

## Super Plan State

Join 节点的 plan state 也继承自 `PlanState` 结构，里面的内容基本上是 `Join` 结构体的复制：

```c
/* ----------------
 *   JoinState information
 *
 *      Superclass for state nodes of join plans.
 * ----------------
 */
typedef struct JoinState
{
    PlanState   ps;
    JoinType    jointype;
    bool        single_match;   /* True if we should skip to next outer tuple
                                 * after finding one inner match */
    ExprState  *joinqual;       /* JOIN quals (in addition to ps.qual) */
} JoinState;
```

---

## Nest Loop Join

看看最经典的嵌套循环连接是怎么实现的。抽象来说，嵌套循环连接类似一个双层循环，左关系为外层循环条件，右关系为内层循环条件。具体如何实现内连接/左外连接等，需要看代码。

### Plan Node

首先观察嵌套循环连接的计划节点结构。除了扩展了一个参数以外，完全继承自 `Join` 结构：

```c
/* ----------------
 *      nest loop join node
 *
 * The nestParams list identifies any executor Params that must be passed
 * into execution of the inner subplan carrying values from the current row
 * of the outer subplan.  Currently we restrict these values to be simple
 * Vars, but perhaps someday that'd be worth relaxing.  (Note: during plan
 * creation, the paramval can actually be a PlaceHolderVar expression; but it
 * must be a Var with varno OUTER_VAR by the time it gets to the executor.)
 * ----------------
 */
typedef struct NestLoop
{
    Join        join;
    List       *nestParams;     /* list of NestLoopParam nodes */
} NestLoop;

typedef struct NestLoopParam
{
    NodeTag     type;
    int         paramno;        /* number of the PARAM_EXEC Param to set */
    Var        *paramval;       /* outer-relation Var to assign to Param */
} NestLoopParam;
```

其中扩展的 `nestParams` 链表是目前外层循环的元组传递给内层循环的执行器参数。

### Plan State

嵌套循环连接的 plan state 定义如下：

```c
/* ----------------
 *   NestLoopState information
 *
 *      NeedNewOuter       true if need new outer tuple on next call
 *      MatchedOuter       true if found a join match for current outer tuple
 *      NullInnerTupleSlot prepared null tuple for left outer joins
 * ----------------
 */
typedef struct NestLoopState
{
    JoinState   js;             /* its first field is NodeTag */
    bool        nl_NeedNewOuter;
    bool        nl_MatchedOuter;
    TupleTableSlot *nl_NullInnerTupleSlot;
} NestLoopState;
```

扩展的字段含义如下：

- `nl_NeedNewOuter` 指示是否需要下一个外层循环元组 (即内层循环是否结束)
- `nl_MatchedOuter` 指示是否找到了一个与当前外层循环元组匹配的内层循环元组
- `nl_NullInnerTupleSlot` 是为左外连接准备的空元组

### Executor Initialization

在 `ExecInitNode()` 生命周期中调用 `ExecInitNestLoop`。与大部分计划节点初始化的套路一致：

1. 首先构造一个 `NestLoopState` 节点，为 plan state 节点设置好执行回调函数
2. 为节点创建表达式上下文
3. 分别为左右孩子节点 (join 两侧的 relation) 递归调用 `ExecInitNode()`
4. 初始化返回元组槽，初始化投影信息
5. 初始化选择条件 (包括节点自己的和 join 中扩展的)
6. 在 plan state 中设置 join 类型
7. 根据 join 类型，设置 plan state 中的 `single_match`
8. 根据 join 类型，对左外连接和反连接，初始化用于 join 的空元组
9. 初始化 `nl_NeedNewOuter` 和 `nl_MatchedOuter` 为连接开始前的初始状态 (需要获取第一个外层元组，外层元组还未找到一个匹配的内层元组)

```c
/* ----------------------------------------------------------------
 *      ExecInitNestLoop
 * ----------------------------------------------------------------
 */
NestLoopState *
ExecInitNestLoop(NestLoop *node, EState *estate, int eflags)
{
    NestLoopState *nlstate;

    /* check for unsupported flags */
    Assert(!(eflags & (EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK)));

    NL1_printf("ExecInitNestLoop: %s\n",
               "initializing node");

    /*
     * create state structure
     */
    nlstate = makeNode(NestLoopState);
    nlstate->js.ps.plan = (Plan *) node;
    nlstate->js.ps.state = estate;
    nlstate->js.ps.ExecProcNode = ExecNestLoop;

    /*
     * Miscellaneous initialization
     *
     * create expression context for node
     */
    ExecAssignExprContext(estate, &nlstate->js.ps);

    /*
     * initialize child nodes
     *
     * If we have no parameters to pass into the inner rel from the outer,
     * tell the inner child that cheap rescans would be good.  If we do have
     * such parameters, then there is no point in REWIND support at all in the
     * inner child, because it will always be rescanned with fresh parameter
     * values.
     */
    outerPlanState(nlstate) = ExecInitNode(outerPlan(node), estate, eflags);
    if (node->nestParams == NIL)
        eflags |= EXEC_FLAG_REWIND;
    else
        eflags &= ~EXEC_FLAG_REWIND;
    innerPlanState(nlstate) = ExecInitNode(innerPlan(node), estate, eflags);

    /*
     * Initialize result slot, type and projection.
     */
    ExecInitResultTupleSlotTL(&nlstate->js.ps, &TTSOpsVirtual);
    ExecAssignProjectionInfo(&nlstate->js.ps, NULL);

    /*
     * initialize child expressions
     */
    nlstate->js.ps.qual =
        ExecInitQual(node->join.plan.qual, (PlanState *) nlstate);
    nlstate->js.jointype = node->join.jointype;
    nlstate->js.joinqual =
        ExecInitQual(node->join.joinqual, (PlanState *) nlstate);

    /*
     * detect whether we need only consider the first matching inner tuple
     */
    nlstate->js.single_match = (node->join.inner_unique ||
                                node->join.jointype == JOIN_SEMI);

    /* set up null tuples for outer joins, if needed */
    switch (node->join.jointype)
    {
        case JOIN_INNER:
        case JOIN_SEMI:
            break;
        case JOIN_LEFT:
        case JOIN_ANTI:
            nlstate->nl_NullInnerTupleSlot =
                ExecInitNullTupleSlot(estate,
                                      ExecGetResultType(innerPlanState(nlstate)),
                                      &TTSOpsVirtual);
            break;
        default:
            elog(ERROR, "unrecognized join type: %d",
                 (int) node->join.jointype);
    }

    /*
     * finally, wipe the current outer tuple clean.
     */
    nlstate->nl_NeedNewOuter = true;
    nlstate->nl_MatchedOuter = false;

    NL1_printf("ExecInitNestLoop: %s\n",
               "node initialized");

    return nlstate;
}
```

### Execution

在 `ExecProcNode()` 生命周期中调用 `ExecNestLoop()`。其核心是一个死循环，在循环内：

1. 如果需要，首先对左孩子递归调用 `ExecProcNode()` 获取一个外层循环元组
2. 设置好暂不需要外层元组的标志，将外层循环的参数传入内层元组
3. 开始对右孩子递归调用 `ExecProcNode()` 获取一个内层循环元组
    1. 如果内层循环元组为空，那么说明内层循环结束，需要外层循环的前进到下一个元组了；但需要查看一下外层循环元组是否匹配过内层循环元组，如果没有，且连接类型为左外连接或反连接，那么就将空元组作为内层循环元组与外层循环元组做一次 join，如果能够通过 plan node 的选择条件，就投影并返回
    2. 如果内层循环元组不为空，那么判断是否通过 `Join` 结构中定义的选择条件，如果通过则找到了一对可以 join 的内外层元组
        1. 设置外层循环元组的 `nl_MatchedOuter` 为 `true` (已被内层循环元组匹配过)
        2. 如果是 anti join，由于外层循环元组已经被成功匹配，因此外层循环可以推进到下一个元组了
            > 它很怨妇，希望外层循环最好永远别被匹配，既然匹配上了那就还是向前看吧
        3. 如果 join 被设置为 `single_match`，那么剩余内层循环元组也不需要被扫描了，直接快进到下一个外层循环元组
            > 相亲，一人只能找一个老婆，这位男士和女嘉宾牵手成功，那么剩下的女嘉宾也不必考虑了
        4. 如果能够通过 plan node 中的选择条件，则投影并返回

循环结束，两个关系中的所有元组都被 join 完毕。

```c
/* ----------------------------------------------------------------
 *      ExecNestLoop(node)
 *
 * old comments
 *      Returns the tuple joined from inner and outer tuples which
 *      satisfies the qualification clause.
 *
 *      It scans the inner relation to join with current outer tuple.
 *
 *      If none is found, next tuple from the outer relation is retrieved
 *      and the inner relation is scanned from the beginning again to join
 *      with the outer tuple.
 *
 *      NULL is returned if all the remaining outer tuples are tried and
 *      all fail to join with the inner tuples.
 *
 *      NULL is also returned if there is no tuple from inner relation.
 *
 *      Conditions:
 *        -- outerTuple contains current tuple from outer relation and
 *           the right son(inner relation) maintains "cursor" at the tuple
 *           returned previously.
 *              This is achieved by maintaining a scan position on the outer
 *              relation.
 *
 *      Initial States:
 *        -- the outer child and the inner child
 *             are prepared to return the first tuple.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecNestLoop(PlanState *pstate)
{
    NestLoopState *node = castNode(NestLoopState, pstate);
    NestLoop   *nl;
    PlanState  *innerPlan;
    PlanState  *outerPlan;
    TupleTableSlot *outerTupleSlot;
    TupleTableSlot *innerTupleSlot;
    ExprState  *joinqual;
    ExprState  *otherqual;
    ExprContext *econtext;
    ListCell   *lc;

    CHECK_FOR_INTERRUPTS();

    /*
     * get information from the node
     */
    ENL1_printf("getting info from node");

    nl = (NestLoop *) node->js.ps.plan;
    joinqual = node->js.joinqual;
    otherqual = node->js.ps.qual;
    outerPlan = outerPlanState(node);
    innerPlan = innerPlanState(node);
    econtext = node->js.ps.ps_ExprContext;

    /*
     * Reset per-tuple memory context to free any expression evaluation
     * storage allocated in the previous tuple cycle.
     */
    ResetExprContext(econtext);

    /*
     * Ok, everything is setup for the join so now loop until we return a
     * qualifying join tuple.
     */
    ENL1_printf("entering main loop");

    for (;;)
    {
        /*
         * If we don't have an outer tuple, get the next one and reset the
         * inner scan.
         */
        if (node->nl_NeedNewOuter)
        {
            ENL1_printf("getting new outer tuple");
            outerTupleSlot = ExecProcNode(outerPlan);

            /*
             * if there are no more outer tuples, then the join is complete..
             */
            if (TupIsNull(outerTupleSlot))
            {
                ENL1_printf("no outer tuple, ending join");
                return NULL;
            }

            ENL1_printf("saving new outer tuple information");
            econtext->ecxt_outertuple = outerTupleSlot;
            node->nl_NeedNewOuter = false;
            node->nl_MatchedOuter = false;

            /*
             * fetch the values of any outer Vars that must be passed to the
             * inner scan, and store them in the appropriate PARAM_EXEC slots.
             */
            foreach(lc, nl->nestParams)
            {
                NestLoopParam *nlp = (NestLoopParam *) lfirst(lc);
                int         paramno = nlp->paramno;
                ParamExecData *prm;

                prm = &(econtext->ecxt_param_exec_vals[paramno]);
                /* Param value should be an OUTER_VAR var */
                Assert(IsA(nlp->paramval, Var));
                Assert(nlp->paramval->varno == OUTER_VAR);
                Assert(nlp->paramval->varattno > 0);
                prm->value = slot_getattr(outerTupleSlot,
                                          nlp->paramval->varattno,
                                          &(prm->isnull));
                /* Flag parameter value as changed */
                innerPlan->chgParam = bms_add_member(innerPlan->chgParam,
                                                     paramno);
            }

            /*
             * now rescan the inner plan
             */
            ENL1_printf("rescanning inner plan");
            ExecReScan(innerPlan);
        }

        /*
         * we have an outerTuple, try to get the next inner tuple.
         */
        ENL1_printf("getting new inner tuple");

        innerTupleSlot = ExecProcNode(innerPlan);
        econtext->ecxt_innertuple = innerTupleSlot;

        if (TupIsNull(innerTupleSlot))
        {
            ENL1_printf("no inner tuple, need new outer tuple");

            node->nl_NeedNewOuter = true;

            if (!node->nl_MatchedOuter &&
                (node->js.jointype == JOIN_LEFT ||
                 node->js.jointype == JOIN_ANTI))
            {
                /*
                 * We are doing an outer join and there were no join matches
                 * for this outer tuple.  Generate a fake join tuple with
                 * nulls for the inner tuple, and return it if it passes the
                 * non-join quals.
                 */
                econtext->ecxt_innertuple = node->nl_NullInnerTupleSlot;

                ENL1_printf("testing qualification for outer-join tuple");

                if (otherqual == NULL || ExecQual(otherqual, econtext))
                {
                    /*
                     * qualification was satisfied so we project and return
                     * the slot containing the result tuple using
                     * ExecProject().
                     */
                    ENL1_printf("qualification succeeded, projecting tuple");

                    return ExecProject(node->js.ps.ps_ProjInfo);
                }
                else
                    InstrCountFiltered2(node, 1);
            }

            /*
             * Otherwise just return to top of loop for a new outer tuple.
             */
            continue;
        }

        /*
         * at this point we have a new pair of inner and outer tuples so we
         * test the inner and outer tuples to see if they satisfy the node's
         * qualification.
         *
         * Only the joinquals determine MatchedOuter status, but all quals
         * must pass to actually return the tuple.
         */
        ENL1_printf("testing qualification");

        if (ExecQual(joinqual, econtext))
        {
            node->nl_MatchedOuter = true;

            /* In an antijoin, we never return a matched tuple */
            if (node->js.jointype == JOIN_ANTI)
            {
                node->nl_NeedNewOuter = true;
                continue;       /* return to top of loop */
            }

            /*
             * If we only need to join to the first matching inner tuple, then
             * consider returning this one, but after that continue with next
             * outer tuple.
             */
            if (node->js.single_match)
                node->nl_NeedNewOuter = true;

            if (otherqual == NULL || ExecQual(otherqual, econtext))
            {
                /*
                 * qualification was satisfied so we project and return the
                 * slot containing the result tuple using ExecProject().
                 */
                ENL1_printf("qualification succeeded, projecting tuple");

                return ExecProject(node->js.ps.ps_ProjInfo);
            }
            else
                InstrCountFiltered2(node, 1);
        }
        else
            InstrCountFiltered1(node, 1);

        /*
         * Tuple fails qual, so free per-tuple memory and try again.
         */
        ResetExprContext(econtext);

        ENL1_printf("qualification failed, looping");
    }
}
```

### Executor End

在 `ExecEndNode()` 生命周期中被调用，主要做一些清理工作。

```c
/* ----------------------------------------------------------------
 *      ExecEndNestLoop
 *
 *      closes down scans and frees allocated storage
 * ----------------------------------------------------------------
 */
void
ExecEndNestLoop(NestLoopState *node)
{
    NL1_printf("ExecEndNestLoop: %s\n",
               "ending node processing");

    /*
     * Free the exprcontext
     */
    ExecFreeExprContext(&node->js.ps);

    /*
     * clean out the tuple table
     */
    ExecClearTuple(node->js.ps.ps_ResultTupleSlot);

    /*
     * close down subplans
     */
    ExecEndNode(outerPlanState(node));
    ExecEndNode(innerPlanState(node));

    NL1_printf("ExecEndNestLoop: %s\n",
               "node processing ended");
}
```

## 思考

为什么嵌套循环连接不能实现 right outer join 和 full outer join 呢？这是它固有的实现决定的。由于左关系在外层循环，右关系在内层循环，左关系重复扫描右关系，因此左连接元组的所有扫描是连续的、stateful 的，可以获知左连接元组是否在右关系中找到了匹配元组；而右连接元组的所有扫描是离散的、stateless 的，不可获知右连接元组是否与左关系存在匹配 (除非用额外的空间记录？)。

