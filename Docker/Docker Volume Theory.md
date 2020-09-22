# Docker - Volume Theory

Created by : Mr Dk.

2020 / 09 / 22 23:16

Nanjing, Jiangsu, China

---

## Features

Docker 的镜像由一系列只读层和一个读写层组合而来。这个设计提高了 Docker 对镜像构建、存储和分发的效率，节省了时间和存储空间，但存在一定的问题：

* 不能在宿主机上很方便地对容器中的文件进行访问
* 多个容器之间无法共享数据
* 删除容器时，容器产生的数据将丢失

Docker 引入了数据卷机制。卷 (volume) 是存在于一个或多个容器中的特定文件或文件夹，以 **独立于联合文件系统** 的形式在宿主机中存在。卷具有以下特定：

* 在容器创建时初始化
* 能在不同容器之间共享和重用
* 对卷中的数据操作会立刻生效
* 对卷中的数据操作不影响镜像本身
* 卷的生命周期独立于容器的生命周期

## Mount

当容器启动时，通过 `-v` 选项将一个卷挂载到容器当中。Docker 支持两种来源的卷：

* 用户自行创建的卷 (`/var/lib/docker/volume/<volume-id>/_data`)
* 宿主机上已有的目录

如果宿主机上不存在指定的目录，那么将会创建一个空文件夹；如果镜像内挂载路径原本已经有文件了，那么原有文件将会被隐藏，以保持和宿主机的卷目录一致。另外，也可以将单个文件作为卷挂载到容器内。宿主机上的挂载文件也会使容器内原有的文件被隐藏，以保证文件一致。

当在 Dockerfile 中通过 `VOLUME` 在容器中添加了卷 (注意这里指定的是 **容器内** 的挂载点)，容器启动时，如果镜像中存在相应的卷文件夹，那么该文件夹中的内容会被全体复制到宿主机上对应的卷文件夹中，并根据容器中的文件设置合适的 **权限** 和 **所有者**。

另外，在启动容器时，可以直接使用 `--volumes-from` 与一个已有容器共享卷。

## Remove

在删除容器时，需要对容器的卷进行妥善处理。当删除卷时，只有当没有任何容器使用这个卷，才能被删除。

如果卷是在创建容器时从宿主机中挂载的，那么无论对容器做什么操作都不会导致其在宿主机中被删除。

## Theory

Docker 中的卷本质上是一个特殊的目录。在容器创建过程中，Docker 将宿主机上的指定目录 (以 `volume-id` 为名称的目录，或宿主机上的指定目录) 挂载到容器中的指定目录上。这里使用的是 **绑定挂载**，这样能够保证挂载完成后宿主机目录和容器内目标目录的表现一致。

实际上，Docker 相当于在创建容器的同时，在容器内执行了以下代码：

```
mount("/var/lib/docker/volumes/<volume_id>/_data", "rootfs/data", "none", MS_BIND, NULL);
mount("/var/log", "rootfs/data", "none", MS_BIND, NULL);
```

在处理完所有的 mount 操作之后，Docker 再将进程的根目录切换到 rootfs 中。这样，容器内部的进程就只能看到以 rootfs 为根的文件目录，以及被 mount 到 rootfs 下的所有卷目录了。由此可见，Docker daemon 为容器挂载卷的核心是组装出合适的 mount 指令：

1. 解析参数，生成参数列表 (参数描述了一个 volume 与宿主机目录的对应关系)
2. 使用参数列表中的参数生成挂载点列表，在宿主机和容器文件目录下创建好挂载点路径
3. 将挂载点列表传给 libcontainer，启动容器，完成所有的 mount 操作

从用户输入的参数中，Docker 可以解析出宿主机上的源目录路径，以及容器内的挂载位置。Docker 会负责维护一个本地的 volume 列表，保存了所有本地有名字的 volume 及其存储路径和驱动名称；如果用户没有指定 volume 名，那么 Docker 将随机生成一个名字，并纳入 volume 列表的管理中。

最终，Docker 为每个容器维护了一个挂载点列表。每个挂载点中的信息如下：

```go
type MountPoint struct {
    Source      string // 源目录
    Destination string // 目的目录
    RW          bool   // 是否可写
    Name        string // 卷的名字
    Driver      string // 卷的驱动名
    Volume      Volume // 本地 volume 信息
    Mode        string // 挂载模式
    Propagation string // 挂载拓展选项
    Named       bool   // 挂载点是否被命名
}
```

如果正要启动的容器想与一个正在运行中的容器共享卷，那么 Docker 将根据容器 ID 查找到相应的容器对象，然后将该对象的 volumes 数组复制到当前容器的挂载点列表中。总之，两种不同来源途径的挂载点会在这一步被统一为格式相同的挂载点，此后 Docker 就不需要关心这个 volume 从何而来了。

| 成员 / 参数 | `-v vol_simple:/containerdir`              | `-v /containerdir`                          | `-v /hostdir:/containerdir:ro` |
| ----------- | ------------------------------------------ | ------------------------------------------- | ------------------------------ |
| Source      | `/var/lib/docker/volumes/vol_simple/_data` | `/var/lib/docker/volumes/<random_id>/_data` | `/hostdir`                     |
| Destination | `/containerdir`                            | `/containerdir`                             | `/containerdir`                |
| RW          | true                                       | true                                        | false                          |
| Name        | vol_simple                                 | random-id                                   | null                           |
| Named       | true                                       | false                                       | false                          |

在容器启动阶段，Docker 会根据目的目录的级数对挂载点列表中的挂载点进行排序 (如避免 `/container/dir` 会覆盖 `/container`)，然后将新的挂载点列表传递给 libcontainer，传递的挂载点包含五个参数：

* Source (源路径)
* Destination (目的路径)
* Device - "bind"
* Flags
* PropagationFlags

这些参数也就是 mount 指令所需要的参数。

在使用 `docker volume rm` 删除卷时，Docker 首先检查是否还有容器在使用卷。如果还有，那么不能删除。如果没有容器在使用卷了，那么 Docker 就会将这个卷从宿主机目录上删除，同时还会删除本地 volume 列表中维护的卷相关信息。

如果使用 `docker rum --rm` 或 `docker rm -v` 在删除容器时同时删除所关联的卷，那么 Docker 会过滤掉挂载点中 `Named` 字段为 true 的卷，即不删除命名的卷。

---

