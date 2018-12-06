# Wireless - KRACK

Created by : Mr Dk.

2018 / 12 / 06 11:02

Nanjing, Jiangsu, China

---

### About

_KRACK_ - _Key Reinstallation Attack_

Breaking _WPA2_ by forcing nonce reuse

Discovered by _Mathy Vanhoef_ of _imec-DistriNet, KU Leuven, 2017_

https://www.krackattacks.com/

![krack-logo](../img/krack-logo.png)

### Keys

四次握手的双向认证基于 _Pairwise Master Key (PMK)_

* 在个人网络中，_PMK_ 来源于 _PSK (Pre-Shared Key)_
* 在企业网络中，_PMK_ 来源于 _802.1X_ 协议协商出的密钥

用 _PMK_ 在双方分别生成 _PTK (Pairwise Transient Key)_

* Client is called __supplicant__
* AP is called __authenticator__

_PTK_ 的生成需要：

* _PMK_
* _ANonce_
* _SNonce_
* _A-MAC_
* _S-MAC_

_PTK_ 的组成：

* _Key Confirmation Key (KCK)_
* _Key Encryption Key (KEK)_
* _Temporal Key (TK)_

### EAPOL

四次握手使用 _EAPOL_ 协议帧

![krack-eapol](../img/krack-eapol.png)

_Replay Counter_ - 用于检测重发次数

* _Authenticator_ 在传输一帧后将 _replay counter_ 增加
* _Supplicant_ 回复 _EAPOL_ 数据帧时使用和想要回复的消息的 _replay counter_

_Nonce_ - 用于存储密钥协商的随机数

_Receive Sequence Counter (RSC)_ - 第一个包含 _GTK_ 的数据包编号

_Key Data_ - 用于传输 _GTK_

* 在 _WPA2_ 协议中，_GTK (Group Temporal Key)_ 在第三次握手时被传送
* 在 _WPA_ 协议中，_GTK_ 在四次握手结束之后被安装
* _GTK_ 本身被 _KEK_ 加密

_Message Integrity Check (MIC)_

* 数据帧的可靠性由 _KCK_ 保证

### WPA/WPA2 4 - Way Handshake

![krack-handshake](../img/krack-handshake.png)

* _Msg1 - Authenticator &rarr; Supplicant_
  * 传递 _Authenticator_ 生成的 _ANonce_ 及其 _MAC_ 地址
* _Msg2 - Supplicant &rarr; Authenticator_
  * 此时 _Supplicant_ 已经具备生成 _PTK_ 的全部条件 - 计算 _PTK_
  * 传递 _Supplicant_ 生成的 _SNonce_ 及其 _MAC_ 地址
* _Msg3 - Authenticator &rarr; Supplicant_
  * 此时 _Authenticator_ 已经具备生成 _PTK_ 的全部条件 - 计算 _PTK_
  * 要求 _Supplicant_ 安装密钥
  * _WPA2_ 协议中还会向 _Supplicant_ 发送 _GTK_
  * 注意：_Replay Counter_ 增加了一次
* _Msg4 - Supplicant &rarr; Authenticator_
  * 确认安装成功

### KRACK

攻击者作为 __中间人__

* 拦截 _Msg4_，使 _Authenticator_ 收不到 _Msg4_，以为 _Supplicant_ 没有收到 _Msg3_

* _Authenticator_ 会重发 _Msg3_ 要求 _supplicant_ 重装已在使用的 _PTK_

* 重装 _PTK_ 会导致 _nonce_ 的复位
  * 对于每一个数据包，在正常情况下，_nonce_ 一直在改变，导致每次加密的密钥都不相同

攻击成因：

* _PTK_ 不变（重装）
* _Nonce_ 复位后，相当于被重用
* 导致加密数据的密钥流（_PTK + Nonce_）重现了

由于 _Supplicant_ 在发出 _Msg4_ 后就认为 _PTK_ 已经安装完毕了

无法察觉到中间人的存在

中间人可以采用该密钥获取 _Supplicant_ 发送的密文信息

---

### Summary

更多细节准备阅读论文

由 _KRACK_ 的发现者发表在 _CCS 2017_ 上

另外 _kismet_ 中已经实现了检测 _KRACK_ 攻击的代码

但是由于没有实施 _KRACK_ 攻击的工具

有效性无从验证

---

