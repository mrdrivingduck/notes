# Java - Lock

Created by : Mr Dk.

2019 / 12 / 26 14:20

Nanjing, Jiangsu, China

---

结合最近阅读 JDK 源码 Lock 部分的一些体会

总结一下 Java 中几种不同概念的锁的区别

(反正以后面试也会问到)

---

## Exclusive Lock && Shared Lock

这两个概念已经在 JDK 的锁实现中得到了体现

在 Java 中除了使用 `synchronized` 关键字进行线程同步外

另外实现了两个锁对象:

* ReentrantLock - 可重入锁
* ReadWriteLock - 读写锁

这两个锁对象的具体功能，在读到它们的源代码时再具体分析

但从区别上讲，ReentrantLock 只能被一个线程持有，互斥访问

而 ReadWriteLock 中读锁是共享锁 (多个线程可以同时读取)

---

## 公平 && 非公平

锁的底层包含一个带有内部 FIFO 队列的 __AQS (AbstractQueuedSynchronizer)__

* 通过对内部 `volatile` 状态变量的原子性读写来维护同步状态和等待线程

如果线程严格按照队列中的 FIFO 顺序依次获得锁，那么就很公平

* 由于严格按照排队顺序，线程不会产生饥饿，因为迟早会轮到它的
* 吞吐率较低，因为严格维护队列，那么入队出队时就会发生线程的休眠和唤醒

非公平锁的含义就是，上来就直接试图占有锁，如果没有成功，再进入队列等待

* 由于线程有概率不休眠而直接获得锁，吞吐率比公平锁高
* 已经处在等待队列上的线程可能因为一直被插队而产生饥饿

在实例化一个锁时，可以带一个参数决定是否实例化为公平锁

具体公平与非公平如何实现，还是看了源代码再作分析

AQS 提供了管理一个原子的状态信息及其等待队列的框架

而这个状态信息具体被如何使用，是继承该框架并实现具体功能的锁决定的

* Semaphore 用这个状态变量来表示剩余数量
* ReentrantLock 用这个状态变量表示拥有它的线程请求了多少次锁
* ......

---

## 乐观 && 悲观

> 首先回顾之前看 Linux 内核同步时
>
> __自旋锁__ 和 __信号量__ 的区别
>
> 在遇上临界区竞争时
>
> 首先想到的应该是使线程休眠并等待
>
> 但是线程的休眠和唤醒是有时间代价的
>
> 如果等待的时间比这个时间代价短
>
> 那还不如直接干等着呢
>
> 这就是 Spin Lock (自旋锁)
>
> 说白了就是浪费一点点的 CPU 时间

这里悲观和乐观的概念，针对的实体就是锁的争用

所谓悲观，就是指 __对锁的竞争成功持悲观态度__

* 当锁的争用较为严重时，竞争成功的概率就相对较低

因此，悲观锁在实现上一旦发现竞争失败，就使线程进入阻塞等待状态

Java 的 `synchronized` 关键字就是悲观锁的典型

* 与 Linux 内核中的信号量类似，涉及线程状态和上下文切换，带来一定的时间开销

乐观，即 __对锁的竞争成功持乐观态度__

* 当锁的争用不怎么严重时，竞争成功的概率较高

乐观锁一旦竞争失败，会很乐观地相信再过会儿就能获得锁

因此会进行自旋等待 (不睡眠)

独占锁是一种悲观锁的设计策略

而共享锁则一种乐观锁的设计策略

### CAS Mechanism

乐观锁在实现上使用了 __CAS (Compare And Swap)__ 机制

CAS 的三个基本参数:

* 内存地址 V
* 旧的预期值 A
* 新的预期值 B

算法机制为: __当内存地址 V 中的变量的值为 A 时，将其更新为 B (成功)；否则不更新 (失败)__

当一个线程发现 V 中的变量不为 A

说明有其它的线程也在修改 A，本次 CAS 操作失败

线程进入自旋重试 CAS 操作:

```java
while (compareAndSwap(V, A, B)) {
    ;
}
```

直到若干次 CAS 操作后，CAS 操作成功

CAS 的原子性由 CPU 的指令保证

* CPU 提供的测试、交换指令保证了原子性 - 比如 x86 的 `XCHG`
* CAS 具体实现于 `sun.misc.Unsafe.compareAndSwapInt()` 中
    * 应当是由 JVM 甚至说是 OS 来负责实现

CAS 机制的特点:

1. 线程不睡眠
2. 自旋具有一定的 CPU 开销
3. 只能保证一个变量的原子性操作

Java 中原子变量就是通过 CAS 机制实现的:

```bash
$ ls java/util/concurrent/atomic
AtomicBoolean.java              AtomicLongArray.java          AtomicReferenceFieldUpdater.java  LongAdder.java
AtomicInteger.java              AtomicLongFieldUpdater.java   AtomicStampedReference.java       Striped64.java
AtomicIntegerArray.java         AtomicMarkableReference.java  DoubleAccumulator.java            package-info.java       AtomicIntegerFieldUpdater.java  AtomicReference.java          DoubleAdder.java
AtomicLong.java                 AtomicReferenceArray.java     LongAccumulator.java
```

### ABA 问题

CAS 机制下，如果一个值从 A 变为 B，又从 B 变为 A

那么 CAS 会认为值没有发生变化

具体可以看一看 `java/util/concurrent/atomic/AtomicStampedReference` 是怎么解决这个问题的

---

## References

https://www.jianshu.com/p/ae25eb3cfb5d

https://www.cnblogs.com/fengzheng/p/9018152.html

https://blog.csdn.net/weixin_38035852/article/details/82081674

https://www.cnblogs.com/wuzhenzhao/p/10256225.html

---

## Summary

以前在 Java 中只用过 `synchronized` 关键字来实现线程同步

现在了解了更多的方法

先搞清原理，之后读完它们的源码

就可以根据具体场景选择性能更好的同步机制

---

