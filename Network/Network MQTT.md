# Network - MQTT

Created by : Mr Dk.

2019 / 06 / 19 15:42

Nanjing, Jiangsu, China

---

## About

__MQTT (Message Queuing Telemetry Transport)__ - 消息队列遥测传输

An ISO standard (ISO/IEC PRF 20922) publish-subscribe-based messaging protocol.

* Works on top of the TCP/IP protocol

为远程设备及网络糟糕状况下设计的消息协议

Andy Stanford-Clark of IBM and Arlen Nipper of Cirrus Link authored the first version of the protocol in 1999.

以下笔记基于标准文档 __MQTT Version 3.1.1, 29 October 2014__

---

## Terminology

### Network Connection

MQTT 底层使用传输层协议作为支持

* 连接客户端和服务器
* 提供有序、无损的双向字节流传输

### Application Message

由 MQTT 协议传输的应用数据

* 与一个 Quality of Service 和一个 Topic Name 相关联

### Client

使用 MQTT 协议的客户端程序

总是由客户端建立与服务器之间的连接

* 发布 (publish) 其它客户端感兴趣的应用信息
* 订阅 (subscribe) 感兴趣的应用信息
* 取消订阅不再感兴趣的应用信息
* 与服务器断开连接

### Server

作为客户端之间的消息中间件程序

* 接受客户端的网络连接
* 接受客户端发布的应用数据信息
* 处理客户端发送的订阅、取消订阅请求
* 向匹配的客户端订阅发送应用数据

### Subscription

一个订阅包含：

* Topic Filter
* Maximum QoS

一个订阅仅和一个会话相关联

一个会话可以包含多个订阅

一个会话内的每个订阅都有一个不同的 Topic Filter

### Topic Name

与应用信息相关联的 label

由服务器对订阅信息进行匹配

并将应用信息的拷贝发送到所有匹配订阅的客户端

### Topic Filter

订阅中的表达式

用于指示一个或多个主题中感兴趣的那个

Topic Filter 可以包含通配符

### Session

客户端和服务器之间的有状态的交互信息

### MQTT Control Packet

带有信息的控制报文

MQTT 标准规定了 __14__ 种控制报文

---

## MQTT Control Packet Format

### Structure

* Fixed header - in all MQTT Control Packets
* Variable header - in some MQTT Control Packets
* Payload - in some MQTT Control Packets

#### Fixed Header

Byte 0

* bit 7-4 - MQTT Control Packet Type
* bit 3-0 - Flags specific to each MQTT Control Packet Type

Byte 1

* Remaining Length

---

## MQTT Control Packets

### CONNECT

客户端向服务器请求连接

> 在客户端和服务器的网络连接建立后
>
> 从客户端发往服务器的第一个报文 __必须__ 是 CONNECT

在一个网络连接中，CONNECT 只能被发送一次

服务器必须将收到的第二个 CONNECT 视为违反协议并中断连接

在 Variable 的 flag 中选择 payload 中是否出现：

* Will Topic
* Will Message
* User Name
* Password

在 payload 中必须出现唯一的客户端 identifier

#### Clean Session

指定了处理会话的状态

客户端和服务器可以保存会话状态

* 如果 CleanSession 设定为 `0`
  * 服务器必须根据客户端 identifier 恢复之前的会话状态
  * 如果之前没有会话状态，服务器必须创建一个新的会话
  * 客户端和服务器必须在双方断开连接后保存会话
  * 服务器在断开连接后还需要接收 `QoS 1` 和 `QoS 2`
* 如果 CleanSession 设定为 `1`
  * 客户端和服务器必须丢弃之前的任何会话，并建立新会话

#### Keep Alive

以秒为单位的时间间隔

* 由客户端负责控制报文的发送间隔不超过 keep-alive 值
* 如果没有其它控制报文，客户端必须发送 PINGREQ 报文用于 keep-alive
* 客户端可以在任意时间发送 PINGREQ，通过 PINGRESP 决定网络和服务器是否正常

如果 Keep Alive 非 0，且服务器在时间间隔内没有收到客户端的控制报文

* 则认为网络错误，主动与客户端断开连接

如果客户端在一定时间内没有收到 PINGRESP，则应当关闭与服务器的连接

#### Client Identifier

用于使服务器识别客户端

* 必须在 CONNECT 的 payload 的第一个 field 中
* zero-byte ClientId

### CONNACK

服务器向客户端确认连接

必须是服务器向客户端发送的第一个报文

#### Session Present

#### Connect Return Code

| Value       | Return Code Response                              |
| ----------- | ------------------------------------------------- |
| 0x00        | Connection Accepted                               |
| 0x01        | Connection Refused, unacceptable protocol version |
| 0x02        | Connection Refused, identifier rejected           |
| 0x03        | Connection Refused, server unavilable             |
| 0x04        | Connection Refused, bad user name or password     |
| 0x05        | Connection Refused, not authorized                |
| 0x06 - 0xFF | Reserved for future use                           |

### PUBLISH

用于在客户端与服务器之间传输 Application Message

#### DUP

* `0` - 表示这是服务器与客户端之间第一次试图传递该信息
* `1` - 表示这是一次重传

#### QoS

| QoS value | Description                 |
| --------- | --------------------------- |
| 0x00      | At most once delivery       |
| 0x01      | At least once delivery      |
| 0x02      | Exactly once delivery       |
| -         | Reserved - must not be used |

#### RETAIN

服务器是否保存 Application Message

#### Topic Name

UTF-8 编码的字符串

必须出现在 PUBLISH 的 variable 头部的第一个 field 中

#### Packet Identifier

### PUBACK - Publish Acknowledgement

用于回复 QoS 等级为 1 的 PUBLISH

### PUBREC - Publish Received

用于回复 QoS 等级为 2 的 PUBLISH

是 QoS 2 协议交换的第二个包

### PUBREL - Publish Release

用于回复 QoS 等级为 2 的 PUBLISH

是 QoS 2 协议交换的第三个包

### PUBCOMP - Publish Complete

用于回复 QoS 等级为 2 的 PUBLISH

是 QoS 2 协议交换的第四个包

### SUBSCRIBE

用于从客户端向服务器订阅

客户端通过订阅在服务器注册其感兴趣的 topic，以获取 publish

在 payload 中包含 UFT-8 编码的字符串，作为 Topic Filter

* 其中可以包含通配符，但如果服务器不支持，需要拒绝带有通配符的连接

### SUBACK

用于从服务器向客户端确认 SUBSCRIBE 的接收和处理

### UNSUBSCRIBE

用于从客户端向服务器取消订阅

### UNSUNACK

用于从服务器向客户端确认 SNSUBSCRIBE 的接收

### PINGREQ

从客户端发送到服务器，向服务器表示客户端依旧存活

### PINGRESP

由服务器向客户端发送，表示服务器依旧存活

### DISCONNECT

由客户端向服务器发送的最后一个报文

表示客户端干净地断开连接

---

## Summary

更多高级特性暂时没看

关于实现，各种语言都提供了库：

<https://github.com/mqtt/mqtt.github.io/wiki/libraries>

今天发现之前的 Vert.x 库也提供了 MQTT 模块

<https://vertx.io/docs/vertx-mqtt/java/>

正在写个 demo 进行测试

---

