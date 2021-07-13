# PostgreSQL - Executor: Limit

Created by : Mr Dk.

2021 / 07 / 14 01:02

Hangzhou, Zhejiang, China

---

`Limit` 节点用于限制返回的元组行数。当 `Limit` 节点从孩子节点获取指定数量的元组后，就结束查询，不再递归调用 `ExecProcNode()` 获取元组了。

## Plan Node

`Limit` 节点还真没有看起来这么简单：

```c
/*
 * LimitOption -
 *  LIMIT option of query
 *
 * This is needed in both parsenodes.h and plannodes.h, so put it here...
 */
typedef enum LimitOption
{
    LIMIT_OPTION_COUNT,         /* FETCH FIRST... ONLY */
    LIMIT_OPTION_WITH_TIES,     /* FETCH FIRST... WITH TIES */
    LIMIT_OPTION_DEFAULT,       /* No limit present */
} LimitOption;

/* ----------------
 *      limit node
 *
 * Note: as of Postgres 8.2, the offset and count expressions are expected
 * to yield int8, rather than int4 as before.
 * ----------------
 */
typedef struct Limit
{
    Plan        plan;
    Node       *limitOffset;    /* OFFSET parameter, or NULL if none */
    Node       *limitCount;     /* COUNT parameter, or NULL if none */
    LimitOption limitOption;    /* limit type */
    int         uniqNumCols;    /* number of columns to check for similarity  */
    AttrNumber *uniqColIdx;     /* their indexes in the target list */
    Oid        *uniqOperators;  /* equality operators to compare with */
    Oid        *uniqCollations; /* collations for equality comparisons */
} Limit;
```

其中，`limitOffset` 和 `limitCount` 分别表示从第几个元组开始返回，以及返回多少个元组。该值将在运行时才能确定。

几个 `unique` 相关的变量用于支持 `WITH TIES` (并列) 类型的 `Limit`。既然要知道两行是否并列，那么肯定要基于某几列的值做一个计算，并用一个函数来判断它们是否相等。如果相等，才是并列的。

## Plan State

`LimitState` 定义了状态机，执行器根据节点的状态执行相应的代码：

```c
/* ----------------
 *   LimitState information
 *
 *      Limit nodes are used to enforce LIMIT/OFFSET clauses.
 *      They just select the desired subrange of their subplan's output.
 *
 * offset is the number of initial tuples to skip (0 does nothing).
 * count is the number of tuples to return after skipping the offset tuples.
 * If no limit count was specified, count is undefined and noCount is true.
 * When lstate == LIMIT_INITIAL, offset/count/noCount haven't been set yet.
 * ----------------
 */
typedef enum
{
    LIMIT_INITIAL,              /* initial state for LIMIT node */
    LIMIT_RESCAN,               /* rescan after recomputing parameters */
    LIMIT_EMPTY,                /* there are no returnable rows */
    LIMIT_INWINDOW,             /* have returned a row in the window */
    LIMIT_WINDOWEND_TIES,       /* have returned a tied row */
    LIMIT_SUBPLANEOF,           /* at EOF of subplan (within window) */
    LIMIT_WINDOWEND,            /* stepped off end of window */
    LIMIT_WINDOWSTART           /* stepped off beginning of window */
} LimitStateCond;

typedef struct LimitState
{
    PlanState   ps;             /* its first field is NodeTag */
    ExprState  *limitOffset;    /* OFFSET parameter, or NULL if none */
    ExprState  *limitCount;     /* COUNT parameter, or NULL if none */
    LimitOption limitOption;    /* limit specification type */
    int64       offset;         /* current OFFSET value */
    int64       count;          /* current COUNT, if any */
    bool        noCount;        /* if true, ignore count */
    LimitStateCond lstate;      /* state machine status, as above */
    int64       position;       /* 1-based index of last tuple returned */
    TupleTableSlot *subSlot;    /* tuple last obtained from subplan */
    ExprState  *eqfunction;     /* tuple equality qual in case of WITH TIES
                                 * option */
    TupleTableSlot *last_slot;  /* slot for evaluation of ties */
} LimitState;
```

其中维护了当前的 offset 和 count，以及用于计算两行是否相等 (with ties) 的表达式结构。

## Init Node

在 `ExecInitNode()` 生命周期中被调用。其主要工作包含：

1. 构造 `LimitState` 节点
2. 递归调用 `ExecInitNode()`
3. 初始化 offset 和 count 的表达式计算环境
4. 如果 `Limit` 节点需要支持 with ties，那么还要初始化一个存放元组的空间，以及等值计算的函数，以便作比较

```c
/* ----------------------------------------------------------------
 *      ExecInitLimit
 *
 *      This initializes the limit node state structures and
 *      the node's subplan.
 * ----------------------------------------------------------------
 */
LimitState *
ExecInitLimit(Limit *node, EState *estate, int eflags)
{
    LimitState *limitstate;
    Plan       *outerPlan;

    /* check for unsupported flags */
    Assert(!(eflags & EXEC_FLAG_MARK));

    /*
     * create state structure
     */
    limitstate = makeNode(LimitState);
    limitstate->ps.plan = (Plan *) node;
    limitstate->ps.state = estate;
    limitstate->ps.ExecProcNode = ExecLimit;

    limitstate->lstate = LIMIT_INITIAL;

    /*
     * Miscellaneous initialization
     *
     * Limit nodes never call ExecQual or ExecProject, but they need an
     * exprcontext anyway to evaluate the limit/offset parameters in.
     */
    ExecAssignExprContext(estate, &limitstate->ps);

    /*
     * initialize outer plan
     */
    outerPlan = outerPlan(node);
    outerPlanState(limitstate) = ExecInitNode(outerPlan, estate, eflags);

    /*
     * initialize child expressions
     */
    limitstate->limitOffset = ExecInitExpr((Expr *) node->limitOffset,
                                           (PlanState *) limitstate);
    limitstate->limitCount = ExecInitExpr((Expr *) node->limitCount,
                                          (PlanState *) limitstate);
    limitstate->limitOption = node->limitOption;

    /*
     * Initialize result type.
     */
    ExecInitResultTypeTL(&limitstate->ps);

    limitstate->ps.resultopsset = true;
    limitstate->ps.resultops = ExecGetResultSlotOps(outerPlanState(limitstate),
                                                    &limitstate->ps.resultopsfixed);

    /*
     * limit nodes do no projections, so initialize projection info for this
     * node appropriately
     */
    limitstate->ps.ps_ProjInfo = NULL;

    /*
     * Initialize the equality evaluation, to detect ties.
     */
    if (node->limitOption == LIMIT_OPTION_WITH_TIES)
    {
        TupleDesc   desc;
        const TupleTableSlotOps *ops;

        desc = ExecGetResultType(outerPlanState(limitstate));
        ops = ExecGetResultSlotOps(outerPlanState(limitstate), NULL);

        limitstate->last_slot = ExecInitExtraTupleSlot(estate, desc, ops);
        limitstate->eqfunction = execTuplesMatchPrepare(desc,
                                                        node->uniqNumCols,
                                                        node->uniqColIdx,
                                                        node->uniqOperators,
                                                        node->uniqCollations,
                                                        &limitstate->ps);
    }

    return limitstate;
}
```

## Node Execution

在 `ExecProcNode()` 生命周期中被调用。其主体是一个 `switch` 语句，根据节点当前的状态，执行对应的代码。

- `LIMIT_INITIAL`：节点第一个被执行，那么首先使用表达式计算 offset 和 count
- `LIMIT_RESCAN`：判断扫描方向 (正向 / 反向)，然后不断递归调用 `ExecProcNode()` 从子节点获取元组，直到 `LimitState` 中的 `position` 超过 `offset`；如果支持 `with ties`，那么还需要拷贝暂存读取到的元组用于之后的等值比较
- `LIMIT_EMPTY`：子结点不返回元组了，因此向上层返回空元组
- `LIMIT_INWINDOW`：节点已经处于 `[offset, offset + count)` 的窗口中，判断扫描方向，并递归调用 `ExecProcNode()` 从子节点获取一个元组 (还需要将元组暂存)
- `LIMIT_WINDOWEND_TIES`：判断扫描方向，递归调用 `ExecProcNode()` 从子节点获取元组，然后调用 `eqfunction` 判断是否与暂存元组相等 (并列)；如果并列，则返回元组；否则返回空元组
- ...

```c
/* ----------------------------------------------------------------
 *      ExecLimit
 *
 *      This is a very simple node which just performs LIMIT/OFFSET
 *      filtering on the stream of tuples returned by a subplan.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *         /* return: a tuple or NULL */
ExecLimit(PlanState *pstate)
{
    LimitState *node = castNode(LimitState, pstate);
    ExprContext *econtext = node->ps.ps_ExprContext;
    ScanDirection direction;
    TupleTableSlot *slot;
    PlanState  *outerPlan;

    CHECK_FOR_INTERRUPTS();

    /*
     * get information from the node
     */
    direction = node->ps.state->es_direction;
    outerPlan = outerPlanState(node);

    /*
     * The main logic is a simple state machine.
     */
    switch (node->lstate)
    {
        case LIMIT_INITIAL:

            /*
             * First call for this node, so compute limit/offset. (We can't do
             * this any earlier, because parameters from upper nodes will not
             * be set during ExecInitLimit.)  This also sets position = 0 and
             * changes the state to LIMIT_RESCAN.
             */
            recompute_limits(node);

            /* FALL THRU */

        case LIMIT_RESCAN:

            /*
             * If backwards scan, just return NULL without changing state.
             */
            if (!ScanDirectionIsForward(direction))
                return NULL;

            /*
             * Check for empty window; if so, treat like empty subplan.
             */
            if (node->count <= 0 && !node->noCount)
            {
                node->lstate = LIMIT_EMPTY;
                return NULL;
            }

            /*
             * Fetch rows from subplan until we reach position > offset.
             */
            for (;;)
            {
                slot = ExecProcNode(outerPlan);
                if (TupIsNull(slot))
                {
                    /*
                     * The subplan returns too few tuples for us to produce
                     * any output at all.
                     */
                    node->lstate = LIMIT_EMPTY;
                    return NULL;
                }

                /*
                 * Tuple at limit is needed for comparison in subsequent
                 * execution to detect ties.
                 */
                if (node->limitOption == LIMIT_OPTION_WITH_TIES &&
                    node->position - node->offset == node->count - 1)
                {
                    ExecCopySlot(node->last_slot, slot);
                }
                node->subSlot = slot;
                if (++node->position > node->offset)
                    break;
            }

            /*
             * Okay, we have the first tuple of the window.
             */
            node->lstate = LIMIT_INWINDOW;
            break;

        case LIMIT_EMPTY:

            /*
             * The subplan is known to return no tuples (or not more than
             * OFFSET tuples, in general).  So we return no tuples.
             */
            return NULL;

        case LIMIT_INWINDOW:
            if (ScanDirectionIsForward(direction))
            {
                /*
                 * Forwards scan, so check for stepping off end of window.  At
                 * the end of the window, the behavior depends on whether WITH
                 * TIES was specified: if so, we need to change the state
                 * machine to WINDOWEND_TIES, and fall through to the code for
                 * that case.  If not (nothing was specified, or ONLY was)
                 * return NULL without advancing the subplan or the position
                 * variable, but change the state machine to record having
                 * done so.
                 *
                 * Once at the end, ideally, we would shut down parallel
                 * resources; but that would destroy the parallel context
                 * which might be required for rescans.  To do that, we'll
                 * need to find a way to pass down more information about
                 * whether rescans are possible.
                 */
                if (!node->noCount &&
                    node->position - node->offset >= node->count)
                {
                    if (node->limitOption == LIMIT_OPTION_COUNT)
                    {
                        node->lstate = LIMIT_WINDOWEND;
                        return NULL;
                    }
                    else
                    {
                        node->lstate = LIMIT_WINDOWEND_TIES;
                        /* we'll fall through to the next case */
                    }
                }
                else
                {
                    /*
                     * Get next tuple from subplan, if any.
                     */
                    slot = ExecProcNode(outerPlan);
                    if (TupIsNull(slot))
                    {
                        node->lstate = LIMIT_SUBPLANEOF;
                        return NULL;
                    }

                    /*
                     * If WITH TIES is active, and this is the last in-window
                     * tuple, save it to be used in subsequent WINDOWEND_TIES
                     * processing.
                     */
                    if (node->limitOption == LIMIT_OPTION_WITH_TIES &&
                        node->position - node->offset == node->count - 1)
                    {
                        ExecCopySlot(node->last_slot, slot);
                    }
                    node->subSlot = slot;
                    node->position++;
                    break;
                }
            }
            else
            {
                /*
                 * Backwards scan, so check for stepping off start of window.
                 * As above, only change state-machine status if so.
                 */
                if (node->position <= node->offset + 1)
                {
                    node->lstate = LIMIT_WINDOWSTART;
                    return NULL;
                }

                /*
                 * Get previous tuple from subplan; there should be one!
                 */
                slot = ExecProcNode(outerPlan);
                if (TupIsNull(slot))
                    elog(ERROR, "LIMIT subplan failed to run backwards");
                node->subSlot = slot;
                node->position--;
                break;
            }

            Assert(node->lstate == LIMIT_WINDOWEND_TIES);
            /* FALL THRU */

        case LIMIT_WINDOWEND_TIES:
            if (ScanDirectionIsForward(direction))
            {
                /*
                 * Advance the subplan until we find the first row with
                 * different ORDER BY pathkeys.
                 */
                slot = ExecProcNode(outerPlan);
                if (TupIsNull(slot))
                {
                    node->lstate = LIMIT_SUBPLANEOF;
                    return NULL;
                }

                /*
                 * Test if the new tuple and the last tuple match. If so we
                 * return the tuple.
                 */
                econtext->ecxt_innertuple = slot;
                econtext->ecxt_outertuple = node->last_slot;
                if (ExecQualAndReset(node->eqfunction, econtext))
                {
                    node->subSlot = slot;
                    node->position++;
                }
                else
                {
                    node->lstate = LIMIT_WINDOWEND;
                    return NULL;
                }
            }
            else
            {
                /*
                 * Backwards scan, so check for stepping off start of window.
                 * Change only state-machine status if so.
                 */
                if (node->position <= node->offset + 1)
                {
                    node->lstate = LIMIT_WINDOWSTART;
                    return NULL;
                }

                /*
                 * Get previous tuple from subplan; there should be one! And
                 * change state-machine status.
                 */
                slot = ExecProcNode(outerPlan);
                if (TupIsNull(slot))
                    elog(ERROR, "LIMIT subplan failed to run backwards");
                node->subSlot = slot;
                node->position--;
                node->lstate = LIMIT_INWINDOW;
            }
            break;

        case LIMIT_SUBPLANEOF:
            if (ScanDirectionIsForward(direction))
                return NULL;

            /*
             * Backing up from subplan EOF, so re-fetch previous tuple; there
             * should be one!  Note previous tuple must be in window.
             */
            slot = ExecProcNode(outerPlan);
            if (TupIsNull(slot))
                elog(ERROR, "LIMIT subplan failed to run backwards");
            node->subSlot = slot;
            node->lstate = LIMIT_INWINDOW;
            /* position does not change 'cause we didn't advance it before */
            break;

        case LIMIT_WINDOWEND:
            if (ScanDirectionIsForward(direction))
                return NULL;

            /*
             * We already past one position to detect ties so re-fetch
             * previous tuple; there should be one!  Note previous tuple must
             * be in window.
             */
            if (node->limitOption == LIMIT_OPTION_WITH_TIES)
            {
                slot = ExecProcNode(outerPlan);
                if (TupIsNull(slot))
                    elog(ERROR, "LIMIT subplan failed to run backwards");
                node->subSlot = slot;
                node->lstate = LIMIT_INWINDOW;
            }
            else
            {
                /*
                 * Backing up from window end: simply re-return the last tuple
                 * fetched from the subplan.
                 */
                slot = node->subSlot;
                node->lstate = LIMIT_INWINDOW;
                /* position does not change 'cause we didn't advance it before */
            }
            break;

        case LIMIT_WINDOWSTART:
            if (!ScanDirectionIsForward(direction))
                return NULL;

            /*
             * Advancing after having backed off window start: simply
             * re-return the last tuple fetched from the subplan.
             */
            slot = node->subSlot;
            node->lstate = LIMIT_INWINDOW;
            /* position does not change 'cause we didn't change it before */
            break;

        default:
            elog(ERROR, "impossible LIMIT state: %d",
                 (int) node->lstate);
            slot = NULL;        /* keep compiler quiet */
            break;
    }

    /* Return the current tuple */
    Assert(!TupIsNull(slot));

    return slot;
}
```

## Execution End

在 `ExecEndNode()` 生命周期中被调用，主要是递归调用 `ExecEndNode()`，以及清理本节点中分配的表达式计算环境。

```c
/* ----------------------------------------------------------------
 *      ExecEndLimit
 *
 *      This shuts down the subplan and frees resources allocated
 *      to this node.
 * ----------------------------------------------------------------
 */
void
ExecEndLimit(LimitState *node)
{
    ExecFreeExprContext(&node->ps);
    ExecEndNode(outerPlanState(node));
}
```

