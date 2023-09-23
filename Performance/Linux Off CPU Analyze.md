# Linux Performance - Off CPU Analyze

Created by: Mr Dk.

2023 / 09 / 24 00:08

Hangzhou, Zhejiang, China

---

## Background

性能问题可以被分为两类：

- On CPU：进程运行在 CPU 上所耗费的时间
- Off CPU：进程被阻塞而离开 CPU 的时间，比如 I/O、锁、定时器等

常规的 CPU 采样只能够收集 On CPU 的统计信息，但无法统计 Off CPU 的统计信息。

## Differences

### CPU Sampling

On CPU 的采样如下图所示。Perf 相关工具的采样原理是，以固定的频率采集当时 CPU 上的进程堆栈信息。当进程因各种因素离开 CPU 时，就不再会被采样了：

```
    CPU Sampling ----------------------------------------------->
     |  |  |  |  |  |  |                      |  |  |  |  |
     A  A  A  A  B  B  B                      B  A  A  A  A
    A(---------.                                .----------)
               |                                |
               B(--------.                   .--)
                         |                   |         user-land
   - - - - - - - - - - syscall - - - - - - - - - - - - - - - - -
                         |                   |         kernel
                         X     Off-CPU       |
                       block . . . . . interrupt
```

### Application Tracing

应用程序内部可以自己实现 Off CPU 统计，但问题在于，追踪所有函数的开销极大，而追踪部分函数又可能丢失真正想追踪的目标：

```
    App Tracing ------------------------------------------------>
    |          |                                |          |
    A(         B(                               B)         A)

    A(---------.                                .----------)
               |                                |
               B(--------.                   .--)
                         |                   |         user-land
   - - - - - - - - - - syscall - - - - - - - - - - - - - - - - -
                         |                   |         kernel
                         X     Off-CPU       |
                       block . . . . . interrupt
```

### Off-CPU Tracing

只追踪 OS 内核将线程从 CPU 上换出的函数，并记录当时的时间戳和用户态堆栈。相对来说，开销小了很多：

```
    Off-CPU Tracing -------------------------------------------->
                         |                   |
                         B                   B
                         A                   A
    A(---------.                                .----------)
               |                                |
               B(--------.                   .--)
                         |                   |         user-land
   - - - - - - - - - - syscall - - - - - - - - - - - - - - - - -
                         |                   |         kernel
                         X     Off-CPU       |
                       block . . . . . interrupt
```

## Overhead

开销是性能追踪中最重要的因素。相对来说，Perf 需要将追踪得到的数据返回用户态并写入文件中，所以产生的数据量和追踪的时间成正比，并且可能受到磁盘 I/O 的限制；而使用 eBPF 则会在内核态捕获并追踪 **唯一** 的堆栈，这意味着追踪数据量并不会随着时间而线性增长。

比如，通过 [eBPF](https://ebpf.io/)/[BCC](https://github.com/iovisor/bcc) 工具 `offcputime`，可以直接得到 Flame Graph 工具能够接受的输入格式，生成 Off CPU 火焰图。当然用 Perf 也可以，就是开销大一点啦。

## References

[Off-CPU Analysis](https://www.brendangregg.com/offcpuanalysis.html)

[Off-CPU Flame Graphs](https://www.brendangregg.com/FlameGraphs/offcpuflamegraphs.html)

[Linux perf_events Off-CPU Time Flame Graph](https://www.brendangregg.com/blog/2015-02-26/linux-perf-off-cpu-flame-graph.html)
