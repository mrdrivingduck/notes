# Java - Condition and LockSupport

Created by : Mr Dk.

2020 / 10 / 31 13:43

Nanjing, Jiangsu, China

---

读 JDK 源代码时遇到了 `java.util.concurrent.locks.Condition` 类，不得其解。

## Monitor Object

每一个 Java 对象都有一组监视器函数，用于与对象锁和 `synchronized` 关键字配合，实现等待 / 通知模式。使用等待 / 通知模式时，前提是需要通过 `synchronized` 关键字获得对象的锁，没有获得到对象锁的线程将阻塞在 **同步队列** 上。调用 `wait()` 函数时，线程将进入等待状态，加入到一个 **等待队列** 中，并释放锁：

```java
synchronized (obj) {
    while (!condition) {
        obj.wait();
    }
    // ...
}
```

由于锁被释放，同步队列上的其它线程得以通过竞争获得对象锁，并进入临界区。存在一个线程调用 `notify()` 系列函数：

```java
synchronized (obj) {
    // ...
    obj.notify();
}
```

调用 `notify()` 系列函数后，会将等待队列上 (一个或多个) 等待时间最久的线程移入同步队列上阻塞，重新参与对象锁的竞争。在线程争取到对象锁后，从 `wait()` 函数处返回。

## Comparison

与 `synchronized` + `wait()` / `notify()` 机制类似，对于实现 `Lock` 接口的 JDK 锁对象，也提供了相应的 Condition 对象实现等待 / 通知模式。具体的使用方式类似，重点在于 Condition 对象是由 Lock 对象得到的：

```java
Lock lock = new ReentrantLock();
Condition condition = lock.newCondition();

public void conditionWait() throws InterruptedException {
    lock.lock(); // 占有锁
    try {
        condition.await(); // 等待
    } finally {
        lock.unlock(); // 确保锁被释放
    }
}

public void conditionSignal() throws InterruptedException {
    lock.lock();
    try {
        condition.signal();
    } finally {
        lock.unlock();
    }
}
```

在对象占有锁并调用 `condition.await()` 后，将会释放锁并进入等待队列；当另一个对象占有锁并调用 `condition.signal()` 后，正在等待中的线程将 **重新进入锁竞争状态**，当再次占有锁后，将从 `condition.await()` 返回。

两种等待 / 通知的实现方式有什么区别呢？

| Items                              | Object Monitor | Condition                                                                 |
| ---------------------------------- | -------------- | ------------------------------------------------------------------------- |
| 前置条件                           | 占据对象锁     | 调用 `Lock.newCondition()` 获取 Condition 对象；调用 `Lock.lock()` 获取锁 |
| 调用方式                           | `obj.wait()`   | `condition.await()`                                                       |
| 等待队列个数                       | 一个           | 多个 (一个 Condition 对象一个队列，一个 Lock 可以产生多个 Condition 对象) |
| 线程释放锁并等待                   | 支持           | 支持                                                                      |
| 线程释放锁并等待，等待时不响应中断 | 不支持         | 支持                                                                      |
| 线程释放锁并超时等待               | 支持           | 支持                                                                      |
| 线程释放锁并等待到将来某个时间     | 不支持         | 支持                                                                      |
| 唤醒等待队列中的一个线程           | 支持           | 支持                                                                      |
| 唤醒等待队列中的全部线程           | 支持           | 支持                                                                      |

## Implementation

每个 Condition 对象内都包含一个 **等待队列**。等待队列是一个 FIFO 队列，每个结点保存了线程引用，同时也维护着头结点和尾结点。当线程调用 `Condition.await()` 函数时，发生以下几件事：

1. 释放锁
2. 将当前线程构造为结点并加入等待队列
3. 线程进入等待状态

其中，`await()` 函数中移入队列的操作并不需要 CAS 操作，因为调用该函数的线程必定已经获取了锁，所以由锁来保证线程安全。

Object 监视器模型中，一个对象包含一个同步队列和 **一个等待队列**；而 JUC 中的 Lock 拥有一个同步队列和 **多个等待队列**。

从队列的角度来看，当调用 `Condition.await()` 函数时，相当于同步队列的头结点移入等待队列中：

```java
/**
 * Implements interruptible condition wait.
 * <ol>
 * <li> If current thread is interrupted, throw InterruptedException.
 * <li> Save lock state returned by {@link #getState}.
 * <li> Invoke {@link #release} with saved state as argument,
 *      throwing IllegalMonitorStateException if it fails.
 * <li> Block until signalled or interrupted.
 * <li> Reacquire by invoking specialized version of
 *      {@link #acquire} with saved state as argument.
 * <li> If interrupted while blocked in step 4, throw InterruptedException.
 * </ol>
 */
public final void await() throws InterruptedException {
    if (Thread.interrupted())
        throw new InterruptedException();
    Node node = addConditionWaiter();
    int savedState = fullyRelease(node);
    int interruptMode = 0;
    while (!isOnSyncQueue(node)) {
        LockSupport.park(this);
        if ((interruptMode = checkInterruptWhileWaiting(node)) != 0)
            break;
    }
    if (acquireQueued(node, savedState) && interruptMode != THROW_IE)
        interruptMode = REINTERRUPT;
    if (node.nextWaiter != null) // clean up if cancelled
        unlinkCancelledWaiters();
    if (interruptMode != 0)
        reportInterruptAfterWait(interruptMode);
}
```

调用 `Condition.signal()` 时，等待队列中等待时间最久的结点将会被移入同步队列中并唤醒。同时，函数还会检查当前线程是否获得锁的前提条件：

```java
/**
 * Moves the longest-waiting thread, if one exists, from the
 * wait queue for this condition to the wait queue for the
 * owning lock.
 *
 * @throws IllegalMonitorStateException if {@link #isHeldExclusively}
 *         returns {@code false}
 */
public final void signal() {
    if (!isHeldExclusively())
        throw new IllegalMonitorStateException();
    Node first = firstWaiter;
    if (first != null)
        doSignal(first);
}
```

被唤醒后的线程 (已经在同步队列中) 将会加入到获取同步状态的竞争中。`Condition.signal()` 与 `Condition.signalAll()` 的区别在于，`signalAll()` 相当于对等待队列中的每一个结点都调用一次 `signal()`。带来的效果是等待队列中的所有结点被移动到同步队列中，并唤醒原来在等待队列中的所有线程。

## Lock Support

`java.util.concurrent.locks.LockSupport` 中定义了一组公共静态函数，提供了基本的线程阻塞 / 唤醒功能。根据源码，基本是通过 `Unsafe` 类调用了 native JVM 函数实现的。

以下函数使当前线程休眠 (不被线程调度器调度)，函数将不会返回，直到以下条件发生：

1. 另一个线程对当前线程调用了 `unpark()`
2. 另一个线程对当前线程发出了中断信号
3. 调用没理由地返回了 😓

可以看到最终通过 `UNSAFE` 类将阻塞目标设置到了 _HotSpot_ 中当前线程的 `parkBlocker` 域上。

```java
private static void setBlocker(Thread t, Object arg) {
    // Even though volatile, hotspot doesn't need a write barrier here.
    UNSAFE.putObject(t, parkBlockerOffset, arg);
}

/**
 * Disables the current thread for thread scheduling purposes unless the
 * permit is available.
 *
 * <p>If the permit is available then it is consumed and the call returns
 * immediately; otherwise
 * the current thread becomes disabled for thread scheduling
 * purposes and lies dormant until one of three things happens:
 *
 * <ul>
 * <li>Some other thread invokes {@link #unpark unpark} with the
 * current thread as the target; or
 *
 * <li>Some other thread {@linkplain Thread#interrupt interrupts}
 * the current thread; or
 *
 * <li>The call spuriously (that is, for no reason) returns.
 * </ul>
 *
 * <p>This method does <em>not</em> report which of these caused the
 * method to return. Callers should re-check the conditions which caused
 * the thread to park in the first place. Callers may also determine,
 * for example, the interrupt status of the thread upon return.
 *
 * @param blocker the synchronization object responsible for this
 *        thread parking
 * @since 1.6
 */
public static void park(Object blocker) {
    Thread t = Thread.currentThread();
    setBlocker(t, blocker);
    UNSAFE.park(false, 0L);
    setBlocker(t, null);
}
```

另外还有超时版本和 DDL 版本：

```java
/**
 * Disables the current thread for thread scheduling purposes, for up to
 * the specified waiting time, unless the permit is available.
 *
 * <p>If the permit is available then it is consumed and the call
 * returns immediately; otherwise the current thread becomes disabled
 * for thread scheduling purposes and lies dormant until one of four
 * things happens:
 *
 * <ul>
 * <li>Some other thread invokes {@link #unpark unpark} with the
 * current thread as the target; or
 *
 * <li>Some other thread {@linkplain Thread#interrupt interrupts}
 * the current thread; or
 *
 * <li>The specified waiting time elapses; or
 *
 * <li>The call spuriously (that is, for no reason) returns.
 * </ul>
 *
 * <p>This method does <em>not</em> report which of these caused the
 * method to return. Callers should re-check the conditions which caused
 * the thread to park in the first place. Callers may also determine,
 * for example, the interrupt status of the thread, or the elapsed time
 * upon return.
 *
 * @param blocker the synchronization object responsible for this
 *        thread parking
 * @param nanos the maximum number of nanoseconds to wait
 * @since 1.6
 */
public static void parkNanos(Object blocker, long nanos) {
    if (nanos > 0) {
        Thread t = Thread.currentThread();
        setBlocker(t, blocker);
        UNSAFE.park(false, nanos);
        setBlocker(t, null);
    }
}

/**
 * Disables the current thread for thread scheduling purposes, until
 * the specified deadline, unless the permit is available.
 *
 * <p>If the permit is available then it is consumed and the call
 * returns immediately; otherwise the current thread becomes disabled
 * for thread scheduling purposes and lies dormant until one of four
 * things happens:
 *
 * <ul>
 * <li>Some other thread invokes {@link #unpark unpark} with the
 * current thread as the target; or
 *
 * <li>Some other thread {@linkplain Thread#interrupt interrupts} the
 * current thread; or
 *
 * <li>The specified deadline passes; or
 *
 * <li>The call spuriously (that is, for no reason) returns.
 * </ul>
 *
 * <p>This method does <em>not</em> report which of these caused the
 * method to return. Callers should re-check the conditions which caused
 * the thread to park in the first place. Callers may also determine,
 * for example, the interrupt status of the thread, or the current time
 * upon return.
 *
 * @param blocker the synchronization object responsible for this
 *        thread parking
 * @param deadline the absolute time, in milliseconds from the Epoch,
 *        to wait until
 * @since 1.6
 */
public static void parkUntil(Object blocker, long deadline) {
    Thread t = Thread.currentThread();
    setBlocker(t, blocker);
    UNSAFE.park(true, deadline);
    setBlocker(t, null);
}
```

当另一个线程对一个已经阻塞的线程调用了 `unpark()` 后，阻塞的线程将恢复被调度。

```java
/**
 * Makes available the permit for the given thread, if it
 * was not already available.  If the thread was blocked on
 * {@code park} then it will unblock.  Otherwise, its next call
 * to {@code park} is guaranteed not to block. This operation
 * is not guaranteed to have any effect at all if the given
 * thread has not been started.
 *
 * @param thread the thread to unpark, or {@code null}, in which case
 *        this operation has no effect
 */
public static void unpark(Thread thread) {
    if (thread != null)
        UNSAFE.unpark(thread);
}
```

---
