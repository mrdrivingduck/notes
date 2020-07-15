# Linux - Ubuntu 18.04 APT Source

Created by : Mr Dk.

2019 / 01 / 06 10:41

Nanjing, Jiangsu, China

---

## Workflow

*Ubuntu 18.04* 默认的软件源在国外，网速较慢；改为国内的软件源更为有效。根据 USTC 给出的 [使用帮助](https://mirrors.ustc.edu.cn/help/ubuntu.html)，直接或间接编辑 `/etc/apt/source.list` 即可。更换时需要注意不同版本之间的代号区别。

```console
$ sudo sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
```

修改完毕后需要更新软件源信息：

```console
$ sudo apt update
```

```console
$ sudo apt upgrade
```

## Attention

`bionic` 是 *Ubuntu 18.04* 的版本代号。如果为不同版本的 Ubuntu 更换 APT 源，需要选择对应版本的 APT 源。

---

