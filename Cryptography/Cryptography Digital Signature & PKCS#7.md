# Cryptography - Digital Signature & PKCS #7

Created by : Mr Dk.

2020 / 05 / 03 01:19

Ningbo, Zhejiang, China

---

## Digital Signature

**数字签名** 用于认证数字信息，对象可以是文本文件、可执行文件、文档等。数字签名基于非对称加密体制，需要一对公私钥的参与。

**数字证书** 是一种电子文档，用于证明 **公钥** 的归属权。其中包含了公钥本身、公钥所有者的身份信息、以及相关的权限。数字证书目前的标准为 RFC 5280 中定义的 X.509 标准。

数字签名的使用场景：

1. 发送方/源地址的认证 (因为只有发送方才持有用于签名的私钥)
2. 保障信息完整性 (不可篡改)
3. 不可抵赖性

## Process

### Key Generation

数字签名与验证需要一对 key pair (公钥 + 私钥)

### Digital Signature Generation

使用安全的 hash 算法，如 *SHA-256* / *SHA-384* / *SHA-512* 计算输入文件或信息的 hash，即 **摘要**。计算出的 hash 被私钥加密，并与被签名的文件一起被发送给接收方进行认证。

### Digital Signature Verification

接收方使用相同的 hash 算法对接受到的文件或数据计算 hash，然后使用发送方的公钥解密签名。如果解密后的签名和计算得到的 hash 完全相同，则意味着数据在传输过程中没有被篡改。

## PKCS \#7 Standard

PKCS (Public Key Cryptography Standards) \#7 被命名为 CMS (Cryptographic Message Syntax Standard)，是 *RSA* 公司提出的最著名的标准。这一标准也是 S/MIME (Secure/Multipurpose Internet Mail Extensions) 的基础。

PKCS \#7 提供了一种用途广泛的创建数字签名的语法和格式。其中，包含了六种类型的数据：

* Data
* Signed Data
* Enveloped Data
* Signed-and-enveloped Data
* Digested Data
* Encrypted Data

这个标准支持对不具备存放签名结构的格式也适用。比如，对于 PDF 文件来说，其结构中有专门用于存储签名的位置；而对于一个普通文本来说，并没有专门存储签名的结构。PKCS \#7 包含了 attached 和 detached 格式：

* Attached 格式中，被签名的数据被内嵌在签名中
* Detached 格式中，被签名的数据与签名分开存放

另外，还有两种类型的签名数据：

* Independent Signatures - 所有的签名者对同样的数据进行签名
* Counter Signatures - 后一个签名者对前一个签名者的签名进行签名

在签名数据中包含的信息：

1. 产生签名的 hash 算法
2. Detached / Attached 格式
3. 签名证书
4. 签名者信息
5. 证书签发者信息
6. 认证属性信息 (类型、数据、签名时间、消息摘要)，也是签名计算的一部分
7. 加密算法
8. 签名值

## References

https://www.cryptomathic.com/news-events/blog/introduction-to-digital-signatures-and-pkcs-7

http://www.pkiglobe.org/pkcs7.html

---

