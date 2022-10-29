# watch

Created by : Mr Dk.

2022 / 10 / 29 11:35

Hangzhou, Zhejiang, China

---

## Background

`watch` 命令能够周期性地执行一条命令，并全屏打印执行结果。这非常适合监控。默认周期为两秒。

## Syntax

```shell:no-line-numbers
$ watch -h

Usage:
 watch [options] command

Options:
  -b, --beep             beep if command has a non-zero exit
  -c, --color            interpret ANSI color and style sequences
  -d, --differences[=<permanent>]
                         highlight changes between updates
  -e, --errexit          exit if command has a non-zero exit
  -g, --chgexit          exit when output from command changes
  -n, --interval <secs>  seconds to wait between updates
  -p, --precise          attempt run command in precise intervals
  -t, --no-title         turn off header
  -x, --exec             pass command to exec instead of "sh -c"

 -h, --help     display this help and exit
 -v, --version  output version information and exit

For more details see watch(1).
```

## Usage

使用 `-n` 参数可以调整周期运行的时间间隔，`-d` 参数可以高亮本次运行和上次运行之间的差异。比如监控网络时：

```shell:no-line-numbers
$ watch -n 1 -d netstat

Every 1.0s: netstat                                                      nat: Sat Oct 29 11:27:31 2022

Active Internet connections (w/o servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 nat:34510               169.254.0.55:http       ESTABLISHED
tcp        0      0 nat:56196               169.254.0.138:8186      ESTABLISHED
tcp        0      1 nat:53986               10.148.188.202:http     SYN_SENT
tcp        0      0 nat:ssh                 112.10.216.174:38489    ESTABLISHED
tcp        0      0 nat:39234               169.254.0.55:5574       ESTABLISHED
Active UNIX domain sockets (w/o servers)
Proto RefCnt Flags       Type       State         I-Node   Path
unix  2      [ ]         DGRAM                    120540811 /run/user/0/systemd/notify
unix  3      [ ]         DGRAM                    15934    /run/systemd/notify
...
```

另外，使用 `-c` 参数可以解释输出中的颜色信息，比如 `neofetch`：

```shell:no-line-numbers
$ watch neofetch

Every 2.0s: neofetch                                              zjt-lenovo: Sat Oct 29 11:24:55 2022

^[?25l^[?7l^[0m^[31m^[1m            .-/+oossssoo+/-.
        `:+ssssssssssssssssss+:`
      -+ssssssssssssssssssyyssss+-
    .ossssssssssssssssss^[37m^[0m^[1mdMMMNy^[0m^[31m^[1msssso.
   /sssssssssss^[37m^[0m^[1mhdmmNNmmyNMMMMh^[0m^[31m^[1mssssss/
  +sssssssss^[37m^[0m^[1mhm^[0m^[31m^[1myd^[37m^[0m^[1mMMMMMMMNddddy^[0m^[31m^[1mssssssss+
 /ssssssss^[37m^[0m^[1mhNMMM^[0m^[31m^[1myh^[37m^[0m^[1mhyyyyhmNMMMNh^[0m^[31m^[1mssssssss/
.ssssssss^[37m^[0m^[1mdMMMNh^[0m^[31m^[1mssssssssss^[37m^[0m^[1mhNMMMd^[0m^[31m^[1mssssssss.
+ssss^[37m^[0m^[1mhhhyNMMNy^[0m^[31m^[1mssssssssssss^[37m^[0m^[1myNMMMy^[0m^[31m^[1msssssss+
oss^[37m^[0m^[1myNMMMNyMMh^[0m^[31m^[1mssssssssssssss^[37m^[0m^[1mhmmmh^[0m^[31m^[1mssssssso
oss^[37m^[0m^[1myNMMMNyMMh^[0m^[31m^[1msssssssssssssshmmmh^[0m^[31m^[1mssssssso
+ssss^[37m^[0m^[1mhhhyNMMNy^[0m^[31m^[1mssssssssssss^[37m^[0m^[1myNMMMy^[0m^[31m^[1msssssss+
.ssssssss^[37m^[0m^[1mdMMMNh^[0m^[31m^[1mssssssssss^[37m^[0m^[1mhNMMMd^[0m^[31m^[1mssssssss.
 /ssssssss^[37m^[0m^[1mhNMMM^[0m^[31m^[1myh^[37m^[0m^[1mhyyyyhdNMMMNh^[0m^[31m^[1mssssssss/
  +sssssssss^[37m^[0m^[1mdm^[0m^[31m^[1myd^[37m^[0m^[1mMMMMMMMMddddy^[0m^[31m^[1mssssssss+
   /sssssssssss^[37m^[0m^[1mhdmNNNNmyNMMMMh^[0m^[31m^[1mssssss/
    .ossssssssssssssssss^[37m^[0m^[1mdMMMNy^[0m^[31m^[1msssso.
      -+sssssssssssssssss^[37m^[0m^[1myyy^[0m^[31m^[1mssss+-
        `:+ssssssssssssssssss+:`
            .-/+oossssoo+/-.^[0m
^[20A^[9999999D^[43C^[0m^[1m^[31m^[1mmrdrivingduck^[0m@^[31m^[1mzjt-lenovo^[0m
^[43C^[0m------------------------^[0m
^[43C^[0m^[31m^[1mOS^[0m^[0m:^[0m Ubuntu 22.04.1 LTS on Windows 10 x86_64^[0m
^[43C^[0m^[31m^[1mKernel^[0m^[0m:^[0m 5.10.16.3-microsoft-standard-WSL2^[0m
^[43C^[0m^[31m^[1mUptime^[0m^[0m:^[0m 1 hour, 5 mins^[0m
^[43C^[0m^[31m^[1mPackages^[0m^[0m:^[0m 780 (dpkg)^[0m
^[43C^[0m^[31m^[1mShell^[0m^[0m:^[0m zsh 5.8.1^[0m
^[43C^[0m^[31m^[1mTerminal^[0m^[0m:^[0m Windows Terminal^[0m
```

这都什么玩意儿啊？因为没有解析 ANSI 的颜色样式序列。加上 `-c` 以后：

```shell:no-line-numbers
$ watch -c neofetch

Every 2.0s: neofetch                                              zjt-lenovo: Sat Oct 29 11:25:31 2022

25l7l            .-/+oossssoo+/-.
        `:+ssssssssssssssssss+:`
      -+ssssssssssssssssssyyssss+-
    .ossssssssssssssssssdMMMNysssso.
   /ssssssssssshdmmNNmmyNMMMMhssssss/
  +ssssssssshmydMMMMMMMNddddyssssssss+
 /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/
.ssssssssdMMMNhsssssssssshNMMMdssssssss.
+sssshhhyNMMNyssssssssssssyNMMMysssssss+
ossyNMMMNyMMhsssssssssssssshmmmhssssssso
ossyNMMMNyMMhsssssssssssssshmmmhssssssso
+sssshhhyNMMNyssssssssssssyNMMMysssssss+
.ssssssssdMMMNhsssssssssshNMMMdssssssss.
 /sssssssshNMMMyhhyyyyhdNMMMNhssssssss/
  +sssssssssdmydMMMMMMMMddddyssssssss+
   /ssssssssssshdmNNNNmyNMMMMhssssss/
    .ossssssssssssssssssdMMMNysssso.
      -+sssssssssssssssssyyyssss+-
        `:+ssssssssssssssssss+:`
            .-/+oossssoo+/-.
mrdrivingduck@zjt-lenovo
------------------------
OS: Ubuntu 22.04.1 LTS on Windows 10 x86_64
Kernel: 5.10.16.3-microsoft-standard-WSL2
Uptime: 1 hour, 6 mins
Packages: 780 (dpkg)
Shell: zsh 5.8.1
Terminal: Windows Terminal
```

## References

- [watch(1) - Linux man page](https://linux.die.net/man/1/watch)
