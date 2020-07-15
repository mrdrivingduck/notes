# Network - V2Ray

Created by : Mr Dk.

2019 / 05 / 09 0:28

Nanjing, Jiangsu, China

---

## About

> Project V 是一个工具集合，它可以帮助你打造专属的基础通信网络。Project V 的核心工具称为 **V2Ray**，其主要负责网络协议和功能的实现，与其它 Project V 通信。V2Ray 可以单独运行，也可以和其它工具配合，以提供简便的操作流程。

V2Ray 支持以下协议：

- [Blackhole](https://www.v2ray.com/chapter_02/protocols/blackhole.html)
- [Dokodemo-door](https://www.v2ray.com/chapter_02/protocols/dokodemo.html)
- [Freedom](https://www.v2ray.com/chapter_02/protocols/freedom.html)
- [HTTP](https://www.v2ray.com/chapter_02/protocols/http.html)
- [MTProto](https://www.v2ray.com/chapter_02/protocols/mtproto.html)
- [Shadowsocks](https://www.v2ray.com/chapter_02/protocols/shadowsocks.html)
- [Socks](https://www.v2ray.com/chapter_02/protocols/socks.html)
- [VMess](https://www.v2ray.com/chapter_02/protocols/vmess.html)

Link:

* https://www.v2ray.com/
* https://github.com/v2ray/v2ray-core

---

## VMess

**VMess** 是 V2Ray 原创的加密通讯协议

* 基于 TCP，所有数据使用 TCP 传输
* 用户 ID —— UUID 作为令牌

---

## Server Configuration

可以在已有的 VPS 上直接配置 V2Ray Server。

下载 V2Ray 的安装脚本：

```console
$ wget https://install.direct/go.sh
```

下载完成后，可能需要修改脚本的权限：

```console
$ sudo chmod 755 ./go.sh
```

执行安装脚本：

```console
$ sudo ./go.sh
```

脚本会从 V2Ray 的官方仓库上下载并安装。重新执行安装脚本可以进行更新。利用以下命令可以分别启动、停止、重启 V2Ray Server：

```console
$ sudo systemctl start v2ray
$ sudo systemctl stop v2ray
$ sudo systemctl restart v2ray
```

安装完成后，配置文件位于 `/etc/v2ray/config.json`。若使用 VMess 协议，则基本不需要修改：

```json
{
  "inbounds": [{
    "port": 15875,
    "protocol": "vmess",
    "settings": {
      "clients": [
        {
          "id": "e2edb465-a814-4124-bb33-1fb4991194df",
          "level": 1,
          "alterId": 64
        }
      ]
    }
  }],
  "outbounds": [{
    "protocol": "freedom",
    "settings": {}
  },{
    "protocol": "blackhole",
    "settings": {},
    "tag": "blocked"
  }],
  "routing": {
    "rules": [
      {
        "type": "field",
        "ip": ["geoip:private"],
        "outboundTag": "blocked"
      }
    ]
  }
}
```

## Disguise

默认配置下，VMess 的转发流量是明文的，容易被 GFW 识别导致服务器 IP 地址被封禁。V2Ray 提供了流量伪装模式，在服务器上运行一个 Web server，并使用 TLS 对流量进行加密；在服务器端，再将 Web server 的流量发送到 V2Ray 的本地端口。以上配置通过 [最好用的 V2Ray 一键安装脚本 & 管理脚本](https://github.com/233boy/v2ray/tree/master) 进行验证并取得成功。

除了上述脚本，实现伪装需要以下额外需求：

* 一台境外服务器
* 一个域名

只要能满足上述需求，直接按照脚本傻瓜式安装即可。大致过程是在服务器上运行一个 Web server (如 [*Caddy*](https://caddyserver.com/))，并指定一个路由用于 V2Ray 的加密通信。使用域名到 [Let's Encrypt](https://letsencrypt.org/) 上申请一个 SSL/TLS 证书 - 这样，境内客户端与境外服务器之间的通信被伪装为 websocket，并由 TLS 进行加密。然后 *Caddy* 将指定路由上的流量转到 V2Ray 的端口。*Caddy* 的配置文件看起来是这样的：

```
<xxxdomain.cn> {
    gzip
timeouts none
    proxy / https://liyafly.com {
        except </routepath>
    }
    proxy </routepath> 127.0.0.1:32057 {
        without </routepath>
        websocket
    }
}
```

将所有除 `/routepath` 以外路由的流量全部转发到 `https://liyafly.com`，只将 `/routepath` 路由的流量转发到 V2Ray 的端口上。用于伪装的域名为 `xxxdomain.cn`，这个域名应该是在申请 SSL/TLS 证书的时候会被用到。

然后在服务器上同时启动 V2Ray 服务和 Caddy 服务即可。客户端软件可以直接扫描服务端生成的配置二维码进行自动配置。

## Client Configuration

### Windows

下载 [v2rayN-Core](https://github.com/2dust/v2rayN)（图形界面，且带有 V2Ray 核心程序），解压到上述目录.打开 GUI，进行服务器的配置（需要与 V2Ray Server 的配置匹配）：

* IP Address
* port
* UUID
* alter ID
* 加密方式
* 传输协议（默认 TCP）
* 伪装类型（不清楚可保持默认）

接下来点击 `启用系统代理` 或 `Enable HTTP Proxy`。在 `系统代理模式` 或 `HTTP Proxy Mode` 中选择 `PAC 模式` / `PAC Mode`（可能需要重启客户端服务后）即可。

### macOS

下载 [V2RayX](https://github.com/Cenmrev/V2RayX)

### iOS

得到一个美区 App Store 账户。在个人设置的 `iTunes & App Store` 中，注销个人 Apple ID，并使用网页上给定的 Apple ID 登录，切换到 App Store 美国区（中国区已下架类似功能 APP）。

在 App Store 中搜索 *Shadowrocket*，由于该账号已购买过该 APP，再次下载不需付费。下载完成后，打开 Shadowrocket，确保安装成功。然后退出该 Apple ID，登录回个人的 Apple ID。

在 Shadowrocket 中：

* 可以直接扫二维码 / URL 添加 Server 配置
* 也可以手动添加 Server 配置（需要与 Server 的配置相匹配）

Shadowrocket 支持的协议有：

* Shadowsocks
* ShadowsocksR
* VMess (暂不支持 KCP)
* Subscribe (用 URL 自动导入所有 Server 配置​)
* Socks5
* Socks5 Over TLS
* HTTP
* HTTPS
* Lua

### Linux (Ubuntu)

使用 [V2RayL](https://github.com/jiangxufeng/v2rayL)。

---

