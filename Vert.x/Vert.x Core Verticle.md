# Vert.x Core - Verticle

Created by : Mr Dk.

2018 / 11 / 03 12:29

Nanjing, Jiangsu, China

---

## About

_Verticle_ 是 _Vert.x_ 提供的一种简单、可扩展、可部署、并发的模型

_Verticle_ 代码块将被 _Vert.x_ 部署并执行

一个 _Vert.x_ 实例默认维护 `N` 个 _event loop threads (事件循环线程)_ ，`N` 默认为处理器核心数的两倍

在同一时间，多个 _Verticle_ 实例运行在同一个 _Vert.x_ 实例上

_Verticle_ 实例之间通过在 _event bus (消息总线)_ 上发送消息来传递信息

## Implementation

两种实现方式 - 

* 实现 `Verticle` 接口
* 继承 `AbstractVerticle` 类

需要覆盖 `start()` 和 `stop()` 函数（两个函数有 __同步版本__ 和 __异步版本__）

* 同步版本 - 在当前线程中直接运行，因此不能执行耗时操作，否则引起事件循环线程阻塞
  * 同步版本的 `start()` 函数完成后 - _Verticle_ 被视为开始运行
  * 同步版本的 `stop()` 函数完成后 - _Verticle_ 被视为停止
* 异步版本 - 带有 `Future` 参数，执行耗时操作
  * 异步版本的 `start(Future<Void>)` 函数完成后 - _Verticle_ __不被视为开始运行__
  * 异步版本的 `stop(Future<Void>)` 函数完成后 - _Verticle_ __不被视为停止__

```java
public class MyVerticle extends AbstractVerticle {
    
    @Override
    public void start() throws Exception {
        super.start();    // 同步版本
    }

    @Override
    public void stop() throws Exception {
        super.stop();     // 同步版本
    }
}
```

```java
public class MyVerticle extends AbstractVerticle {

    @Override
    public void start(Future<Void> startFuture) throws Exception {
        super.start(startFuture);    // 异步版本
    }

    @Override
    public void stop(Future<Void> stopFuture) throws Exception {
        super.stop(stopFuture);      // 异步版本
    }
}
```

## Verticle Types

* Standard Verticles （最常见，默认）
  * 分配调用了 `start()` 函数的那一个事件循环线程执行
  * _Vert.x_ 保证一个 _Verticle_ 实例中的所有代码都被同一个事件循环线程执行
  * 因此，在同一实例中，可以以 __单线程__ 方式编码，不需要自己创建线程，让 _Vert.x_ 操心线程分配的事情

* Worker Verticles

  * 使用 _Vert.x_ 的 _worker thread pool_ 中的线程执行，而不是事件循环线程
  * _pool size_ 可在 `Vertx` 实例化时或 `Verticle` 部署时设置 
  * 用于执行会引起阻塞的代码
  * 不会被超过一个线程并发执行，但可能在不同的时间被不同的线程执行

  ```java
  DeploymentOptions options = new DeploymentOptions().setWorker(true);
  vertx.deployVerticle(new MyVerticle(), options);
  ```

* Multi-threaded Worker Verticles

  * 特性与 _Worker Verticles_ 类似，但可被不同的线程并发执行

> 2019.07.29 - Update
>
> 每个 Standard Verticle 内部的所有代码会被同一个 event-loop thread 执行
>
> 但是每个 standard verticle 会被不同的 event-loop thread 执行
>
> 因此，如果 standard verticle 之间存在共享的数据结构
>
> 还是需要加锁的。。。。。。 😫 我还一直以为不用
>
> 具体实验方式：
>
> 1. 使用 Java 的 `Thread.currentThread().getId()` 获取当前线程 id
> 2. 实例化两个相同的 Verticle 实例，为每个实例传入一个 `String` 类型的实例标识用于区分
> 3. 在每个实例中，对共享数据结构中的 `int` 变量在固定次数的 for 循环中进行 `++` 操作，变量最终理论正确结果应该是循环次数 × Verticle 实例数量
> 4. 打印实例标识、线程 id、共享数据结构中的变量值
>
> 观察发现：
>
> * 每个 Verticle 实例标识与一个线程 id 相对应，说明不同的 Verticle 被不同的事件循环线程执行
> * 有一定几率最终结果不等于期望值 - 操作共享数据未加锁导致

## Deployment

* 自己实例化一个 _Verticle_ 对象，通过 `deployVerticle()` 函数传递对象参数

  ```java
  Verticle myVerticle = new MyVerticle();
  vertx.deployVerticle(myVerticle);
  ```

* 直接在 `deployVerticle()` 中指定 _Verticle name_，由 _Vert.x_ 负责对象实例化（甚至是其它语言的 _Verticle_）

  ```java
  vertx.deployVerticle("iot.zjt.MyVerticle");
  ```

* 部署时可附带参数

  ```java
  DeploymentOptions options = new DeploymentOptions()
      .setInstances(16) // 实例化对象个数
      .setConfig(new JsonObject().put("key", "value")); // 想传入的参数
  vertx.deployVerticle("iot.zjt.MyVerticle", options);
  ```

* 部署/解除部署时可使用 `lambda` 表达式指定异步操作

  ```java
  vertx.deployVerticle("iot.zjt.MyVerticle", res -> {
      if (res.succeeded()) {
          // TO DO ...
      } else {
          // TO DO ...
      }
  });
  ```

  ```java
  vertx.undeploy(deploymentID, res -> {
      if (res.succeeded()) {
          // TO DO ...
      } else {
          // TO DO ...
      }
  });
  ```

## Vert.x Instance

* 不是 __daemon threads__ _(守护线程 - 运行在后台，独立于控制终端，周期性执行某种任务)_
* 因此会阻止 _JVM_ 退出
* 如果完成了和 _Vert.x_ 有关的一切操作，调用 `vertx.close()` 关闭，它将会 -
  * 关闭所有内部线程池
  * 关闭所有其它资源
  * 允许 _JVM_ 退出

## Timer

在 _Standard Verticles_ 中，不能通过线程休眠来产生延时 - 会导致事件循环线程阻塞

采用 __定时器 + Handler__ 实现

* 设置定时器后会返回一个 `timerID`，同时也会传递到 _Handler_ 中
* `timerID` 可用于注销定时器

单次定时器

```java
long timerID = vertx.setTimer(1000, id -> {
    // TO DO ...
});
```

周期定时器

```java
long timerID = vertx.setPeriodic(1000, id -> {
    // TO DO ...
});
```

定时器注销

```java
vertx.cancelTimer(timerID);
```

* 周期性定时器中不适合做耗时操作，否则易引发 `stack up` 问题

## Automatic Clean-up

在 _Verticles_ 内部注册的定时器、handler 等，会在 _unenployed_ 时自动解除注册

---

## Summary

通过阅读 _Vert.x_ 的官方文档

对 _Vert.x_ 的运行机制和 _Verticle_ 的相关概念都有了进一步的了解

特别的 这是时隔一年半后 再次阅读 _Vert.x_ 文档

当时读文档的时候是大二 相关知识没有学 看得一头雾水

而现在看起来就没有那么费劲了

原来一年半真的可以学很多东西

---

