# Cryptography - JWT

Created by : Mr Dk.

2020 / 03 / 09 22:18

Ningbo, Zhejiang, China

------

## Introduction

JWT 全名 _JSON Web Token_ ，是一个开放标准 (RFC 7519)。其定义了一种 __紧凑__ 且 __自包含__ 的模式，通过 JSON 对象，保证双方通信的安全。其主要应用场景在于签发 token。

Token 分为两类：

* 签名 token - 用于验证其中自包含信息的 __完整性__ (即未经篡改)
* 加密 token - 用于对其它实体隐藏其中的信息

使用场景：

* 授权
    * 用户登录成功后，发放 token
    * 之后用户访问所有的受限资源都需要携带这个 token，无需再进行认证
    * 开销小，可以在跨域场景中方便使用
* 信息交换
    * 用于使用了公私钥签名，验证信息是否遭到篡改

JWT 支持用一个密钥 + _HMAC_ 算法的签名方式，也支持 _RSA_ 或 _ECDSA_ 的公私钥签名方式。

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

然后，这个 JSON 对象被 base64 编码后，成为 token 的第一部分。

### Payload

负载中包含了用户信息以及其它数据的声明，通常包含三种类型：

* 注册声明
    * 不强制但推荐使用，是一些预定义的字段
    * `iss` (issuer), `exp` (expiration time), `sub` (subject), `aud` (audience)
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

这个 JSON 也会被 base64 编码，然后成为 token 的第二部分。

### Signature

编码后的 header + `.` + 编码后的 payload 作为签名对象，使用 header 中指定的算法，和一个密钥，对签名对象进行签名。这个签名用于认证 token 的不可篡改性。

```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

签名结果被 base64 编码后，成为 token 的第三部分。

## How do JWT work?

当用户使用账号密码成功登录后，产生一个 JWT 并返回。之后用户如果想要访问受保护的路由或资源，就需要在请求中加入 JWT。通常来说，token 以 `Bearer` 模式被放置在 `Authorization` 头部：

```
Authorization: Bearer <token>
```

成为一种无状态的认证机制。如果 token 中已经包含了必要的认证信息，那么查询数据库的操作就可以被省略了。

## Compare

类似的东西还有 _Simple Web Tokens (SWT)_ 和 _Security Assertion Martup Language Tokens (SAML)_ 。

由于 JSON 比 XML 的冗余性小，因此 JWT 比 SAML 编码后更小，更适合 HTTP 环境下的传输。而 SWT 只能使用对称加密进行签名。

---

