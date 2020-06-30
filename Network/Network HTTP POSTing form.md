# HTTP - POST 提交表单的两种方式

Created by : Mr Dk.

2018 / 11 / 08 10:16

Nanjing, Jiangsu, China

---

## URLEncoded

是 HTML 中默认的表单提交方式（`<form>` 中的 `enctype`），提交的数据按照 `key1=val1&key2=val2` 的方式进行编码。

```
POST http://www.example.com HTTP/1.1
Content-Type: application/x-www-form-urlencoded;charset=utf-8

title=test&sub%5B%5D=1&sub%5B%5D=2&sub%5B%5D=3
```

在 *Apache HTTP Components* 中的编程方式：

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

`<form>` 中的 `enctype` 为 `multipart/form-data`，将会产生一个 *boundary* 用于分割字段。可用于上传文件：

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

