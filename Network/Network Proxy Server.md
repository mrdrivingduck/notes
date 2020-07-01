# Network - Proxy Server

Created by : Mr Dk.

2020 / 07 / 02 0:29

Nanjing, Jiangsu, China

---

## About

**代理 (Proxy)** 是一种特殊的网络服务，能够允许一台计算机通过该服务与另一台计算机实现非直接连接。代理的应用非常广泛，根据应用场景的不同，发展出了各式各样的代理服务。比如，最最基本的功能就是流量的转发，如果再配合上一定的转发规则，就能成为一个简易的防火墙。

代理在概念上可以被区分为 *正向代理 (Forward Proxy)* 和 *反向代理 (Reverse Proxy)*。

正向代理位于客户端与目标服务器之前。客户端向代理服务器发送请求，由代理服务器向目标服务器转发请求并将目标服务器的响应转发给客户端。正向代理实际上代理了客户端，与目标服务器进行交互。典型的应用就是 xxx。国内的客户端连接不到墙外的目标服务器，但可以通过一台能够访问目标服务器的代理完成访问。正向代理的几个用途：

* 作为中介，使客户端能够突破访问限制
* 代理服务器能够缓存目标服务器的部分响应信息，其它用户访问信息时，可以直接使用缓存而不再与目标服务器通信
* 目标服务器只知道代理服务器与其通信，从而隐藏了客户端 IP

反向代理也位于客户端与目标服务器之间。反向代理将客户端的请求转发到内网中的服务器上进行处理，并将处理结果返回给客户端。实际上是代理了目标服务器，与客户端通信。客户端只知道自己正与代理服务器通信，但不知道是哪个目标服务器为自己提供了服务。由此，服务器通过反向代理隐藏了自身的 IP 地址。反向代理的用途：

* 负载均衡，根据各个内网服务器的负载情况，将客户端请求转发到不同的目标服务器上
* 代理服务器缓存各个内网服务器上共同的静态内容，从而提高访问速度
* 作为 Web 攻击 (DoS/DDoS) 的防护

## Proxy Server

[*Nginx*](https://en.wikipedia.org/wiki/Nginx) (Engine X) 是一款非常有名的高性能 Web 服务器 / 负载均衡器 / 反向代理 (其实也可以作正向代理，不就是流量转发嘛...)。高性能的原因有：

1. 直接由 C 语言实现
2. 使用高性能多路复用模型 (如 EPOLL) 处理高并发
3. ...

在使用时，只需要在 `/etc/nginx/nginx.conf` 中进行配置即可：

* 作 Web server 时，配置静态资源的路径、监听的端口号
* 重定向、流量转发时，配置匹配 URL 的规则
* ...

[*Caddy*](https://caddyserver.com/) 是一款 Golang 实现的轻量级 Web server / 反向代理 / 负载均衡器 / API 网关 / ...，特性是默认自动将连接配置为 HTTPS。

## Application

前段时间在开发自己的 blog，通过访问 GitHub 的 GraphQL v4 API 获取 repo 里的一些内容。博客上线之后发现，GraphQL API 的 end point 在国内总是访问失败。正好手上有一台位于 Seoul 的服务器运行了 Caddy，于是决定配置一下试试。

目的很简单，原先用于访问 GitHub API 的 HTTP payload 不变，只将目标 URL 由 `api.github.com` 修改为 Seoul 服务器的 IP 地址。这样，HTTP request 就发送到了 Seoul 的服务器上。接下来，由 Seoul 服务器将接收到的流量转发到 `api.github.com` 上即可。HTTP 响应也经历相反的转发过程。Seoul 服务器在其中扮演正向代理的角色。

过程分为两步：

1. 修改网页代码中的目标 URL (这也太简单了)
2. 在 Seoul 服务器的 Caddy 上配置转发规则

对 Caddy 的配置，实际上是编辑 `/etc/caddy/` 下的 `Caddyfile`。以下是 Caddy 1 的配置，最近新出了 Caddy 2，配置方式应该有所改变。以 [proxy 的配置方式](https://caddyserver.com/v1/docs/proxy) 为例：

```
xxx.xxx.mrdrivingduck.cn {
    gzip
    timeouts none
    proxy / https://www.baidu.com {
        except /foolmeonce /blog/apiv4
    }
    proxy /foolmeonce 127.0.0.1:43666 {
        without /foolmeonce
        websocket
    }
    proxy /blog/apiv4 https://api.github.com/graphql {
        without /blog/apiv4
    }
}
```

首先，第一条规则中 `except` 的含义是过滤：除了 `/foolmeonce` 和 `/blog/apiv4` 的流量，其它流量全部转发到 xx (不好意思李总 😁)。

第二条规则中 `without` 的语义是，在转发前将 URL 前缀剪去，如 `/foolmeonce/api` without `/foolmeonce` == `/api`。也就是对于所有匹配 `/foolmeonce` 的 URL，将这一段前缀剪掉后，转发到 `127.0.0.1:43666`。

第三条规则类似，对于所有 `/blog/apiv4` 的请求，将请求 URL 前缀剪去后，发送到 GitHub API end point 上。

---

## References

[正向代理和反向代理详解](https://www.cnblogs.com/xuepei/p/10437114.html)

---

