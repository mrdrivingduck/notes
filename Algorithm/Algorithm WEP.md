# Algorithm - WEP

Created by : Mr Dk.

2018 / 11 / 26 13:40

Nanjing, Jiangsu, China

---

### Concept

__有线等效加密__（_Wired Equivalent Privacy_，__WEP__）

又称 __无线加密协议__（_Wireless Encryption Protocol_，__WEP__）

是用于保护无线网络信息安全的一种体制

是 _IEEE 802.11_ 标准的一部分

* 使用 _RC4_ 加密技术保证 __机密性__
* 使用 _CRC-32_ 校验技术保证 __完整性__

### Theory

#### Encryption

使用一个 24-bit 的初始化向量 _IV_

* 将 _IV_ 与密码一起作为 _RC4_ 的密钥

* 将数据与其 _CRC-32_ 校验作为明文

* 将明文用密钥加密得到密文

将 _IV_ 与密文一起发送

![wep-encryption](../img/wep-encryption.png)

#### Decryption

得到 _IV_ 与密文

* 将提取出的 _IV_ 与密码一起作为 _RC4_ 的密钥
* 用密钥将密文解密为明文
* 从明文中提取出数据和 _CRC-32_ 校验

将数据进行 _CRC-32_ 校验，并与提取出的校验和进行比较

如果校验和相同，则接收端接收到了原始数据

![wep-decryption](../img/wep-decryption.png)

---

### Summary

这是一个最简单的无线网络安全算法

现在已经被人破解腻了

已经过时很久

被 _WPA_ / _WPA2_ 给取代

---

