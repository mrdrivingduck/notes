# Syzkaller - Usage

Created by : Mr Dk.

2019 / 07 / 06 10:46

Nanjing, Jiangsu, China

---

## Overview

根据 syzkaller 的架构，用户需要在 host （也就是自己的电脑）上启动 `syz-manager`。`syz-manager` 会自动在 host 上创建 VM，并进行 fuzzing。

因此，准备工作主要分为以下几步：

1. 准备特定版本的编译器 (GCC ✔️)
2. 准备特定版本的 Linux 内核源码
3. 进行一些编译配置后，用编译器编译 Linux 内核
4. 得到内核的二进制文件和内核启动映像
5. 使用脚本创建 Linux 发布版的外围映像
6. 安装 QEMU，并测试编译得到的 Linux 内核和映像，以及 `ssh`
7. 编辑 syzkaller 的配置文件
8. 启动 `syzkaller-manager`，在浏览器上访问指定端口，查看 fuzzing 情况

接下来是我的配置和运行过程：

* host - Ubuntu 18.04
* GCC - gcc version 7.4.0 (Ubuntu 7.4.0-1ubuntu1~18.04.1)
* kernel - Linux-5.1.16
* Image - Debian-stretch
* QEMU - QEMU emulator version 2.11.1(Debian 1:2.11+dfsg-1ubuntu7.15)

基本参考 syzkaller 官方文档中的配置过程： [Setup: Ubuntu host, QEMU vm, x86-64 kernel](https://github.com/google/syzkaller/blob/master/docs/linux/setup_ubuntu-host_qemu-vm_x86-64-kernel.md)

---

## GCC

直接使用了 `apt` 下载的 GCC，版本是 `7.4.0`，这个版本用于编译最新的 Linux 内核没什么问题。

值得一提的是，如果编译稍早版本的内核，需要使用更低版本的 GCC，不然就 **报错报错报错**。在编译配置中将 `CC` 配置为 `$GCC/bin/gcc` 即可使用该版本的编译器。

---

## Kernel

在 https://www.kernel.org/ 下载了 `2019-07-03` 更新的稳定版本 - `5.1.16`，100 多 M 直接用 Git 下得我有点痛苦啊。后来用了自己的服务器下载，再用 scp 拉回来。。。国内的网络环境我真是 😫

进入内核源码目录 `$KERNEL`，生成默认的编译配置：

```console
$ cd $KERNEL
$ make defconfig
$ make kvmconfig
```

在生成的 `.config` 中开启一些编译选项。这些开启的选项记录的一些内核信息会被 syzkaller 使用到：

```
CONFIG_KCOV=y
CONFIG_DEBUG_INFO=y
CONFIG_KASAN=y
CONFIG_KASAN_INLINE=y
```

可以在 vim 中使用 `/` 来查找。一般来说，可以找到对应字段的注释，如：

```
# CONFIG_DEBUG_INFO is not set
```

对于较新版本的 Linux 内核，以下两个选项也要开启 (老版本内核没有这两个选项)：

> 这两个选项很重要！否则虚拟机会进入 rescue mode

```
CONFIG_CONFIGFS_FS=y
CONFIG_SECURITYFS=y
```

开启这些选项后，会导致更多的子选项可用，所以需要重新生成 config：

```console
$ make oldconfig
```

完成后，开始编译内核：

```console
$ make CC="$GCC/bin/gcc" -j64
```

在编译中如果出现错误，可能的原因如下：

* 编译器版本不适合 (太高)
* 少了一些库
  * 上网搜一下对应错误是因为缺了哪个库导致的
  * 然后 `apt` 补一下对应的库

在编译结束后 (不知道用了多久...中途出去吃了个渝合重庆老火锅 😅，回来已经编完了)，在内核源码目录下，生成了内核二进制文件和启动映像：

* `$KERNEL/vmlinux` - kernel binary
* `$KERNEL/arch/x86/boot/bzImage` - packed kernel image

---

## Image

为了能够运行一个 OS，还需要有用户空间的硬盘映像 (不可能直接使用一个内核)。另外，由于这个虚拟机会被 host 上的 syzkaller 守护进程通过 SSH 远程连接，因此也需要将一些密钥之类的提前保存在虚拟机中。

首先在 host 中安装 *debootstrap*，用于制作虚拟机使用的硬盘映像：

```console
$ sudo apt install debootstrap
```

[Debian Wiki](https://wiki.debian.org/Debootstrap) - 

> debootstrap is a tool which will install a Debian base system into a subdirectory of another, already installed system. It doesn't require an installation CD, just access to a Debian repository. It can also be installed and run from another operating system, so, for instance, you can use debootstrap to install Debian onto an unused partition from a running Gentoo system. It can also be used to create a rootfs for a machine of a different architecture, which is known as "cross-debootstrapping". There is also a largely equivalent version written in C: cdebootstrap, which is smaller.

*Debootstrap* 只需要通过网络，就能在一个已经运行的系统 (host) 中安装 (给虚拟机使用的) *Debian* 系统。

Syzkaller 官方给出了一个自动创建一个映像工作目录的脚本。首先创建一个目录 `$IMAGE` 用于存放映像，然后下载脚本并执行，生成 Linux 发布版的映像：

```console
$ cd $IMAGE/
$ wget https://raw.githubusercontent.com/google/syzkaller/master/tools/create-image.sh -O create-image.sh
$ chmod +x create-image.sh
$ ./create-image.sh
```

脚本默认创建了一个最小化的 Debian-stretch 的 Linux image (stretch 是 Debian 9 的代号)。也可以在运行脚本时，指定其它发布版，比如 Debian 10：

```console
$ ./create-image.sh --distribution buster
```

当然也可以装非最小化版本，比如带上了 `git`、`vim` 等工具。但是 syzkaller 的运行不需要用到它们：

```console
$ ./create-image.sh --feature full
```

其中的坑：

* 很显然，这个 `.sh` 脚本中的某一行会使用到 debootstrap
* debootstrap 需要通过网络下载 Debian 的相关文件
* 根据 Debian Wiki，debootstrap 默认从中央仓库下载 - http://deb.debian.org/debian/
* 好了 🙂，这又 tm 慢得要死了，然后等了 20 min 之后来了句网络错误，曰

查阅 debootstrap 文档，发现命令之后可以带参数指定镜像：

```console
$ debootstrap
I: usage: [OPTION]... <suite> <target> [<mirror> [<script>]]
```

诶握草，这就好办：查一查 Debian 的 [镜像网站](https://www.debian.org/mirror/list)。最后选了一下，感觉从 NUAA 连 USTC 的镜像是最快的，不知道是不是都属于教育系统的原因。。。

Fine...编辑一下 `create-image.sh` 这个脚本，在 `debootstrap` 这一行 (Line `79`) 的最后加入镜像：http://mirrors.ustc.edu.cn/debian/

```sh
sudo debootstrap --include=$PREINSTALL_PKGS $RELEASE $DIR http://mirrors.ustc.edu.cn/debian/
```

这样真的快好多。

另外，脚本还默认在虚拟机硬盘中预置一些文件。比如 SSH 密钥、配置等。最终，在 `$IMAGE` 下得到：`$IMAGE/stretch.img`。

---

## QEMU

直接使用 `apt` 安装 QEMU。另外，`net-tools` 也需要被安装，因为我发现不安装可能会导致虚拟机网卡失效。

```console
$ sudo apt install qemu-system-x86 net-tools
```

测试刚才的 kernel 和 image 是否能在 QEMU 中运行：

```console
$ qemu-system-x86_64 \
  -kernel $KERNEL/arch/x86/boot/bzImage \
  -append "console=ttyS0 root=/dev/sda debug earlyprintk=serial slub_debug=QUZ"\
  -hda $IMAGE/stretch.img \
  -net user,hostfwd=tcp::10021-:22 -net nic \
  -enable-kvm \
  -nographic \
  -m 2G \
  -smp 2 \
  -pidfile vm.pid \
  2>&1 | tee vm.log
```

然后它就会启动虚拟机。启动完成后，用户名为 `root` 应该不用密码直接就进去了。

由于 `syz-manager` 需要通过 `ssh` 控制 VM，还要测试一下 `ssh` 的可用性：

```console
$ ssh -i $IMAGE/stretch.id_rsa -p 10021 -o "StrictHostKeyChecking no" root@localhost
```

我试了 ok 的，然后就 `poweroff` 关机了，这样又回到了 host 的命令行。

---

## Syzkaller

下载 syzkaller 理论上的方法：

```console
$ go get -u -d github.com/google/syzkaller/...
```

> 最烦的是下载 syzkaller 的过程，GitHub 又是慢啊，`go get` 也没有。最后通过把 syzkaller 的仓库导入到 Gitee 然后从 Gitee 上 clone 才解决。

反正不管怎么整，最后的效果就是要保证：在 `$GOPATH/src/github.com/google/` 目录下有一个 `syzkaller/` 的文件夹，里面是 `syzkaller` 的源码 (GitHub 仓库对应的文件夹)。

接下来，编译 syzkaller。在 `$GOPATH/bin` 中会生成 `syz-fuzzer` 和 `syz-manager`。

```console
$ cd $GOPATH/src/github.com/google/syzkaller
$ make
```

在 syzkaller 的源码目录下，创建配置文件 `my.cfg`：

```json
{
    "target": "linux/amd64",
    "http": "127.0.0.1:56741",
    "workdir": "$GOPATH/src/github.com/google/syzkaller/workdir",
    "kernel_obj": "$KERNEL",
    "image": "$IMAGE/stretch.img",
    "sshkey": "$IMAGE/stretch.id_rsa",
    "syzkaller": "$GOPATH/src/github.com/google/syzkaller",
    "procs": 8,
    "type": "qemu",
    "vm": {
        "count": 4,
        "kernel": "$KERNEL/arch/x86/boot/bzImage",
        "cpu": 2,
        "mem": 2048
    }
}
```

* `http` 指的是 syzkaller 运行时，可以通过浏览器从该地址查看 fuzzing 状态
* `workdir` - 工作目录，需要创建
* 其它显然是一些虚拟机配置
* `$GOPATH`、`$KERNEL`、`$IMAGE` 需要被替换为实际上相应的路径

在 syzkaller 的源码目录下，创建工作目录，并使用该配置文件启动 `syz-manager`：

```console
$ mkdir workdir
$ sudo ./bin/syz-manager -config=my.cfg
2019/07/06 10:54:37 loading corpus...
2019/07/06 10:54:37 serving http on http://127.0.0.1:56741
2019/07/06 10:54:37 serving rpc on tcp://[::]:36699
2019/07/06 10:54:37 booting test machines...
2019/07/06 10:54:37 wait for the connection from test machine...
2019/07/06 10:54:51 machine check:
2019/07/06 10:54:51 syscalls                : 1390/2733
2019/07/06 10:54:51 code coverage           : enabled
2019/07/06 10:54:51 comparison tracing      : CONFIG_KCOV_ENABLE_COMPARISONS is not enabled
2019/07/06 10:54:51 extra coverage          : extra coverage is not supported by the kernel
2019/07/06 10:54:51 setuid sandbox          : enabled
2019/07/06 10:54:51 namespace sandbox       : /proc/self/ns/user does not exist
2019/07/06 10:54:51 Android sandbox         : enabled
2019/07/06 10:54:51 fault injection         : CONFIG_FAULT_INJECTION is not enabled
2019/07/06 10:54:51 leak checking           : CONFIG_DEBUG_KMEMLEAK is not enabled
2019/07/06 10:54:51 net packet injection    : /dev/net/tun does not exist
2019/07/06 10:54:51 net device setup        : enabled
2019/07/06 10:54:51 corpus                  : 513 (0 deleted)
2019/07/06 10:54:57 VMs 4, executed 1139, cover 19545, crashes 0, repro 0
2019/07/06 10:55:07 VMs 4, executed 3134, cover 24729, crashes 0, repro 0
2019/07/06 10:55:17 VMs 4, executed 6689, cover 25739, crashes 0, repro 0
2019/07/06 10:55:27 VMs 4, executed 12912, cover 26182, crashes 0, repro 0
2019/07/06 10:55:37 VMs 4, executed 22786, cover 26258, crashes 0, repro 0
2019/07/06 10:55:47 VMs 4, executed 30311, cover 26298, crashes 0, repro 0
```

Fuzzing 开始了，访问上述 HTTP 地址可以实时查看 fuzzing 状态。

---

## Summary

可能我下载的内核代码是最新版本的缘故，Fuzzing 了三个小时，一次 crash 也没有，佛了 😑。

---

