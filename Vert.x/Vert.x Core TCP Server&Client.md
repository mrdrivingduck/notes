# Vert.x Core - TCP Server & Client

Created by : Mr Dk.

2018 / 11 / 06 22:19

Nanjing, Jiangsu, China

---

### TCP Server

#### Creating & Configuration

```java
Vertx vertx = Vertx.vertx();
NetServerOptions options = new NetServerOptions()
    .setPort(8081)
    .setLogActivity(true);

// NetServer server = vertx.createNetServer();
NetServer server = vertx.createNetServer(options);
```

* `logging` 功能由 _Netty_ 提供，不由 _Vert.x_ 提供

#### Handling incoming connections

```java
Vertx vertx = Vertx.vertx();
NetServer server = vertx.createNetServer();

server.connectHandler(socket -> {               // Handle connections
    
    socket.handler(buffer -> {                  // Read from socket
        System.out.println(buffer.length());
    });
    
    socket.write("data");                       // Write to socket
    socket.sendFile("file.dat");                // Send file to socket
    
    socket.closeHandler(v -> {                  // Notified when socket closed
        // TO DO ... (v -> void)
    });
    socket.close();                             // Close the socket
});
```

* 获得 _socket_、关闭 _socket_、读、写 - 全部都是 __异步__ 操作
* `connectHandler` 必须在服务器开始监听前设置

#### Starting to work

```java
// server.listen(8081, "localhost");
server.listen(8081, "localhost", res -> {
    if (res.succeeded()) {
        // Server is now listening
    } else {
        // Server failed to bind
    }
});
```

#### Closing server

```java
server.close(res -> {
    if (res.succeeded()) {
        // Server is closed
    } else {
        // Server failed to close
    }
});
```

* 如果 `NetServer` 或 `NetClient` 是在 _Verticles_ 中创建的，那么在 _Verticles_ 解除部署时会自动 _clean-up_

#### Multicore server

* TCP Server 的 _handlers_ 总是在一个 _event loop thread_ 上执行 - _CPU_ 最多只有一个 _core_ 被使用
* 如何利用多核 _CPU_ ？

一种可能的方法：

```java
for (int i = 0; i < 10; i++) {
    NetServer server = vertx.createNetServer();
    server.connectHandler(socket -> {
        // socket jobs
    });
    server.listen(8080, "localhost");
}
```

另一种方式：（将逻辑写在 _Verticle_ 中，实例化多个 _Verticles_）

```java
DeploymentOptions options = new DeploymentOptions().setInstances(10);
vertx.deployVerticle("NetServerVerticle", options);
```

如此一来，所有的 _CPU core_ 都将被利用

__为什么多个服务器实例可以监听同一个端口不会发生冲突？__

* _Vert.x_ __不会__ 在同一个域名端口下再创建一个新的 `NetServer`
* _Vert.x_ 内部仅维护一个 `NetServer`
* 到来的连接将会 __轮流分发__ 到任何一个 `connectHandler` 中
* 每一个 `connectHandler` 依旧被单线程执行，但接受连接扩展到了多核心上 - __并发 &rarr; 并行__

### TCP Client

#### Creating & Configuration

```java
Vertx vertx = Vertx.vertx();
NetClientOptions options = new NetClientOptions()
    .setConnectTimeout(10000)
    .setReconnectAttempts(10)
    .setReconnectInterval(500)
    .setLogActivity(true)；
NetClient client = vertx.createNetClient(options);
```

* `Logging` 功能由 _Netty_ 提供，不由 _Vert.x_ 提供
* 目前 _Vert.x_ 不支持 __连接中途中断__ 后的重新连接
* 重新连接的尝试次数与间隔 __只对初始连接有效__

#### Making connections

```java
Vertx vertx = Vertx.vertx();
NetClient client = vertx.createNetClient();

client.connect(8080, "localhost", res -> {
    if (res.succeeded()) {
        // Connected
        NetSocket socket = res.result();
        // TO DO socket read/write
        // ...
    } else {
        // Failed to connect
    }
});
```

### Enable SSL/TLS for server & client

暂略，等有需求时再详细研究

---

### Summary

__传输层__ _Socket_ 的简单异步封装

---

