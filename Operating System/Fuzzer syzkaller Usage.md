# Fuzzer - syzkaller Usage

Created by : Mr Dk.

2019 / 07 / 06 10:46

Nanjing, Jiangsu, China

---

## Overview

根据 syzkaller 的架构

用户需要在 host （也就是自己的电脑）上启动 `syz-manager`

`syz-manager` 会自动在 host 上创建 VM，并进行 fuzzing

因此，准备工作主要分为以下几步：

1. 准备特定版本的编译器 (GCC ✔️)
2. 准备特定版本的 Linux 内核源码
3. 进行一些编译配置后，用编译器编译 Linux 内核
4. 得到内核的二进制文件和内核启动映像
5. 使用脚本创建 Linux 发布版的外围映像
6. 安装 QEMU，并测试编译得到的 Linux 内核和映像，以及 `ssh`
7. 编辑 syzkaller 的配置文件
8. 启动 `syzkaller-manager`，在浏览器上访问指定端口，查看 fuzzing 情况

接下来展示一下我的配置和运行过程

* host - _Ubuntu 18.04_
* GCC - gcc version 7.4.0 (Ubuntu 7.4.0-1ubuntu1~18.04.1)
* kernel - Linux-5.1.16
* Image - Debian-stretch
* QEMU - QEMU emulator version 2.11.1(Debian 1:2.11+dfsg-1ubuntu7.15)

基本参考 syzkaller 官方文档 - [Setup: Ubuntu host, QEMU vm, x86-64 kernel](https://github.com/google/syzkaller/blob/master/docs/linux/setup_ubuntu-host_qemu-vm_x86-64-kernel.md)

---

## GCC

直接使用了 `apt` 下载的 GCC，版本是 `7.4.0`

编译最新的 Linux 内核没什么问题

值得一提的是，如果编译稍早版本的内核

需要使用更低版本的 GCC，不然就报错报错报错

在之后的编译配置中将 `CC` 配置为 `$GCC/bin/gcc` 即可使用该版本的编译器

---

## Kernel

在 https://www.kernel.org/ 下载了 `2019-07-03` 更新的稳定版本 - `5.1.16`

100 多 M 直接用 Git 下得我有点痛苦啊

后来用了自己的服务器下载，再用 scp 拉回来。。。国内的网络环境我真是 😫

进入内核源码目录 `$KERNEL`，生成默认的编译配置：

```bash
$ cd $KERNEL
$ make defconfig
$ make kvmconfig
```

在生成的 `.config` 中打开一些选项：

```
CONFIG_KCOV=y
CONFIG_DEBUG_INFO=y
CONFIG_KASAN=y
CONFIG_KASAN_INLINE=y
```

* 可以在 vim 中使用 `/` 来查找

* 一般来说，可以找到对应字段的注释，如：

  ```
  # CONFIG_DEBUG_INFO is not set
  ```

对于较新版本的 Linux 内核：

```
CONFIG_CONFIGFS_FS=y
CONFIG_SECURITYFS=y
```

开启这些选项后，会导致更多的子选项可用，所以需要重新生成 config

```bash
$ make oldconfig
```

完成后，开始编译内核：

```bash
$ make CC="$GCC/bin/gcc" -j64
```

在编译结束后（不知道用了多久...中途出去吃了个火锅 😅）

在内核源码目录下，生成了：

* `$KERNEL/vmlinux` - kernel binary
* `$KERNEL/arch/x86/boot/bzImage` - packed kernel image

---

## Image

先需要安装 _debootstrap_：

```bash
$ sudo apt install debootstrap
```

[Debian Wiki](https://wiki.debian.org/Debootstrap) - 

> debootstrap is a tool which will install a Debian base system into a subdirectory of another, already installed system. It doesn't require an installation CD, just access to a Debian repository. It can also be installed and run from another operating system, so, for instance, you can use debootstrap to install Debian onto an unused partition from a running Gentoo system. It can also be used to create a rootfs for a machine of a different architecture, which is known as "cross-debootstrapping". There is also a largely equivalent version written in C: cdebootstrap, which is smaller.

* 这个程序只需要通过网络，就能在一个已经运行的系统中安装 Debian 系统

创建一个映像工作目录 `$IMAGE`，下载脚本，生成 Linux 发布版的映像

```bash
$ cd $IMAGE/
$ wget https://raw.githubusercontent.com/google/syzkaller/master/tools/create-image.sh -O create-image.sh
$ chmod +x create-image.sh
$ ./create-image.sh
```

* 脚本默认创建了一个最小化的 Debian-stretch 的 Linux image
  * stretch 是 Debian 9 的代号

也可以在运行脚本时，指定其它发布版，比如 Debian 7

```bash
$ ./create-image.sh --distribution wheezy
```

当然也可以装非最小化版本，比如带上了 `git`、`vim` 等工具：

* 但是 syzkaller 的运行不需要用到它们

```bash
$ ./create-image.sh --feature full
```

但其中比较坑的一点：

* 很显然，这个 `.sh` 脚本中的某一行会使用到 debootstrap
* debootstrap 需要通过网络下载 Debian 的相关文件
* 根据 Debian Wiki，debootstrap 默认从中央仓库下载 - http://deb.debian.org/debian/
* 好了 🙂，这又 tm 慢得要死了，然后等了 20 min 之后来了句网络错误，曰

后来发现在 debootstrap 命令之后可以带参数指定镜像：

```bash
$ debootstrap
I: usage: [OPTION]... <suite> <target> [<mirror> [<script>]]
```

诶握草，这就很可以啦 - 查一查 Debian 的[镜像网站](https://www.debian.org/mirror/list)

最后选了一下，感觉从 NUAA 连 USTC 的镜像是最快的

不知道是不是都属于教育系统的原因。。。

Fine...编辑一下 `create-image.sh` 这个脚本

在 `debootstrap` 这一行 (Line `79`) 的最后加入镜像 - http://mirrors.ustc.edu.cn/debian/

```sh
sudo debootstrap --include=$PREINSTALL_PKGS $RELEASE $DIR http://mirrors.ustc.edu.cn/debian/
```

这样真的快好多

最终，在 `$IMAGE` 下得到：`$IMAGE/stretch.img`

---

## QEMU

直接使用 `apt` 安装 QEMU：

```bash
$ sudo apt install qemu-system-x86
```

然后测试一下刚才的 kernel 和 image 是否能在 QEMU 中运行：

```bash
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

然后它就会启动虚拟机，启动完成后，用户名为 `root` 应该不用密码直接就进去了

由于 `syz-manager` 需要通过 `ssh` 控制 VM，还要测试一下 `ssh` 的可用性：

```bash
$ ssh -i $IMAGE/stretch.id_rsa -p 10021 -o "StrictHostKeyChecking no" root@localhost
```

我试了 ok 的，然后就 `poweroff` 关机了，这样又回到了 host 的命令行

---

## Syzkaller

最烦的是下载 syzkaller 的过程

GitHub 又是慢啊，`go get` 也没有

最后通过把 syzkaller 的仓库导入到 Gitee

然后从 Gitee 上 clone 才解决

理论上的方法：

```bash
$ go get -u -d github.com/google/syzkaller/...
```

反正不管怎么整，最后的效果就是要保证：

在 `$GOPATH/src/github.com/google/` 目录下有一个 `syzkaller/` 的文件夹

里面是 `syzkaller` 的源码（GitHub 仓库对应的文件夹）

接下来，编译 syzkaller，在 `$GOPATH/bin` 中会生成 `syz-fuzzer` 和 `syz-manager`

```bash
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

在 syzkaller 的源码目录下，创建工作目录

并使用该配置文件启动 `syz-manager`：

```bash
$ mkdir workdir
$ ./bin/syz-manager -config=my.cfg
```

Fuzzing 开始了，访问上述 HTTP 地址可以实时查看 fuzzing 状态

---

## Summary

可能我下载的内核代码是最新版本的缘故

Fuzzing 了三个小时，一次 crash 也没有，佛了 😑

但是 syzkaller 的配置过程和用法大概就是这样

---

