# Vert.x Web - Routing

Created by : Mr Dk.

2018 / 11 / 08 14:38

Nanjing, Jiangsu, China

---

### About

`Router` 向多个挂载的 `Route` 转发接收到的 _HTTP_ 请求

对每个 `Route` 可以设置它们的过滤方式

用于过滤不同的 _HTTP_ 请求，触发不同业务逻辑的 _handler_

### Routing by exact path

指定 _URL_ 的过滤

对于 _URL_ `/test/next/`，以下路径也符合条件

* `/test/next`
* `/test/next//`

```java
Route route = router.route("/test/next/");
route.handler(routingContext -> {
    // TO DO ...
});
```

### Routing by paths that begin with sth.

```java
Route route = router.route("/test/next/*");
// Route route = router.route().path("/test/next/*");
route.handler(routingContext -> {
    // TO DO ...
})
```

### Capturing path parameters

```java
Route route = router.route(HttpMethod.POST, "/test/param/:user/:passwd/");

route.handler(routingContext -> {

    String user = routingContext.request().getParam("user");
    String passwd = routingContext.request().getParam("passwd");

    // TO DO ...
});
```

### Routing with regular expressions

```java
Route route = router.route().pathRegex(".*foo");
// Route route = router.routeWithRegex(".*foo");
route.handler(routingContext -> {
    // 正则表达式含义：匹配任何以 'foo' 结尾的路径
    
});
```

### Capturing path parameters with regular expressions

```java
Route route = router.routeWithRegex(".*123")
    .pathRegex("\\/([^\\/]+)\\/([^\\/]+)")
    .handler(routingContext -> {
        String name = routingContext.request().getParam("param0");
        String passwd = routingContext.request().getParam("param1");
    });

/**
 * 正则表达式含义：
 *     / ([^/]+) / ([^/]+)
 *     匹配不含 '/' 的子表达式一次或多次，保证 URL 只有两个 '/'，即只有两个参数
 *     /zjt/123 -> param0:'zjt'; param1:'123'
 */
```

### Using named capture groups

```java
Route route = router.routeWithRegex(".*123")
    .pathRegex("\\/(?<name>[^\\/]+)\\/(?<passwd>[^\\/]+)")
    .handler(routingContext -> {
        String name = routingContext.request().getParam("name");      // "param0"
        String passwd = routingContext.request().getParam("passwd");  // "param1"
    });
```

### Routing by HTTP method

```java
Route route = router.route().method(HttpMethod.POST);
route.handler(routingContext -> {
    // TO DO ... POST
});
```

```java
Route route = router.route(HttpMethod.POST, "/test/next/");
route.handler(routingContext -> {
    // TO DO ... POST with "/test/next/"
});
```

```java
router.get().handler(routingContext -> {
    // TO DO ... GET
});

router.get("/test/next/").handler(routingContext -> {
    // TO DO ... GET with "/test/next/"
});

router.getWithRegex(".*next").handler(routingContext -> {
	// TO DO ... GET ended by "next"
});
```

可以使用 _Vert.x_ 特色的 _fluent API_ 过滤多种 _HTTP method_

```java
Route route = router.route()
    .method(HttpMethod.POST)
    .method(HttpMethod.PUT);
route.handler(routingContext -> {
    // TO DO ... POST | PUT
});
```

### Routing by Content-Type of request

```java
router.route()
    .consumes("text/html")
    .handler(routingContext -> {
        // Request with "Content-Type" == "text/html"
    });
```

* 可使用 _fluent API_ 过滤多种 `Content-Type`
* 可使用 `*` 代替所有 _MIME_ 类型，如 - 
  * `text/*`
  * `*/json`

### Routing by Accept types of client

`Accept` 字段位于 _HTTP_ 的 __请求头部__，指明客户端可以接受的 _MIME_ 类型

```html
Accept: application/json;q=0.7, text/html;q=0.8, text/plain
```

服务器倾向于选择 `q` 值更大的 _MIME_ 类型（`q` 值默认为 `1.0`）

* `q` 值匹配 `;` 之前的那个属性

```java
router.route()
    .produces("application/json")
    .produces("text/html")
    .handler(routingContext -> {
        String acceptableContentType = routingContext.getAcceptableContentType();
        /**
         * 在上面的例子中
         * 结果为 "text/html" 
         * 因为它的 q 最大
         */
    });
```

### Enable & Disable

The __match__ can be enabled or disabled

```java
route.enable();
route.disable();
```

---

### Summary

_Vert.x Web_ 提供的路由过滤方式足够多了

应该能够满足开发需求

---

