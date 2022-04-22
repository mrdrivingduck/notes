# Compiler - Multi-version GCC

Created by : Mr Dk.

2020 / 05 / 07 22:50

Nanjing, Jiangsu, China

---

在不同版本的 Linux distribution 中，有着不同默认版本的 GCC。比如 Ubuntu 18.04 自带 GCC 7.5.0，Ubuntu 20.04 自带 GCC 9.3.0。但是，有时编译一些以前的代码，会因为高版本编译器的严格要求而无法通过，使得我们不得不同时安装低版本的编译器。

通过源码编译安装好麻烦。最方便的方法当然是通过 APT 来安装历史版本的 GCC。但是如何管理多个版本的 GCC 是个麻烦事。使用 `build-essential` 可以进行方便地管理：

```console
$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 9
$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 8
$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 7
```

然后通过如下命令可以替换 `gcc` 默认指向的 GCC 版本：

```bash
sudo update-alternatives --config gcc
```
