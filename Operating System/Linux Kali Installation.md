# Linux - Kali Installation

Created by : Mr Dk.

2019 / 01 / 13 22:30

Nanjing, Jiangsu, China

---

## About

制作 _U_ 盘安装镜像时，使用 `Win32 Disk Imager` 制作

否则在安装阶段无法识别光盘介质

插拔 _U_ 盘也没有用

用 `Win32 Disk Imager` 制作的 _U_ 盘镜像可以被识别

## Disk Partition

* `Ext4 文件系统` - 主分区，挂载根目录 `/`
* `交换分区` - _SWAP_ 分区

## Software Source

2018 年最新的 _Kali 2.0_ 国内可用软件源记录：

```bash
$ vim /etc/apt/sources.list
```

_USTC_：

```
deb http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
deb-src http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
```

_Alibaba Cloud_

```
deb http://mirrors.aliyun.com/kali kali-rolling main non-free contrib
deb-src http://mirrors.aliyun.com/kali kali-rolling main non-free contrib
```

别的没用过不记了

---

## Summary

__装系统：千古奇坑__ 我自闭了 😑

---

