# Network - SSL/TLS

Created by : Mr Dk.

2018 / 11 / 05 14:20

Nanjing, Jiangsu, China

---

## Concept

_SSL (Secure Sockets Layer)_ 及其继任者 _TLS (Transport Layer Security)_ 是一种安全协议

由 _Netscape_ 公司开发，目的是为互联网通信提供安全及数据完整性保障

## Features

* 工作在网络协议栈的 __传输层__ 之上
* 与高层的 __应用层__ 协议无耦合，应用层协议能透明地运行在 _TLS_ 协议上

  * _HTTP_ &rarr; _HTTPS_ (_HTTP over TLS / HTTP over SSL / HTTP Secure_)

    ![https](../img/https.png)

  * _FTP_ &rarr; _FTPS_

  * ...

## History

_SSL_ 由 _Taher Elgamal_ 编写基础算法，历史版本 _1.0_、_2.0_、_3.0_

2014 年 10 月，_Google_ 发现 _SSL 3.0_ 存在设计缺陷，建议禁用此协议

_ITEF（互联网工程任务组，Internet Engineering Task Force）_ 将 _SSL_ 标准化，称其为 _TLS_

## Theory

* Asymmetric Encryption
* Symmetric Encryption
* SSL/TLS Certificate

![ssl/tls](../img/ssl.png)

协议执行过程：

1. 客户端向服务器发起 _SSL_ 请求
2. 服务器向客户端发送 _SSL_ 证书副本，其中包含了服务器公钥
3. 客户端检验证书是否由信任的 _CA_ 组织发布，是否有效；如果客户端信任该证书，则产生一个对称会话密钥，并用服务器公钥加密后发送给服务器
4. 服务器用私钥解密对称会话密钥，返回一个用对称会话密钥加密的确认信息到客户端，开始加密对话
5. 客户端和服务器使用会话密钥全程加密对话

## Implementation

Not yet.

---

## Summary

搞清楚了 _数字证书_ 的机制以后

这个协议就变得非常简单了

一年里不知道有几次想弄明白这个东西

但是每次都半途而废了

今天终于算是弄明白了

毕竟身处网络安全实验室

这点知识还是一定要了解的

---

