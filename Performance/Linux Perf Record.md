# Linux Performance - Perf Record

Created by: Mr Dk.

2023 / 09 / 18 20:55 💣

Hangzhou, Zhejiang, China

---

## Background

`perf record` 用于采样程序运行时的统计信息并记录到文件中。采样结果可以被转移到其它机器上进行分析，需要和其它 `perf` 子命令配合使用。采样的粒度可以是每个线程、每个进程、每个 CPU、某几类事件，等等。

## Usage

文档过长，选项过多，暂不一一记录。根据性能分析大师 Brendan Gregg 提供的一些 [One-Liners](https://www.brendangregg.com/perf.html)，比较常用的命令：

```shell
# Sample CPU stack traces (via frame pointers) for the specified PID, at 99 Hertz, for 10 seconds:
perf record -F 99 -p PID -g -- sleep 10
```

其中：

- `-F` 表示采样频率赫兹数（每秒采样多少次），以更高的频率采样也可以，但会带来更多开销；以 `99` Hz 采样可以与 CPU 时钟周期错开，防止采样到一些因时钟周期而产生的特定行为
- `-p` 表示被采样的进程号，也可以是一个逗号分隔的列表；`-t` 同理，表示线程号
- `-a` 表示在所有 CPU 上采样，自 Linux 4.11 开始已经是默认选项；通过 `-C` 可以指定 CPU 列表或范围采样
- `-g` 表示记录采样时的程序调用栈
- `-- sleep 10` 表示采样 10s

`-e` 可以指定记录的事件。什么事件都不指定时，默认追踪 `cycles` 事件（时钟周期数）。

采样结束以后，在当前目录下将会生成一个采样结果文件 `perf.data`（用 `-o` 参数可以重命名）。

## References

[Kernel Wiki - Sampling with perf record](https://perf.wiki.kernel.org/index.php/Tutorial#Sampling_with_perf_record)

[perf-record(1) — Linux manual page](https://man7.org/linux/man-pages/man1/perf-record.1.html)

[perf Examples](https://www.brendangregg.com/perf.html)
