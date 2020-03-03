# Go - Install & Basic Config

Created by : Mr Dk.

2019 / 07 / 05 12:11

Nanjing, Jiangsu, China

---

## About Go

Go is an open source programming language that makes it easy to build simple, reliable, and efficient software. - https://golang.org/

Wiki - 

> __Go__ (__Golang__) 是 Google 开发的一种静态强类型、编译型、并发型，并具有垃圾回收功能的编程语言。与 2009 年 11 月正式宣布推出，成为开放源代码项目，并在 Linux 及 Mac OS X 平台上进行了实现，后来追加了 Windows 系统下的实现。

Go 的语法接近 C 语言，但对于变量的声明有所不同。Go 支持垃圾回收功能，特色在于令人简易使用的并行设计 - Goroutine：

* 能够让程序以异步的方式运行
* 非常适合网络服务

Goroutine 类似于线程，但不属于系统层面，相当于轻量级的线程。一个 Go 程序可以运行超过数万个 Goroutine。

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

## Command

```bash
$ go
Go is a tool for managing Go source code.

Usage:

        go <command> [arguments]

The commands are:

        bug         start a bug report
        build       compile packages and dependencies
        clean       remove object files and cached files
        doc         show documentation for package or symbol
        env         print Go environment information
        fix         update packages to use new APIs
        fmt         gofmt (reformat) package sources
        generate    generate Go files by processing source
        get         download and install packages and dependencies
        install     compile and install packages and dependencies
        list        list packages or modules
        mod         module maintenance
        run         compile and run Go program
        test        test packages
        tool        run specified go tool
        version     print Go version
        vet         report likely mistakes in packages

Use "go help <command>" for more information about a command.
```

### build & run & clean

执行 Go 程序需要先编译。与其它语言类似，Go 程序的入口位于 `main` package 的 `main` 函数：

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello World")
}
```

执行 `go build` 能够编译并生成可执行文件：

```bash
$ go build hello.go
$ ./hello.exe
Hello World
```

如果 `go build` 的对象是一个包，而不是一个带有入口的函数，将不会生成可执行文件。

`go run` 相当于将上述的两部合并为一步，不再产生中间文件：

```bash
$ go run hello.go
```

清除产生的可执行文件（默认清除所有可执行文件）：

```bash
$ go clean [xxx.go]
```

### install

我的理解是，相当于 `npm` 的全局安装吧。安装的位置位于工作目录下，即所谓 `$GOPATH`：

* 默认位于用户目录下 - `~/go/`
* 生成的可执行文件位于 `$GOPATH/bin`

### get

```bash
$ go get github.com/google/syzkaller
```

目前支持的几个源中包含 GitHub。实际上是先 `git clone` 了对应仓库，再用 `go install` 进行编译和安装。源码将会下载到 `$GOPATH/src` 下，并根据来源的仓库名逐级划分文件夹 - `$GOPATH/src/github.com/google/syzkaller`。

`go install` 产生的可执行文件位于 - `$GOPATH/bin` 中。因此 `$GOPATH` 下大概会是这样：

```
$GOPATH
|
|-- src/
|   |
|   |-- github.com/
|       |
|       |-- google/
|           |
|           |-- syzkaller/
|-- bin/
|   |
|   |-- syz-manager
|-- pkg/   
```

这条命令最毒的地方在于，官方文档给的例子 - `golang.org/x/*` 等目标源都是被墙的 😡。所以要到 GitHub 上 Golang 组织的仓库中把几个基本包的镜像 clone 下来，而且在 `$GOPATH` 中的路径形式需要与链接一致，不能按着 GitHub 来：

* 即目录结构为：`$GOPATH/src/golang.org/x/*`
* `*` 为从 GitHub 上 clone 下来的文件夹

好像几个基本的包不需要 install，只需要在源码目录里放着就行？这个还没太搞清楚。

Golang 给了一个官方的教程程序 - _tour_ ，依赖于 _net_ 和 _tools_ 这两个包：

* 这两个包由于在 golang.org 上被墙，只能从 GitHub 镜像上下载
* 哦，_tour_ 好像也只能从 GitHub 镜像上下载

然后在 tour 的目录中 `go install`：

* 会自动寻找到依赖的 _net_ 和 _tools_ ，编译
* 在 `$GOPATH/bin` 下生成了 `tour.exe`
* 运行 `tour.exe`，在浏览器访问对应端口，就可以开始学习 Golang 的旅程了

---

