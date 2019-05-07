# Wireless - WPA

Created by : Mr Dk.

2018 / 12 / 03 19:31

Nanjing, Jiangsu, China

---

## Concept

_WPA_ 全名为 _Wi-Fi Protected Access_，即 “_Wi-Fi_ 访问保护”

是 _IEEE 802.11i_ 标准完备之前替代 _WEP_ 的过渡方案

实现了 __部分__ _IEEE 802.11i_ 标准

---

## Version

* _WPA-Enterprise_ - 企业版

  * 使用 _IEEE 802.1X_ 认证服务器向各终端用户 __分发不同的密钥__
  * 协议涉及三部分：
    * 申请者 - 需要连接到 _LAN_ / _WAN_ 的客户端设备
    * 验证者 - 网络设备，_Switch_ 或 _AP_
    * 验证服务器 - 运行着支持 _EAP_ 和 _RADIUS_ 协议的主机
  * 申请者不允许通过验证者访问受保护一侧的网络，直到申请者的身份被验证和授权
  * 申请者向验证者提供凭据 - 用户名/密码 或 数字证书
  * 验证者将凭据转发给验证服务器进行验证
  * 若验证服务器认为凭据有效，则申请者被允许访问受保护网络的资源

  ![802.1X](../img/802.1X.png)

* _WPA-Personal_ - 个人版

  * 使用预先设定好的密钥 _PSK (pre-shared key)_
  * 同一无线路由器下所有终端都使用该密钥

---

## Theory

### Encryption

_WPA_ 协议使用 _128_ 位密钥和 _48_ 位的初始化向量（_IV_），以及 _RC4_ 算法进行加密

* _WEP_ 协议直接将密钥和 _IV_ 连接，作为 _RC4_ 算法的密钥 - _Related-key attack_
* _WPA_ 中使用动态改变密钥的 “临时密钥完整性协议” _Temporal Key Integrity Protocol, TKIP_
  * 密钥混合功能 - 密钥和 _IV_ 不再是简单连接
  * 使用序列计数器 _Sequence Counter_ 用于防御重放攻击 _Replay Attacks_ - 数据包顺序不匹配时自动拒收
  * 使用 _64_ 位的信息完整性代码 _Message Integrity Check, MIC_ 防止假包或数据包篡改

### Integrity

除了认证和加密外，_WPA_ 对所载数据的完整性检查也提供了巨大的改进

* _WEP_ 使用 _CRC_ 循环冗余校验，容易在不知道 _WEP_ 密钥的情况下被篡改数据和 _CRC_
* _WPA_ 中使用了 _MIC_，配合帧计数器，以避免重放攻击

---

## Status

支持 _WEP_ 协议的设备硬件可以直接支持 _WPA_

* _WEP_ 和 _WPA_ 在底层使用了同样的 _RC4_ 算法加密
* _MIC_ 算法是大多数旧网卡能使用的条件下找到的最强的算法

安全性提升：

* 加长的密钥和 _IV_
* 减少和密钥相关的数据包个数
* 新的消息完整性验证机制

---

## Summary

安全性比 _WEP_ 略强一些

---

