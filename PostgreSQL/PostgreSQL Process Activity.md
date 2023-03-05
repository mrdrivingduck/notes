# PostgreSQL - Process Activity

Created by : Mr Dk.

2023 / 03 / 06 00:07

Hangzhou, Zhejiang, China

---

## Background

PostgreSQL 是一个多进程架构的数据库。在数据库运行过程中，PostgreSQL 提供了丰富的系统视图来展示目前系统的运行状况，涵盖了系统的方方面面。这些视图主要分为两类：

- 用于展示系统当前运行情况的视图
- 用于展示系统截至目前累积的统计信息的视图

前者展示的是某个瞬间的系统状态，后者展示的是截止目前的一个时间段内的系统状态。这些系统视图全部以 `pg_stat_` 开头。本文将分析其中最为常用的 `pg_stat_activity` 系统视图的实现，该视图用于展示某一时刻 PostgreSQL 所有服务器进程的活动状态，可被用于查询实时连接数、慢 SQL 的执行状态等。

本文基于 PostgreSQL 15 稳定分支 `REL_15_STABLE` 的如下版本号作分析：

```
commit f61e60102f08305f3cb9e55a7958b8036a02fe39
Author: Tom Lane <tgl@sss.pgh.pa.us>
Date:   Sat Mar 4 13:32:35 2023 -0500

    Avoid failure when altering state of partitioned foreign-key triggers.
    
    Beginning in v15, if you apply ALTER TABLE ENABLE/DISABLE TRIGGER to
    a partitioned table, it also affects the partitions' cloned versions
    of the affected trigger(s).  The initial implementation of this
    located the clones by name, but that fails on foreign-key triggers
    which have names incorporating their own OIDs.  We can fix that, and
    also make the behavior more bulletproof in the face of user-initiated
    trigger renames, by identifying the cloned triggers by tgparentid.
    
    Following the lead of earlier commits in this area, I took care not
    to break ABI in the v15 branch, even though I rather doubt there
    are any external callers of EnableDisableTrigger.
    
    While here, update the documentation, which was not touched when
    the semantics were changed.
    
    Per bug #17817 from Alan Hodgson.  Back-patch to v15; older versions
    do not have this behavior.
    
    Discussion: https://postgr.es/m/17817-31dfb7c2100d9f3d@postgresql.org
```

## View Definition

`pg_stat_activity` 是一个系统视图，其视图定义如下：

```sql
CREATE VIEW pg_stat_activity AS
    SELECT
            S.datid AS datid,
            D.datname AS datname,
            S.pid,
            S.leader_pid,
            S.usesysid,
            U.rolname AS usename,
            S.application_name,
            S.client_addr,
            S.client_hostname,
            S.client_port,
            S.backend_start,
            S.xact_start,
            S.query_start,
            S.state_change,
            S.wait_event_type,
            S.wait_event,
            S.state,
            S.backend_xid,
            s.backend_xmin,
            S.query_id,
            S.query,
            S.backend_type
    FROM pg_stat_get_activity(NULL) AS S
        LEFT JOIN pg_database AS D ON (S.datid = D.oid)
        LEFT JOIN pg_authid AS U ON (S.usesysid = U.oid);
```

从视图定义中可以看出，视图中的主要信息来自 `pg_stat_get_activity` 函数，辅以将函数中输出的每个进程连接到的数据库 oid 与用户 oid 分别与 `pg_database` 和 `pg_authid` 两张系统表进行连接，从而得到每个进程连接到的数据库名和用户名。所以接下来简要分析 `pg_stat_get_activity` 函数的实现。

## Implementation

### Backend Status Array

`pg_stat_get_activity` 函数是一个 set returning function，返回的每一行都是一个进程的活动信息。其信息的来源是，PostgreSQL 的每一个进程（包括服务客户端连接的后端进程，以及其它后台辅助进程）都会在共享内存中维护一个 `PgBackendStatus` 结构体，其中记录了这个进程正在进行的活动，其定义如下：

```c
/* ----------
 * PgBackendStatus
 *
 * Each live backend maintains a PgBackendStatus struct in shared memory
 * showing its current activity.  (The structs are allocated according to
 * BackendId, but that is not critical.)  Note that this is unrelated to the
 * cumulative stats system (i.e. pgstat.c et al).
 *
 * Each auxiliary process also maintains a PgBackendStatus struct in shared
 * memory.
 * ----------
 */
typedef struct PgBackendStatus
{
    /*
     * To avoid locking overhead, we use the following protocol: a backend
     * increments st_changecount before modifying its entry, and again after
     * finishing a modification.  A would-be reader should note the value of
     * st_changecount, copy the entry into private memory, then check
     * st_changecount again.  If the value hasn't changed, and if it's even,
     * the copy is valid; otherwise start over.  This makes updates cheap
     * while reads are potentially expensive, but that's the tradeoff we want.
     *
     * The above protocol needs memory barriers to ensure that the apparent
     * order of execution is as it desires.  Otherwise, for example, the CPU
     * might rearrange the code so that st_changecount is incremented twice
     * before the modification on a machine with weak memory ordering.  Hence,
     * use the macros defined below for manipulating st_changecount, rather
     * than touching it directly.
     */
    int         st_changecount;

    /* The entry is valid iff st_procpid > 0, unused if st_procpid == 0 */
    int         st_procpid;

    /* Type of backends */
    BackendType st_backendType;

    /* Times when current backend, transaction, and activity started */
    TimestampTz st_proc_start_timestamp;
    TimestampTz st_xact_start_timestamp;
    TimestampTz st_activity_start_timestamp;
    TimestampTz st_state_start_timestamp;

    /* Database OID, owning user's OID, connection client address */
    Oid         st_databaseid;
    Oid         st_userid;
    SockAddr    st_clientaddr;
    char       *st_clienthostname;  /* MUST be null-terminated */

    /* Information about SSL connection */
    bool        st_ssl;
    PgBackendSSLStatus *st_sslstatus;

    /* Information about GSSAPI connection */
    bool        st_gss;
    PgBackendGSSStatus *st_gssstatus;

    /* current state */
    BackendState st_state;

    /* application name; MUST be null-terminated */
    char       *st_appname;

    /*
     * Current command string; MUST be null-terminated. Note that this string
     * possibly is truncated in the middle of a multi-byte character. As
     * activity strings are stored more frequently than read, that allows to
     * move the cost of correct truncation to the display side. Use
     * pgstat_clip_activity() to truncate correctly.
     */
    char       *st_activity_raw;

    /*
     * Command progress reporting.  Any command which wishes can advertise
     * that it is running by setting st_progress_command,
     * st_progress_command_target, and st_progress_param[].
     * st_progress_command_target should be the OID of the relation which the
     * command targets (we assume there's just one, as this is meant for
     * utility commands), but the meaning of each element in the
     * st_progress_param array is command-specific.
     */
    ProgressCommandType st_progress_command;
    Oid         st_progress_command_target;
    int64       st_progress_param[PGSTAT_NUM_PROGRESS_PARAM];

    /* query identifier, optionally computed using post_parse_analyze_hook */
    uint64      st_query_id;
} PgBackendStatus;
```

可以看到其中记录了进程的 pid、进程的类型、进程正在进行的活动，以及客户端连接 / 事务 / 查询 / 状态开始的时间。在共享内存中，所有进程的这个结构被维护在一个数组中：

```c
static PgBackendStatus *BackendStatusArray = NULL;
```

既然是存放在共享内存中，就可能同时被多个进程读写，所以需要一定的进程同步机制。这个结构体的进程同步机制是使用结构体中的 `st_changecount` 计数器实现的。当一个进程需要修改该结构体中的信息时，首先需要自增这个计数器；在修改完毕以后，也需要自增这个计数器。当进程想要读取这个结构时，首先需要记录下该结构的计数器数值，然后将共享内存中的结构拷贝到进程私有内存后，再次检查这个计数器的值。如果计数器的值没有变，并且是一个偶数，那么说明进程私有内存中的结构体副本是安全可用的；否则说明结构在拷贝过程中发生了并发更新，需要重新到共享内存中拷贝一个正确的副本。在这个并发协议中，**更新这个结构的开销比读取这个结构的开销要低**，这正是设计者想要获得的 trade off：每一个进程在进入不同的状态时都需要更新这个结构，频率极高，并且每个进程只更新自己的结构；而对该结构的访问只会出现在显式调用 `pg_stat_get_activity` 时，其频率相对来说是很低的。

### Local Backend Status Table

在某个进程想要获取共享内存中 `BackendStatusArray` 数组的所有内容时，就需要把整个数组中的内容拷贝一份到该进程私有的内存中，再进行后续的操作。这个过程由 `pgstat_read_current_status` 函数实现：

```c
/* ----------
 * pgstat_read_current_status() -
 *
 *  Copy the current contents of the PgBackendStatus array to local memory,
 *  if not already done in this transaction.
 * ----------
 */
static void
pgstat_read_current_status(void)
{
    volatile PgBackendStatus *beentry;
    LocalPgBackendStatus *localtable;
    LocalPgBackendStatus *localentry;
    char       *localappname,
               *localclienthostname,
               *localactivity;
#ifdef USE_SSL
    PgBackendSSLStatus *localsslstatus;
#endif
#ifdef ENABLE_GSS
    PgBackendGSSStatus *localgssstatus;
#endif
    int         i;

    if (localBackendStatusTable)
        return;                 /* already done */

    pgstat_setup_backend_status_context();

    /*
     * Allocate storage for local copy of state data.  We can presume that
     * none of these requests overflow size_t, because we already calculated
     * the same values using mul_size during shmem setup.  However, with
     * probably-silly values of pgstat_track_activity_query_size and
     * max_connections, the localactivity buffer could exceed 1GB, so use
     * "huge" allocation for that one.
     */
    localtable = (LocalPgBackendStatus *)
        MemoryContextAlloc(backendStatusSnapContext,
                           sizeof(LocalPgBackendStatus) * NumBackendStatSlots);
    localappname = (char *)
        MemoryContextAlloc(backendStatusSnapContext,
                           NAMEDATALEN * NumBackendStatSlots);
    localclienthostname = (char *)
        MemoryContextAlloc(backendStatusSnapContext,
                           NAMEDATALEN * NumBackendStatSlots);
    localactivity = (char *)
        MemoryContextAllocHuge(backendStatusSnapContext,
                               pgstat_track_activity_query_size * NumBackendStatSlots);
#ifdef USE_SSL
    localsslstatus = (PgBackendSSLStatus *)
        MemoryContextAlloc(backendStatusSnapContext,
                           sizeof(PgBackendSSLStatus) * NumBackendStatSlots);
#endif
#ifdef ENABLE_GSS
    localgssstatus = (PgBackendGSSStatus *)
        MemoryContextAlloc(backendStatusSnapContext,
                           sizeof(PgBackendGSSStatus) * NumBackendStatSlots);
#endif

    localNumBackends = 0;

    beentry = BackendStatusArray;
    localentry = localtable;
    for (i = 1; i <= NumBackendStatSlots; i++)
    {
        /*
         * Follow the protocol of retrying if st_changecount changes while we
         * copy the entry, or if it's odd.  (The check for odd is needed to
         * cover the case where we are able to completely copy the entry while
         * the source backend is between increment steps.)  We use a volatile
         * pointer here to ensure the compiler doesn't try to get cute.
         */

        /* ... */
    }

    /* Set the pointer only after completion of a valid table */
    localBackendStatusTable = localtable;
}
```

该函数会从共享内存的 `BackendStatusArray` 结构体中复制一份到进程私有内存中，保存在如下数组里：

```c
/* Status for backends including auxiliary */
static LocalPgBackendStatus *localBackendStatusTable = NULL;

/* Total number of backends including auxiliary */
static int  localNumBackends = 0;
```

进程私有内存中的 `LocalPgBackendStatus` 结构体相比于共享内存中的 `PgBackendStatus` 结构体，除了原有的所有信息，还新增了事务相关的信息：

```c
/* ----------
 * LocalPgBackendStatus
 *
 * When we build the backend status array, we use LocalPgBackendStatus to be
 * able to add new values to the struct when needed without adding new fields
 * to the shared memory. It contains the backend status as a first member.
 * ----------
 */
typedef struct LocalPgBackendStatus
{
    /*
     * Local version of the backend status entry.
     */
    PgBackendStatus backendStatus;

    /*
     * The xid of the current transaction if available, InvalidTransactionId
     * if not.
     */
    TransactionId backend_xid;

    /*
     * The xmin of the current session if available, InvalidTransactionId if
     * not.
     */
    TransactionId backend_xmin;
} LocalPgBackendStatus;
```

### Get Activity

最终，`pg_stat_get_activity` 函数利用了上述 `pgstat_read_current_status` 函数的支持，从共享内存中拷贝所有进程的状态信息到进程私有内存中，然后依次把私有内存中每一个进程的状态信息进行进一步的加工，然后组装为元组返回。

```c
/*
 * Returns activity of PG backends.
 */
Datum
pg_stat_get_activity(PG_FUNCTION_ARGS)
{
#define PG_STAT_GET_ACTIVITY_COLS   30
    int         num_backends = pgstat_fetch_stat_numbackends();
    int         curr_backend;
    int         pid = PG_ARGISNULL(0) ? -1 : PG_GETARG_INT32(0);
    ReturnSetInfo *rsinfo = (ReturnSetInfo *) fcinfo->resultinfo;

    InitMaterializedSRF(fcinfo, 0);

    /* 1-based index */
    for (curr_backend = 1; curr_backend <= num_backends; curr_backend++)
    {
        /* for each row */
        Datum       values[PG_STAT_GET_ACTIVITY_COLS];
        bool        nulls[PG_STAT_GET_ACTIVITY_COLS];

        /* ... */

        tuplestore_putvalues(rsinfo->setResult, rsinfo->setDesc, values, nulls);

        /* If only a single backend was requested, and we found it, break. */
        if (pid != -1)
            break;
    }

    return (Datum) 0;
}
```

在当前版本（PostgreSQL 15）中，该函数返回的每一行都包含 30 个列，其中的信息为：

1. 进程连接到的数据库 oid
2. 进程的 pid
3. 通过该进程登录的用户 ID
4. 连接到该进程的应用名称
5. 进程当前状态
6. 进程当前正在执行的 SQL
7. 进程当前的等待事件类型
8. 进程当前的等待事件
9. 进程进入当前事务的开始时间
10. 进程进入当前活动的开始时间
11. 当前进程启动的时间
12. 进程进入当前状态的开始时间
13. 客户端 IP 地址
14. 客户端域名
15. 客户端端口号
16. 进程当前事务的事务 ID
17. 进程当前的 xmin
18. 后台进程类型（如果这个进程是一个后台进程）
19. 是否启用了 SSL
20. SSL 版本
21. SSL 加密套件
22. SSL bits
23. SSL 客户端 DN
24. SSL 客户端序列号
25. SSL 发放方 DN
26. 是否启用了 GSS
27. GSS Principle
28. GSS 是否启用加密
29. 进程的并行组 leader 的 pid
30. 查询标识符

其中，暴露到 `pg_stat_activity` 视图中的只有其中的部分列。另外，部分列做了权限控制，只有 superuser 或具有 `pg_read_all_stats` 角色的用户才可以看到所有进程这些列的信息。

## References

[PostgreSQL Documentation - 28.2. The Cumulative Statistics System](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW)
