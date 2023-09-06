# mpstat

Created by : Mr Dk.

2023 / 09 / 07 0:16

Hangzhou, Zhejiang, China

---

## Background

`mpstat` 能够显示所有 CPU 的统计信息。

## Usage

```shell
$ mpstat --help
Usage: mpstat [ options ] [ <interval> [ <count> ] ]
Options are:
[ -A ] [ -n ] [ -T ] [ -u ] [ -V ]
[ -I { SUM | CPU | SCPU | ALL } ] [ -N { <node_list> | ALL } ]
[ --dec={ 0 | 1 | 2 } ] [ -o JSON ] [ -P { <cpu_list> | ALL } ]
```

## Processors

使用 `-P ALL` 可以打印所有 CPU 的信息：

```shell
$ mpstat -P ALL
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    09/07/23        _x86_64_        (8 CPU)

00:24:10     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
00:24:10     all    0.62    0.00    0.35    0.20    0.00    0.09    0.00    0.00    0.00   98.74
00:24:10       0    0.61    0.00    0.39    0.28    0.00    0.38    0.00    0.00    0.00   98.35
00:24:10       1    0.60    0.00    0.23    0.44    0.00    0.18    0.00    0.00    0.00   98.55
00:24:10       2    0.66    0.00    0.40    0.26    0.00    0.04    0.00    0.00    0.00   98.65
00:24:10       3    0.72    0.00    0.38    0.07    0.00    0.03    0.00    0.00    0.00   98.81
00:24:10       4    0.58    0.00    0.43    0.18    0.00    0.03    0.00    0.00    0.00   98.79
00:24:10       5    0.59    0.00    0.35    0.05    0.00    0.01    0.00    0.00    0.00   99.00
00:24:10       6    0.71    0.00    0.40    0.18    0.00    0.01    0.00    0.00    0.00   98.70
00:24:10       7    0.49    0.00    0.26    0.13    0.00    0.01    0.00    0.00    0.00   99.11
```

还可以提供一个 CPU 列表只看某几个 CPU：

```shell
$ mpstat -P 1,5
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    09/07/23        _x86_64_        (8 CPU)

00:25:16     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
00:25:16       1    0.58    0.00    0.22    0.43    0.00    0.18    0.00    0.00    0.00   98.59
00:25:16       5    0.57    0.00    0.33    0.05    0.00    0.01    0.00    0.00    0.00   99.03
```

## Periodically

每隔指定时间打印一次，指定打印次数：

```shell
$ mpstat 1 5
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    09/07/23        _x86_64_        (8 CPU)

00:27:03     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
00:27:04     all    0.12    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00   99.88
00:27:05     all    0.00    0.00    0.12    0.00    0.00    0.00    0.00    0.00    0.00   99.88
00:27:06     all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
00:27:07     all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
00:27:08     all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
Average:     all    0.02    0.00    0.02    0.00    0.00    0.00    0.00    0.00    0.00   99.95
```

## References

[mpstat(1) - Linux man page](https://linux.die.net/man/1/mpstat)

[mpstat Command in Linux with Examples](https://www.geeksforgeeks.org/mpstat-command-in-linux-with-examples/)
