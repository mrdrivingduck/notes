# iotop

Created by : Mr Dk.

2023 / 02 / 19 20:53

Hangzhou, Zhejiang, China

---

## Background

`iotop` 是一个类似 `top` 的 I/O 监视器。它能够在 Linux 2.6.20 及之后的内核中被用于监控进程或线程当前的 I/O 使用情况。使用 Python 实现。注意，运行这个程序需要 root 权限。

## Usage

```shell
$ iotop -h
Usage: /usr/sbin/iotop [OPTIONS]

DISK READ and DISK WRITE are the block I/O bandwidth used during the sampling
period. SWAPIN and IO are the percentages of time the thread spent respectively
while swapping in and waiting on I/O more generally. PRIO is the I/O priority
at which the thread is running (set using the ionice command).

Controls: left and right arrows to change the sorting column, r to invert the
sorting order, o to toggle the --only option, p to toggle the --processes
option, a to toggle the --accumulated option, i to change I/O priority, q to
quit, any other key to force a refresh.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -o, --only            only show processes or threads actually doing I/O
  -b, --batch           non-interactive mode
  -n NUM, --iter=NUM    number of iterations before ending [infinite]
  -d SEC, --delay=SEC   delay between iterations [1 second]
  -p PID, --pid=PID     processes/threads to monitor [all]
  -u USER, --user=USER  users to monitor [all]
  -P, --processes       only show processes, not all threads
  -a, --accumulated     show accumulated I/O instead of bandwidth
  -k, --kilobytes       use kilobytes instead of a human friendly unit
  -t, --time            add a timestamp on each line (implies --batch)
  -q, --quiet           suppress some lines of header (implies --batch)
  --no-help             suppress listing of shortcuts
```

```shell
$ iotop
Total DISK READ:         0.00 B/s | Total DISK WRITE:         0.00 B/s
Current DISK READ:       0.00 B/s | Current DISK WRITE:       0.00 B/s
    TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN     IO>    COMMAND                                                3168099 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.02 % [kworker/u4:0-events_freezable_power_]
      1 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % init
      2 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [kthreadd]
      3 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [rcu_gp]
      4 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [rcu_par_gp]
      6 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [kworker/0:0H-kblockd]
      9 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [mm_percpu_wq]
     10 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [ksoftirqd/0]
     11 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [rcu_sched]
     12 rt/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [migration/0]
     13 rt/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [idle_inject/0]
     14 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [cpuhp/0]
     15 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [cpuhp/1]
     16 rt/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [idle_inject/1]
     17 rt/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [migration/1]
     18 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [ksoftirqd/1]
     20 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [kworker/1:0H-kblockd]
     21 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [kdevtmpfs]
     22 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [netns]
     23 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [rcu_tasks_kthre]
     24 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [kauditd]
     25 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [khungtaskd]
     26 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [oom_reaper]
     27 be/0 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [writeback]
     28 be/4 root        0.00 B/s    0.00 B/s  0.00 %  0.00 % [kcompactd0]
  keys:  any: refresh  q: quit  i: ionice  o: active  p: procs  a: accum                                                  sort:  r: asc  left: SWAPIN  right: COMMAND  home: TID  end: COMMAND
```

使用 `-o` 参数只打印当前正在进行 I/O 的进程/线程。

使用 `-p PID` 参数可以只观测某个进程的 I/O。

使用 `-a` 参数可以进入 **累加模式**。输出的数值不是带宽（瞬时值），而是 `iotop` 启动后的累计值。

使用 `-t` 参数可以在每一行输出中带上时间戳。

## References

[iotop Command in Linux with Examples](https://www.geeksforgeeks.org/iotop-command-in-linux-with-examples/)

[iotop(1) - Linux man page](https://linux.die.net/man/1/iotop)
