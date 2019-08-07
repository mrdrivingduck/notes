# Cryptography - Digital Certificate 数字证书

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

_client_ &rarr; _server_ : Hello.

_server_ &rarr; _client_ : Hello, I'm server.

_client_ &rarr; _server_ : "......"

出现问题：

* 消息以明文的方式传输
* 黑客可以冒充服务器发出 "Hello, I'm server."，诱导客户端与自己通信，从而取得客户端的隐私信息

解决思路：

* 引入非对称加密机制
* 由于只有服务器持有自己的 _私钥_
* 那么客户端只要用服务器的 _公钥_ 解密，那么就可以保证通信对方是服务器

### Round 2

_client_ &rarr; _server_ : Hello.

_server_ &rarr; _client_ : Hello, I'm server. My __public key = ***__.

_client_ &rarr; _server_ : Prove me u r server.

_server_ &rarr; _client_ : Hello, I'm server. { Hello, I'm server. }[ _RSA_ 私钥加密 ] - `{}` 中表示密文，`[]` 中表示加密方式

_client_ &rarr; _server_ : { username = xxx, passwork = ***, money = ? }[ _RSA_ 公钥加密 ]

_server_ &rarr; _client_ : { money = $$$ }[ _RSA_ 私钥加密 ]

解决问题：

* 黑客由于没有服务器的 _私钥_ ，因此无法冒充服务器

存在问题：

* 由于服务器的 _公钥_ 是公开的，因此从服务器到客户端的通信是无法保密的
* 只要有服务器的 _公钥_ 就可以解密内容
* 服务器也不可能用 _公钥_ 进行加密，因为客户端没有 _私钥_

解决思路：

* 引入对称加密机制
  * 在可靠的单向通信中商定一个对称加密算法及其密钥

### Round 3

_client_ &rarr; _server_ : Hello.

_server_ &rarr; _client_ : Hello, I'm server. My __public key = ***__.

_client_ &rarr; _server_ : Prove me u r server.

_server_ &rarr; _client_ : Hello, I'm server. { Hello, I'm server. }[ _RSA_ 私钥加密 ]

__client generate a secret key with a symmetric encryption algorithm__

_client_ &rarr; _server_ : { Communicate with symmetric encryption. __Algorithm = xxx, key = ***__ }[ _RSA_ 公钥加密 ]

_server_ &rarr; _client_ : { Roger. }[ 对称加密算法加密 ]

_client_ &rarr; _server_ : { username = xxx, passwork = ***, money = ? }[ 对称加密算法加密 ]

_server_ &rarr; _client_ : { money = $$$ }[ 对称加密算法加密 ]

解决问题：

* 由于 _对称加密算法和密钥_ 由公钥加密，由于黑客没有私钥，因此无法破解
* 保证只有服务器知道用于此次会话中对称加密算法的密钥

通过 __非对称加密算法__ （如 _RSA_ ）的掩护

服务器和客户端安全地商量了一个 __对称加密算法__ 及其 __密钥__，保证了之后通信过程的安全

存在问题：如何获取公钥，并判断公钥一定属于服务器？

* 将公钥放在互联网某个固定地址，客户端可以实现下载 - __不安全__
  * 该地址可以被伪造
* 每次开始通信前，服务器将公钥发送给客户端 - __不安全__
  * 任何人都可以产生密钥对
  * 黑客只需要产生一对密钥，然后向客户端发送公钥即可冒充服务器

问题根源：__无法确认公钥来源是否可靠__

解决思路：

* 引入 __数字证书__，包含内容：
  * 证书发布机构
  * 证书有效期
  * 公钥
  * 证书所有者
  * 签名及使用算法
  * 指纹及使用算法（摘要）
* 假设前提：数字证书可保证数字证书中的 _公钥_ 确实是证书所有者的

### 完整过程

* 客户端向服务器发送一个通信请求
* 服务器向客户端发送自己的数字证书，其中包含服务器 _公钥_
* 客户端生成对称加密算法密钥，用 _公钥_ 加密后发送给服务器
  * 由于只有服务器有 _私钥_ 用于解密，确保了这一过程的安全性
* 服务器与客户端使用对称加密算法通信

## Components of Certificate

* _Issuer_ （证书发布机构）
  * 证书的创建者，不是使用者
  * _CA_ 机构（Certificate Authority）
* _Valid from_ & _Valid to_ （证书有效期）
  * 过期作废
* _Public key_ （公钥）
* _Subject_ （证书所有者）
  * 这个证书是颁布给谁的
  * 某企业、某机构、某网址
* _Signature algorithm_ （数字签名算法）
  * 利用证书里的 _公钥_，使用该算法对指纹进行解密
* _Thumbprint_ & _Thumbprint algorithm_ （指纹及指纹算法）
  * 指纹被签名算法和 _CA_ 机构私钥加密后，与证书放在一起
  * 保证证书的 __完整性__ 与 __非篡改性__

## Procedure

_CA_ 机构除了向别人发布证书外，也有自己的证书

* 用于解密其余证书的指纹
* _Microsoft&copy;_ 等操作系统提供商会根据权威安全机构的评估选取一些信誉很好的 _CA_ 机构
* 将这些 _CA_ 机构的证书默认安装在操作系统内

因此证书的内容如下：

* Issuer
* Subject
* Valid from
* Valid to
* Public key
* ...
* { 证书指纹及指纹算法（摘要 + 摘要算法） }[ _CA_ 机构私钥加密 ] - 实际上是一个 __数字签名__

客户端得到证书后：

* 在操作系统中寻找对应 _Issuer_ 的 _CA_ 机构 _公钥_
* 用 _CA_ 机构的 _公钥_ 解密证书的数字签名，得到证书指纹和指纹算法
* 使用指纹算法对证书进行计算，将得到的结果与解密的证书指纹进行对比
* 若指纹相同，则证书没有被篡改
* 那么证书中的 _Public key_ 一定属于 _Subject_ 中的公司，从而保证了 _公钥_ 的来源是安全的

接下来，客户端使用证书中的 _公钥_ 就可以去对应公司的服务器商定会话的对称加密算法和密钥了

---

## Summary

整套数字证书机制如何保证安全性？

* 数字证书包括：证书本身 + 数字签名

* 数字签名由 _CA_ 机构私钥加密，由操作系统提供的 _CA_ 机构公钥解密，可保证证书的来源与安全性

* 证书中的公钥保证从 __客户端__ 到 __服务器__ 的单向通讯可靠
  * 客户端可在单向通讯中与服务器商定用于对话的对称加密算法及其密钥
* 客户端与服务器商定的对称加密算法及其密钥保证 __客户端__ 与 __服务器__ 的对话可靠

一整套机制保证了通讯安全性

---

这一套机制需要很多基础设施及理论支持

从 __非对称加密__ 与 __对称加密__

到 __数字签名与指纹__

以及 __数字证书__

还需要专门的 _CA_ 机构与 _OS_ 提供商的支持

研发这一整套机制的人是真的 _nb_ ！

---

