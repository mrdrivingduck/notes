# Network - V2Ray

Created by : Mr Dk.

2019 / 05 / 09 0:28

Nanjing, Jiangsu, China

---

## About

> Project V 是一个工具集合，它可以帮助你打造专属的基础通信网络。Project V 的核心工具称为 __V2Ray__，其主要负责网络协议和功能的实现，与其它 Project V 通信。V2Ray 可以单独运行，也可以和其它工具配合，以提供简便的操作流程。

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

<https://www.v2ray.com/>

<https://github.com/v2ray/v2ray-core>

---

## VMess

__VMess__ 是 V2Ray 原创的加密通讯协议

* 基于 TCP，所有数据使用 TCP 传输
* 用户 ID —— UUID 作为令牌

---

## Server Configuration

可以在已有的 VPS 上直接配置 V2Ray Server

下载 V2Ray 的安装脚本：

```bash
$ wget https://install.direct/go.sh
```

下载完成后，可能需要修改脚本的权限：

```bash
$ sudo chmod 755 ./go.sh
```

执行安装脚本：

```bash
$ sudo ./go.sh
```

脚本会从 V2Ray 的官方仓库上下载并安装

* 重新执行安装脚本可以 __更新__

利用以下命令可以分别启动、停止、重启 V2Ray Server：

```bash
$ sudo systemctl start v2ray
$ sudo systemctl stop v2ray
$ sudo systemctl restart v2ray
```

安装完成后，配置文件位于 `/etc/v2ray/config.json`

若使用 VMess 协议，则基本不需要修改：

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

---

## Client Configuration

### Windows

从 <https://github.com/v2ray/v2ray-core/releases> 下载对应 OS 32/64 bit 的 V2Ray Core，解压

从 <https://github.com/2dust/v2rayN> 下载 v2rayN（图形界面），解压到上述目录

打开 GUI，进行服务器的配置（需要与 V2Ray Server 的配置匹配）

* IP Address
* port
* UUID
* alter ID
* 加密方式
* 传输协议（默认 TCP）
* 伪装类型（不清楚可保持默认）

接下来点击 `启用系统代理` 或 `Enable HTTP Proxy`

在 `系统代理模式` 或 `HTTP Proxy Mode` 中选择 `PAC 模式` / `PAC Mode`

（可能需要重启客户端服务后）即可 surfing the Internet scientifically

### macOS

从 https://github.com/Cenmrev/V2RayX 中下载 _V2RayX_

运行 V2RayX 后，在 `Configure…` 中配置好 VMess Server 的信息

运行 `PAC Mode`

### iOS

用 iPhone Safari 打开 <http://ice8.net/>

在个人设置的 `iTunes & App Store` 中，注销个人 Apple ID

使用网页上给定的 Apple ID 登录，切换到 App Store 美国区（中国区已下架类似功能 APP）

在 App Store 中搜索 __Shadowrocket__

由于该账号已购买过该 APP，再次下载不需付费

下载完成后，打开 Shadowrocket，确保安装成功

__退出该 Apple ID，登录回个人的 Apple ID__

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

又免费，功能又强大 🤙

### Others

其它 OS 暂时用不到，网上教程也很多

---

