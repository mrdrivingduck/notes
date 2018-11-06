# Vert.x - TCP Server & Client

Created by : Mr Dk.

2018 / 11 / 06 10:08

Nanjing, Jiangsu, China

---

### Server

#### Creating & Configuration

```java
Vertx vertx = Vertx.vertx();
NetServerOptions options = new NetServerOptions().setPort(8081);

// NetServer server = vertx.createNetServer();
NetServer server = vertx.createNetServer(options);
```

#### Handling incoming connections

```java
Vertx vertx = Vertx.vertx();
NetServer server = vertx.createNetServer();
// Handle connections
server.connectHandler(socket -> {
    // Read from socket
    socket.handler(buffer -> {
        System.out.println(buffer.length());
    });
    // Write to socket
    socket.write("data");
    // Notified when socket closed
    socket.closeHandler(v -> {
        // TO DO ... (v -> void)
    });
});
```

#### Starting to work

`connectHandler` must be set before listening.

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

