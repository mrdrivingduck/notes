# Vert.x Core - Event Bus

Created by : Mr Dk.

2018 / 11 / 04 17:51

Nanjing, Jiangsu, China

---

## About

_Event Bus（事件总线）_ 是 _Vert.x_ 的神经系统

每一个 _Vert.x_ 实例都有一个事件总线实例

* 允许相同或不同 _Vert.x_ 实例之下的应用互相通信
* 通信无视实现语言
* 支持多 _nodes_ 的分布式对等消息系统

## Theory

### Addressing

* _Messages_ 被送往指定的地址
* 地址的形式是一个简单的 _String_
* _Vert.x_ 不关心地址的具体形式，但最好在开发时人为制定一种模式

### Handlers

* _handlers_ 被注册在一个地址上
* 消息在 _handlers_ 中被接收到
* 多个不同的 _handlers_ 可以被注册在同一个地址上
* 一个 _handler_ 可以被注册在多个不同的地址上

在 _event bus_ 上某个地址注册后，会返回一个没有注册 _handlers_ 的 `MessageConsumer<?>` 对象

* 该对象用于注册/解除注册 _handler_
* `<>` 中的泛型为接收到消息的数据类型
  * 支持简单数据类型、`String`
  * 支持 _Vert.x_ 内置的 `Buffer`
  * 支持 _Vert.x_ 内置的 `JSON`
  * 支持自定义对象，但需要自定义和注册 `MessageCodec<?, ?>`

```java
Vertx vertx = Vertx.vertx();
EventBus eb = vertx.eventBus();

MessageConsumer<String> msgConsumer = eb.consumer("ADDRESS_STR");
msgConsumer.handler(message -> {
    System.out.println(message.body());  // return a 'String'
    
    msgConsumer.unregister(res -> {
        if (res.succeeded()) {
            // TO DO ...
        } else {
            // TO DO ...
        }
    });
});
```

### Message Codec

对 __自定义对象__ 进行编码/解码

对官方文档进行了粗浅研究，结果如下：

* `MessageCodec<?, ?>` 泛型的两个类分别为输入类对象和输出类对象

* Override five methods:

  * `encodeToWire` - 将输入类对象编码到 `Buffer` 中

  * `decodeFromWire` - 将输出类对象从 `Buffer` 中解码

  * `transform` - 在消息通过 _event bus_  __本地__ 传送时被调用（不需要编码/解码）

  * `name` - 唯一的名称，用于在发送消息和解除注册时标识该 `codec` 

  * `systemCodecID` - "Used to identify system codecs. Should always return -1 for a user codec."

    ```java
    MessageCodec<Entity, Entity> mCodec = new MessageCodec<Entity, Entity>() {
    
        @Override
        public void encodeToWire(Buffer buffer, Entity s) {
    
        }
    
        @Override
        public Entity decodeFromWire(int pos, Buffer buffer) {
            return null;
        }
    
        @Override
        public Entity transform(Entity s) {
            return s;
        }
    
        @Override
        public String name() {
            return "EntityCodec";
        }
    
        @Override
        public byte systemCodecID() {
            return -1;
        }
    };
    ```

* 两种注册方式

  * 单次注册

    ```java
    EventBus eb = vertx.eventBus();
    eb.registerCodec(myCodec);
    DeliveryOptions options = new DeliveryOptions().setCodecName(myCodec.name());
    eb.send("ADDRESS_STR", new Entity(), options);
    // eb.unregisterCodec(myCodec.name());
    ```

  * 永久注册

    ```java
    EventBus eb = vertx.eventBus();
    eb.registerDefaultCodec(Entity.class, myCodec);
    eb.send("ADDRESS_STR", new Entity());
    // eb.unregisterDefaultCodec(Entity.class);
    ```

### Message

在 _handlers_ 中被接收

主要分为两部分：

* `headers` - 头部，可在发送前放入参数

* `body` - 消息体，由 `MessageConsumer<?>` 泛型指定消息对象的数据类型

  ```java
  DeliveryOptions options = new DeliveryOptions();
  options.addHeader("header", "value");
  eventBus.send("ADDRESS_STR", "This is a test msg.", options);
  ```

对于任何 _handlers_，_Vert.x_ 保证接收到的消息顺序与发送者的发送顺序一致

可设定超时时间

可手动设定发送失败信息

## Messaging Pattern

### Publish / Subscribe

消息被发布到某一个地址，__所有__ 注册到该地址的 _handlers_ 都会接收到消息

下面的例子中，两个 `MessageConsumer<String>` 都会收到消息

```java
Vertx vertx = Vertx.vertx();
EventBus eb = vertx.eventBus();

eb.consumer("ADDRESS", message -> {
    System.out.println(message.body());
});

eb.consumer("ADDRESS", message -> {
    System.out.println(message.body());
});

eb.publish("ADDRESS", "2345");
```

### Request / Response

是一种 __point-to-point__ 的模式

消息被发送到某一个地址，__只有一个__ 注册到该地址的 _handler_ 会接收到消息

* 如果某个地址注册了超过一个 _handler_，将会使用一种非严格的轮转调度选择某一个 _handler_

发送者发送消息时，可以选择注册一个 `reply handler`，用于处理收到回应后的逻辑 _(OPTION)_

* 当接收者收到消息后，可以选择发送一个 `reply`，唤起发送者的 `reply handler`
* 返回到发送者的 `reply` 也可以被回复，__双方可以无限制地互相回复__

```java
Vertx vertx = Vertx.vertx();
EventBus eb = vertx.eventBus();

MessageConsumer<String> mc1 = eb.consumer("ADDRESS");
mc1.handler(message -> {
    System.out.println("mc1 got msg:" + message.body());
    message.reply("mc1 got message", reply -> {
        // Get reply from sender again
        System.out.println(reply.result().body());
        vertx.close();
    });
});

MessageConsumer<String> mc2 = eb.consumer("ADDRESS");
mc2.handler(message -> {
    System.out.println("mc2 got msg:" + message.body());
    message.reply("mc2 got message");
});

eb.send("ADDRESS", "Hello", req -> {
    if (req.succeeded()) {
        System.out.println("Get reply:" + req.result().body());
        req.result().reply("Sender reply again");    // Reply again
    } else {
        System.out.println("Get reply failed.");
    }
});
```

---

## Summary

主要弄清楚两种信息发送模式的区别

以及各种 _handler_ 的回调关系

---

