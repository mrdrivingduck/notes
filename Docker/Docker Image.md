# Docker - Image

Created by : Mr Dk.

2020 / 09 / 07 17:02

Nanjing, Jiangsu, China

---

## 什么是 Docker 镜像

Docker 容器从镜像中启动。Docker 镜像由多层文件系统叠加而成。最底层是 **bootfs (引导文件系统)** - 当一个容器启动后，bootfs 就会被 unmount，从而留出更多内存供 initrd 磁盘镜像使用。

在 bootfs 层之上，是 **rootfs (root 文件系统)**，可以是一种或多种操作系统 (如 Ubuntu 或 Debian)。在传统的 Linux 引导过程中，rootfs 会先以只读方式加载，在引导结束并完成完整性检查后，会被切换为读写模式。而 Docker 中的 rootfs 永远是只读状态 - 通过 *联合加载技术 (Union Mount)*，Docker 还会在 rootfs 上加载更多的只读文件系统，而从容器外面看起来只能看到一个文件系统。

以上文件系统就是镜像。在容器启动完成后，Docker 会在镜像最顶层加载一个 **读写文件系统**。之后在 Docker 中运行的程序将操作读写层。读写层一开始是空的。当文件系统发生变化时 (比如修改了一个文件)，那么文件将首先从读写层以下的只读层复制到读写层中，并应用修改。该文件的只读版本依然存在，但已经被读写层中的副本遮盖隐藏。这种机制被称为 *写时复制 (Copy-on-Write)*。Docker 的每一个只读镜像层都是只读的，每当创建新容器时，Docker 会构建出镜像栈，然后在最顶层添加一个读写层。也就是说，读写层只包含当前容器中被修改了的文件。

## 相关命令

列出主机上可用的镜像 (位于 `/var/lib/docker`)：

```console
$ sudo docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
ubuntu              20.04               4e2eef94cd6b        2 weeks ago         73.9MB
hello-world         latest              bf756fb1ae65        8 months ago        13.3kB
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
```

从 Docker Registry 上拉取镜像。同一个仓库 (如 `ubuntu`) 可以有多个不同的镜像 (`12.04` / `12.10` / `precise`)。

```console
$ sudo docker pull ubuntu:20.04
20.04: Pulling from library/ubuntu
54ee1f796a1e: Already exists
f7bfea53ad12: Already exists
46d371e02073: Already exists
b66c17bbf772: Already exists
Digest: sha256:31dfb10d52ce76c5ca0aa19d10b3e6424b830729e32a89a7c6eee2cda2be67a5
Status: Downloaded newer image for ubuntu:20.04
docker.io/library/ubuntu:20.04
```

为了区分同一个仓库中的不同镜像，Docker 提供了 **标签 (tag)** 功能。每个标签对一些特定的镜像层进行标记。通过在仓库名后加一个冒号和标签名来指定仓库中的镜像。另外，一个镜像也可以有多个标签。

Docker Hub 上有两种类型的仓库：

* 用户仓库 - 存放用户创建的镜像，包含用户名和仓库名
* 顶层仓库 - 由 Docker 与选定的优质厂商合作，只包含仓库名 (如 `ubuntu` 仓库)

当运行 `docker run` 时，如果本地没有镜像，则 Docker 会先从 Docker Hub 下载镜像。如果镜像的标签没有指定，那么默认下载 `latest` 标签的镜像。在下载镜像时，可以指定镜像的 tag：

```bash
sudo docker pull fedora:21
```

在 Docker Hub 可以查找公共的镜像，也可以通过命令完成：

```console
$ sudo docker search puppet
NAME                                               DESCRIPTION                                     STARS               OFFICIAL            AUTOMATED
puppet/puppetserver                                A Docker Image for running Puppet Server. Wi…   93
alekzonder/puppeteer                               GoogleChrome/puppeteer image and screenshots…   75                                      [OK]
buildkite/puppeteer                                A Puppeteer Docker image based on Puppeteer’…   54                                      [OK]
puppet/puppetdb                                    A Docker image for running PuppetDB             33
devopsil/puppet                                    Dockerfile for a container with puppet insta…   31                                      [OK]
macadmins/puppetmaster                             Simple puppetmaster based on CentOS 6           26                                      [OK]
puppet/puppetboard                                 The Puppet Board dashboard for PuppetDB         19
puppet/puppet-agent-alpine                         Puppet Agent as a Docker Image. Based on Alp…   17
puppet/puppet-agent                                Puppet Agent as a Docker Image.                 13
puppet/puppetexplorer                              The Puppet Explorer dashboard for PuppetDB      13
puppet/puppet-agent-ubuntu                         Puppet Agent as a Docker Image. Based on the…   13
zenato/puppeteer-renderer                          Puppeteer(Chrome headless node API) based we…   11                                      [OK]
puppet/puppet-dev-tools                            Puppet development tools such as PDK, onceov…   8
camptocamp/puppetserver                            Puppetlabs's puppetserver                       7                                       [OK]
puppet/continuous-delivery-for-puppet-enterprise   Automated testing and promotion of infrastru…   4
jumanjiman/puppet                                  Use Puppet to configure CoreOS hosts            3
vpgrp/puppet                                       Docker images of Puppet.                        2                                       [OK]
vladgh/puppetserver                                Vlad's Puppet Server                            2                                       [OK]
vladgh/puppet                                      Ubuntu 16.04 LTS Base image with Puppet         2                                       [OK]
ccaum/puppet-dev                                   Puppet development tools in Docker              1
vladgh/puppetserverdb                              Vlad's Puppet Server configured for PuppetDB    1                                       [OK]
puppet/puppet-bolt                                 Puppet Bolt as a docker image                   1
terzom/puppetboard                                 Puppetboard is a web interface to PuppetDB p…   0                                       [OK]
ananace/puppetlint                                 Docker images with Puppet-lint and checks fo…   0                                       [OK]
ipcrm/puppet_webapp                                                                                0
```

## 构建镜像

与 Git 类似，通过 `docker commit` 就可以构建自己的镜像并发布，但这种方法不被推荐使用。最好是编写 Dokcerfile 文件后使用 `docker build` 命令。通常来说，一般用户是基于一个已有的基础镜像构建一个新镜像。

显然，`docker commit` 会将创建容器的镜像与容器当前状态之间有差异的部分构建为一个新的镜像层，因此更新应当非常轻量。只需要给出容器 ID、远程仓库，以及可选的提交信息和作者信息。

```bash
sudo docker commit -m"..." -a"..." 4aab3ce3cb76 jamtur01/apache2:webserver
```

但是更为推荐的是使用 Dockerfile + `docker build` 命令来构建镜像，这样构建出的镜像更具备 **可重复性** 和 **透明性**。Dockerfile 由一系列执行和参数组成，按顺序从上到下依次执行。每条指令被执行后，Docker 都会构建一个新的镜像层并 commit。如果 Dockerfile 执行到某条指令时失败了，那么用户将得到失败前的最后一个正确构建的镜像。在修改 Dockerfile 之后重新执行 `docker build` 时，Docker 会将已经构建成功的镜像作为缓存，直接从那个缓存层开始继续构建。如果确定不要使用构建缓存，那么可以使用 `docker build --no-cache`。

如果想深入探究镜像如何被构建：

```bash
sudo docker history 22d47c8cb6e5
```

## 启动容器

基于新构建的镜像启动容器时，在 `docker run` 中附加 `-p` 标志来控制该容器运行时暴露哪些端口给宿主机：

```bash
sudo docker run -d -p 80 --name mycontainer someone/somerepo nginx -g "daemon off;"
```

这样，就在容器中暴露了 `80` 端口。容器的暴露端口将会与宿主机上的一个较大的随机端口相映射。通过以下命令可以查看容器的端口映射情况：

```bash
sudo docker ps -l
sudo docker port 6751b94bb5c0 80
```

当然，也可以在命令行直接指定端口的映射关系，但是需要小心这种做法，因为一个宿主机端口只能被一个容器端口映射。

```bash
sudo docker run -d -p 8080:80 --name mycontainer someone/somerepo nginx -g "daemon off;"
```

## Dockerfile 指令

### FROM 指令

每个 Dockerfile 的第一条指令必须是 `FROM`，该指令指定一个已经存在的镜像作为当前容器的基础镜像 (base image)。

### MAINTAINER 指令

`MAINTAINER` 指令，告诉 Docker 该镜像的作者是谁，邮件是多少。

### RUN 指令

`RUN` 指令会在当前镜像中运行指定的命令。每条 `RUN` 指令都会创建一个新的镜像层 - 如果指令执行成功，那么这个新的镜像层将会被 commit。`RUN` 指令默认由容器中的 `/bin/sh -c` 运行，但也支持 Linux execve 系统调用形式的 `RUN` 命令。

### EXPOSE 指令

`EXPOSE` 指令指定了当前容器中将要暴露的端口。Docker 不会自动打开这些端口，而是要在运行 `docker run` 命令时显式指定。

```dockerfile
FROM ubuntu:14.04
MAINTAINER someone "someone@some.com"
RUN apt update && apt install -y nginx
RUN [ "apt", "install", "-y", "nginx" ]
EXPOSE 80
```

### CMD 指令

`CMD` 指令一个容器启动时要运行的命令，这与 `docker run` 指定的启动命令非常类似。与 `RUN` 类似，`CMD` 也支持类似 execve 风格的调用方式。`docker run` 命令中的启动命令将会覆盖 Dockerfile 中的 `CMD` 指令。

### ENTRYPOINT 指令

与 `CMD` 指令类似，但是处理 `docker run` 的命令行覆盖问题。在 `docker run` 命令行中指定的任何参数都会被当作参数传递给 `ENTRYPOINT` 指令中指定的命令。

### WORKDIR 指令

从镜像创建新容器时，在容器内部设置一个工作目录，用于指令 `ENTRYPOINT` 或 `CMD` 指令。

### ENV 指令

在镜像构建过程中设置环境变量，且环境变量可以在后续的任何 `RUN` 指令或其它指令中使用。另外，还可以通过 `docker run` 命令的 `-e` 标志传递环境变量 - 这些变量将只会在运行时有效。

### USER 指令

指定镜像以什么用户去运行。

### VOLUME 指令

用于向基于镜像创建的容器添加 **卷**。卷可以是存在于一个或多个容器内的特定目录，该目录绕过联合文件系统，使用户能够将数据、数据库或其它内容添加到镜像中，而不用产生镜像层，并且允许多个容器间共享这些内容。

### ADD 指令

将构建环境下的文件和目录复制到镜像中 - 因此需要 **源文件位置** 和 **目的文件位置** 两个参数。当源文件是一个归档文件时，Docker 还会自动将归档解开。

### COPY 指令

与 `ADD` 指令非常类似，但不同的是 `COPY` 只关心复制文件，而不关心提取和解压。

### LABEL 指令

用于为 Docker 镜像添加元数据。

### STOPSIGNAL 指令

设置停止容器时向容器发送的系统调用信号。

### ARG 指令

定义可以在 `docker build` 命令运行时传递的变量：

```dockerfile
ARG build
ARG webapp_user=user
```

```bash
sudo docker build --build-arg build=1234 -t someone/somerepo .
```

另外，Docker 还预定义了一组 `ARG` 变量，可以在构建时直接使用。

### ONBUILD 指令

为镜像添加触发器。当这个镜像被其它镜像用作基础镜像时，触发器将会被执行。也就是说，在基础镜像 A 中设置了 `ONBUILD` 指令后，在 B 镜像使用 A 镜像作为基础镜像时，在 B 镜像 Dockerfile 的 `FROM` 指令执行后，将会触发 A 中设置的指令。

`ONBUILD` 触发器会按照在父镜像中指定的顺序执行，且只能被继承一次 (在孙子镜像中不会被执行)。

## 将镜像推送到 Docker Hub

与 Git 类似，在镜像被构建完毕后，通过 `docker push` 可以将镜像保存到仓库中。

可以将包含 Dockerfile 的目录推送到 Docker Hub 上，并触发自动构建，自动产生一个新镜像。

## 删除镜像

如果不再需要一个镜像了，就可以使用 `docker rmi` 命令删除镜像。

---

