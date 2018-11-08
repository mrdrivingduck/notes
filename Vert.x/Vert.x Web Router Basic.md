# Vert.x Web - Router Basic

Created by : Mr Dk.

2018 / 11 / 08 11:48

Nanjing, Jiangsu, China

---

### Router - One of the core concepts of Vert.x-Web

`Router` - 一个核心对象，维护 0 个或多个 `Route`

总体概念 - 

* 从 _Vert.x_ 实例中获取`Router` 实例
* 在 `Router` 上注册多个 `Route`，对应相同或不同的 _URL_
* 在每个 `Route` 上注册一个或多个 _handler_，用于处理 `HttpServerRequest`
* 若 _HTTP_ 请求的 _URL_ 符合 `Route` 的过滤条件，`request` 将被送入该 `Route` 的第一个 _handler_
* 处理完毕可以选择进入下一个符合条件的 _handler_ 继续处理，或是直接结束请求

### A Basic Example

```java
Vertx vertx = Vertx.vertx();
HttpServer server = vertx.createHttpServer();
Router router = Router.router(vertx);

Route route = router.route();
route.handler(routingContext -> {
    HttpServerResponse response = routingContext.response();
    response.putHeader("content-type", "text/plain");
    response.end("I love u");
});

server.requestHandler(router::accept).listen(9001, "localhost");
```

由于 `route` 没有任何过滤条件，所以所有的 _HTTP Request_ 都将会被送入 _handler_ 中

送入 _handler_ 中的参数对象是一个 `RoutingContext`，其中包含了 - 

* `HttpServerRequest`
* `HttpServerResponse`
* 其余有用的参数

### Next Handler & Order

_Vert.x_ 将 _HTTP_ 请求路由到第一个符合条件的 `Route`，调用它的第一个 _handler_ 并传入 `RoutingContext`

* 如果不想在这个 _handler_ 中结束 `response`，可使用 `next` 函数
  * 下一个符合条件的 _handler_ 将得到 `RoutingContext`
  * 在下一个 _handler_ 中做继续处理

_handler_ 默认使用 __事件循环线程__ 对请求进行处理

* 如果需要做一些阻塞线程的操作 - 不要忘了原则：__Don't block the event-loop!__
  * 使用 `blockingHandler` 代替 `handler` 即可

关于多个 _handler_ 的调用顺序 - 

* By default routes are matched in the order they are added to the router.

```java
Vertx vertx = Vertx.vertx();
HttpServer server = vertx.createHttpServer();
Router router = Router.router(vertx);

// First route to be called
Route route1 = router.route("/test/next/handler/");
route1.handler(routingContext -> {        // First handler to be called
    HttpServerResponse response = routingContext.response();
    response.setChunked(true);
    response.write("route1\n");
    routingContext.next();                // Not end yet
}).handler(routingContext -> {            // Second handler to be called
    HttpServerResponse response = routingContext.response();
    response.write("route2\n");
    routingContext.next();                // Not end yet
}).blockingHandler(routingContext -> {    // Third handler to be called
    HttpServerResponse response = routingContext.response();
    response.write("route3\n");
    routingContext.next();                // Not end yet
});

// Second route to be called
Route route2 = router.route("/test/next/handler/");
route2.handler(routingContext -> {        // Forth handler to be called
    HttpServerResponse response = routingContext.response();
    response.write("route4\n");
    routingContext.response().end();      // Response end
});

server.requestHandler(router::accept).listen(9001, "localhost");
```

---

### Summary

_Vert.x Web_ 中提供 _Router_

可以比 _Vert.x Core_ 中更为方便地开发 _HTTP Server_

本章只记录了 _Vert.x Web_ 中的核心概念

下一章详细学习 _Router_ 的超多种过滤方式

---

