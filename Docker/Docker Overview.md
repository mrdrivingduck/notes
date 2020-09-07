# Docker - Overview

Created by : Mr Dk.

2020 / 09 / 06 23:11

Nanjing, Jiangsu, China

---

## 1. 简介

Hypervisor 虚拟化通过一个中间层，将一台或多台独立的机器虚拟运行于物理硬件之上，而容器则直接运行于 OS 内核之上的用户空间中。容器技术可以让多个 **独立的用户空间** 运行在同一台宿主机上。在超大规模多租户服务部署、轻量级沙盒或对安全性要求不太高的隔离环境中，容器技术非常流行。

得益于现代 Linux 内核的特性，容器和宿主机之间的隔离更加彻底。容器有独立的网络、存储栈，还有资源管理能力。容器运行 **不需要虚拟层和管理层**，而是使用 OS 的系统调用接口，从而降低了运行单个容器的开销，使得宿主机中可以运行更多的容器。

Docker 则是一个能够把开发的应用程序自动部署到容器中的开源引擎。

Docker 是一个 C/S 架构的程序。Docker 客户端向 Docker 服务器或守护进程 (Docker 引擎) 发出请求，服务器或守护进程完成工作并返回结果。Docker 提供了 CLI 以及一套 RESTful API 与守护进程进行交互。

Docker 镜像是基于 **联合文件系统** 的一种层次结构，由一系列指令逐步构建出来。我个人的理解是，镜像相当于一个保存在文件系统中的进程实时运行状态。当镜像被放入容器中运行后，就成为了一个或多个进程。

Docker Registry 是用来保存用户构建的镜像的地方，可以与 Git 仓库类比。

容器是基于镜像启动起来的，容器中可以运行一个或多个进程。镜像是 Docker 生命周期中的构建或打包阶段，而容器则是启动或执行阶段。

Docker 的技术组件如下：

* 原生的 Linux 容器格式 (`libcontainer`)
* Linux 内核的 namespace，用于隔离文件系统、进程、网络
  * 文件系统隔离 (每个容器都有自己的 `root` 文件系统)
  * 进程隔离 (每个容器都运行在自己的进程环境中)
  * 网络隔离 (容器间的虚拟网络接口和 IP 地址都是分开的)
* 资源隔离和分组 (cgroups) - 分配硬件资源到每个 Docker 容器
* 写时复制 (文件系统是分层的、快速的)
* 容器产生的 `STDIN`、`STDOUT`、`STDERR` 这些 I/O 流都会被记入日志
* 交互式 shell - 创建一个伪 tty 终端，并连接到 `STDIN`

## 2. Docker 守护进程

在 Docker 安装完毕后，需要确认 Docker 守护进程是否开始运行。并可以通过命令改变守护进程的监听端口号、绑定的 socket 等。

```bash
sudo status docker
```

```bash
service docker stop
service docker start
```

## 3. Docker 的简易使用

查看 docker 程序是否存在，功能是否正常：

```bash
sudo docker info
```

使用 `docker run` 来启动第一个 Docker 容器。首次启动时，Docker 会在本地检查是否存在镜像，如果没有，则会到 Registry 上拉取镜像。

* `-i` 表示容器的 `STDIN` 开启
* `-t` 表示 Docker 要为容器分配一个伪 tty 终端

上述两个选项用于启动一个交互式的容器。`ubuntu` 是要启动的镜像，`/bin/bash` 是镜像启动后执行的命令。

```bash
sudo docker run -i -t ubuntu /bin/bash
```

在交互式容器中查看 `/etc/hosts` 文件，可以看到容器有了自己的网卡和 IP 地址。在退出交互式容器的 bash 后，容器停止运行，但镜像依旧存在。通过以下命令可以查看所有的容器 (已停止的和正在运行的)：

```bash
sudo docker ps -a
```

Docker 会为每一个容器自动生成一个随机的名称。如果想要自行指定容器名称，可以在 `docker run` 命令中显式指定。容器的命名有助于分辨容器。

```bash
sudo docker run --name mycontainer -i -t ubuntu /bin/bash
```

通过以下命令重新启动一个容器：

```bash
sudo docker start mycontainer
```

附着到一个正在运行的容器上：

```bash
sudo docker attach mycontainer
```

创建一个后台运行的守护式容器：在 `docker run` 命令上加上 `-d` 参数。通过以下命令可以查看容器的日志。与 `tail` 命令十分类似。

```bash
sudo docker logs mycontainer
```

查看容器内部的进程：

```bash
sudo docker top mycontainer
```

显示一个或多个容器的统计信息：

```bash
sudo docker stats mycontainer
```

在容器内部启动新进程：

```bash
sudo docker exec -d mycontainer touch /etc/new_config_file # 后台进程
sudo docker exec -t -i mycontainer /bin/bash # 交互式进程
```

停止守护式容器：

```bash
sudo docker stop mycontainer
```

在 `docker run` 命令中加入 `--restart` 选项，可以使 Docker 检查容器的退出代码后，决定是否要重启容器。查看更多的容器信息：

```bash
sudo docker inspect mycontainer
```

如果容器不再被使用，则可以删除：

```bash
sudo docker rm mycontainer
```

---

