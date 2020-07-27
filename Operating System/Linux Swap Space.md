# Linux - Swap Space

Created by : Mr Dk.

2020 / 07 / 27 17:56

Nanjing, Jiangsu, China

---

## About

交换空间 (Swap Space) 是磁盘上用于暂时保存 RAM 中不常用数据的空间。当 RAM 的空间不够使用时，OS 会将 RAM 中的部分数据暂时存放到 swap space 中，进而给活跃的程序腾出内存。Swap space 由内核的内存管理程序使用，以页面为单位进行对换。

在 Linux 中，可以专门在磁盘上划分出一个 swap 分区，也可以在文件系统中创建一个指定大小的文件 swap file 作为 swap 空间。Swap space 的推荐大小因硬件而异，也因运行软件的需求而异。一般推荐的大小：

* RAM < 2GB - RAM 的两倍大小
* RAM 2-8GB - RAM 相同大小
* RAM 9-64GB - 0.5 倍 RAM 大小
* RAM > 64GB - 按应用程序需求而定

## Swap File

我的工作机器在安装 Linux 时没有单独划分 swap space，内存只有 8GB。在运行实验程序时，内存几近用完。系统自动为我分配的一个 2GB 的 swap file 似乎也不太够用。于是我决定将 swap file 扩充为 16GB。

首先，需要停止使用机器上现有的 swap file，即需要把 swap file 中暂存的内存搬回真正的物理 RAM 中去，相当于卸载一个分区：

```console
$ sudo swapoff /swapfile
```

此时，我正好开着任务管理器，发现 swap 分区中的数据被一点一点地搬回内存，内存占用率瞬间升高。当任务管理器显示 swap space 已经禁止使用时，swap file 就正式停止工作了。可以使用 `rm` 命令将其删掉。

接下来，新建一个 16GB 的 swap file，并设置其权限：

```console
$ sudo fallocate -l 16G /swapfile
$ sudo chmod 0600 /swapfile
```

接下来将 swap file 设置为 swap space：

```console
$ sudo mkswap /swapfile
Setting up swapspace version 1, size = 16 GiB (17179865088 bytes)
no label, UUID=6c4feed5-2e17-477b-b097-88bc85c6dd2e
```

最后启用 swap space：

```console
$ sudo swapon /swapfile
```

任务管理器中重新显示了 swap space，并已经被扩容为 16GB。这就是挺喜欢 Linux 的地方 - 一切自己动手。 😁

---

## References

[Linux 增加 swap 分区和删除 swapfile 文件的方法](https://blog.csdn.net/Seven_tester/article/details/82628866?utm_medium=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.edu_weight&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.edu_weight)

[如何在 Ubuntu 16.04 上增加 Swap 分区](https://baijiahao.baidu.com/s?id=1600715185132290794&wfr=spider&for=pc)

---

