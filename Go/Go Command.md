# Go - Command

Created by : Mr Dk.

2019 / 07 / 06 0:30

Nanjing, Jiangsu, China

---

## About

Golang 有很多命令：

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

---

## build & run & clean

执行 Go 程序需要先编译

与其它语言类似，Go 程序的入口位于 `main` package 的 `main` 函数：

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

如果 `go build` 的对象是一个包，而不是一个带有入口的函数，将不会生成可执行文件

`go run` 相当于将上述的两部合并为一步，不再产生中间文件：

```bash
$ go run hello.go
```

清除产生的可执行文件（默认清除所有可执行文件）：

```bash
$ go clean [xxx.go]
```

---

## install

我的理解是，相当于 `npm` 的全局安装吧

安装的位置位于工作目录下，即所谓 `$GOPATH`

* 默认位于用户目录下 - `~/go/`
* 生成的可执行文件位于 `$GOPATH/bin`

------

## get

```bash
$ go get github.com/google/syzkaller
```

目前支持的几个来源中包含 GitHub

在内部，实际上是先 `git clone` 了对应仓库

再用 `go install` 进行编译和安装

源码将会下载到 `$GOPATH/src` 下

并根据来源的仓库名逐级划分文件夹 - `$GOPATH/src/github.com/google/syzkaller`

`go install` 产生的可执行文件位于 - `$GOPATH/bin` 中

因此 `$GOPATH` 下大概会是这样：

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

这条命令最毒的地方在于

官方教程给的实例 - `golang.org/x/*` 等目标都是被墙的 😡

所以要到 GitHub 上 Golang 组织的仓库中把几个基本包的镜像 clone 下来

而且在 `$GOPATH` 中的路径形式需要与链接一致，不能按着 GitHub 来：

* 即目录结构为：`$GOPATH/src/golang.org/x/*`
* `*` 为从 GitHub 上 clone 下来的文件夹

好像几个基本的包不需要 install，只需要在源码目录里放着就行？

这个还没太搞清楚

Golang 给了一个官方的教程程序 - _tour_

依赖于 _net_ 和 _tools_ 这两个包

* 这两个包由于在 golang.org 上被墙，只能从 GitHub 镜像上下载
* 哦，_tour_ 好像也只能从 GitHub 镜像上下载

然后在 tour 的目录中 `go install`

* 会自动寻找到依赖的 _net_ 和 _tools_，编译
* 在 `$GOPATH/bin` 下生成了 `tour.exe`
* 运行 `tour.exe`，在浏览器访问对应端口，就可以开始学习 Golang 的旅程了

---

## Summary

。。。。。。继续学吧

这语言真的让人挺感兴趣的 😴

---

