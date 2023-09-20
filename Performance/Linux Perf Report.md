# Linux Performance - Perf Report

Created by: Mr Dk.

2023 / 09 / 20 23:19

Hangzhou, Zhejiang, China

---

## Background

`perf record` 的输出默认会被写入到 `perf.data` 中。通过 `perf report` 命令可以从该采样文件中读取并产生简明的运行时热点情况，默认按开销从高到低排序。

## Usage

### Basic

```shell
$ perf report

Samples: 192K of event 'cycles', Event count (approx.): 134062098663
  Children      Self  Command   Shared Object         Symbol
+   99.15%     0.00%  postgres  [unknown]             [k] 0x49564100642d3b3d
+   99.15%     0.00%  postgres  libc-2.32.so          [.] __libc_start_main
+   99.15%     0.00%  postgres  postgres              [.] startup_hacks
+   99.15%     0.00%  postgres  postgres              [.] PostmasterMain
+   99.15%     0.00%  postgres  postgres              [.] ServerLoop
+   99.15%     0.00%  postgres  postgres              [.] BackendStartup
+   99.15%     0.00%  postgres  postgres              [.] ExitPostmaster
+   99.05%     0.08%  postgres  postgres              [.] PostgresMain
+   91.92%     0.14%  postgres  postgres              [.] exec_simple_query
+   29.00%     0.01%  postgres  postgres              [.] finish_xact_command
+   28.55%     0.05%  postgres  postgres              [.] PortalRun
+   26.79%     0.06%  postgres  postgres              [.] PortalRunMulti
+   26.13%     0.05%  postgres  postgres              [.] ProcessQuery
+   25.37%     1.79%  postgres  postgres              [.] MemoryContextCheck
+   25.12%    15.12%  postgres  postgres              [.] AllocSetCheck
+   20.95%     0.01%  postgres  postgres              [.] ExecutorRun
+   20.93%     0.02%  postgres  pgaudit.so            [.] pgaudit_ExecutorRun_hook
+   20.92%     0.01%  postgres  postgres              [.] standard_ExecutorRun
+   20.88%     0.04%  postgres  postgres              [.] standard_ExecutorRun_NonPX
+   20.68%     0.03%  postgres  polar_htap.so         [.] htap_ExecutePlan_hook
+   20.67%     0.04%  postgres  postgres              [.] ExecutePlan
+   20.40%     0.02%  postgres  postgres              [.] ExecProcNode
+   20.33%     0.02%  postgres  postgres              [.] ExecProcNodeFirst
+   18.99%     0.07%  postgres  postgres              [.] ExecModifyTable
+   16.45%     0.04%  postgres  postgres              [.] pg_plan_queries
+   16.34%     0.02%  postgres  postgres              [.] pg_plan_query
+   16.32%     0.03%  postgres  postgres              [.] planner
+   16.27%     0.04%  postgres  pg_hint_plan.so       [.] pg_hint_plan_planner
+   16.13%     0.03%  postgres  polar_htap.so         [.] htap_planner_hook
+   16.02%     0.12%  postgres  postgres              [.] standard_planner
```

其中，最右边一列中：

- `.` 表示用户空间的符号
- `k` 表示内核级别的符号
- `g`/`u`/`H` 表示虚拟化环境中，虚拟机的内核级、用户级、虚拟机管理软件级别的符号

### Children

上述输出中，从上到下显示了被采样次数最多的函数，这里的采样次数是包括函数自身和函数所调用的子函数的。所以排名最靠前的函数实际上是入口函数。上述输出等价于加入了 `--children`。如果想看具体哪个函数在自身调用层级上消耗的时间较多，不包括子函数的开销，则需要指定 `--no-children` 参数：

```shell
$ perf report --no-children

Samples: 192K of event 'cycles', Event count (approx.): 134062098663
  Overhead  Command   Shared Object         Symbol
+   15.12%  postgres  postgres              [.] AllocSetCheck
+    9.97%  postgres  postgres              [.] sentinel_ok
+    2.30%  postgres  postgres              [.] AllocSetAlloc
+    2.07%  postgres  postgres              [.] base_yyparse
+    1.79%  postgres  postgres              [.] MemoryContextCheck
+    1.44%  postgres  postgres              [.] MemoryContextAllocZeroAligned
+    1.18%  postgres  postgres              [.] heap_hot_search_buffer
+    1.15%  postgres  postgres              [.] hash_bytes
+    1.03%  postgres  postgres              [.] hash_search_with_hash_value
+    0.91%  postgres  postgres              [.] POLAR_MEMORY_ACCOUNT_INC_ALLOCATED
+    0.89%  postgres  postgres              [.] expression_tree_walker
+    0.86%  postgres  postgres              [.] SearchCatCacheInternal
+    0.81%  postgres  postgres              [.] core_yylex
+    0.72%  postgres  postgres              [.] pg_checksum_block
+    0.70%  postgres  libc-2.32.so          [.] __memset_evex_unaligned_erms
+    0.62%  postgres  postgres              [.] polar_lwlock_stat_acquire
+    0.54%  postgres  postgres              [.] palloc0
+    0.51%  postgres  postgres              [.] GetPrivateRefCountEntry
     0.48%  postgres  postgres              [.] palloc
     0.40%  postgres  postgres              [.] AllocSetFreeIndex
     0.40%  postgres  libc-2.32.so          [.] __memmove_evex_unaligned_erms
     0.33%  postgres  postgres              [.] AllocSetFree
     0.32%  postgres  postgres              [.] pg_atomic_compare_exchange_u32_impl
```

从上面的结果中可以看出，热点位于 PostgreSQL 的 MemoryContext Check 中。这是 debug 模式下的性能问题根源。

## References

[Kernel Wiki - Sample analysis with perf report](https://perf.wiki.kernel.org/index.php/Tutorial#Sample_analysis_with_perf_report)

[perf-report(1) — Linux manual page](https://man7.org/linux/man-pages/man1/perf-report.1.html)
