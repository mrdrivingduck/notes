# Cryptography - JWT

Created by : Mr Dk.

2020 / 03 / 09 22:18

Ningbo, Zhejiang, China

------

## Introduction

JWT 全名 *JSON Web Token*，是一个开放标准 (RFC 7519)。其定义了一种 **紧凑** 且 **自包含** 的模式，通过 JSON 对象，保证双方通信的安全。

主要应用场景在于签发 token。本来，服务器需要通过会话 id 来区分用户；而使用 token 后，服务器将不再需要维护会话状态。根据 token 中的用户信息对用户进行区分。同时，在有效期内，token 是用户访问的凭据 - 用于替代账号密码，减少数据库的访问次数。

Token 分为两类：

* 签名 token - 用于验证其中自包含信息的 **完整性** (即未经篡改)
* 加密 token - 用于对其它实体隐藏其中的信息

使用场景：

* 授权
    * 用户登录成功后，发放 token
    * 之后用户访问所有的受限资源都需要携带这个 token，无需再进行认证
    * 开销小，可以在跨域场景中方便使用
* 信息交换
    * 用于使用了公私钥签名，验证信息是否遭到篡改

JWT 支持用一个密钥 + *HMAC* 算法的签名方式，也支持 *RSA* 或 *ECDSA* 的公私钥签名方式。

## Token Structure

Token 由三部分构成，这三部分用 `.` 分隔：

* Header
* Payload
* Signature

即 `<header>.<payload>.<signature>`。

### Header

头部包含两部分：

* Token 的类型 - `JWT`
* 签名算法 - `HMAC SHA 256` / `RSA`

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

然后，这个 JSON 对象被 Base64Url 编码后，成为 token 的第一部分。

> Base64Url 与 Base64 有细微差别 - 个别字符的编码不一样。
>
> 主要是为了保证产生的 token 能够在 URL 中传输。

### Payload

负载中包含了用户信息以及其它数据的声明，通常包含三种类型：

* 注册声明
    * 不强制但推荐使用，是一些预定义的字段
      * `iss` (issuer) 发行者
      * `exp` (expiration time) 过期时间
      * `sub` (subject) 主题
      * `aud` (audience) 观众
* 公共声明
    * 可以随意定义，但要避免冲突
* 私人声明
    * 在双方都同意使用的基础上进行使用

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "admin": true
}
```

这个 JSON 也会被 Base64Url 编码，然后成为 token 的第二部分。

### Signature

编码后的 header + `.` + 编码后的 payload 作为签名对象，使用 header 中指定的算法，和一个密钥，对签名对象进行签名。这个签名用于认证 token 的不可篡改性。

```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

签名结果被 Base64Url 编码后，成为 token 的第三部分。

当使用 *HMAC* 的加密方式时，用于生成 token 和验证 token 的密钥是同一个。因此，token 产生过程和验证过程无法分开。如果分开，那就意味着相同的密钥分布了很多份，一旦泄露，就有灾难性的后果。这与对称加密的性质类似。

而当使用 *RSA* 或 *ECDSA* 的加密方式时，生成 token 和验证 token 的过程就可以解耦了。生成 token 的过程可以由一个专门的认证服务器负责。认证服务器持有私钥，负责对 token 的前两部分进行签名；而普通的应用服务器只负责认证，任意多的应用服务器全部持有公钥也不会有什么问题 - 用公钥解密签名后，如果内容未经篡改，就说明一定是认证服务器签发的未经篡改的 token。

这样一来，只有两种可能才会遭受攻击：

1. 账号密码泄露 - 通过账号密码可以直接获取合法 token
2. 私钥泄露 - 这样攻击者可以任意伪造 token

## How do JWT work?

当用户使用账号密码成功登录后，产生一个 JWT 并返回。之后用户如果想要访问受保护的路由或资源，就需要在请求中加入 JWT。通常来说，token 以 `Bearer` 模式被放置在 `Authorization` 头部：

```
Authorization: Bearer <token>
```

成为一种无状态的认证机制。如果 token 中已经包含了必要的认证信息，那么查询数据库的操作就可以被省略了。

## Compare

类似的东西还有 *Simple Web Tokens (SWT)* 和 *Security Assertion Martup Language Tokens (SAML)*。

由于 JSON 比 XML 的冗余性小，因此 JWT 比 SAML 编码后更小，更适合 HTTP 环境下的传输。而 SWT 只能使用对称加密进行签名。

---

