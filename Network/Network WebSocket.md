# Network - WebSocket

Created by : Mr Dk.

2019 / 04 / 29 0:05

Nanjing, Jiangsu, China

---

## What

__WebSocket__ 是一种在单个 TCP 连接上进行的 __全双工__ 通信协议

于 2011 年被 IETF (Internet Engineering Task Force) 制定为 RFC 6455 标准，并由 RFC 7936 补充

__WebSocket__ 中，浏览器和服务器只需要完成一次握手

两者之间就可以创建持久性的连接

并进行双向数据传输

最重要的是，允许服务端向客户端推送数据

---

## Why

WebSocket 需要客户端和服务端同时支持

WebSocket 是 HTML5 中的协议

* 但和 HTML 本身没有关系
* 就好比可以用 HTTP 传输非 HTML 格式的数据

WebSocket 是一个新的应用层协议，与 HTTP 有一点交集，但：

* HTTP 是非持久协议
* WebSocket 是持久协议

HTTP 的生命周期由 HTTP Request 界定

* 一个 Request 对应一个 Response
* 且 Response 是被动的，不能主动发起

WebSocket 借用 HTTP 协议来完成初始的握手

* 客户端和服务端握手完成，并都开始使用 WebSocket 模式
* 双方可以开始进行全双工通信
* 服务端可以主动发起与客户端的通信

---

## How

WebSocket 首先会借用 HTTP 完成初始握手

客户端发送：

```
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
Origin: http://example.com
```

对比传统的 HTTP 协议，多出了一些信息：

```
Upgrade: websocket
Connection: Upgrade
```

作用是告诉服务器，通信协议升级为 WebSocket

```
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
```

* `Sec-WebSocket-Key` 由浏览器随机生成，用于验证身份
* `Sec-WebSocket-Protocol` 是用户定义的字符串，区分不同服务所需要的协议
* `Sec-WebSocket-Version` 在 WebSocket 标准化之前不统一，标准化后，统一使用 `13`

服务端返回：

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
Sec-WebSocket-Protocol: chat
```

同样，服务端返回同意升级协议：

```
Upgrade: websocket
Connection: Upgrade
```

```
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
Sec-WebSocket-Protocol: chat
```

* `Sec-WebSocket-Accept` 是经过服务器确认，并经过加密后的 `Sec-WebSocket-Key`
* `Sec-WebSocket-Protocol` 是服务器最终使用的协议

---

## Compare

与目前已有的一些信息传递机制：

### AJAX 轮询

客户端每隔几秒发送一次请求

询问服务器是否有新信息

存在问题：

* 客户端需要不断向服务端发送请求
* HTTP 请求中包含较长的头部，真正有效的部分很少
* 浪费带宽，信息交换效率低下

__需要服务端有较高的处理效率，较多的资源__

### Long Poll

也是轮询的方式，但是采取 __阻塞__ 策略

客户端发起连接后，如果没有消息

服务端就一直不发送 Response，直到有消息

存在问题：

* 服务端需要同时维护很多个阻塞的长连接

__需要服务端有较高的并发能力（同时接待客户）__

且存在共同的问题：

* 客户端不断建立 HTTP 连接，被动等待服务端处理

### WebSocket

整个连接只需要一次 HTTP 握手

通讯过程中不需要重复传输身份鉴别信息

服务端一直保持连接状态信息，直到连接被释放

* 由 `ping/pong` 帧维持连接状态

---

## Summary

听别人说过这个东西

一开始还以为是传输层的协议

没想到是一个听起来挺好用的应用层协议

了解原理后，最直观的应用场景就是聊天室了：

服务端主动推送别人发的新信息给客户端

但是对于它为何能够提高服务器的处理效率

还是不是特别有概念

维持状态信息也需要资源啊

只是握手过程简单了许多

因此当服务端与客户端握手

并记录了所有的客户端信息，维护长连接后

就不会再有各个客户端频繁且无用的 HTTP 请求了

---

