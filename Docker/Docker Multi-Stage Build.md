# Docker - Multi-Stage Build

Created by : Mr Dk.

2022 / 05 / 11 23:35

Hangzhou, Zhejiang, China

---

目的：产生更小的镜像。

## Background

最近要发布一个带有可执行文件的 Docker 镜像，可供用户直接 `docker run` 起来就可以使用了。其中，可执行文件需要通过源码编译获取。

所以最简单的做法是：

1. 在容器内准备好编译代码和运行可执行文件的所有依赖
2. 克隆源码
3. 编译构建可执行文件
4. 镜像打包

但是这种做法有几个问题：

- 镜像内的编译工具在编译完毕后不再被使用
- 镜像内的源码没有必要保留，但是删除源码并不能减小镜像大小

## Multi-Stage Image Building

Docker 支持多阶段的镜像构建，这是减小最终镜像的有效手段。多阶段构建允许在一个 Dockerfile 中使用多个 `FROM` 指令。配合 `COPY --from` 指令将 **编译镜像** 中构建完毕的可执行文件拷贝到另一个 **运行时镜像** 当中。其中：

- 编译镜像中包含编译源码所需要的所有依赖
- 运行时镜像中包含可执行文件运行所需要的所有依赖
- 编译镜像中产生的可执行文件被拷贝到运行时镜像中

这样来看，运行时镜像的层次主要有：

- 基础镜像
- ~~编译工具和依赖~~
- 运行时依赖
- ~~源码~~
- 可执行文件
- ~~（删除源码）~~

可见，多阶段构建的镜像能够减少不必要的镜像层，从而减小镜像的大小。

## Practice

其具体实践方式的伪代码如下：

```Dockerfile
FROM building_image AS building
RUN install building tools
RUN clone the code
RUN build the code

FROM running_image
RUN install running dependencies
COPY --from=building <path_in_building_image> <path_in_running_image>
ENTRYPOINT ...
```

最终，发布运行版的容器镜像即可。

其中 `COPY` 指令有一个挺坑的地方：如果想递归拷贝整个目录（保持目录和文件的结构），那么 **不能使用通配符**，否则目录的结构将会被 **拉平**。这与 `cp` 命令不同。

> It's important to note that the secret sauce here is that there is ONE source directory, and ONE target directory specified. Any other combination copies the contents of the source directory(ies) to the target directory.

## References

[About Docker Multi-Stage Builds and COPY --from](https://levelup.gitconnected.com/docker-multi-stage-builds-and-copy-from-other-images-3bf1a2b095e0)

[stackoverflow - Dockerfile copy keep subdirectory structure](https://stackoverflow.com/questions/30215830/dockerfile-copy-keep-subdirectory-structure)
