# Linux - Namespace

Created by : Mr Dk.

2020 / 09 / 19 10:15

Nanjing, Jiangsu, China

---

在深入 Docker 的原理之前，首先需要了解 Linux kernel 提供的哪些特性能够被 Docker 使用。Docker 容器的本质实际上是宿主机的进程。Docker 如何使用 Linux 提供的功能使容器进程与宿主机进程隔离呢？答案是 namespace。

Linux 内核实现 namespace 的主要目的就是为了实现 **轻量级虚拟化 (容器)** 服务。在同一 ns 下的进程能够互相感知对方，而对外界的进程一无所知，从而达到隔离的目的。

## System Calls

在 Linux kernel 3.8 以后，内核共支持六种类型的 namespace 隔离：

| Namespace         | 系统调用参数    | 隔离内容               |
| ----------------- | --------------- | ---------------------- |
| UTS namespace     | `CLONE_NEWUTS`  | 主机名                 |
| IPC namespace     | `CLONE_NEWIPC`  | 进程间通信机制         |
| PID namespace     | `CLONE_NEWPID`  | 进程编号               |
| Network namespace | `CLONE_NEWNET`  | 网络设备、协议栈、端口 |
| Mount namespace   | `CLONE_NEWNS`   | 文件系统挂载点         |
| User namespace    | `CLONE_NEWUSER` | 用户和用户组           |

通过在 namespace 的系统调用中传入上述参数 (同时多个参数则使用 `|`)，从而实现相应的隔离功能。Namespace 的系统调用主要有三个：

- `clone()` - 是 `fork()` 系统调用的更一般形式，在创建子进程的同时，创建了一个新的 namespace
- `setns()` - 将一个进程加入一个已经存在的 namespace 中
- `unshare()` - 在原先进程上进行 namespace 隔离，即跳出目前的 namespace (Docker 中未使用)

## UTS Namespace

UTS (UNIX Time-sharing System) namespace 提供了 **主机名** 和 **域名** 的隔离，这样每个 Docker 容器都有独立的主机名和域名，从而在网络上可被视为一个独立的结点。在调用 `clone()` 产生子进程时指定 `CLONE_NEWUTS`，并在子进程中调用 `sethostname()`，那么父进程的 hostname 将保持不变；如果没有 UTS 隔离，那么父进程与子进程将共用一个 hostname，父进程的 hostname 可以在子进程中被修改。

## IPC Namespace

进程间通信 (Inter-Process Communication, IPC) 涉及的资源包括 **信号量**、**消息队列** 和 **共享内存**。IPC 资源实际上对应的是一个全局唯一的 32-bit ID，因此 IPC namespace 实际上就是一套独立的 IPC ID 系统。同一个 IPC namespace 下的进程彼此可见；否则进程互不可见。

Docker 使用 IPC namespace 实现容器与宿主机、容器与容器之间的 IPC 隔离。使用 IPC namespace 的系统并不多，比较有名的有 PostgreSQL。

## PID Namespace

PID namespace 的隔离其实比较好理解。每个进程都会有一个唯一的 PID。一个 PID namespace 实际上就是一套独立的进程计数程序。内核为所有的 PID namespace 维护一个树状结构。树的最顶层 (根) 是在系统初始化时创建的，称为 root namespace。之后创建的 namespace 都是 root namespace 的子结点。

1. 每个 PID namespace 中的第一个进程的 PID 为 `1` (功能与 `init` 进程类似，负责接收孤儿进程，并最终回收资源)
2. PID namespace 中的进程不能影响 **父结点** 或 **兄弟结点** 中的进程 (因为 PID 在其它 namespace 中失去意义)
3. 在新的 PID namespace 重新挂载 `/proc` 文件系统，将只能看到当前 PID namespace 中的其它进程
4. 在 root namespace 中可以看到 **所有** 的进程 (因此可以在容器外部监控容器内进程)

一个进程所在的 PID namespace 是永远不会变的！如果想要通过 `setns()` 或 `unshare()` 改变进程的 PID namespace，将需要 `clone()` 出一个子进程，将子进程加入到新的 PID namespace 中，原先的父进程在原先的 PID namespace 中结束。这是因为用户态程序和库都认为进程 PID 是一个常量，是通过 `getpid()` 得到的，函数将返回调用者所在的 PID namespace 中的 PID，PID 的变化将引起用户进程崩溃。

> ？

## Mount Namespace

Mount namespace 通过隔离 **文件系统挂载点** 实现了隔离文件系统。创建 mount namespace 时，会将当前的文件结构复制给新的 mount namespace，两者严格隔离，新的 namespace 中的所有 mount 操作只影响自身的文件系统。

> 顺嘴一提 mount 操作的本质（参见 `mount` 系统调用的 [源代码](../../linux-kernel-comments-notes/Chapter 12 - 文件系统/Chapter 12.6 - super.c 程序.md)）。Mount 操作实际上是将一个文件系统的 super block 关联到 rootfs 的一个路径上 (实际上是一个 inode 上)。这里 mount 隔离的意思应该是，假设在 mount namespace 1 中，将文件系统挂载到了 `/home/fs/` 下；而在 mount namespace 2 中，`/home/fs/` 路径上没有任何挂载。

这种完全的挂载隔离其实不太方便 - 假如父 namespace 中 mount 了一个新设备，在子 namespace 中是无法自动 mount 这个设备的。之后引入的 **挂载传播 (mount propagation)** 解决了这个问题，具体的解决方式是详细定义了挂载事件如何在 namespace 之间传播，细化了隔离的粒度：

1. 共享关系 (share relationship) - 一个 namespace 中的 mount 事件会传播到其它共享的 namespace 中，反之亦然
2. 从属关系 (slave relationship) - 同上，但是传播是单向的，反之不行

基于这两种行为，定义了如下几种 mount 状态：

- share mount (主动传播 mount 事件)
- slave mount (被动接收 mount 事件)
- shared and slave mount (同时传播和接收 mount 事件)
- private mount (既不传播也不接收 mount 事件)
- unbind-able mount (不允许执行 mount，即创建 mount namespace 时文件对象不可被复制)

通过使用 `mount` 命令时附加参数，可以指定 mount 的状态。

在 `CLONE_NEWNS` 生效后，子进程进行的 mount 与 unmount 操作只对子进程所在的 mount namespace 有效，而父进程所在的 mount namespace 中的挂载信息不会被子进程破坏。

## Network Namespace

Network namespace 主要对网络资源进行隔离，包括网络设备、协议栈、路由表、防火墙、socket 等。一个物理网络设备 **只能存在于一个 network namespace 中**，一般来说设备都会被分配在 root namespace 中。但是可以通过创建 _veth pair (虚拟网络设备对)_ 来进行不同 network namespace 之间的通信目的 - 类似一个管道。

Docker 的经典做法是，创建一个 veth pair，一端放在新的 namespace 中，命名为 `eth0`；另一端绑定在宿主机的 `docker0` 网桥上。在 veth pair 创建完毕之前，Docker daemon 与容器内进程通过 pipe 进行通信。

## User Namespace

User namespace 主要隔离安全相关的标识符和属性，比如用户 ID、root 目录、密钥等。一个在容器外没有特权的普通用户，可以在容器中创建一个 root 用户进程。

---

## References

[DOCKER 基础技术：LINUX NAMESPACE（上）](https://coolshell.cn/articles/17010.html)

[DOCKER 基础技术：LINUX NAMESPACE（下）](https://coolshell.cn/articles/17029.html)

[知乎 - Linux 环境隔离机制 -- Linux Namespace](https://zhuanlan.zhihu.com/p/47571649)

---
