# Vert.x Core - Future

Created by : Mr Dk.

2018 / 11 / 12 23:41

Nanjing, Jiangsu, China

---

## About

_Future_ 在 _Vert.x_ 中用于 __异步协同__

我的个人理解 _Future_ 用于标识一个的异步事件结束

并带有异步事件的执行状态（成功/失败）

可以解决异步场景下的两种需求：

* 对几个 __并行__ 的异步事件的执行结果进行汇总协同
* 对有链式前驱关系的 __串行__ 异步事件的结果进行协同

## Concurrent composition

Running several asynchronous operations in parallel.

大致调用原理：

* 初始化并取得一个 `Future<?>` 实例
* 在异步操作的 handler 参数中传入一个 `Handler<AsyncResult<?>>`
  * 异步操作包括：
    * HttpServer 或 NetServer 的端口绑定与监听
    * MongoClient 的数据库操作
    * ...
  * 该 handler 中包含异步操作的结果 `AsyncResult<?>`
  * 在该 handler 中实现 `Future<?>` 的 `complete` 或 `fail` 的逻辑
  * 以上所有泛型根据异步操作中的 `Handler<AsyncResult<?>>` 参数的泛型决定
* 在异步操作结束时，自动调用 handler 来决定 Future 的完成或是失败
* `CompositeFuture` 接收多个 `Future` 参数，并挂载 handler 来协同所有 `Future` 完成后的结果
  * handler 中携带的参数为 `CompositeFuture` - 其中包含执行状态（成功/失败）

协同模式

* `CompositeFuture.all()`
  * 接收最多六个 `Future` 参数，返回一个 `CompositeFuture`，包含协同结果
    * 协同成功 - 当且仅当所有的 `Future` 都返回成功
    * 协同失败 - 至少有一个 `Future` 返回失败
* `CompositeFuture.any()`
  * 接收最多六个 `Future` 参数，返回一个 `CompositeFuture`，包含协同结果
    * 协同成功 - 至少有一个 `Future` 返回成功
    * 协同失败 - 当且仅当所有的 `Future` 返回失败
* `CompositeFuture.join()`
  * 接收最多六个 `Future` 参数，返回一个 `CompositeFuture`，包含协同结果
    * 协同成功 - 当且仅当所有的 `Future` 返回成功
    * 协同失败 - 所有的 `Future` 都已完成且至少有一个 `Future` 失败

e.g.

初始化并取得 `Future<?>` 实例

```java
Future<HttpServer> httpServerFuture = Future.future();
Future<NetServer> netServerFuture = Future.future();
```

在异步操作参数中传入 `Handler<AsyncResult<?>>`，实现 `Future<?>` 的完成/失败逻辑

```java
Vertx vertx = Vertx.vertx();
HttpServer httpServer = vertx.createHttpServer();
NetServer netServer = vertx.createNetServer();
httpServer.requestHandler(request -> {
    request.response().end();
});
netServer.connectHandler(socket -> {
    socket.close();
});

httpServer.listen(httpServerFuture.completer());  // Complete directly
netServer.listen(server -> {                      // Implement completion
    // server is an 'AsyncResult<NetServer>' object
    if (server.succeeded()) {
        netServerFuture.complete();
    } else {
        netServerFuture.fail(server.cause().getMessage());
    }
});
```

协同所有 `Future<?>` 的执行结果

```java
CompositeFuture.all(Arrays.asList(httpServerFuture, netServerFuture)).setHandler(ar -> {
    // ar is an 'AsyncResult<CompositeFuture>' object
    if (ar.succeeded()) {
        // All futures succeeded
        System.out.println("All succeeded");
    } else {
        // At least one future failed
        System.out.println("At least one failed");
    }
});
```

## Sequential composition

Chain asynchronous operations.

大致调用原理：

* 初始化并取得一个代表链式协同结束状态的 `Future<?>`
* 初始化并取得一个起始的 `Future<?>` 实例
* 在第一个异步操作中传入 `Handler<AsyncResult<?>>` ，实现起始 `Future<?>` 的完成/失败逻辑
  * 异步操作结束时，该 `Handler` 被调用，改变 `Future<?>` 的状态为完成或失败
* 从起始 `Future<?>` 实例开始链式调用 `compose()` 函数
  * 调用者 `Future<?>` 的状态改变为 _完成_ 时被调用
  * 调用链中间环节版本 - `compose(Handler<AsyncResult<?>>)`
    * handler 中包含异步操作结果 `AsyncResult<?>`，可对结果进行操作
    * 取得下一个 `Future<?>` 实例
    * 在下一个异步操作中传入 handler，其中实现了下一个 `Future<?>` 的完成状态
    * 在该 `compose()` 中返回下一个 `Future<?>` 实例
    * 使用 _fluent API_ 链式调用下一个 `Future<?>` 实例的 `compose()`
    * 下一个 `compose()` 会在下一个 `Future<?>` 的状态为完成时被调用
  * 调用链结束版本 - `compose(Handler<AsyncResult<?>>, Future<?>)`
    * handler 中包含异步操作结果 `AsyncResult<?>`，可对结果进行操作
    * 参数中的 `Future<?>` 为一开始定义的协同结束状态
    * 对结果处理完毕后，需要对代表结束状态的 `Future<?>` 实现完成/失败逻辑
    * 最后一个 `Future<?>` 结束后，调用链结束
* 为结束状态的 `Future<?>` 设置 handler，在链式操作结束后被调用

e.g.

初始化结束状态 `Future<?>`

```java
Future<Void> endFuture = Future.future();
```

实例化第一个异步操作的 `Future<?>`

```java
Future<HttpServer> httpFuture = Future.future();

Vertx vertx = Vertx.vertx();
HttpServer httpServer = vertx.createHttpServer();
httpServer.requestHandler(request -> {
    request.response().end();
});
httpServer.listen(httpFuture.completer());
```

开始链式调用 `compose()`

```java
httpFuture.compose(server -> {
    // Called when 'httpFuture' succeeded
    // 'server' is a 'HttpServer' object
    System.out.println("HTTP Server listening");
    
    Future<NetServer> netFuture = Future.future();
    NetServer netServer = vertx.createNetServer();
    netServer.connectHandler(socket -> {
        socket.end();
    });
    netServer.listen(netFuture.completer());
    return netFuture;
}).compose(server -> {
    // Called when 'netFuture' succeeded
    // 'server' is a 'NetServer' object
    System.out.println("TCP Server listening");
    
    Future<List<String>> mongoFuture = Future.future();
    JsonObject mongoConfig = new JsonObject()
        .put("connection_string", "mongodb://localhost:27017")
        .put("db_name","test");
    MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);
    mongoClient.getCollections(mongoFuture.completer());
    return mongoFuture;
}).compose(res -> {
    // Called when 'mongoFuture' succeeded
    // 'res' is a 'List<String>' object
    System.out.println("DB Operation succeeded");
    endFuture.complete();
}, endFuture);

endFuture.setHandler(v -> {
    // Called when 'endFuture' succeeded
    System.out.println("Ending");
});
```

---

## Summary

这篇 _note_ 写了三个多小时。。。

终于把 _Future_ 的机制弄清楚了个大概

学习该机制的驱动力是

_WIDS_ 后端代码中的数据库初始化部分有链式调用关系

因此我认为需要引入 _Future_ 机制加以修改

否则将可能引发问题

---

