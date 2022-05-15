# Network - WebSocket

Created by : Mr Dk.

2019 / 04 / 29 0:05

Nanjing, Jiangsu, China

---

## What

_WebSocket_ 是一种在单个 TCP 连接上进行的 **全双工** 通信协议，于 2011 年被 IETF (Internet Engineering Task Force) 制定为 RFC 6455 标准，并由 RFC 7936 补充。_WebSocket_ 中，浏览器和服务器只需要完成一次握手，两者之间就可以创建持久性的连接，并进行双向数据传输。最重要的是，允许服务端向客户端推送数据。

---

## Why

WebSocket 需要客户端和服务端同时支持。WebSocket 是 HTML5 中的协议，但和 HTML 本身没有关系，就好比可以用 HTTP 传输非 HTML 格式的数据。WebSocket 是一个新的应用层协议，与 HTTP 有一点交集，但：

- HTTP 是非持久协议
- WebSocket 是持久协议

HTTP 的生命周期由 HTTP Request 界定，一个 Request 对应一个 Response，且 Response 是被动的，不能主动发起；WebSocket 借用 HTTP 协议来完成初始的握手：客户端和服务端握手完成，并都开始使用 WebSocket 模式。双方可以开始进行全双工通信，服务端可以主动发起与客户端的通信。

---

## How

WebSocket 首先会借用 HTTP 完成初始握手。客户端发送：

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

作用是告诉服务器，通信协议升级为 WebSocket。

```
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
```

- `Sec-WebSocket-Key` 由浏览器随机生成，用于验证身份
- `Sec-WebSocket-Protocol` 是用户定义的字符串，区分不同服务所需要的协议
- `Sec-WebSocket-Version` 在 WebSocket 标准化之前不统一，标准化后，统一使用 `13`

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

- `Sec-WebSocket-Accept` 是经过服务器确认，并经过加密后的 `Sec-WebSocket-Key`
- `Sec-WebSocket-Protocol` 是服务器最终使用的协议

---

## Compare

与目前已有的一些信息传递机制的比较：

### AJAX 轮询

客户端每隔几秒发送一次请求，询问服务器是否有新信息。存在问题：

- 客户端需要不断向服务端发送请求
- HTTP 请求中包含较长的头部，真正有效的部分很少
- 浪费带宽，信息交换效率低下
- 需要服务端有较高的处理效率，较多的资源

### Long Poll

也是轮询的方式，但是采取 **阻塞** 策略。客户端发起连接后，如果没有消息，服务端就一直不发送 Response，直到有消息。

存在问题：

- 服务端需要同时维护很多个阻塞的长连接
- 需要服务端有较高的并发能力 (同时接待客户)

且存在共同的问题：

- 客户端不断建立 HTTP 连接，被动等待服务端处理

### WebSocket

整个连接只需要一次 HTTP 握手，通讯过程中不需要重复传输身份鉴别信息。服务端一直保持连接状态信息，直到连接被释放。由 `ping/pong` 帧维持连接状态。

---
