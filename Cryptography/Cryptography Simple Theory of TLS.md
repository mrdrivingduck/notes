# Cryptography - Simple Theory of TLS

Created by : Mr Dk.

2018 / 11 / 05 13:08

Nanjing, Jiangsu, China

---

## Precondition

* Asymmetric & Symmetric encryption algorithm
* Digital signature
* Digital Digest (Finger Print)

## An evolution of a communication

### Round 1

client &rarr; server : Hello.

server &rarr; client : Hello, I'm server.

client &rarr; server : "......"

出现问题：

* 消息以明文的方式传输
* 黑客可以冒充服务器发出 "Hello, I'm server."，诱导客户端与自己通信，从而取得客户端的隐私信息

解决思路：引入非对称加密机制
* 由于只有服务器持有自己的 **私钥**
* 那么客户端只要用服务器的 **公钥** 解密，那么就可以保证通信对方是服务器

### Round 2

client &rarr; server : Hello.

server &rarr; client : Hello, I'm server. My **public key = xxx**.

client &rarr; server : Prove me u r server.

server &rarr; client : Hello, I'm server. { Hello, I'm server. }[ *RSA* 私钥加密 ] - `{}` 中表示密文，`[]` 中表示加密方式

client &rarr; server : { username = xxx, passwork = ***, money = ? }[ *RSA* 公钥加密 ]

server &rarr; client : { money = $$$ }[ *RSA* 私钥加密 ]

解决问题：

* 黑客由于没有服务器的 **私钥** ，因此无法冒充服务器

存在问题：

* 由于服务器的 **公钥** 是公开的，因此从服务器到客户端的通信是无法保密的
* 只要有服务器的 **公钥** 就可以解密内容
* 服务器也不可能用 **公钥** 进行加密，因为客户端没有 **私钥**

解决思路：引入对称加密机制

* 在可靠的单向通信中商定一个对称加密算法及其密钥

### Round 3

client &rarr; server : Hello.

server &rarr; client : Hello, I'm server. My **public key = xxx**.

client &rarr; server : Prove me u r server.

server &rarr; client : Hello, I'm server. { Hello, I'm server. }[ *RSA* 私钥加密 ]

**client generate a secret key with a symmetric encryption algorithm**

client &rarr; server : { Communicate with symmetric encryption. **Algorithm = xxx, key = xxx** }[ *RSA* 公钥加密 ]

server &rarr; client : { Roger. }[ 对称加密算法加密 ]

client &rarr; server : { username = xxx, passwork = ***, money = ? }[ 对称加密算法加密 ]

server &rarr; client : { money = $$$ }[ 对称加密算法加密 ]

解决问题：

* 由于 **对称加密算法和密钥** 由公钥加密，由于黑客没有私钥，因此无法破解
* 保证只有服务器知道用于此次会话中对称加密算法的密钥

通过 **非对称加密算法** (如 *RSA* )的掩护，服务器和客户端安全地商量了一个 **对称加密算法** 及其 **密钥**，保证了之后通信过程的安全。

存在问题：如何获取公钥，并判断公钥一定属于服务器？

* 将公钥放在互联网某个固定地址，客户端可以实现下载 - **不安全** - 该地址可以被伪造
* 每次开始通信前，服务器将公钥发送给客户端 - **不安全**
  * 任何人都可以产生密钥对
  * 黑客只需要产生一对密钥，然后向客户端发送公钥即可冒充服务器

问题根源：**无法确认公钥来源是否可靠**

解决思路：

* 引入 **数字证书**，包含内容：
  * 证书发布机构
  * 证书有效期
  * 公钥
  * 证书所有者
  * 签名及使用算法
  * 指纹及使用算法 (摘要)
* 假设前提：数字证书可保证数字证书中的 **公钥** 确实是证书所有者的

### 完整过程

* 客户端向服务器发送一个通信请求
* 服务器向客户端发送自己的数字证书，其中包含服务器 **公钥**
* 客户端生成对称加密算法密钥，用 **公钥** 加密后发送给服务器
  * 由于只有服务器有 **私钥** 用于解密，确保了这一过程的安全性
* 服务器与客户端使用对称加密算法通信

## Components of Certificate

* Issuer (证书发布机构)
  * 证书的创建者，不是使用者
  * CA 机构(Certificate Authority)
* Valid from & Valid to (证书有效期)
  * 过期作废
* Public key (公钥)
* Subject (证书所有者)
  * 这个证书是颁布给谁的
  * 某企业、某机构、某网址
* Signature algorithm (数字签名算法)
  * 利用证书里的公钥，使用该算法对指纹进行解密
* Thumbprint & Thumbprint algorithm (指纹及指纹算法)
  * 指纹被签名算法和 CA 机构私钥加密后，与证书放在一起
  * 保证证书的 **完整性** 与 **非篡改性**

## Procedure

CA 机构除了向别人发布证书外，也有自己的证书，用于解密其余证书的指纹。Microsoft© 等操作系统提供商会根据权威安全机构的评估选取一些信誉很好的 CA 机构，将这些 CA 机构的证书默认安装在操作系统内。

因此证书的内容如下：

* Issuer
* Subject
* Valid from
* Valid to
* Public key
* ...
* { 证书指纹及指纹算法(摘要 + 摘要算法) }[ *CA* 机构私钥加密 ] - 实际上是一个 **数字签名**

客户端得到证书后：

* 在操作系统中寻找对应 Issuer 的 CA 机构公钥
* 用 CA 机构的 **公钥** 解密证书的数字签名，得到证书指纹和指纹算法
* 使用指纹算法对证书进行计算，将得到的结果与解密的证书指纹进行对比
* 若指纹相同，则证书没有被篡改
* 那么证书中的 **Public key** 一定属于 **Subject** 中的公司，从而保证了公钥的来源是安全的

接下来，客户端使用证书中的公钥就可以去对应公司的服务器商定会话的对称加密算法和密钥了。

---

## Summary

整套数字证书机制如何保证安全性？

* 数字证书包括：证书本身 + 数字签名
* 数字签名由 CA 机构私钥加密，由操作系统提供的 CA 机构公钥解密，可保证证书的来源与安全性
* 证书中的公钥保证从 **客户端** 到 **服务器** 的单向通讯可靠
* 客户端可在单向通讯中与服务器商定用于对话的对称加密算法及其密钥
* 客户端与服务器商定的对称加密算法及其密钥保证 **客户端** 与 **服务器** 的对话可靠

---

