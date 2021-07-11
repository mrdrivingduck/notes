# PostgreSQL - Executor: Material

Created by : Mr Dk.

2021 / 07 / 11 20:15

Hangzhou, Zhejiang, China

---

该节点被翻译为 **物化** 节点，含义为将子计划中的元组缓存在当前节点中。如果子计划节点需要被反复访问，并且每次返回的元组都相同，那么对子计划返回的元组进行缓存可以提高性能。

## Tuple Store

元组缓存使用 `Tuplestorestate` 结构，维护了用于缓存的内存空间和临时文件。之后准备专门分析一下和这个结构相关的代码。先明确几个相关 API 的功能：

- `tuplestore_begin_heap` 构造并初始化存储结构
- `tuplestore_puttupleslot` 将元组 append 到 tuple store 的最后
- `tuplestore_gettupleslot` 从 tuple store 中读取元组
- `tuplestore_end` 释放 tuple store

## Plan Node

物化节点较为简单，直接继承自 `Plan` 结构：

```c
/* ----------------
 *      materialization node
 * ----------------
 */
typedef struct Material
{
    Plan        plan;
} Material;
```

## Plan State

物化节点的 state 节点继承自 `Scan State`：

```c
/* ----------------
 *   MaterialState information
 *
 *      materialize nodes are used to materialize the results
 *      of a subplan into a temporary file.
 *
 *      ss.ss_ScanTupleSlot refers to output of underlying plan.
 * ----------------
 */
typedef struct MaterialState
{
    ScanState   ss;             /* its first field is NodeTag */
    int         eflags;         /* capability flags to pass to tuplestore */
    bool        eof_underlying; /* reached end of underlying plan? */
    Tuplestorestate *tuplestorestate;
} MaterialState;

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
```

其中 `ScanState` 中维护了与扫描相关的信息，而 `MaterialState` 中额外扩展了用于缓存元组的 `Tuplestorestate`，以及指示该节点的子计划是否已经扫描完毕的 `eof_underlying`。

## Initialization

初始化操作在 `ExecInitNode()` 生命周期中被调用，主要工作是分配和 `Material` 节点对应的 `MaterialState` 节点，还要对子节点递归调用 `ExecInitNode()`。在这里，首先把 `eof_underlying` 设置为 `false`，表示底层子节点还没有扫描完成 (EOF)。

与其它节点初始化过程不同的是，物化节点不需要初始化选择和投影信息。

```c
/* ----------------------------------------------------------------
 *      ExecInitMaterial
 * ----------------------------------------------------------------
 */
MaterialState *
ExecInitMaterial(Material *node, EState *estate, int eflags)
{
    MaterialState *matstate;
    Plan       *outerPlan;

    /*
     * create state structure
     */
    matstate = makeNode(MaterialState);
    matstate->ss.ps.plan = (Plan *) node;
    matstate->ss.ps.state = estate;
    matstate->ss.ps.ExecProcNode = ExecMaterial;

    /*
     * We must have a tuplestore buffering the subplan output to do backward
     * scan or mark/restore.  We also prefer to materialize the subplan output
     * if we might be called on to rewind and replay it many times. However,
     * if none of these cases apply, we can skip storing the data.
     */
    matstate->eflags = (eflags & (EXEC_FLAG_REWIND |
                                  EXEC_FLAG_BACKWARD |
                                  EXEC_FLAG_MARK));

    /*
     * Tuplestore's interpretation of the flag bits is subtly different from
     * the general executor meaning: it doesn't think BACKWARD necessarily
     * means "backwards all the way to start".  If told to support BACKWARD we
     * must include REWIND in the tuplestore eflags, else tuplestore_trim
     * might throw away too much.
     */
    if (eflags & EXEC_FLAG_BACKWARD)
        matstate->eflags |= EXEC_FLAG_REWIND;

    matstate->eof_underlying = false;
    matstate->tuplestorestate = NULL;

    /*
     * Miscellaneous initialization
     *
     * Materialization nodes don't need ExprContexts because they never call
     * ExecQual or ExecProject.
     */

    /*
     * initialize child nodes
     *
     * We shield the child node from the need to support REWIND, BACKWARD, or
     * MARK/RESTORE.
     */
    eflags &= ~(EXEC_FLAG_REWIND | EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK);

    outerPlan = outerPlan(node);
    outerPlanState(matstate) = ExecInitNode(outerPlan, estate, eflags);

    /*
     * Initialize result type and slot. No need to initialize projection info
     * because this node doesn't do projections.
     *
     * material nodes only return tuples from their materialized relation.
     */
    ExecInitResultTupleSlotTL(&matstate->ss.ps, &TTSOpsMinimalTuple);
    matstate->ss.ps.ps_ProjInfo = NULL;

    /*
     * initialize tuple type.
     */
    ExecCreateScanSlotFromOuterPlan(estate, &matstate->ss, &TTSOpsMinimalTuple);

    return matstate;
}
```

## Execution

在 `ExecProcNode()` 生命周期中被执行。只要目前访问的是 tuple store 的尾部，就要递归调用子节点的 `ExecProcNode()` 获取一个元组缓存到 tuple store 中并返回。Tuple store 本身只有在以下情况中才会被读取：

- 反向扫描
- 重新扫描
- Mark / restore

首先，如果是第一次进入物化节点，那么 tuple store 暂时还为空，需要调用 `tuplestore_begin_heap()` 初始化。接着判断当前是否已经到达 tuple store 的最后 (EOF)：

- 如果不是，那么可以直接调用 `tuplestore_gettupleslot()` 从 tuple store 取得缓存元组
- 如果是，那么对子节点调用 `ExecProcNode()` 获取元组
  - 如果从子节点返回空元组，说明扫描结束，将 `eof_underlying` 设置为 `true`
  - 如果从子节点返回元组，则调用 `tuplestore_puttupleslot()` 将元组放入 tuple store 后返回元组

> 下次可以重点研究一下 tuple store 是怎么放置元组的。

```c
/* ----------------------------------------------------------------
 *      ExecMaterial
 *
 *      As long as we are at the end of the data collected in the tuplestore,
 *      we collect one new row from the subplan on each call, and stash it
 *      aside in the tuplestore before returning it.  The tuplestore is
 *      only read if we are asked to scan backwards, rescan, or mark/restore.
 *
 * ----------------------------------------------------------------
 */
static TupleTableSlot *         /* result tuple from subplan */
ExecMaterial(PlanState *pstate)
{
    MaterialState *node = castNode(MaterialState, pstate);
    EState     *estate;
    ScanDirection dir;
    bool        forward;
    Tuplestorestate *tuplestorestate;
    bool        eof_tuplestore;
    TupleTableSlot *slot;

    CHECK_FOR_INTERRUPTS();

    /*
     * get state info from node
     */
    estate = node->ss.ps.state;
    dir = estate->es_direction;
    forward = ScanDirectionIsForward(dir);
    tuplestorestate = node->tuplestorestate;

    /*
     * If first time through, and we need a tuplestore, initialize it.
     */
    if (tuplestorestate == NULL && node->eflags != 0)
    {
        tuplestorestate = tuplestore_begin_heap(true, false, work_mem);
        tuplestore_set_eflags(tuplestorestate, node->eflags);
        if (node->eflags & EXEC_FLAG_MARK)
        {
            /*
             * Allocate a second read pointer to serve as the mark. We know it
             * must have index 1, so needn't store that.
             */
            int         ptrno PG_USED_FOR_ASSERTS_ONLY;

            ptrno = tuplestore_alloc_read_pointer(tuplestorestate,
                                                  node->eflags);
            Assert(ptrno == 1);
        }
        node->tuplestorestate = tuplestorestate;
    }

    /*
     * If we are not at the end of the tuplestore, or are going backwards, try
     * to fetch a tuple from tuplestore.
     */
    eof_tuplestore = (tuplestorestate == NULL) ||
        tuplestore_ateof(tuplestorestate);

    if (!forward && eof_tuplestore)
    {
        if (!node->eof_underlying)
        {
            /*
             * When reversing direction at tuplestore EOF, the first
             * gettupleslot call will fetch the last-added tuple; but we want
             * to return the one before that, if possible. So do an extra
             * fetch.
             */
            if (!tuplestore_advance(tuplestorestate, forward))
                return NULL;    /* the tuplestore must be empty */
        }
        eof_tuplestore = false;
    }

    /*
     * If we can fetch another tuple from the tuplestore, return it.
     */
    slot = node->ss.ps.ps_ResultTupleSlot;
    if (!eof_tuplestore)
    {
        if (tuplestore_gettupleslot(tuplestorestate, forward, false, slot))
            return slot;
        if (forward)
            eof_tuplestore = true;
    }

    /*
     * If necessary, try to fetch another row from the subplan.
     *
     * Note: the eof_underlying state variable exists to short-circuit further
     * subplan calls.  It's not optional, unfortunately, because some plan
     * node types are not robust about being called again when they've already
     * returned NULL.
     */
    if (eof_tuplestore && !node->eof_underlying)
    {
        PlanState  *outerNode;
        TupleTableSlot *outerslot;

        /*
         * We can only get here with forward==true, so no need to worry about
         * which direction the subplan will go.
         */
        outerNode = outerPlanState(node);
        outerslot = ExecProcNode(outerNode);
        if (TupIsNull(outerslot))
        {
            node->eof_underlying = true;
            return NULL;
        }

        /*
         * Append a copy of the returned tuple to tuplestore.  NOTE: because
         * the tuplestore is certainly in EOF state, its read position will
         * move forward over the added tuple.  This is what we want.
         */
        if (tuplestorestate)
            tuplestore_puttupleslot(tuplestorestate, outerslot);

        ExecCopySlot(slot, outerslot);
        return slot;
    }

    /*
     * Nothing left ...
     */
    return ExecClearTuple(slot);
}
```

## Clean Up

在 `ExecEndNode()` 生命周期中被调用。调用 `tuplestore_end()` 释放 tuple store，然后对子节点递归调用 `ExecEndNode()`。

```c
/* ----------------------------------------------------------------
 *      ExecEndMaterial
 * ----------------------------------------------------------------
 */
void
ExecEndMaterial(MaterialState *node)
{
    /*
     * clean out the tuple table
     */
    ExecClearTuple(node->ss.ss_ScanTupleSlot);

    /*
     * Release tuplestore resources
     */
    if (node->tuplestorestate != NULL)
        tuplestore_end(node->tuplestorestate);
    node->tuplestorestate = NULL;

    /*
     * shut down the subplan
     */
    ExecEndNode(outerPlanState(node));
}
```

