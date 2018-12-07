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

