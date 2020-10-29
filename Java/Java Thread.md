# Java - Thread

Created by : Mr Dk.

2020 / 10 / 29 17:11

Nanjing, Jiangsu, China

---

## Java Thread

Java 程序天生就是多线程程序，在启动一个普通的 Java 程序时，将起码包含以下线程：

1. Main 线程 - 用户程序入口
2. Reference Handler - 清楚引用的线程
3. Finalizer - 调用对象 finalize 函数的线程
4. Signal Dispatcher - 分发处理发送给 JVM 进程信号的线程

## Thread Priority

在 Java 线程中，通过整形成员变量 `priority` 来控制线程优先级，取值范围为 1 - 10。在线程创建的时候可以使用 `setPriority(int)` 函数来修改默认的优先级 `5`。在不同 JVM 和 OS 上，线程的规划会存在差异，有些 OS 甚至会忽略对线程优先级的设定 - 因此线程优先级 **不能作为程序正确性的依赖**。

## Thread Status

Java 线程在生命周期中只可能有如下几种状态：

* `NEW` - 初始状态，刚刚被创建，还没有调用 `start()` 函数
* `RUNNABLE` - 运行状态，笼统地包含 OS 中的 **就绪** 和 **运行** 两种状态
* `BLOCKED` - 阻塞状态，线程阻塞于锁
* `WAITING` - 等待状态，需要等待其它线程做出一些特定的动作 (通知 / 中断)
* `TIME_WAITING` - 超时等待，在指定时间内自行返回
* `TERMINATED` - 终止状态，线程执行完毕

Daemon 线程工作在程序后台进行调度和支持工作，但是 JVM 退出时 Daemon 线程中的 `finally` 块不一定会被执行，所以不能依靠 `finally()` 来进行资源关闭或清理。

## Start / Stop

### Build

线程对象在构造时需要提供属性：

* 所属线程组
* 线程优先级
* 是否是 daemon 线程
* ...

一个新构造的线程对象由其 parent 线程进行空间分配，并继承了 parent 线程的大部分信息，但是会获得一个唯一的 ID 来标识这个线程。至此，线程对象就在堆上初始化完毕等待运行。

### Start

线程对象初始化完毕后，调用 `start()` 即可启动线程。具体含义是 parent 线程 (即调用 `start()` 的线程) 告知 JVM 的线程调度器可以启动该线程。

### Interrupt

中断可以理解为线程的一个 **标志位** 属性，表示线程是否被其它线程中断过。当其它线程通过调用该线程的 `interrupt()` 可以将该线程的中断标志位置为。线程可以通过 `isInterrupted()` 函数检查自身的中断标志位来对中断进行响应，还可以调用 `Thread.interrupted()` 对当前线程的中断标志位进行 **复位**。

### Suspend / Resume / Stop

这些是 **过时** 的线程 API：

* `suspend()` - 暂停线程
* `resume()` - 线程继续工作
* `stop()` - 停止线程

这些 API 过期的原因有，对于 `suspend()` 来说，在调用后线程不会释放已经占有的资源，而是占着资源进入睡眠状态，这样很容易引发死锁；类似地，`stop()` 终结线程时，没有给予线程完成资源释放工作的机会，从而无法保证资源的正常释放。

上面提到的中断实际上是一种安全而优雅的停止线程的方式 - 线程只需要检查自身的中断标志位就可以决定是否停止。

## Inter-Thread Communication

### Synchronized

对于 `synchronized` 函数块来说，JVM 使用 `monitorenter` 和 `monitorexit` 指令实现同步；对于 `synchronized` 函数来说，则是依靠函数修饰符上的 `ACC_SYNCHRONIZED` 实现。本质上，是对一个对象的 monitor 进行排他获取。任意一个对象都有自己的 monitor。在进入 `synchronized` 修饰的代码时，线程需要获取到锁对象的 monitor 才能进入临界区，其它线程将会被 **阻塞** 在临界区的入口处，进入 `BLOCKED` 状态。

当线程进入 `BLOCKED` 状态后，将会进入到相应对象的 **同步队列 (Synchronized Queue)** 中。当锁对象被线程释放后，释放操作将会唤醒阻塞在同步队列中的线程，使这些线程重新尝试对锁对象的 monitor 进行获取。

### Wait / Notify

线程 A 调用了对象 O 的 `wait()` 函数后进入 `WAITING` 状态，线程 B 调用对象 O 的 `notify()` / `notifyAll()` 函数后，线程 A 将从 `wait()` 函数返回进行后续工作。使用细节：

1. 使用 `wait()` / `notify()` / `notifyAll()` 时 **需要对调用对象加锁**
2. 调用 `wait()` 后，线程状态由 `RUNNING` 变为 `WAITING`，**放弃锁** 并进入 **等待队列 (Wait Queue)**
3. 调用 `notify()` / `notifyAll()` 后，等待线程暂时不会从 `wait()` 返回 (因为锁还在调用 `notify()` 的线程手上)
4. `notify()` 函数将等待队列中的一个等待线程移入同步队列；`notifyAll()` 函数将等待队列中的全部线程都移入同步队列，被移动的线程状态由 `WAITING` 变为 `BLOCKED`
5. 调用 `notify()` 的线程释放锁后，某个之前正在等待的线程重新获得了锁，此时才会从 `wait()` 返回并继续向下进行

等待方的编程范式：

```java
synchronized (lock) { // 获取对象锁
    while (!condition) { // 条件不满足，每轮等待要重新检查等待条件
        lock.wait(); // 等待
    }
    // lock TO DO ...
}
```

通知方的编程范式：

```java
synchronized (lock) {
    // condition TO DO ...
    lock.notifyAll();
}
```

### Pipe

另外，线程间还可以通过 `PipedOutputStream` / `PipedInputStream` / `PipedReader` / `PipedWriter` 来创建两个线程之间的管道进行通信。这类流都需要调用 `connect()` 函数将输入流和输出流绑定，否则将会抛出异常。

### Thread.join()

如果线程 A 中执行了 `thread.join()`，代表线程 A 将等待 `thread` 线程终止后，才会从这个函数返回；另外，这个函数还有超时版本。通过线程 A 调用的 `thread.join()` 的源代码来看看线程 A 是如何等待的：

```java
/**
  * Waits at most {@code millis} milliseconds for this thread to
  * die. A timeout of {@code 0} means to wait forever.
  *
  * <p> This implementation uses a loop of {@code this.wait} calls
  * conditioned on {@code this.isAlive}. As a thread terminates the
  * {@code this.notifyAll} method is invoked. It is recommended that
  * applications not use {@code wait}, {@code notify}, or
  * {@code notifyAll} on {@code Thread} instances.
  *
  * @param  millis
  *         the time to wait in milliseconds
  *
  * @throws  IllegalArgumentException
  *          if the value of {@code millis} is negative
  *
  * @throws  InterruptedException
  *          if any thread has interrupted the current thread. The
  *          <i>interrupted status</i> of the current thread is
  *          cleared when this exception is thrown.
  */
public final synchronized void join(long millis)
    throws InterruptedException {
    long base = System.currentTimeMillis();
    long now = 0;

    if (millis < 0) {
        throw new IllegalArgumentException("timeout value is negative");
    }

    if (millis == 0) {
        while (isAlive()) {
            wait(0);
        }
    } else {
        while (isAlive()) {
            long delay = millis - now;
            if (delay <= 0) {
                break;
            }
            wait(delay);
            now = System.currentTimeMillis() - base;
        }
    }
}
```

对于非定时版本来说，`millis` 参数会传入 `0L`，那么函数实际有效的逻辑只有：

```java
while (isAlive()) {
    wait(0);
}
```

也就是不断判断 `thread` 线程是否还存活，如果还存活，就继续等待。当 `thread` 线程自身终止时，将会调用自身的 `notifyAll()` 函数，从而通知所有等待该线程终止的线程 (包括线程 A)。

### ThreadLocal

> 下次单独研究 👶

## Timeout Waiting

如何在 wait / notify 编程范式中加入超时等待的功能？定义变量：

* 剩余等待时间 `remaining = T` (初始化)
* 超时时间 `future = now + T`

那么只需要对等待 `remaining` 的时间即可。如果中途线程被唤醒，那么需要重新计算一下剩余等待时间：

* 如果剩余等待时间还有，那么继续 wait
* 如果剩余等待时间已过，那么退出

```java
public synchronized Object get(long mills) throws InterruptedException {
    // 隐式对当前对象加锁
    
    long future = System.currentTimeMillis() + mills; // 超时时间
    long remaining = mills; // 剩余时间
    
    // 结果还未满足，且还有剩余时间
    while ((result == null) && remaining > 0) {
        wait(remaining); // 等待
        remaining = future - System.currentTimeMillis(); // 被唤醒后重新计算剩余时间
    }
    
    // 结果已满足 OR 剩余时间已经耗尽
    // 返回结果
    return result;
}
```

---

