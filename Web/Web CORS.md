# Web - CORS

Created by : Mr Dk.

2020 / 02 / 04 18:29

Ningbo, Zhejiang, China

---

## 同源策略

由 *Netscape* 提出的著名安全策略，是浏览器最基本、最核心的安全功能。

一个 **域** 包含三个要素：

* 协议 - HTTP/HTTPS
* 域名
* 端口

这三个要素相同，就是同一个域。不同域的客户端脚本在没有明确授权的情况下，不能读写对方资源。比如，从前端 `localhost:8080` 的网页上向后端 `localhost:8081` 发送 HTTP 请求，浏览器控制台报错：

```
Access to XMLHttpRequest at 'localhost:8081/test/normal' from origin 'http://localhost:8080' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: http, data, chrome, chrome-extension, https.
```

因为从前端到后端的请求是一个跨域请求，出于安全原因，浏览器限制发起这样的请求。比如，从某个恶意网页中，发起了对某个电商网站的请求，如果电脑上存有该电商网站的 Cookies，那么不用账号密码就能登录。这样恶意网页就获得了用户在电商网站的个人信息。

同源策略的限制：

1. 无法通过 JavaScript 读取非同源的 Cookie、LocalStorage、IndexDB
2. 无法通过 JavaScript 获取非同源的 DOM
3. 无法通过 JavaScript 发送非同源的 AJAX 请求

---

## CORS (Cross-Origin Resource Sharing)

是一种 W3C 标准和机制，所有的现代浏览器都支持这个功能，让网页的受限资源能够被其他域名的页面访问。允许浏览器向跨域服务器发出 `XMLHttpRequest` 请求。如果浏览器发现资源访问跨域，会自动向 HTTP 添加 `Origin` 头部，说明本次请求来自哪个域 (协议 + 域名 + 端口)。服务器根据这个头部，决定是否同意请求：

* 如果 `Origin` 在许可范围中，服务器返回的响应中会增加如下的响应头
* 如果 `Origin` 不在许可范围中，服务器会返回正常回应，但不会增加响应头，因此浏览器会因为没有找到特定的响应头而抛出错误

```
Access-Control-Allow-Origin: ...
Access-Control-Allow-Credentials: ...
Access-Control-Expose-Headers: ...
```

因此，在自行实现的后端代码中，对于合法的跨域访问请求，需要在响应头中加入上述的头部。*Spring Boot* 等 Web 框架也提供了对应的注解 `@CrossOrigin`。

---

## References

https://zh.wikipedia.org/wiki/%E8%B7%A8%E4%BE%86%E6%BA%90%E8%B3%87%E6%BA%90%E5%85%B1%E4%BA%AB

https://www.ruanyifeng.com/blog/2016/04/cors.html

https://blog.csdn.net/xcbeyond/article/details/84453832

https://www.jianshu.com/p/2547b0a15707

---

