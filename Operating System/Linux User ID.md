# Linux - User ID

Created by : Mr Dk.

2021 / 03 / 10 16:49

Nanjing, Jiangsu, China

---

## User ID in Files

查看一个文件的信息：

```console
$ ls -alt README.md
-rw-r--r-- 1 mrdrivingduck mrdrivingduck 18596 Mar  9 22:22 README.md
```

可以看到，其中的信息包含：

* 文件类型
	* `-`：常规文件
	* `d`：目录名
	* `s`：符号链接
	* `p`：命名管道
	* `c`：字符设备文件
	* `b`：块设备文件
* 文件宿主 / 文件宿主所在组 / 其它用户 对当前文件的操作权限
* 链接计数
* 文件宿主用户名
* 文件宿主组名
* 文件大小
* 最后修改时间
* 文件名

以上信息全部包含在 inode 的结点定义中：

* `i_mode`：文件类型和权限
* `i_nlinks`：链接数 (多少个文件目录项指向当前 inode)
* `i_uid`：文件宿主的用户 id
* `i_gid`：文件宿主的组 id
* `i_size`：文件长度
* `i_mtime`：文件修改时间
* `i_zone[9]`：指向该文件使用的磁盘块

文件名保存在以目录项为内容的磁盘块中。

其中，`i_mode` 是一个 16-bit 的数，其定义如下：

* bit 15-12 表示文件类型
* bit 11-9 是特殊标志位：
	* `01` - 执行时设置用户 ID **(set-user-ID)**
	* `02` - 执行时设置组 ID **(set-group-ID)**
	* `04` - 目录的受限删除标志
* bit 8-6 为文件宿主的 R/W/X 权限
* bit 5-3 为文件宿主所在组的 R/W/X 权限
* bit 2-0 为其它用户的 R/W/X 权限

## User ID of Users

Linux 中一个用户具有以下两个 ID：

* (真实) 用户 ID ((r)uid) 
* (真实) 用户组 ID ((r)gid)

对应的 ID 存放在 `/etc/passwd` 文件中，除了包含用户的两个 ID 外，还包含了：

* 用户的默认工作目录
* 用户的默认 shell

```
mrdrivingduck:x:1000:1000:,,,:/home/mrdrivingduck:/usr/bin/zsh
```

## User ID of Processes

每个进程启动时，进程数据结构中会分别记录三种用户 ID 和三种组 ID：

* (r)uid / (r)gid：拥有进程的 (真实) 用户 ID / (真实) 组 ID
* euid / egid：有效用户 ID / 有效组 ID
* suid / sgid：保存用户 ID / 保存组 ID

`ruid` / `rgid` 是启动进程的用户对应的用户 ID 和组 ID。**`euid` / `egid` 用于进程访问文件时的权限判断**。通常来说，`euid` / `egid` 就是进程的 `ruid` / `rgid`。因此，进程只能访问进程有效用户 (真实用户) (组) 允许访问的文件。

当进程对应的可执行文件中 `set-user-ID` / `set-group-ID` 置位时，`suid` / `sgid` 保存了 **可执行文件的宿主用户 ID**；否则，`suid` / `sgid` 等于进程的 `euid` / `egid`。在面对这类设置了标志位的特殊的可执行文件时，进程的 `euid` / `egid` 被设置为 `suid` / `sgid`，从而使进程可以以可执行文件宿主的权限访问文件。

典型例子：Linux 中的 `passwd` 命令。该命令的可执行文件权限如下：

```console
$ ls -alt /usr/bin/passwd
-rwsr-xr-x 1 root root 68208 May 28  2020 /usr/bin/passwd
```

可以看到，该可执行文件的宿主是 root 用户。该程序的功能是允许用户修改自己的口令，口令需要保存到 `/etc/passwd` 文件中：

```console
$ ls -alt /etc/passwd
-rw-r--r-- 1 root root 1723 Jan 11 17:14 /etc/passwd
```

该文件的宿主是 root 用户，并且只有 root 用户才有权限写入该文件。如果普通用户执行 `passwd` 程序，其 `euid` 将会是普通用户而不是 root，从而无法写入 `/etc/passwd` 文件。解决的方法是对 `passwd` 程序设置为 `set-user-ID`。当普通用户执行该程序时，其 `euid` 将会变为 root 用户，从而有权限对 `/etc/passwd` 文件进行写入。

使用 `set-user-ID` 的还有 `sudo`、`su` 等命令。

---

## References

Linux 内核完全注释 V5.0.1 - 8.10 sys.c 程序

Linux 内核完全注释 V5.0.1 - 12.1 文件系统 总体功能

---

