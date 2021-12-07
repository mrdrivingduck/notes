# Linux: Package Manager

Created by : Mr Dk.

2021 / 12 / 07 13:55

Nanjing, Jiangsu, China

---

如果说到不同的 Linux distribution 之间最大的差别，或许软件包管理可以称得上是其中一个。软件包管理器是一个工具，允许用户在操作系统上对一个软件进行 **全生命周期管理**：下载、安装、删除、升级等，类似于手机上的 App Store。

为什么会有软件包管理器的出现？软件包通常指各种形式的应用程序（GUI / cmd / lib），本质上包含：可执行文件、配置、依赖程序。从最原始的方式来说，软件是以源代码的方式分发的。在一台电脑上安装软件的过程是从源码开始编译安装：

- 下载源码
- 在本地对软件进行配置（`./configure`）并安装依赖程序
- 编译（`make`）
- 安装（可执行文件拷贝至系统目录 `make install`）

这种软件分发方式十分复杂，在一定程度上也限制了软件分发的自由度。为了摆脱这种复杂的方式，Linux distribution 提出了各自的打包格式，为用户直接提供可执行文件，并对版本、描述等 **元数据** 以及 **依赖关系** 进行管理。Debian 类系统提出了 DEB 格式（`.deb`），Red Hat Linux 提出了 RPM 格式（`.rpm`）。

有了软件包管理器，用户可以直接通过管理器下载可执行文件。在下载一个软件时，软件包管理器还会解析该软件的所有依赖，与该可执行文件一起安装。

## Yum

### 基本使用

Yum (Yellow dog Updater, Modified) 是一个基于 RPM 包的管理器。特此记录一些基本用法：

```bash
yum update
yum install xxx
yum remove xxx
```

### 软件包搜索相关

根据软件名称模糊查找软件源上可用的软件包：

```bash
yum search gcc
```

查询哪些软件包里带有特定的可执行文件：

```bash
yum provides */[file]
```

### 额外软件源

基于干净的 CentOS 7 容器为上层应用搭建环境时发现，默认软件源里的软件包太少了。可以加入一些额外的官方软件源。

Extra Packages for Enterprise Linux (EPEL)：企业版 Linux 附加软件包，创建、维护及管理针对企业版 Linux 的高质量附加软件包集合。

```bash
yum install epel-release
yum update
```

Software Collections (SCL)：软件选集仓库。

> 企业级 Linux 发行版本都被设计成持久可用的。它们的设计亦包括在发行版本使用期内维持 ABI／API 兼容性，因此只要某个发行版本仍获支持，你在它发行首日所写的程序便可一直运作。现时 CentOS 的寿命是 10 年。然而，这意味著在发行版本使用期的尾段，它所包含的程序语言或数据库版本（例如 php、python、perl 或 mysql、postgresql）对比「尖端」Linux 发行版本所提供的就显得古旧。
>
> 对行多企业用户而言，这不是问题……试想想一间大型零售商，耗资一千万以缺省的语言创建了一个盘点方案，她期望在整个 10 年使用期内安心地应用该方案，以便获得投资在程序上的回报。不过有很多企业亦希望能以较新的程序创建软件。她们想同时拥有稳定性及较新的软件。她们要求这些软件兼容其它系统软件，好让她们能选择遁序改进或较新的软件作开发之用。
>
> 让我介绍软件选集，又名 SCL。举个例说：SCL 容许你执行 CentOS 提供的缺省 python（这样 yum 及其它 CentOS 工具便可用），又容许你同时安装较新版的 python 作创建及执行程序之用。

```bash
yum install centos-release-scl
yum update
```

## References

[稀土掘金 - Linux 黑话解释：什么是包管理器？它是如何工作的？](https://juejin.cn/post/6884417656699486221)

[Wikipedia - yum (software)](https://en.wikipedia.org/wiki/Yum_(software))

[Find which package contains a specific file](https://www.garron.me/en/linux/find-which-package-library-belongs.html)

[CentOS 软件选集（SCL）软件库](https://wiki.centos.org/zh/AdditionalResources/Repositories/SCL)

[Extra Packages for Enterprise Linux (EPEL)](https://docs.fedoraproject.org/en-US/epel/)
