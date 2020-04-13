# Network - frp

Created by : Mr Dk.

2019 / 06 / 13 14:30

Nanjing, Jiangsu, China

---

## About

[*frp*](https://github.com/fatedier/frp) 是一款开源的内网穿透工具，由 Go 语言实现，可在多种平台上运行。

作用：使外网设备能够访问内网环境中的服务。比如，通过外网 SSH 或远程登录到内网主机

---

## Architecture

需要一台具有公网 IP 地址的服务器，以及若干台内网主机。

![frp-architecture](../img/frp-architecture.png)

总体上是 C-S 架构

* 在具有公网 IP 地址的服务器上运行服务端
  * 监听一个指定的端口，用于接收内网客户端的穿透请求
  * 在公网服务器上开放客户端指定的端口，用于穿透
* 在内网运行客户端
  * 指定远程服务端的 IP 地址和端口号，连接到远程服务器
  * 设定本机的开放端口和远程服务器上的相应穿透端口

> e.g.
>
> frp 服务端运行于公网服务器的 12666 端口
>
> 内网主机的 frp 客户端连接到公网服务器的 12666 端口上
>
> 内网 frp 客户端希望将内网本地的 80 端口通过公网服务器的 13000 端口穿透出去
>
> 这样，所有用户都能够通过访问公网服务器的 13000 端口
>
> 间接访问内网主机的 80 端口
>
> 从而实现了穿透

---

## Usage

在 [GitHub Release](https://github.com/fatedier/frp/releases) 上下载对应操作系统、体系结构的程序：

* `frps` - 服务端程序
* `frps.ini` - 服务端配置文件
* `frpc` - 客户端程序
* `frps.ini` - 客户端配置文件

### Server

在 `frps.ini` 中配置服务端绑定端口：

```ini
# frps.ini
[common]
bind_port = 12666
```

然后启动服务端程序：

```bash
$ ./frps -c ./frps.ini
```

该服务端程序会阻塞命令行，所以可以使其在后台运行，将输出重定向到了 log 文件中：

```bash
$ ./frps -c ./frps.ini > log &
```

可以通过 `tail` 命令查看最新的 log：

```bash
$ tail log
```

### Client

在 `frpc.ini` 中配置远程服务器信息，以及想要穿透的端口。假设公网服务器的 IP 地址为 `x.x.x.x` ：

```ini
# frpc.ini
[common]
server_addr = x.x.x.x
server_port = 12666

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 13000
```

将本机的 `22` (SSH) 端口通过远程服务器的 `13000` 端口穿透出去。这样任意地址访问公网服务器的 `13000` 端口就相当于访问内网机器的 `22` 端口了。

启动客户端：

```bash
$ ./frpc -c ./frpc.ini
```

---

## Function

更多高级的功能暂时用不到，我的需求是：把我的那台厚重但性能强劲的笔记本接入实验室内网，使我可以在任何地方用苏菲远程连接到它，干一些比较吃性能的活。

如果笔记本跑 Linux，可以通过 SSH 连接：

```ini
# frpc.ini
[common]
server_addr = x.x.x.x
server_port = 12666

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 13000
```

如果笔记本跑 Windows，可以通过 Windows 的远程桌面连接：

* 前提是要在设置中开启允许被远程连接

```ini
# frpc.ini
[common]
server_addr = x.x.x.x
server_port = 12666

[remote]
type = tcp
local_ip = 127.0.0.1
local_port = 3389
remote_port = 13000
```

`3389` 是 Windows 远程桌面的默认端口。将 `3389` 端口通过公网的 `13000` 端口实现穿透。

由于 SSH 和远程桌面的流量都需要经过公网服务器，所以连接到公网服务器的延迟决定了一部分的服务质量。一开始我使用了用于科学上网的美国 Hostwinds 服务器，延迟高得令人发指。后来改用了使用阿里云的国内服务器，延迟情况好了很多。

---

## Summary

*frp* 这个项目好像还是中国人开发的呢~中国开发者给力！ 😎

---

