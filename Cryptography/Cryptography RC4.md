# Cryptography - RC4

Created by : Mr Dk.

2018 / 11 / 26 12:56

Nanjing, Jiangsu, China

---

## Concept

*RC4 (Rivest Cipher 4)* 是一种流加密算法：

* 密钥长度可变
* 对称加密
* 曾在 *SSL/TLS* 、 *WEP* 、 *WPA* 等算法中被使用

## Theory

### 初始化算法 KSA（Key-Scheduling Algorithm）

初始化一个固定长度的 *S-box*，将互不重复的元素装入 *S-box*。根据任意长度（1-255）的密钥打乱 *S-box*。

### 伪随机子密码生成算法 PRGA（Pseudo-Random Generation Algorithm）

每收到一个字节，就通过算法定位 *S-box* 中的一个元素，将该元素与输入字节 **异或（xor）**：

* 如果输入字节是明文，则异或后得到密文
* 如果输入字节是密文，则异或后得到明文

该过程中 *S-box* 会发生改变。

---

