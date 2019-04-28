# HTTP - POST 提交表单的两种方式

Created by : Mr Dk.

2018 / 11 / 08 10:16

Nanjing, Jiangsu, China

---

## URLEncoded

是 _HTML_ 中默认的表单提交方式（`<form>` 中的 `enctype`）

提交的数据按照 `key1=val1&key2=val2` 的方式进行编码 

```
POST http://www.example.com HTTP/1.1
Content-Type: application/x-www-form-urlencoded;charset=utf-8

title=test&sub%5B%5D=1&sub%5B%5D=2&sub%5B%5D=3
```

在 _Apache HTTP Components&trade;_ 的编程方式

```java
// 参数准备 key-value
List<BasicNameValuePair> paramPairs = new ArrayList<>();
paramPairs.add(new BasicNameValuePair("name", "zjt"));
paramPairs.add(new BasicNameValuePair("passwd", "123"));
UrlEncodedFormEntity postEntity = new UrlEncodedFormEntity(paramPairs);
// HttpPost 初始化
CloseableHttpClient httpClient = HttpClients.createDefault();
HttpPost httpPost = new HttpPost(uri);
postEntity.setContentType("application/x-www-form-urlencoded");
postEntity.setContentEncoding("utf-8");
httpPost.setEntity(postEntity);
// 执行
CloseableHttpResponse response = httpClient.execute(httpPost);
```

## Multipart

`<form>` 中的 `enctype` 为 `multipart/form-data`

将会产生一个 _boundary_ 用于分割字段

可用于上传文件

```
POST http://www.example.com HTTP/1.1
Content-Type:multipart/form-data; boundary=----WebKitFormBoundaryrGKCBY7qhFd3TrwA

------WebKitFormBoundaryrGKCBY7qhFd3TrwA
Content-Disposition: form-data; name="text"

title
------WebKitFormBoundaryrGKCBY7qhFd3TrwA
Content-Disposition: form-data; name="file"; filename="chrome.png"
Content-Type: image/png

PNG ... content of chrome.png ...
------WebKitFormBoundaryrGKCBY7qhFd3TrwA--
```

---

## Summary

阅读 _Vert.x_ 框架文档时，发现框架支持这两种 _POST_ 方式

之前开发 _Kismet_ 的 _Java_ 客户端时

也需要使用 _POST_ 方式访问 _Kismet_ 的 _RESTful API_

当时由于不了解 `application/x-www-form-urlencoded`

被坑了好久。。。。。。

今天写了笔记 希望下次不要被坑了

---

