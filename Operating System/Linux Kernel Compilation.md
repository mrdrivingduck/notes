# Linux - Kernel Compilation

Created by : Mr Dk.

2020 / 05 / 08 11:16

Nanjing, Jiangsu, China

---

对如何编译 Linux 内核进行总结。内核的编译基于 Makefile，因此编译命令基本上围绕 `make` 进行。

## Source Code

Linux 官方提供一个稳定版的内核 git 地址：

```
git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
```

另外，在 GitHub 上也有相应的镜像。[Linus Torvalds](https://github.com/torvalds/linux) 的镜像只有 `x.xx` 版本的 tag，另外还有维护了[稳定版](https://github.com/gregkh/linux) tag `x.xx.xx` 的镜像。

## Dependencies

这些依赖与内核源代码无关，主要是编译一些脚本、工具。比如用于内核模块签名的工具 `scripts/sign-file.c`。

```console
$ sudo apt install libelf-dev libssl-dev
```

## Configuration

在下载完源代码并解压后，第一件事是进行编译前的配置。需要进行配置的原因是，内核可以运行在不同的硬件平台上，并且不同机器的硬件环境也不一样，因此有些设备驱动需要被编译，有些不需要。

另外，一些较为核心的功能可以选择编译到内核核心的二进制文件中；一些不太核心的功能，可以选择编译为内核模块，当需要使用时才被动态加载。这样，可以保证内核核心二进制文件尽可能小。

以下命令会根据当前机器的体系结构，生成一个新的默认配置文件 `.config`：

```console
$ make defconfig # New config with default from ARCH supplied defconfig
```

另外还有几个自动的配置：

```console
$ make allnoconfig # New config where all options are answered with no'
$ make allyesconfig	# New config where all options are accepted with yes'
$ make allmodconfig	# New config selecting modules when possible'
$ make alldefconfig # New config with all symbols set to default'
```

如果想根据系统启动以来已经加载的模块进行编译，使得内核仅支持当前已经加载的模块，从而简化配置流程：

```console
$ make localmodconfig
```

如果想通过一个 GUI 进行手动配置，则可以使用如下几个命令。(使用这几个命令需要安装用于支持相关 GUI 的软件包，比如 GTK、QT 等)：

```console
$ make menuconfig # Update current config utilising a menu based program'
$ make xconfig # Update current config utilising a Qt based front-end
$ make gconfig # Update current config utilising a GTK+ based front-end
```

由于我进行的一些开发是在 QEMU 虚拟机中运行的。因此在 `make defconfig` 后，直接运行如下命令自动配置一些设备驱动相关的选项，并开启一些新的选项：

```console
$ make kvmconfig # Enable additional options for kvm guest kernel support
```

也可以直接编辑 `.config` 进行配置。在配置完毕后，需要通过如下命令将配置更新：

```console
$ make oldconfig # Update current config utilising a provided .config as base'
```

另外还有一些相关的选项，可以在 `scripts/kconfig/Makefile` 中找到。

## Compiler

对于特定版本的 kernel，最好使用合适版本的 GCC 编译器进行编译。比如，2018 年 release 的 kernel，对应 Ubuntu 18.04 上自带的 GCC 版本 (GCC 7.5.0) 可以成功编译，而 Ubuntu 20.04 上自带的 GCC 9.3.0 就不行。所以最好是在与 kernel 版本相当的 OS 上编译。

如果机器环境的问题没法解决，那么就需要安装不同版本的编译器。推荐使用 `build-essential` 对不同版本的编译器进行管理。有两种方式：

1. 通过 `build-essential` 将系统的 `gcc` 命令指向合适版本 (如 `gcc-7`)
2. 在执行 Makefile 脚本时，指定 `CC` 和 `HOSTCC` 使用特定版本 (如 `CC=/usr/bin/gcc-7`)

最后开始编译核心与模块：

```console
$ make vmlinux # 未经压缩的核心
$ make modules # 模块
$ make bzImage # 经过压缩的核心
```

或者直接编译全部 (多任务加速)：

```console
$ make -j8
```

编译完毕后的 `bzImage` 可以直接被 QEMU 使用。如果想要将内核主映像和模块安装到真机：

```console
$ sudo make modules_install
$ sudo make install
```

然后重启电脑后进入 GRUB 后，选择高级启动选项，然后选择编译好的内核启动。

如果想要将内核编译为 debian 包 (或其它压缩形式)，然后通过 `dpkg` 来安装，相关的支持命令位于 `scripts/package/Makefile` 中：

```makefile
# Help text displayed when executing 'make help'
# ---------------------------------------------------------------------------
help: FORCE
	@echo '  rpm-pkg             - Build both source and binary RPM kernel packages'
	@echo '  binrpm-pkg          - Build only the binary kernel RPM package'
	@echo '  deb-pkg             - Build both source and binary deb kernel packages'
	@echo '  bindeb-pkg          - Build only the binary kernel deb package'
	@echo '  tar-pkg             - Build the kernel as an uncompressed tarball'
	@echo '  targz-pkg           - Build the kernel as a gzip compressed tarball'
	@echo '  tarbz2-pkg          - Build the kernel as a bzip2 compressed tarball'
	@echo '  tarxz-pkg           - Build the kernel as a xz compressed tarball'
	@echo '  perf-tar-src-pkg    - Build $(perf-tar).tar source tarball'
	@echo '  perf-targz-src-pkg  - Build $(perf-tar).tar.gz source tarball'
	@echo '  perf-tarbz2-src-pkg - Build $(perf-tar).tar.bz2 source tarball'
	@echo '  perf-tarxz-src-pkg  - Build $(perf-tar).tar.xz source tarball'
```

## References

[一文学会如何下载编译 Linux Kernel](https://www.jianshu.com/p/5542b4015f37)

[Custom Compiled Kernel on Debian & Ubuntu](https://www.linode.com/docs/tools-reference/custom-kernels-distros/custom-compiled-kernel-debian-ubuntu/)

[How to compile and install Linux Kernel 5.6.9 from source code](https://www.cyberciti.biz/tips/compiling-linux-kernel-26.html)

[How to Compile a Linux Kernel](https://www.linux.com/topic/desktop/how-compile-linux-kernel-0/)

---
