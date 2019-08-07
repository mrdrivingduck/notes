# Cryptography - RC4

Created by : Mr Dk.

2018 / 11 / 26 12:56

Nanjing, Jiangsu, China

---

## Concept

_RC4（Rivest Cipher 4）_ 是一种流加密算法

* 密钥长度可变
* 对称加密
* 曾在 _SSL / TLS_ 、 _WEP_ 、 _WPA_ 等算法中被使用

## Theory

### 初始化算法 KSA（Key-Scheduling Algorithm）

初始化一个固定长度的 _S-box_

将互不重复的元素装入 _S-box_

根据任意长度（1-255）的密钥打乱 _S-box_

### 伪随机子密码生成算法 PRGA（Pseudo-Random Generation Algorithm）

每收到一个字节，就通过算法定位 _S-box_ 中的一个元素

将该元素与输入字节 __异或（xor）__

* 如果输入字节是明文，则异或后得到密文
* 如果输入字节是密文，则异或后得到明文

该过程中 _S-box_ 会发生改变

---

## Summary

对密码学不是太懂

这个算法确实算是比较简单的了

但是到了现在已经过时了

---

