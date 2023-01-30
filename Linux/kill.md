# kill

Created by : Mr Dk.

2023 / 01 / 30 10:53

Hangzhou, Zhejiang, China

---

## Background

`kill` 用于向进程发送信号。

## Usage

列出可以发送的信号：

```shell
$ kill -l
 1) SIGHUP       2) SIGINT       3) SIGQUIT      4) SIGILL       5) SIGTRAP
 6) SIGABRT      7) SIGBUS       8) SIGFPE       9) SIGKILL     10) SIGUSR1
11) SIGSEGV     12) SIGUSR2     13) SIGPIPE     14) SIGALRM     15) SIGTERM
16) SIGSTKFLT   17) SIGCHLD     18) SIGCONT     19) SIGSTOP     20) SIGTSTP
21) SIGTTIN     22) SIGTTOU     23) SIGURG      24) SIGXCPU     25) SIGXFSZ
26) SIGVTALRM   27) SIGPROF     28) SIGWINCH    29) SIGIO       30) SIGPWR
31) SIGSYS      34) SIGRTMIN    35) SIGRTMIN+1  36) SIGRTMIN+2  37) SIGRTMIN+3
38) SIGRTMIN+4  39) SIGRTMIN+5  40) SIGRTMIN+6  41) SIGRTMIN+7  42) SIGRTMIN+8
43) SIGRTMIN+9  44) SIGRTMIN+10 45) SIGRTMIN+11 46) SIGRTMIN+12 47) SIGRTMIN+13
48) SIGRTMIN+14 49) SIGRTMIN+15 50) SIGRTMAX-14 51) SIGRTMAX-13 52) SIGRTMAX-12
53) SIGRTMAX-11 54) SIGRTMAX-10 55) SIGRTMAX-9  56) SIGRTMAX-8  57) SIGRTMAX-7
58) SIGRTMAX-6  59) SIGRTMAX-5  60) SIGRTMAX-4  61) SIGRTMAX-3  62) SIGRTMAX-2
63) SIGRTMAX-1  64) SIGRTMAX
```

### 基本语法

直接使用进程号。使用 `-s` 可以指定要发送的信号类型：

```shell
$ kill -s HUP 12345
$ kill -SIGHUP 12345
```

### 向一个范围内的进程发送信号

使用 shell 的语法实现，将会展开为闭区间内的所有进程号：

```shell
$ kill {3457..3464}
bash: kill: (3457) - No such process
bash: kill: (3458) - No such process
bash: kill: (3459) - No such process
bash: kill: (3460) - No such process
bash: kill: (3461) - No such process
bash: kill: (3462) - No such process
bash: kill: (3463) - No such process
bash: kill: (3464) - No such process
```

## References

[kill(1) — Linux manual page](https://man7.org/linux/man-pages/man1/kill.1.html)

[Stackoverflow - How to kill a range of consecutive processes in Linux?](https://stackoverflow.com/questions/49756870/how-to-kill-a-range-of-consecutive-processes-in-linux)
