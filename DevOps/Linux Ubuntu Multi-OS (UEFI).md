# Linux - Ubuntu Multi-OS (UEFI)

Created by : Mr Dk.

2019 / 01 / 06 10:33

Nanjing, Jiangsu, China

---

## About

在 *Win10* 系统上安装 *Ubuntu* 多系统。前提是电脑支持 UEFI。

## Steps

1. 从 *Win10* 系统的磁盘中压缩出一块未分配磁盘
2. 使用 *UltraISO* 和 `.iso` 光盘映像制作启动盘
3. 在 U 盘上写入 `ubuntu-18.04-desktop-amd64.iso` 光盘映像文件
4. 重启计算机，插入 U 盘，进入 `BIOS`，将 U 盘引导优先级调制最高；保存后退出，计算机将再次自动重启，进入 U 盘启动
5. 进入安装界面，尽量先脱机安装 - 默认软件源大多在国外，网速慢
6. 硬盘分区 (重点)

## 硬盘分区

`这台计算机已经安装了多个操作系统。您准备怎么做？`

(选择刚才割出的空余的磁盘空间)

- [ ] 安装 Ubuntu，与其他系统共存
- [ ] 清除整个磁盘并安装 Ubuntu
- [x] 其它选项

这里与传统的 MBR boot 方式不同，不再需要单独分一个 `/boot`。

第一个分区，用于安装系统内核。选择空闲空间，点击 `+`

* 大小 - 30720MB (30GB)
* 新分区的类型 - `逻辑分区`
* 新分区的位置 - `空间起始位置`
* 用于 - `Ext4 日志文件系统`
* 挂载点 - `/`

第二个分区，用作 swap space。选择空闲空间，点击 `+`

* 大小 - 2048MB
* 新分区的类型 - `逻辑分区`
* 新分区的位置 - `空间起始位置`
* 用于 - `交换空间`

第三个分区，用于用户数据。选择空闲空间，点击 `+`

* 大小 - 剩余所有空间
* 新分区的类型 - `逻辑分区`
* 新分区的位置 - `空间起始位置`
* 用于 - `Ext4 日志文件系统`
* 挂载点 - `/home`

## 引导设备

`安装启动引导器的设备 ：` - 这是安装系统 boot loader 的位置。找到系统上已经有的 EFI System Partition (ESP) 分区，将 boot loader 安装到这里。在这个分区的 `efi` 目录下，每一个子目录都是一个系统的 boot loader。

---

## References

[EFI + GPT 模式下 Linux 与 Windows 双系统要诀](http://www.linuxdown.net/install/config/2018/0405/18934.html)

[Linux 系统中添加硬盘，并挂载到已有的目录](https://blog.csdn.net/jiandanjinxin/article/details/69969217?utm_source=blogxgwz0)

[How the Linux Kernel Boots](https://mrdrivingduck.github.io/blog/#/markdown?repo=how_linux_works_notes&path=Chapter%205%20-%20How%20the%20Linux%20Kernel%20Boots.md)

---

