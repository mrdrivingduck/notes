# PostgreSQL (Extension) - pg_duckdb

Created by: Mr Dk.

2026 / 02 / 07 0:27

Hangzhou, Zhejiang, China

---

## 背景

[DuckDB](https://github.com/duckdb/duckdb) 是一款高性能的嵌入式分析型数据库。与传统 C/S 架构的数据库不同，它可以直接嵌入在应用程序中，作为进程内库 (不是内裤) 被使用。DuckDB 的核心特性包括：采用列式存储，能够高效压缩数据；采用向量化执行引擎，能够充分利用 CPU 缓存和 SIMD；采用并行化的查询处理，能够自动利用多核心的 CPU；支持全面的 SQL 标准和复杂查询，提供丰富的分析函数；此外还支持丰富的数据格式 (Parquet / CSV / JSON / ...) 与数据源 (S3 / HTTP / ...)，也支持 [Apache Arrow](https://arrow.apache.org/) 格式的零拷贝数据交换。是数据科学家的利器。

在 SQL 语法的实现上，DuckDB 紧密遵循了 PostgreSQL 的 dialect，因此两者天然有一定的血缘关系。DuckDB 官方推出了 [pg_duckdb](https://github.com/duckdb/pg_duckdb) 这款 PostgreSQL 插件，使 DuckDB 能够被嵌入到 PostgreSQL 的进程内。安装该插件后，PostgreSQL 便获得了 DuckDB 的上述所有能力。在保持其擅长的事务处理能力的同时，极大增强了数据分析能力。

本文基于 pg_duckdb 的 v1.1.1 版本，简要分析 pg_duckdb 是如何将 DuckDB 嵌入到 PostgreSQL 中为其提供分析能力的。

## 加速 PostgreSQL 的分析查询

PostgreSQL 的表数据使用行式存储，其执行器的执行模型也是逐行处理数据的经典火山模型。这种执行模型对分析型查询来说并不是特别高效。而如前所述，DuckDB 内部有面向列式存储的向量化执行引擎，能够出色地完成分析型查询。如果能够将 PostgreSQL 的表数据输入到 DuckDB 的向量化执行引擎中执行，就能极大提升 PostgreSQL 的分析能力。

要完成这个目标，理论上 DuckDB 需要能够识别 PostgreSQL 的表格式并读取数据，而且需要能够判断表内每一行数据的可见性。幸运的是，DuckDB 本身并不需要具有这个能力，pg_duckdb 会尽量复用 PostgreSQL 的现成能力，将 PostgreSQL 格式的数据喂入 DuckDB 的执行器中。

首先，pg_duckdb 使用 PostgreSQL 的 planner hook 机制，在 SQL 处理进入优化器阶段时接管，将执行流桥接到 pg_duckdb 的 C++ 代码中，并检查当前 SQL 是否需要/能够使用 DuckDB 来执行。

```c
void
DuckdbInitHooks(void) {
    prev_planner_hook = planner_hook ? planner_hook : standard_planner;
    planner_hook = DuckdbPlannerHook;

    /* ... */
}
```

检查内容包含是否启用了强制 DuckDB 执行的 GUC 参数、语法树中是否包含 DuckDB 的元素、SQL 语法是否是只读等等。只有通过检查，才会为后续扫描产生一个 DuckDB 的执行计划节点：

```cpp
static PlannedStmt *
DuckdbPlannerHook_Cpp(Query *parse, const char *query_string, int cursor_options, ParamListInfo bound_params) {
    if (pgduckdb::IsExtensionRegistered()) {
        if (pgduckdb::NeedsDuckdbExecution(parse)) {
            pgduckdb::TriggerActivity();
            pgduckdb::IsAllowedStatement(parse, true);

            return DuckdbPlanNode(parse, cursor_options, true);
        } else if (pgduckdb::ShouldTryToUseDuckdbExecution(parse)) {
            pgduckdb::TriggerActivity();
            PlannedStmt *duckdbPlan = DuckdbPlanNode(parse, cursor_options, false);
            if (duckdbPlan) {
                return duckdbPlan;
            }
            /* If we can't create a plan, we'll fall back to Postgres */
        }
        if (parse->commandType != CMD_SELECT && !pgduckdb::pg::AllowWrites()) {
            elog(ERROR, "Writing to DuckDB and Postgres tables in the same transaction block is not supported");
        }
    }

    /* ... */

    return prev_planner_hook(parse, query_string, cursor_options, bound_params);
}
```

接下来，将 PostgreSQL 的语法树 deparse 为 DuckDB 兼容的 SQL 语句，并传入 DuckDB 中得到一个 prepared statement。pg_duckdb 将相关信息组装好以后，构造一个 PostgreSQL 可以识别的 CustomScan 算子，并为这个算子注册了扫描时的回调函数：

```cpp
static Plan *
CreatePlan(Query *query, bool throw_error) {
    int elevel = throw_error ? ERROR : WARNING;
    /*
     * Prepare the query, se we can get the returned types and column names.
     */

    duckdb::unique_ptr<duckdb::PreparedStatement> prepared_query = DuckdbPrepare(query);

    if (prepared_query->HasError()) {
        elog(elevel, "(PGDuckDB/CreatePlan) Prepared query returned an error: %s", prepared_query->GetError().c_str());
        return nullptr;
    }

    CustomScan *duckdb_node = makeNode(CustomScan);

    /* ... */

    duckdb_node->custom_private = list_make1(query);
    duckdb_node->methods = &duckdb_scan_scan_methods;

    return (Plan *)duckdb_node;
}
```

在实际执行扫描时，当 PostgreSQL 的火山模型执行器试图从 CustomScan 算子拉出一行元组时，算子将从自己已经计算完毕的 Data Chunk 中构造一行并填入 PostgreSQL 的 TableTupleSlot。如果 Data Chunk 已经被消费完，则从 DuckDB 的向量化执行器中再拉取一批 Data Chunk：

```cpp
static TupleTableSlot *
Duckdb_ExecCustomScan_Cpp(CustomScanState *node) {
    DuckdbScanState *duckdb_scan_state = (DuckdbScanState *)node;
    try {
        /* ... */

        bool already_executed = duckdb_scan_state->is_executed;
        if (!already_executed) {
            ExecuteQuery(duckdb_scan_state);
        }

        if (duckdb_scan_state->fetch_next) {
            duckdb_scan_state->current_data_chunk = duckdb_scan_state->query_results->Fetch();
            duckdb_scan_state->current_row = 0;
            duckdb_scan_state->fetch_next = false;
            if (!duckdb_scan_state->current_data_chunk || duckdb_scan_state->current_data_chunk->size() == 0) {
                MemoryContextReset(duckdb_scan_state->css.ss.ps.ps_ExprContext->ecxt_per_tuple_memory);
                ExecClearTuple(slot);
                return slot;
            }
        }

        for (idx_t col = 0; col < duckdb_scan_state->column_count; col++) {
            // FIXME: we should not use the Value API here, it's complicating the LIST conversion logic
            auto value = duckdb_scan_state->current_data_chunk->GetValue(col, duckdb_scan_state->current_row);
            if (value.IsNull()) {
                slot->tts_isnull[col] = true;
            } else {
                slot->tts_isnull[col] = false;
                if (!pgduckdb::ConvertDuckToPostgresValue(slot, value, col)) {
                    throw duckdb::ConversionException("Value conversion failed");
                }
            }
        }

        /* ... */

        ExecStoreVirtualTuple(slot);
        return slot;
    } catch (std::exception &ex) {
        /* ... */
    }
}
```

那么 DuckDB 的向量化执行器所需要的数据从哪来？在早些时候构造 DuckDB 的 prepared statement 时，原先对 PostgreSQL 表访问的部分将会被替换为 DuckDB 的 `pgduckdb_postgres_scan()` 函数，其中传入了要扫描的 PostgreSQL 表名、快照信息等。该函数的内部实现中，会根据要扫描的列，组装出一条对 PostgreSQL 进行全表扫描的 SQL：

```cpp
void
PostgresScanGlobalState::ConstructTableScanQuery(const duckdb::TableFunctionInitInput &input) {
    /* SELECT COUNT(*) FROM */
    if (input.column_ids.size() == 1 && input.column_ids[0] == UINT64_MAX) {
        scan_query << "SELECT COUNT(*) FROM " << pgduckdb::GenerateQualifiedRelationName(rel);
        count_tuples_only = true;
        return;
    }
    /*
     * We need to read columns from the Postgres tuple in column order, but for
     * outputting them we care about the DuckDB order. A map automatically
     * orders them based on key, which in this case is the Postgres column
     * order
     */
    /* ... */

    scan_query << "SELECT ";

    /* ... */

    scan_query << " FROM " << GenerateQualifiedRelationName(rel);

    /* ... */

    if (query_filters.size()) {
        scan_query << " WHERE ";
        scan_query << FilterJoin(query_filters, " AND ");
    }
}
```

这条 SQL 最终会被依次重新输入到 PostgreSQL 的解析器、优化器、执行器中，以获取 PostgreSQL 的表数据：

```cpp
void
PostgresTableReader::InitUnsafe(const char *table_scan_query, bool count_tuples_only) {
    List *raw_parsetree_list = pg_parse_query(table_scan_query);
    Assert(list_length(raw_parsetree_list) == 1);
    RawStmt *raw_parsetree = linitial_node(RawStmt, raw_parsetree_list);

#if PG_VERSION_NUM >= 150000
    List *query_list = pg_analyze_and_rewrite_fixedparams(raw_parsetree, table_scan_query, nullptr, 0, nullptr);
#else
    List *query_list = pg_analyze_and_rewrite(raw_parsetree, table_scan_query, nullptr, 0, nullptr);
#endif

    /* ... */

    PlannedStmt *planned_stmt = standard_planner(query, table_scan_query, 0, nullptr);

    table_scan_query_desc = CreateQueryDesc(planned_stmt, table_scan_query, GetActiveSnapshot(), InvalidSnapshot,
                                            None_Receiver, nullptr, nullptr, 0);

    ExecutorStart(table_scan_query_desc, 0);

    /* ... */
}
```

综上所述，pg_duckdb 从优化器开始介入执行流程，在执行计划中插入了能够调用 DuckDB 的 CustomScan 算子，将语法树 deparse 为 SQL 并转移给 DuckDB 执行，并将 SQL 中对 PostgreSQL 的表引用修改为 DuckDB 的 UDF。UDF 中重新拼接了全表扫描 PostgreSQL 表的 SQL，然后复用 PostgreSQL 对 SQL 的完整处理周期来得到 PostgreSQL 的表数据。

## 根据 UDF 直接使用 DuckDB 执行

对于 DuckDB 部分内置 UDF，pg_duckdb 在 PostgreSQL 中也注册了相应的 UDF。在 PostgreSQL 中识别到 SQL 中存在这些 UDF 时，相应的 SQL 会直接使用 DuckDB 来执行。这样在 PostgreSQL 中也可以直接使用 DuckDB 内置 UDF 提供的能力，比如直接从 S3 上读取 Parquet / CSV / JSON 文件，读取 Iceberg 等数据湖表格式等。

依旧回到 pg_duckdb 实现的 planner hook 中。对于 PostgreSQL 解析器输出的语法树，pg_duckdb 做了一次遍历来搜索语法树中是否存在需要直接使用 DuckDB 来执行的元素：

```cpp
bool
NeedsDuckdbExecution(Query *query) {
    return ContainsDuckdbItems((Node *)query, NULL);
}

static bool
ContainsDuckdbItems(Node *node, void *context) {
    if (node == NULL)
        return false;

    /* ... */

    if (IsA(node, FuncExpr)) {
        FuncExpr *func = castNode(FuncExpr, node);
        if (pgduckdb::IsDuckdbOnlyFunction(func->funcid)) {
            return true;
        }
    }

    if (IsA(node, Aggref)) {
        Aggref *func = castNode(Aggref, node);
        if (pgduckdb::IsDuckdbOnlyFunction(func->aggfnoid)) {
            return true;
        }
    }

#if PG_VERSION_NUM >= 160000
    return expression_tree_walker(node, ContainsDuckdbItems, context);
#else
    return expression_tree_walker(node, (bool (*)())((void *)ContainsDuckdbItems), context);
#endif
}
```

而所谓 DuckDB-only 的函数全部被放置在一个缓存中。缓存的构造方式也非常直接，目前使用了硬编码：

```cpp
/*
 * Returns true if the function with the given OID is a function that can only
 * be executed by DuckDB.
 */
bool
IsDuckdbOnlyFunction(Oid function_oid) {
    Assert(cache.valid);

    foreach_oid(duckdb_only_oid, cache.duckdb_only_functions) {
        if (duckdb_only_oid == function_oid) {
            return true;
        }
    }
    return false;
}

/*
 * Builds the list of Postgres OIDs of functions that can only be executed by
 * DuckDB. The resulting list is stored in cache.duckdb_only_functions.
 */
static void
BuildDuckdbOnlyFunctions() {
    /* This function should only be called during cache initialization */
    Assert(!cache.valid);
    Assert(!cache.duckdb_only_functions);
    Assert(cache.extension_oid != InvalidOid);

    /*
     * We search the system cache for functions with these specific names. It's
     * possible that other functions with the same also exist, so we check if
     * each of the found functions is actually part of our extension before
     * caching its OID as a DuckDB-only function.
     */
    const char *function_names[] = {"read_parquet",
                                    "read_csv",
                                    "iceberg_scan",
                                    "iceberg_metadata",
                                    "iceberg_snapshots",
                                    "delta_scan",
                                    "read_json",
                                    "approx_count_distinct",
                                    "query",
                                    "view",
                                    "json_exists",
                                    "json_extract",
                                    "json_extract_string",
                                    "json_array_length",
                                    "json_contains",
                                    "json_keys",
                                    "json_structure",
                                    "json_type",
                                    "json_valid",
                                    "json",
                                    "json_group_array",
                                    "json_group_object",
                                    "json_group_structure",
                                    "json_transform",
                                    "from_json",
                                    "json_transform_strict",
                                    "from_json_strict",
                                    "json_value",
                                    "strftime",
                                    "strptime",
                                    "epoch",
                                    "epoch_ms",
                                    "epoch_us",
                                    "epoch_ns",
                                    "make_timestamp",
                                    "make_timestamptz",
                                    "time_bucket",
                                    "union_extract",
                                    "union_tag",
                                    "cardinality",
                                    "element_at",
                                    "map_concat",
                                    "map_contains",
                                    "map_contains_entry",
                                    "map_contains_value",
                                    "map_entries",
                                    "map_extract",
                                    "map_extract_value",
                                    "map_from_entries",
                                    "map_keys",
                                    "map_values"};

    for (uint32_t i = 0; i < lengthof(function_names); i++) {
        CatCList *catlist = SearchSysCacheList1(PROCNAMEARGSNSP, CStringGetDatum(function_names[i]));

        for (int j = 0; j < catlist->n_members; j++) {
            /* ... */
            cache.duckdb_only_functions = lappend_oid(cache.duckdb_only_functions, function->oid);
            /* ... */
        }

        ReleaseSysCacheList(catlist);
    }
}
```

在识别到 SQL 中存在 DuckDB-only 的函数后，则 SQL 一定需要通过 DuckDB 来执行。之后的流程与前述类似，planner hook 将会创建 CustomScan 算子，并将 PostgreSQL 的语法树 deparse 为 DuckDB 的 SQL，并转移到 DuckDB 执行。

该特性使 PostgreSQL 借助 DuckDB UDF 具备了读取外部数据源的能力。甚至可以将外部数据源与 PostgreSQL 的表进行关联查询。

## 创建并管理 DuckDB 格式的表

如前所述，pg_duckdb 使 PostgreSQL 可以使用 DuckDB 的向量化执行引擎来访问 PostgreSQL 的表数据。但是 PostgreSQL 的表依旧是行式存储的，无法利用到列式存储所具有的高压缩、列裁剪等能力。有没有办法让 PostgreSQL 能够使用 DuckDB 的列式存储呢？

答案是肯定的。pg_duckdb 在 PostgreSQL 中以 [Table AM](https://www.postgresql.org/docs/current/tableam.html) 的形式暴露了一个名为 `duckdb` 的 AM，用户可以在创建一张表时显式声明这张表的 AM 为 `duckdb`，使这张表被创建在 DuckDB 管理的存储中，而不是 PostgreSQL 管理的表文件里：

```sql
CREATE FUNCTION duckdb._am_handler(internal)
    RETURNS table_am_handler
    SET search_path = pg_catalog, pg_temp
    AS 'MODULE_PATHNAME', 'duckdb_am_handler'
    LANGUAGE C;

CREATE ACCESS METHOD duckdb
    TYPE TABLE
    HANDLER duckdb._am_handler;
```

```c
Datum
duckdb_am_handler(FunctionCallInfo /*funcinfo*/) {
    PG_RETURN_POINTER(&duckdb_methods);
}
```

对于这个 Table AM 的各个回调函数，pg_duckdb 实现得非常敷衍，基本上是能不支持就不支持，就算支持也直接返回空操作。这里的根本原因是，由于这个 AM 的表数据实际上由 DuckDB 管理，所以 PostgreSQL 本身不再有必要回调这些函数了。pg_duckdb 产生的 CustomScan 算子中会直接使用 DuckDB 完成执行，永远不会使用这些 PostgreSQL 的 Table AM 回调函数。

与前述处理方法类似，如果 PostgreSQL 接收到了一条操作 Table AM 为 `duckdb` 表的 SQL，同样会在 pg_duckdb 的 planner hook 中被判断和识别出来：

```cpp
static bool
ContainsDuckdbItems(Node *node, void *context) {
    if (node == NULL)
        return false;

    if (IsA(node, Query)) {
        Query *query = (Query *)node;
        if (ContainsDuckdbTables(query->rtable)) {
            return true;
        }
#if PG_VERSION_NUM >= 160000
        return query_tree_walker(query, ContainsDuckdbItems, context, 0);
#else
        return query_tree_walker(query, (bool (*)())((void *)ContainsDuckdbItems), context, 0);
#endif
    }

    /* ... */
}

static bool
ContainsDuckdbTables(List *rte_list) {
    foreach_node(RangeTblEntry, rte, rte_list) {
        if (IsDuckdbTable(rte->relid)) {
            return true;
        }
    }
    return false;
}

static bool
IsDuckdbTable(Oid relid) {
    return pgduckdb::DuckdbTableAmGetName(relid) != nullptr;
}
```

然后对应的 PostgreSQL 语法树就会被 deparse 为 DuckDB 的 SQL，并在 CustomScan 算子中通过 DuckDB 来完成执行。

## 总结

pg_duckdb 通过 PostgreSQL 提供的一些较为灵活的可扩展性机制，将 DuckDB 这个强大的分析型数据库所具备的能力赋予了 PostgreSQL，极大增强了 PostgreSQL 的分析能力。此外，该插件也为 PostgreSQL 集成其它的计算工具提供了参考。
