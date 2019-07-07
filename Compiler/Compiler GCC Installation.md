# Compiler - GCC Installation

Created by : Mr Dk.

2019 / 07 / 07 10:36

Nanjing, Jiangsu, China

---

## Why

编译一些比较早期的东西 (对 就是 Linux 的 old kernel)

用 Ubuntu 18.04 自带的 GCC 要求太高。。通过不了

```bash
$ gcc -v
Using built-in specs.
COLLECT_GCC=gcc
COLLECT_LTO_WRAPPER=/usr/lib/gcc/x86_64-linux-gnu/7/lto-wrapper
OFFLOAD_TARGET_NAMES=nvptx-none
OFFLOAD_TARGET_DEFAULT=1
Target: x86_64-linux-gnu
Configured with: ../src/configure -v --with-pkgversion='Ubuntu 7.4.0-1ubuntu1~18.04.1' --with-bugurl=file:///usr/share/doc/gcc-7/README.Bugs --enable-languages=c,ada,c++,go,brig,d,fortran,objc,obj-c++ --prefix=/usr --with-gcc-major-version-only --program-suffix=-7 --program-prefix=x86_64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/lib --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --with-sysroot=/ --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-gnu-unique-object --disable-vtable-verify --enable-libmpx --enable-plugin --enable-default-pie --with-system-zlib --with-target-system-zlib --enable-objc-gc=auto --enable-multiarch --disable-werror --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --with-tune=generic --enable-offload-targets=nvptx-none --without-cuda-driver --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu
Thread model: posix
gcc version 7.4.0 (Ubuntu 7.4.0-1ubuntu1~18.04.1)
```

7.4.0 ...嗯 有点高了

于是下载了 GCC 6 的源码

用 7.4.0 的 GCC 编译安装

> 试图用 7.4.0 的 GCC 编译安装 GCC 5
>
> 没能成功
>
> 看来只能一级一级退下来编译？

---

## How

首先，下载源码，GitHub 上就有镜像 - https://github.com/gcc-mirror/gcc

下载了一个 gcc-6.5.0 的

下载完成后，解压，进入源码目录：

```bash
tar -zxvf gcc-6_5_0-release.tar.gz
...
cd gcc-gcc-6_5_0-release
```

直接 `make` 就等着报错吧

错误显示，源码编译安装也是需要一些依赖的

> 我内心：哦草 😥 那不是还要把依赖下载下来一个个编译安装？？？

后来上网搜了下，原来目录下有一个自动安装依赖的脚本

```bash
$ ./contrib/download_prerequisites
```

自动连接到了 `gcc.gnu.org` 上下载对应的依赖，这很可以

依赖安装完毕后，在源码目录下创建一个 build 目录

```bash
$ mkdir gcc-build
$ cd gcc-build
```

用其外层目录的 `configure` 文件来进行编译前配置：

```bash
$ ../configure --enable-checking=release --enable-languages=c,c++ --disable-multilib --prefix=/usr/local/gcc-6.5.0 --program-suffix=-6.5
```

* `--enable-checking` - 这个不知道干啥的，似乎是检查是否是 release？
* `enable-languages=c,c++` - 配置要安装的编译器所支持的语言
* `disable-multilib` - 仅安装支持 x64 的编译器
* `--prefix=...` - 将最终的 bin 安装到 `/usr/local/gcc-6.5.0` 下
  * 目前，系统自带的 GCC 位于 `/usr/bin/gcc` 下
  * 如果不指定安装位置，新的 GCC 会默认被安装到 `/usr/local/gcc` 下
  * 为了便于区分，将目录指定一下版本会比较好
* `--program-suffix=...` - 最终编译出来的 bin 位于 `/usr/local/gcc-6.5.0/bin` 下
  * `$GCC/bin` 下的 GCC 的名称默认就是 `gcc`
  * 为了便于区分，使其被命名为 `gcc-6.5`

```bash
$ make -j8
$ sudo make install
```

安装完毕后，测试安装是否成功：

```bash
$ /usr/local/gcc-6.5.0/bin/gcc-6.5 -v
使用内建 specs。
COLLECT_GCC=/usr/local/gcc-6.5.0/bin/gcc-6.5
COLLECT_LTO_WRAPPER=/usr/local/gcc-6.5.0/libexec/gcc/x86_64-pc-linux-gnu/6.5.0/lto-wrapper
目标：x86_64-pc-linux-gnu
配置为：../configure --prefix=/usr/local/gcc-6.5.0 --enable-checking=release --enable-languages=c,c++ --disable-multilib --program-suffix=-6.5
线程模型：posix
gcc 版本 6.5.0 (GCC)
```

我去。。。咋是中文的。。。反正就是成功了 🙄

Maybe 接下来可以用 GCC 6.5.0 来编译安装 GCC 5 了

刚才在 `make` 时没有加参数，默认用的是系统自带的 GCC 7

如果要使用 GCC 6 进行编译，应该要在 `make` 命令上配置参数显式声明

```bash
$ make CC="/usr/local/gcc-6.5.0/bin/gcc-6.5" -j8
```

---

