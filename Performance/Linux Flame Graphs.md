# Linux Performance - Flame Graphs

Created by: Mr Dk.

2023 / 09 / 20 23:19

Hangzhou, Zhejiang, China

---

## Background

火焰图（Flame Graph）是性能优化大师 Brendan Gregg 发明的可视化性能分析方法，将采样得到的统计数据以直观的形式通过图表展示出来，解决了采样数据量较大、难以直观分析的问题。火焰图可以有 on-CPU / off-CPU 火焰图、内存火焰图、冷热火焰图、差分火焰图等等。一般来说，通过 `perf record` 采样的数据能够得到的是 on-CPU 火焰图，展示了 CPU 运行过程中被采样最频繁的函数。然而，这并不能反映出程序因阻塞而离开 CPU 的时间，所以还需要通过其它方式进行采样，并产生 off-CPU 火焰图进行全面的分析。两者结合可以解释 100% 的程序运行时间。

每一簇火焰的宽度表示被采样命中的次数（按字母排序），每一簇火焰的高度表示被采样时的栈深度。一簇火焰越宽，表示采样时遇到它所对应的函数最频繁；一簇火焰越高，表示采样时它的调用栈越深。

![flamegraph](https://www.brendangregg.com/FlameGraphs/cpu-mysql-updated.svg)

## Generation

如何得到一张火焰图呢？一般来说需要三步：

1. 采样数据
2. 折叠堆栈
3. 产生火焰图

### Sampling

使用 Perf / eBPF / DTrace 都是可以的。

### Folding Stacks

采样后的数据需要被加工才能产生火焰图。Brendan Gregg 的 [FlameGraph](https://github.com/brendangregg/FlameGraph) GitHub 仓库中已经提供了加工采样后数据的脚本：

```shell
git clone https://github.com/brendangregg/FlameGraph
cd FlameGraph
```

仓库内有一堆 `stackcollapse-*.pl` 的脚本。根据采样时使用的工具，选择相对应的工具来进行加工即可：

```shell
$ ls -l | grep stackcollapse-
-rwxrwxr-x 1 postgres postgres     1185 Sep 17 11:28 stackcollapse-aix.pl
-rwxrwxr-x 1 postgres postgres     1901 Sep 17 11:28 stackcollapse-bpftrace.pl
-rwxrwxr-x 1 postgres postgres     3910 Sep 17 11:28 stackcollapse-chrome-tracing.py
-rwxrwxr-x 1 postgres postgres     2304 Sep 17 11:28 stackcollapse-elfutils.pl
-rwxrwxr-x 1 postgres postgres     1816 Sep 17 11:28 stackcollapse-gdb.pl
-rwxrwxr-x 1 postgres postgres     3631 Sep 17 11:28 stackcollapse-go.pl
-rwxrwxr-x 1 postgres postgres      680 Sep 17 11:28 stackcollapse-instruments.pl
-rwxrwxr-x 1 postgres postgres     1786 Sep 17 11:28 stackcollapse-java-exceptions.pl
-rwxrwxr-x 1 postgres postgres     5207 Sep 17 11:28 stackcollapse-jstack.pl
-rwxrwxr-x 1 postgres postgres     1858 Sep 17 11:28 stackcollapse-ljp.awk
-rwxrwxr-x 1 postgres postgres    13179 Sep 17 11:28 stackcollapse-perf.pl
-rwxrwxr-x 1 postgres postgres     6527 Sep 17 11:28 stackcollapse-perf-sched.awk
-rwxrwxr-x 1 postgres postgres     2675 Sep 17 11:28 stackcollapse-pmc.pl
-rwxrwxr-x 1 postgres postgres     1569 Sep 17 11:28 stackcollapse-recursive.pl
-rwxrwxr-x 1 postgres postgres     7871 Sep 17 11:28 stackcollapse-sample.awk
-rwxrwxr-x 1 postgres postgres     2309 Sep 17 11:28 stackcollapse-stap.pl
-rwxrwxr-x 1 postgres postgres     2983 Sep 17 11:28 stackcollapse-vsprof.pl
-rwxrwxr-x 1 postgres postgres     3434 Sep 17 11:28 stackcollapse-vtune-mc.pl
-rw-rw-r-- 1 postgres postgres     3174 Sep 17 11:28 stackcollapse-vtune.pl
-rwxrwxr-x 1 postgres postgres     1938 Sep 17 11:28 stackcollapse-wcp.pl
-rwxrwxr-x 1 postgres postgres     5683 Sep 17 11:28 stackcollapse-xdebug.php
```

### Generating Flame Graph

假设使用了 Perf 采样，当前路径下会有 `perf.data`。使用如下命令就可以生成火焰图：

```shell
perf script | ./stackcollapse-perf.pl > out.perf-folded
./flamegraph.pl out.perf-folded > perf.svg
```

然后直接通过浏览器访问 `perf.svg` 即可。

## References

[Flame Graphs](https://www.brendangregg.com/flamegraphs.html)

[CPU Flame Graphs](https://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html)

[Off-CPU Flame Graphs](https://www.brendangregg.com/FlameGraphs/offcpuflamegraphs.html)

[Off-CPU Analysis](https://www.brendangregg.com/offcpuanalysis.html)
