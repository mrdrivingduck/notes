# Go - Environment

Created by : Mr Dk.

2019 / 07 / 05 12:11

Nanjing, Jiangsu, China

---

## About Go

Go is an open source programming language that makes it easy to build simple, reliable, and efficient software. - https://golang.org/

Wiki - 

> __Go__ (__Golang__) 是 Google 开发的一种静态强类型、编译型、并发型，并具有垃圾回收功能的编程语言。与 2009 年 11 月正式宣布推出，成为开放源代码项目，并在 Linux 及 Mac OS X 平台上进行了实现，后来追加了 Windows 系统下的实现。

Go 的语法接近 C 语言，但对于变量的声明有所不同

Go 支持垃圾回收功能

Go 的特色在于令人简易使用的并行设计 - Goroutine

* 能够让程序以异步的方式运行
* 非常适合网络服务

Goroutine 类似于线程，但不属于系统层面，相当于轻量级的线程

一个 Go 程序可以运行超过数万个 Goroutine

---

## Installation

下载地址 - https://golang.org/dl/

### Windows

直接下载 `.msi` 安装程序

自动配置环境变量等

### Linux

下载 `.tar.gz` 压缩包

将压缩包解压到 `/usr/local` 目录下：

```bash
$ tar -C /usr/local -zxvf go1.12.6.linux-amd64.tar.gz
```

添加 Go 的 `/bin` 到环境变量中：

```bash
$ vim /etc/profile
```

```
export GOROOT=/usr/local/go
export PATH=$PATH:$GOROOT/bin
```

```bash
$ source /etc/profile
```

测试配置是否成功：

```bash
$ go version
go version go1.12.6 linux/amd64
```

---

## Summary

一直说要学一学 Golang 的

不过最近可能没时间

今天在配 syzkaller 的环境

必须得配置一下 Golang 了

顺便写了个 hello world 感受了一下

之后哪天有空再仔细学叭

对 Golang 的一些特性还是很感兴趣哒 😈

---

