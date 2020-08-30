# Linux - GRUB Boot

Created by : Mr Dk.

2020 / 05 / 21 19:11

Nanjing, Jiangsu, China

---

一台电脑上装了三个系统：

* Windows 10
* Ubuntu 18.04
* Deepin

直接把 deepin 的空间给回收了，但 GRUB 记录没有清理。重新开机以后直接进入了 GRUB 的命令行，无法自动 boot 了。

## 进入 Windows 10

首先输入 GRUB 命令 `ls`，列出本机上所有的硬盘及其分区：`(hd0,1) (hd0,2) (hd1,1) ...`，然后输入 `ls (hd0,1)/` 即可查看分区中的文件系统目录。通过这种方式，找到 Windows 10 的 boot 分区。

找到 boot 分区后，使用 `set root=(hd0,2)` 来设置当前目录，然后在文件目录中寻找 `/efi/Microsoft/Boot/bootmgfw.efi`。

```grub
chainloader /efi/Microsoft/Boot/bootmgfw.efi
```

然后最终输入 `boot` 命令即可引导启动。

启动完毕后，试图安装一些基于 Win 的引导修复软件。但是基本上都要收费，而且也没有修复成。所以尝试进入 Ubuntu 系统进行修复。

## 进入 Ubuntu

使用 U 盘制作一个 Ubuntu 启动盘，然后从 U 盘启动，并进入试用模式。然后下载 [boot-repair](https://github.com/yannmrn/boot-repair) 自动修复：

```console
$ sudo add-apt-repository ppa:yannubuntu/boot-repair && sudo apt update
$ sudo apt install -y boot-repair
$ boot-repair
```

## Reference

[CSDN - 修复 Ubuntu 启动项](https://blog.csdn.net/gyjun0230/article/details/48790501)

[CSDN - 【一顿操作】用 Grub2 命令行引导启动 Windows 10](https://blog.csdn.net/hikkilover/article/details/82290873)

---

