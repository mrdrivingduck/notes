# Cryptography - OAuth 2.0

Created by : Mr Dk.

2020 / 08 / 18 21:54

Nanjing, Jiangsu, China

---

## What is OAuth?

[OAuth](https://en.wikipedia.org/wiki/OAuth) 是一个开放的授权标准，最新的 2.0 版本为 [RFC 6749](https://tools.ietf.org/html/rfc6749)。OAuth 引入了一个授权层，分离两种不同的角色：

* 客户端 (比如一个第三方应用)
* 资源所有者 (比如用户)

经过资源所有者的同意后，资源服务器可以向客户但颁发一个 token。客户端持有 token，就能够直接向资源服务器请求数据。

### 抽象场景

对应于一个生活中的场景就是快递。假设小区进出需要密码，每个业主有自己的密码。某天业主出去上班了，快递小哥来了；业主希望快递小哥能把快递送到家门口去，而快递小哥不知道进入小区的密码；业主又不想把自己的密码告诉快递小哥。这时应该怎么办呢？业主希望快递小哥能够在不知道密码的情况下进入小区，且拥有的唯一权限是送货 (别的事没权限做)。

一种授权机制：由快递小哥通过小区的门禁系统申请授权，向业主提交自己的身份；业主确认信息属实后，同意授予快递小哥进入小区的权限。门禁系统经过业主确认后，向快递小哥出示了一个临时通行令牌 (token)。这个 token 有以下特点：

1. Token 可复用，因为快递小哥可能每天都会来送货，业主不必每天都申请
2. Token 短期有效，一旦过时，需要重新申请 token
3. Token 只有通过小区门禁的权限，没有使用小区其它设施的权限

### 实际场景

在互联网场景中，其实在很多地方都已经用到了 OAuth。比如，在登录 Zoom 时，可以选择使用 Google 账号登录；在登录 LeetCode 时，可以选择使用 GitHub 登录。可以仔细回味一下当时发生了些啥。

当点击 Zoom 中的 *使用 Google 账户登录* 时，客户端将弹出一个浏览器框，并访问到 Google 的认证页面上，需要用户输入 Google 的账号和密码。在验证账号和密码成功后，Google 会提示用户，*即将授予 Zoom 以下权限：访问用户头像...* 等等。这样就完成了一次授权。之后，在 Zoom 上可以直接使用用户 Google 账号的部分信息，比如头像、用户名等。

在授权成功后，Zoom 是如何访问用户的 Google 账号信息的呢？授权成功后，Google 向 Zoom 发送了一个 token，这个 token 由于是在用户自身的授意下发放的，因此拥有与用户的账号密码相似的效果。Token 可以被重复使用一段时间，所以 Zoom 用户在短时间内不需要再次向 Google 认证。另外，这个 token 只具有当时授权时列出的权限 - Zoom 无法使用这个 token 访问用户的其它信息。

### Token 与密码的差别

通过上述场景，我们可以看到 token 与密码之间存在的一些差异：

1. Token 是短期的，过期后会失效；密码一般来说长期有效
2. Token 可以随时被 *资源所有者* 撤回
3. Token 有明确的权限范围，只能做规定好的某几件事；而密码一般对应了完整的权限

通过上述机制，能够保证 token 让第三方应用获得权限而不用反复打扰用户，又随时可控，不会危及资源所有者的资源安全。只要有了 token，一般系统不会再次确认身份 - 所以 token 与密码一样也必须保密，泄露 token 与泄露密码的后果都是严重的。

## RFC 6749 规定的四种授权方式

作为定义 OAuth 2.0 的标准，RFC 6749 规定了适用不同场景的四种授权方式：

* Authorization code (授权码)
* Implicit (隐藏式)
* Password (密码式)
* Client credentials (客户端凭证)

首先，对于第三方应用来说，不管使用哪一种授权方式，都必须先到想要获取权限的资源服务器系统中备案 - 比如，对于 Zoom 来说，如果想要支持 Google 账号登录，就必须先到 Google 处备案，表明自己的身份。Google 会向 Zoom 发放两个身份识别码：

* Client ID - 客户端 ID
* Client secret - 客户端密钥

在进行授权时，Zoom 需要把这两个属性一同发送给 Google，以表明是 Zoom 正在请求 Google 授权。

### Authorization Code

这是最常用、最安全的授权方式，适合 **有后端的 web 应用**。因为一些认证的细节直接在后端完成，并不会造成敏感信息的泄露。

以 Zoom 为例，Zoom 的前端设计了一个按钮 (使用 Google 登录)，用户在点击按钮后，Zoom 前端会跳转到 Google 的认证服务发送请求。请求的 URL 中包含以下信息：

* 授权方式类型 (这里显然是需要 Google 认证服务返回 **授权码**)
* Google 接受或拒绝请求后的跳转 URL (callback)
* Client ID (表明这是 Zoom 在申请授权)
* 要求的权限范围

接下来，用户会看到 Google 的认证界面，输入账号密码后，Google 会询问用户是否同意给予 Zoom 权限。如果用户选择同意，那么 Google 会跳转到 Zoom 提供的 callback，并附带一个 **授权码**。Zoom 的后端收到授权码后，就可以在后端向 Google 请求 token。请求 token 时需要提供的信息有：

* Client ID + Client secret
* 授权类型为 `AUTHORIZATION_CODE`
* 授权码
* Token 颁发后的 callback URL

这样一来，Google 通过 callback 将 token 发送到了 Zoom 的后台。自此，Zoom 后端可以用 token 直接访问用户在 Google 上的资源了。

### Implicit

面向纯前端应用，此时没有后端，token 就必须存储在前端。还是以 Zoom 为例。首先 Zoom 会使用户跳转到 Google 的认证界面。此时，需要用户给出的参数有：

* 授权方式为 `token`，表示直接返回 token
* Client ID
* Callback URL
* 权限范围

用户在 Google 上认证成功后，Google 会调用 callback URL，将 token 发送到 Zoom。由此，Zoom 在前端直接拿到令牌。这种方法很不安全，所以一般 token 的有效期会很短。

### Password

如果用户高度信任第三方应用 (假设 Zoom)，那么可以直接将资源的用户名与密码直接告诉第三方应用。Zoom 首先直接向用户索要 Google 账户和密码，然后直接向 Google 请求 token。请求所带的参数如下：

* 授权方式为 `password`
* Username + password
* Client ID

Google 在这个 HTTP 响应中直接返回 token。

### Client Credentials

这种方法适用于没有前端的 CLI 应用。那么 Zoom 将直接在命令行上向 Google 发送请求，需要的参数包含：

* 授权方式为 `client_credentials`
* Client ID + Client secret

Google 验证通过后，直接返回 token。这种 token 是针对第三方应用 (Zoom) 的，而不是针对用户的。

## Using Token

在拿到 token 之后，在访问受限资源时，需要在每个请求头中加入信息：

```
Authorzation: Bear <TOKEN>
```

## Updating Token

OAuth 2.0 允许用户自动更新 token。资源服务器在颁发 token 时，将一次性颁发两个 token：一个用于获取数据，一个用于获取新的 token。获取数据的 token 到期前，用户以 `refresh_token` 的授权方式发送 `refresh_token`。资源服务器在通过之后，就会颁发新的 token。

---

## References

[阮一峰的网络日志 - OAuth 2.0 的一个简单解释](http://www.ruanyifeng.com/blog/2019/04/oauth_design.html)

[阮一峰的网络日志 - OAuth 2.0 的四种方式](http://www.ruanyifeng.com/blog/2019/04/oauth-grant-types.html)

[RFC 6749 - The OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)

[Wikipedia - OAuth](https://en.wikipedia.org/wiki/OAuth#OAuth_2.0)

---

