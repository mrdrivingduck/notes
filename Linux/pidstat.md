# pidstat

Created by : Mr Dk.

2023 / 08 / 14 00:23

Hangzhou, Zhejiang, China

---

## Background

`pidstat` 用于打印 Linux 任务（进程/线程）的统计信息。

## Usage

```shell
$ pidstat --help
Usage: pidstat [ options ] [ <interval> [ <count> ] ] [ -e <program> <args> ]
Options are:
[ -d ] [ -H ] [ -h ] [ -I ] [ -l ] [ -R ] [ -r ] [ -s ] [ -t ] [ -U [ <username> ] ]
[ -u ] [ -V ] [ -v ] [ -w ] [ -C <command> ] [ -G <process_name> ] [ --human ]
[ -p { <pid> [,...] | SELF | ALL } ] [ -T { TASK | CHILD | ALL } ]
```

### Filter

使用 `-c` 参数按命令名称过滤：

```shell
$ pidstat -C postgres
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      08/14/2023      _x86_64_        (104 CPU)

12:02:25 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
12:02:25 AM  1000    513728    0.00    0.00    0.00    0.00    0.00    58  postgres
12:02:25 AM  1000   1000582    0.00    0.00    0.00    0.00    0.00    44  postgres
12:02:25 AM  1000   1000587    0.00    0.00    0.00    0.00    0.00    89  postgres
12:02:25 AM  1000   1000590    0.00    0.00    0.00    0.00    0.00    79  postgres
12:02:25 AM  1000   1000591    0.00    0.00    0.00    0.00    0.00    25  postgres
12:02:25 AM  1000   1000593    0.00    0.00    0.00    0.00    0.00    36  postgres
12:02:25 AM  1000   1000625    0.00    0.00    0.00    0.00    0.00    27  postgres
12:02:25 AM  1000   1000627    0.00    0.00    0.00    0.00    0.00   103  postgres
...
```

使用 `-p` 参数按 pid 过滤：

```shell
$ pidstat -p 513728
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      08/14/2023      _x86_64_        (104 CPU)

12:03:34 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
12:03:34 AM  1000    513728    0.00    0.00    0.00    0.00    0.00    58  postgres
```

### CPU Utilization

使用 `-u` 参数将会打印 CPU 使用情况：

- `%usr`：用户空间 CPU 使用量
- `%system`：内核空间 CPU 使用量
- `%guest`：虚拟机 CPU 使用量
- `%wait`：等待被执行的 CPU 使用量
- `%CPU`：CPU 总使用量
- `CPU`：执行该任务的 CPU 编号

```shell
$ pidstat -p 513728 -u
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      08/14/2023      _x86_64_        (104 CPU)

12:13:28 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
12:13:28 AM  1000    513728    0.00    0.00    0.00    0.00    0.00    58  postgres
```

### Context Switching

使用 `-w` 参数将会打印上下文切换信息：

- `cswch/s`：每秒自愿发生的上下文切换次数（比如因等待资源而阻塞）
- `nvcswch/s`：每秒非自愿发生的上下文切换次数（比如时间片用完）

```shell
$ pidstat -p 513728 -w
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      08/14/2023      _x86_64_        (104 CPU)

12:13:41 AM   UID       PID   cswch/s nvcswch/s  Command
12:13:41 AM  1000    513728      0.00      0.00  postgres
```

### Memory Utilization

使用 `-r` 参数将会打印缺页和内存使用信息：

- `minflt/s`：每秒钟不需要从内存装载的缺页次数
- `majflt/s`：每秒钟需要从内存装载的缺页次数
- `VSZ`：虚拟内存 kB 数
- `RSS`：非 swap 的物理内存 kB 数
- `%MEM`：目前使用的物理内存占所有物理内存的比例

```shell
$ pidstat -p 513728 -r
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      08/14/2023      _x86_64_        (104 CPU)

12:15:29 AM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
12:15:29 AM  1000    513728      0.00      0.00 2980112      80   0.00  postgres
```

### I/O Statistics

使用 `-d` 参数将会打印 I/O 统计信息：

- `kB_rd/s`：每秒从磁盘上读取的 kB 数
- `kB_wr/s`：每秒写入磁盘的 kB 数
- `iodelay`：等待 I/O 完成的时钟周期数

```shell
$ pidstat -d
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      08/14/2023      _x86_64_        (104 CPU)

12:21:36 AM   UID       PID   kB_rd/s   kB_wr/s kB_ccwr/s iodelay  Command
12:21:36 AM     0         1     -1.00     -1.00     -1.00   11739  systemd
12:21:36 AM     0       778     -1.00     -1.00     -1.00    2611  kswapd0
12:21:36 AM     0       779     -1.00     -1.00     -1.00     140  kswapd1
...
```

### Threads

使用 `-t` 参数可以打印一个进程内所有线程的信息：

```shell
$pidstat -p 399853 -t
Linux 5.10.134-007.ali5000.al8.x86_64 (3970e7e00014)    08/13/2023      _x86_64_        (104 CPU)

04:26:16 PM   UID      TGID       TID    %usr %system  %guest   %wait    %CPU   CPU  Command
04:26:16 PM  1000    399853         -    0.00    0.00    0.00    0.00    0.00    20  postgres
04:26:16 PM  1000         -    399853    0.00    0.00    0.00    0.00    0.00    20  |__postgres
04:26:16 PM  1000         -    399854    0.00    0.00    0.00    0.00    0.00     9  |__postgres
04:26:16 PM  1000         -    399855    0.00    0.00    0.00    0.00    0.00    17  |__pxadps399853
```

## References

[pidstat(1) — Linux manual page](https://man7.org/linux/man-pages/man1/pidstat.1.html)

[Monitor and Find Statistics for Linux Processes Using pidstat Tool](https://www.geeksforgeeks.org/monitor-and-find-statistics-for-linux-procesess-using-pidstat-tool/)
