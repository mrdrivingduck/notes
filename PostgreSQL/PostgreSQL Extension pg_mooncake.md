# PostgreSQL (Extension) - pg_mooncake

Created by: Mr Dk.

2026 / 02 / 14 16:02

Ningbo, Zhejiang, China

---

## 背景

[pg_mooncake](https://github.com/Mooncake-Labs/pg_mooncake) 是一款使 PostgreSQL 具备对行式存储的 Heap 表创建 [Iceberg](https://iceberg.apache.org/) 格式的副本列存表的插件，通过 PostgreSQL 的逻辑复制能力自动维护两张表的数据同步。插件主体由 Rust 实现。用户可以根据业务查询的类型来选择查询行存表还是列存表，如果选择的是列存表，则借助 [pg_duckdb](https://github.com/duckdb/pg_duckdb) 的能力读取并计算列存数据。

本文简析其关键能力是如何实现的。

## Moonlink 服务

pg_mooncake 的核心能力实现在一个叫做 [moonlink](https://github.com/Mooncake-Labs/moonlink) 的组件中。该组件对外提供 RPC 服务，管理着列存表的元数据，也管理与 PostgreSQL 的逻辑复制以维持行列存的同步。官方建议在生产环境中把这个组件作为一个服务独立部署，但也支持将这个组件运行在一个 PostgreSQL 的 background worker 进程中：

```rust
pub(crate) fn init() {
    BackgroundWorkerBuilder::new("moonlink")
        .set_library("pg_mooncake")
        .set_function("moonlink_main")
        .enable_shmem_access(None)
        .set_start_time(BgWorkerStartTime::ConsistentState)
        .set_restart_time(Some(Duration::from_secs(15)))
        .load();
}
```

Moonlink 组件启动后，会在 PostgreSQL 的数据目录下创建一个专用的独立目录，并在其中创建用于 RPC 的 Unix Socket：

```rust
#[tokio::main]
pub async fn start() {
    let config = ServiceConfig {
        base_path: "pg_mooncake".to_owned(),
        data_server_uri: None,
        rest_api_port: None,
        otel_ingestion_api_port: None,
        tcp_port: None,
        log_directory: None,
        otel_export_target: None,
    };
    start_with_config(config).await.unwrap();
}

pub async fn start_with_config(config: ServiceConfig) -> Result<()> {
    // ...

    // Start RPC server on Unix socket
    let socket_path = std::path::PathBuf::from(&config.base_path).join("moonlink.sock");
    let rpc_backend = backend.clone();
    let rpc_handle = tokio::spawn(async move {
        if let Err(e) = rpc_server::start_unix_server(rpc_backend, socket_path).await {
            error!("RPC server failed: {}", e);
        }
    });

    // ...
}
```

## 基于逻辑复制的行列存同步

pg_mooncake 插件对用户暴露以下存储过程，为一张行存表创建列存表副本：

```sql
CALL mooncake.create_table('c', 'r');
```

在 PostgreSQL 中执行这个存储过程后，将首先在 PostgreSQL 的 catalog 中注册这张表，以便将来对这张表的查询能够被 binder 识别；然后再调用 moonlink 的 RPC 让 moonlink 服务也同步创建这张表的列存副本，并准备好行列同步：

```rust
#[pg_extern(sql = "
CREATE PROCEDURE mooncake.create_table(dst text, src text, src_uri text DEFAULT NULL, table_config json DEFAULT NULL) LANGUAGE c AS 'MODULE_PATHNAME', '@FUNCTION_NAME@';
")]
fn create_table(dst: &str, src: &str, src_uri: Option<&str>, table_config: Option<&str>) {
    // ...
    create_mooncake_table(&dst, &dst_uri, &src, &src_uri);
    // ...
    block_on(moonlink_rpc::create_table(
        &mut *get_stream(),
        DATABASE.clone(),
        dst,
        src,
        src_uri,
        table_config,
    ))
    .expect("create_table failed");
}
```

在 PostgreSQL 中创建这张表时，需要先从 catalog 中查回行存表的列定义，然后按原样拼接出创建列存表的 SQL，并声明这张表使用的 table AM 为 `mooncake`：

```rust
fn create_mooncake_table(dst: &str, dst_uri: &str, src: &str, src_uri: &str) {
    // ...

    let get_columns_query = format!(
        // ...
        src.replace("'", "''")
    );

    let create_table_query = format!("CREATE TABLE {dst} ({columns}) USING mooncake");
    client
        .simple_query(&create_table_query)
        .unwrap_or_else(|_| panic!("error creating table: {dst}"));
}
```

当 `create_table` 的 RPC 调用到达 moonlink 以后，moonlink 知道需要开始同步一张新的表。如果逻辑复制所需要的复制槽、发布等还没有被初始化，则先进行必要的创建：

```rust
impl PostgresConnection {
    pub async fn new(uri: String) -> Result<Self> {
        // ...
        postgres_client
            .simple_query(
                "DROP PUBLICATION IF EXISTS moonlink_pub; CREATE PUBLICATION moonlink_pub WITH (publish_via_partition_root = true);",
            )
            .await
            .map_err(PostgresSourceError::from)?;

        // ...
    }
}

impl ReplicationClient {
    // ...

    pub async fn get_logical_replication_stream(
        &self,
        publication: &str,
        slot_name: &str,
        start_lsn: PgLsn,
    ) -> Result<LogicalReplicationStream, ReplicationClientError> {
        let options = format!(
            r#"("proto_version" '2', "publication_names" {}, "streaming" 'on')"#,
            quote_literal(publication),
        );

        let query = format!(
            r#"START_REPLICATION SLOT {} LOGICAL {} {}"#,
            quote_identifier(slot_name),
            start_lsn,
            options
        );

        // ...
    }
}
```

创建完毕后，将要同步的行存表加入到发布中开始订阅变更，然后进行行表的快照全量数据拷贝并写入 Parquet 文件。

## 借助 DuckDB 读取列存表

对于一张带有列存表副本的 PostgreSQL 行存表来说，如何从 PostgreSQL 中读取列存表呢？列存的元数据维护在 moonlink 服务中，读取并处理列存数据需要基于列式存储的向量化执行器。因此，pg_mooncake 借助 pg_duckdb 来完成这个目标：

- pg_duckdb 使 PostgreSQL 具备将 SQL 改写并转发到 DuckDB 中执行的能力
- pg_mooncake 为 DuckDB 实现了一套 Storage Extension，并在底层以 moonlink 作为元数据服务；这样 DuckDB 可以通过这个 Storage Extension 感知列存表是否存在，以及知道如何扫描列存表
- pg_mooncake 在 DuckDB 中实现了 `mooncake_scan` 函数来扫描列存表，该函数会通过 moonlink 服务获取 SQL 查询对应的 LSN 下可见的数据版本和 Parquet 文件列表，并复用 DuckDB 的 `parquet_scan` 来完成 Iceberg 中的 Parquet 文件读取，复用 DuckDB 的向量化执行器实现对列存数据的分析

### Mooncake Table AM

首先，pg_duckdb 默认只识别自带的 `duckdb` table AM，在遇到 `duckdb` table AM 的表时将会改写 SQL 并转发到 DuckDB。而 pg_mooncake 将自带的 `mooncake` table AM 也注册到了 pg_duckdb 中，作为同类型的 table AM 处理：

```rust
extern "C" {
    fn RegisterDuckdbTableAm(name: *const c_char, am: *const pg_sys::TableAmRoutine) -> bool;
}

pub(crate) fn init() {
    let name = CString::new("mooncake").expect("name should not contain an internal 0 byte");
    let res = unsafe { RegisterDuckdbTableAm(name.as_ptr(), std::ptr::addr_of!(MOONCAKE_AM)) };
    assert!(res, "error registering mooncake table AM");
}
```

与 pg_duckdb 提供的 `duckdb` table AM 类似，pg_mooncake 提供的 `mooncake` table AM 也基本没有做任何实现。因为实际的执行是在 DuckDB 内完成的：

```rust
#[pg_guard]
extern "C-unwind" fn mooncake_scan_getnextslot(
    _scan: pg_sys::TableScanDesc,
    _direction: pg_sys::ScanDirection::Type,
    _slot: *mut pg_sys::TupleTableSlot,
) -> bool {
    unimplemented!("mooncake_scan_getnextslot");
}
```

### DuckDB Storage Extension

在 pg_duckdb 的 planner hook 中，对 `mooncake` table AM 的列存表访问，在语法树经过 deparse 以后将会得到类似 `mooncake.schema.table` 的全限定名，对应到 DuckDB 中的 `mooncake` 数据库。

而 pg_mooncake 通过 DuckDB 的 [`ATTACH`](https://duckdb.org/docs/stable/sql/statements/attach) 语法，向 DuckDB 注册了 `mooncake` 类型的 Storage Extension，从而实现对 `mooncake` 数据库下的元数据 (catalog) 管理与表访问：

```cpp
class MooncakeStorageExtension : public StorageExtension {
public:
    MooncakeStorageExtension();
};

MooncakeStorageExtension::MooncakeStorageExtension() {
    attach = MooncakeAttach;
    create_transaction_manager = MooncakeCreateTransactionManager;
}

unique_ptr<Catalog> MooncakeAttach(optional_ptr<StorageExtensionInfo> storage_info, ClientContext &context,
                                   AttachedDatabase &db, const string &name, AttachInfo &info, AttachOptions &options) {
    // ...
    return make_uniq<MooncakeCatalog>(db, std::move(uri), std::move(database));
}

unique_ptr<TransactionManager> MooncakeCreateTransactionManager(optional_ptr<StorageExtensionInfo> storage_info,
                                                                AttachedDatabase &db, Catalog &catalog) {
    return make_uniq<MooncakeTransactionManager>(db, catalog);
}
```

这些 Storage Extension 需要实现的回调函数在底层通过 FFI 从 C++ 代码进入了 Rust 代码，然后对 moonlink 服务进行 RPC，从而取得相应的信息。

### Mooncake Scan Function

DuckDB 的 Storage Extension 中需要被实现的最重要的一个回调就是 `GetScanFunction`，即获取对当前表进行扫描的函数。对于 mooncake 表来说，其核心扫描逻辑复用了 DuckDB 已有的 `parquet_scan`：

```cpp
TableFunction MooncakeTable::GetScanFunction(ClientContext &context, unique_ptr<FunctionData> &bind_data) {
    TableFunction mooncake_scan = GetParquetScan(context);
    mooncake_scan.name = "mooncake_scan";
    mooncake_scan.init_global = MooncakeScanInitGlobal;
    mooncake_scan.to_string = MooncakeScanToString;
    mooncake_scan.get_bind_info = MooncakeScanGetBindInfo;
    mooncake_scan.get_multi_file_reader = MooncakeMultiFileReader::Create;
    mooncake_scan.function_info = make_shared_ptr<MooncakeFunctionInfo>(*this);
    // ...
    bind_data = mooncake_scan.bind(context, bind_input, return_types, names);
    return mooncake_scan;
}

static TableFunction &GetParquetScan(ClientContext &context) {
    ExtensionLoader loader(*context.db, "mooncake");
    return loader.GetTableFunction("parquet_scan").functions.GetFunctionReferenceByOffset(0);
}
```

在执行初始化的 `init_global` 函数中，用专门为 mooncake 实现的 `MooncakeScanInitGlobal` hook
掉了 `parquet_scan` 自己的 `init_global` 函数，并在其中额外增加了获取列存表对应数据文件的步骤：

```cpp
static unique_ptr<GlobalTableFunctionState> MooncakeScanInitGlobal(ClientContext &context,
                                                                   TableFunctionInitInput &input) {
    auto &bind_data = input.bind_data->Cast<MultiFileBindData>();
    bind_data.file_list->Cast<MooncakeMultiFileList>().LazyInitialize(context, bind_data.names, input.column_ids,
                                                                      input.filters);
    return GetParquetScan(context).init_global(context, input);
}
```

为了获取要扫描的 Parquet 文件列表，依旧需要借助 moonlink 服务：

```cpp
MooncakeTableMetadata &MooncakeTable::GetTableMetadata() {
    lock_guard<mutex> guard(lock);
    if (!metadata) {
        metadata = make_uniq<MooncakeTableMetadata>(moonlink, schema.name, name, lsn);
    }
    return *metadata;
}

MooncakeTableMetadata::MooncakeTableMetadata(Moonlink &moonlink, const string &schema, const string &table,
                                             uint64_t lsn)
    : moonlink(moonlink), schema(schema), table(table) {
    data = moonlink.ScanTableBegin(schema, table, lsn);
    uint32_t *ptr = reinterpret_cast<uint32_t *>(data->ptr);

    // ...
}
```

在获取到需要扫描的原始文件列表后，再进一步处理谓词下推、删除向量等，然后真正开始执行 `parquet_scan`。该函数会读取 Parquet 文件并过滤掉不符合条件或已经删除的行，返回为 DuckDB 的 DataChunk。这些 DataChunk 经由 DuckDB 的向量化执行器完成计算后，通过 pg_duckdb 的 CustomScan 算子返回到 PostgreSQL 中。

由此，pg_mooncake 借助 pg_duckdb 串联了 PostgreSQL、DuckDB、moonlink，使 PostgreSQL 具备了读取 mooncake 列存表的能力。

## 总结

pg_mooncake 主要提供了一个基于 Iceberg 的列存元数据管理 + 数据同步的引擎。借助 DuckDB / pg_duckdb，用户可以通过 PostgreSQL 作为入口对行存表的列存副本进行扫描和计算，从而加速业务中可能出现的分析型查询。
