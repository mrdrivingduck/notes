# Wireless - WPA2

Created by : Mr Dk.

2018 / 12 / 03 20:17

Nanjing, Jiangsu, China

---

### Concept

_WPA2_ 是完整的 _IEEE 802.11i_ 标准认证形式

经过了 _Wi-Fi_ 联盟的验证

### Version

* _WPA2-Enterprise_ - 企业版

  * 使用 _IEEE 802.1X_ 认证服务器向各终端用户 __分发不同的密钥__

* _WPA2-Personal_ - 个人版

  * 使用预先设定好的密钥 _PSK (pre-shared key)_
  * 同一无线路由器下所有终端都使用该密钥

### Theory

在工作过程上与 _WPA_ 基本相同，改进的地方如下：

引入了 _CCMP (Counter Mode Cipher Block Chaining Message Authentication Code Protocol)_ 协议

* 使用该协议的 _CTR mode_ 保证数据机密性（_AES_ 算法）
* 使用该协议的 _CBC-MAC_ 消息认证码保证数据的完整性及其验证

### WPA3

于 _2018 年 6 月 25 日_ 正式发布

---

### Summary

从 _WEP_ 到 _WPA_ 再到 _WPA2_ 是一个循序渐进的过程

---

