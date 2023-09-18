# Linux Performance - Perf Event

Created by: Mr Dk.

2023 / 09 / 18 12:55 💣

Hangzhou, Zhejiang, China

---

## Background

Linux 内核提供 `perf_event` 子系统，其对应的前端工具被称为 `perf`。这是一个强大的性能剖析工具，跟随内核版本被不断更新、加强。`perf` 利用了 Linux 内核中的大量性能计数器，支持对某个特定线程/进程、每个特定 CPU、每种事件单独计数；也利用了 [Tracepoints](https://www.kernel.org/doc/Documentation/trace/tracepoints.txt)，即内核代码中特定位置的钩子（Hook），可以执行动态注册的函数（Probe）。

## Events

`perf` 支持对一系列可衡量的事件进行观测，从中可以洞悉程序的热点代码和性能问题。这些事件的来源有：

- Software Event：来自于 Linux 内核代码中的计数器，比如上下文切换次数
- PMU (Performance Monitoring Unit) Hardware Event：每种处理器内的性能计数器，比如 L1 缓存 miss 次数
- Hardware Cache Event：不同 CPU 的共性性能指标，可能会映射到不同 CPU 的不同硬件计数器上，或干脆不可用
- Tracepoint Event

```bash
$ perf list

List of pre-defined events (to be used in -e):

  branch-misses                                      [Hardware event]
  bus-cycles                                         [Hardware event]
  cache-misses                                       [Hardware event]
  cache-references                                   [Hardware event]
  cpu-cycles OR cycles                               [Hardware event]
  instructions                                       [Hardware event]
  stalled-cycles-backend OR idle-cycles-backend      [Hardware event]
  stalled-cycles-frontend OR idle-cycles-frontend    [Hardware event]

  alignment-faults                                   [Software event]
  bpf-output                                         [Software event]
  context-switches OR cs                             [Software event]
  cpu-clock                                          [Software event]
  cpu-migrations OR migrations                       [Software event]
  dummy                                              [Software event]
  emulation-faults                                   [Software event]
  major-faults                                       [Software event]
  minor-faults                                       [Software event]
  page-faults OR faults                              [Software event]
  task-clock                                         [Software event]

  duration_time                                      [Tool event]

  L1-dcache-load-misses                              [Hardware cache event]
  L1-dcache-loads                                    [Hardware cache event]
  L1-icache-load-misses                              [Hardware cache event]
  L1-icache-loads                                    [Hardware cache event]
  LLC-load-misses                                    [Hardware cache event]
  LLC-loads                                          [Hardware cache event]
  branch-load-misses                                 [Hardware cache event]
  branch-loads                                       [Hardware cache event]
  dTLB-load-misses                                   [Hardware cache event]
  dTLB-loads                                         [Hardware cache event]
  iTLB-load-misses                                   [Hardware cache event]
  iTLB-loads                                         [Hardware cache event]

  ali_drw_21000/chi_rxdat/                           [Kernel PMU event]
  ali_drw_21000/chi_rxrsp/                           [Kernel PMU event]
```

## References

[Kernel Wiki - perf: Linux profiling with performance counters](https://perf.wiki.kernel.org/index.php/Main_Page)

[Tutorial - Linux kernel profiling with perf](https://perf.wiki.kernel.org/index.php/Tutorial)
