# Network - GitHub Accelerating

Created by : Mr Dk.

2019 / 05 / 29 10:07

Nanjing, Jiangsu, China

---

记录加速 GitHub 访问的几种方式。

GitHub 真的是让人又爱又恨。爱它在于它真的是一个宝藏网站，也是 IT 人士的身份名片；恨它在于受限于网络环境，和它打交道真是太痛苦了。我们总在不停探索与 GFW 和国内 ISP 斗智斗勇的方法。

## Web Page

GitHub 不在 PAC 列表中。如果代理速度够快的话，可以手动将 GitHub 添加到 PAC 列表中。

## DNS Configuration

GitHub 速度慢的另一个原因是受到了国内 DNS 污染。可以到专门的域名解析网站，解析以下三个域名，并将这三个域名的 IP 地址配置到操作系统的 DNS 表中。这样就可以绕过 DNS 服务器，通过本地的 DNS 解析直接访问相应的 IP 地址。

> 目前来看用处不大了。

```
github.com
github.global.ssl.fastly.net
assets-cdn.github.com
```

在 [域名解析网站](https://www.ipaddress.com/) 中，分别查询这三个域名的 IP 地址：

- github.com
- github.global.ssl.fastly.net
- assets-cdn.github.com

### Windows

打开 `C:\Windows\System32\drivers\etc\hosts` （管理员权限）

在最后加上刚才查询到的 IP 地址

注意事项：

1. `#` 用于注释
2. 每条记录单独一行
3. IP 地址在第一列，域名在第二列

```
# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

# localhost name resolution is handled within DNS itself.
#	127.0.0.1       localhost
#	::1             localhost

# Github
151.101.185.194 github.global.ssl.fastly.net
192.30.253.112 github.com
192.30.253.113 github.com
185.199.108.153 assets-cdn.github.com
185.199.109.153 assets-cdn.github.com
185.199.110.153 assets-cdn.github.com
185.199.111.153 assets-cdn.github.com
```

添加完成后，保存文件，刷新 DNS 缓存使之生效：

```powershell
ipconfig /flushdns
```

## Git Configuration

Git 也支持代理，不管是 _SSH_ 方式还是 _HTTPS_ 方式。具体方式参考 [另一篇文章](../Git/Git%20Proxy.md)。

## Repository

想要把整个仓库 clone 下来，却发现速度太慢。国内的 [Gitee](https://gitee.com/) 网站提供了一个很好的功能：**仓库导入**。在 Gitee 中新建一个仓库，并给出 GitHub 对应仓库的链接，点击创建。大约需要几分钟时间，Gitee 就会把 GitHub 上的仓库原封不动地导入到 Gitee 上，成为一个类似镜像的 Gitee 仓库。然后从 Gitee 上 `git clone`，就是国内的网速了。

另外，Gitee 的页面上有个刷新键，可以随时从 GitHub 的仓库同步。

## File Downloading

在 GitHub 上，某些项目的 release 中会带有一些已经编译好的可执行文件。如果想下载这些文件，GitHub 会重定向到 AWS 上进行下载，速度极慢。

[GitHub Proxy](https://ghproxy.com/) 提供 release、archive 等文件下载的加速服务。🤞
