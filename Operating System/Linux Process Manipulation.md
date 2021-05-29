# Linux - Process Manipulation

Created by : Mr Dk.

2021 / 05 / 29 10:19

Hangzhou, Zhejiang, China

---

## ps aux

使用 `ps aux` 命令可以查看进程的相关信息：

```console
$ ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.5 168344 11548 ?        Ss   Mar06   1:02 /lib/systemd/systemd --system --deserialize
root           2  0.0  0.0      0     0 ?        S    Mar06   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        I<   Mar06   0:00 [rcu_gp]
root           4  0.0  0.0      0     0 ?        I<   Mar06   0:00 [rcu_par_gp]
root           6  0.0  0.0      0     0 ?        I<   Mar06   0:00 [kworker/0:0H-kblockd]
root           9  0.0  0.0      0     0 ?        I<   Mar06   0:00 [mm_percpu_wq]
root          10  0.0  0.0      0     0 ?        S    Mar06   0:35 [ksoftirqd/0]
root          11  0.0  0.0      0     0 ?        I    Mar06  12:36 [rcu_sched]
root          12  0.0  0.0      0     0 ?        S    Mar06   0:25 [migration/0]
root          13  0.0  0.0      0     0 ?        S    Mar06   0:00 [idle_inject/0]
root          14  0.0  0.0      0     0 ?        S    Mar06   0:00 [cpuhp/0]
root          15  0.0  0.0      0     0 ?        S    Mar06   0:00 [kdevtmpfs]
root          16  0.0  0.0      0     0 ?        I<   Mar06   0:00 [netns]
root      232461  0.0  0.2 169736  4332 ?        S    23:25   0:00 (sd-pam)
root      232481  2.3  0.2  12992  6092 pts/0    Ss   23:25   0:00 -zsh
root      232502  0.0  0.1  11492  3228 pts/0    R+   23:25   0:00 ps aux
```

其中：

- `USER` 表示用户名
- `PID` 表示当前进程号
- `%CPU` 表示进程使用的 CPU 百分比
- `%MEM` 表示进程使用的内存百分比
- `VSZ` 表示内存使用的虚拟内存 (Kb)
- `RSS` 表示进程占用的固定内存量 (Kb)
- `TTY` 表示进程绑定的终端
- `STAT` 表示进程的状态
  - `R` (Running) - 正在运行或处于就绪队列中
  - `S` (Sleeping) - 睡眠中，正等待信号
  - `I` (Idle) - 空闲
  - `Z` (Zombie) - 进程已僵死，终止但 pid 依旧存在
  - `D` (Uninterruptible Sleeping) - 不可中断睡眠 (一般正在 I/O)
  - `T` (Terminated) - 收到终止信号后终止运行的进程
  - `P` - 等待 swap
  - ...
- `START` 表示进程启动的时间和日期
- `TIME` 进程使用的总 CPU 时间
- `COMMAND` 执行的命令

## 骚操作

今天需要 SSH 连接到开发机上完成一个很耗时的工作：用 `pgbench` 向 PostgreSQL 导入数据 (3h 左右)。但是 SSH 连接一旦断开，导入数据就会失败。想到的方法是直接在开发机上 `nohup`，并以后台模式 (`%`) 运行。但是有一个问题：`pgbench` 命令启动后，需要人为输入一个密码 (连接到数据库) 才能继续进行。如果后台运行 `pgbench`，那么进程将一直挂起等待密码输入。这可咋整？

骚操作：

1. 前台执行 `pgbench`，并手动输入密码
2. 按下 Ctrl + Z，这会使一个正在交互执行 (前台) 命令被换到后台，并处于暂停状态 (上述 `S` 状态)
3. 使用 `bg` 命令使后台暂停的进程继续执行

在第一步前台执行命令时，可以将命令的 stdout 和 stderr 重定向到一个日志文件中。在该进程在后台继续执行后，通过观察日志文件，可以看到进程的实时输出。

## Signals

Linux 的进程之间可以互相发送信号。进程接收到信号后，会根据策略选择：

- 忽略信号 (`SIGKILL` 和 `SIGSTOP`) 不能被忽略
- 捕捉信号
  - 执行缺省的信号处理函数
  - 自行注册信号处理函数

Linux 支持的信号类型：

- 编号 1-31：非可靠信号，多次发送相同的信号，进程可能只会收到 1 次
- 编号 32-64：可靠信号，通过队列保证信号不丢失

> 对于非可靠信号，Linux kernel 中的实现好像是一个 bitmap。对一个进程发送一次信号意味着 set bitmap 中的对应位。进程处理完信号后，会将对应的位 reset。如果进程还没能来得及处理信号，发送信号的进程多次对 bitmap 的位进行 set，其结果还是和只发送一次信号一致。所以信号会丢失。

对于正在进行交互的进程 (前台进程)，可以通过键盘直接发送控制字符：

- `Ctrl + C`：发送 `SIGINT`，默认情况会导致进程退出，但进程自己决定如何响应
- `Ctrl + Z`：发送 `SIGTSTP`，使进程切换到后台，并暂停进程

通过 `fg` 命令可以使后台进程返回到前台并继续运行；也可以通过 `bg` 命令使后台进程在后台继续运行。

## References

[简书 - 常用 Linux 中 ps 命令学习及 ps aux 与 ps -ef 的区别](https://www.jianshu.com/p/e1abfb1d9e8d)

[Server Fault - Using nohup when initial input is required](https://serverfault.com/questions/72417/using-nohup-when-initial-input-is-required)

[Ask Ubuntu - What is the difference between Ctrl-z and Ctrl-c in the terminal?](https://askubuntu.com/questions/510811/what-is-the-difference-between-ctrl-z-and-ctrl-c-in-the-terminal)

---

