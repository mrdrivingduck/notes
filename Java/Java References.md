# Java - References

Created by : Mr Dk.

2020 / 11 / 10 17:33

Nanjing, Jiangsu, China

---

理解并实验了 Java 中几种不同类型的引用及其特性。该问题来源于研究 JDK 源代码的 `ThreadLocal` 类时，其中的 `ThreadLocalMap` 使用的是所谓 _弱引用_。在 _马士兵_ 老师的 _多线程与高并发_ 书籍中找到了答案。

## Strong References

强引用就是默认的引用类型，任何被强引用的对象都不会被 GC，除非强引用变量被重新指向 `null`。做一个简单的小型实验：创建一个测试类，重写该类的 `finalize()` 函数。

> Java 会在 GC 对象时自动调用 `finalize()` 函数，重写该函数仅为观察对象的时机。实际上，该函数永远不用也不应该被重写。

```java
class TestReference {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("GC happened.");
    }
}
```

```java
TestReference r = new TestReference();
System.out.println("First GC trial.");
System.gc();
r = null;
System.out.println("Second GC trial.");
System.gc();
System.in.read(); // GC 在其它线程中进行，防止当前线程结束
```

得到的运行结果如下。可以看到，强引用只有在赋值为 `null` 后才会发生 GC。

```
First GC trial.
Second GC trial.
GC happened.
```

## Soft References

软引用需要被显式使用。对于被软引用的对象来说，JVM 在内存充裕时不会急着 GC 它；只有当 JVM 急需内存时，才会回收被软引用的对象。可以通过调低 JVM 的堆内存来测试：

```java
SoftReference<TestReference> r = new SoftReference<>(new TestReference());
System.gc();
System.out.println(r.get()); // maybe not null
// ... fulfill JVM's memory
System.out.println(r.get()); // maybe null
System.in.read(); // GC 在其它线程中进行，防止当前线程结束
```

这个特性可以用于实现 **缓存** - 如果内存够用，就保留对象用于提升性能；如果内存不够用，就回收缓存保证 JVM 有足够的内存正常运行。

## Weak References

弱引用需要被显式使用。如果 JVM 检测到一个对象 **只被弱引用** (没有任何强引用或软引用)，那么将会 GC 该对象。

```java
WeakReference<TestReference> r = new WeakReference<>(new TestReference());
System.out.println(r.get()); // not null
System.gc(); // GC
System.out.println(r.get()); // null
System.in.read(); // GC 在其它线程中进行，防止当前线程结束
```

这一特性主要体现在 Java 的 `ThreadLocal` 类中。该类在当前线程对象内维护一个称为 `ThreadLocalMap` 的 map，里面的 key 是弱引用的 `ThreadLocal` 对象，value 是想要保存在线程内部保存的局部变量。当线程用强引用实例化一个 `ThreadLocal` 对象并作为某个局部变量的 key 放入线程 map 中时，此时堆上的 `ThreadLocal` 对象被引用两次：

- 程序中的强引用
- 线程内的 `ThreadLocalMap` 弱引用

当程序中强引用所在的函数结束后，该引用作为函数内的局部变量 (栈上变量) 也消失了。此时，如果线程一直运行下去 (假设它是一个后台线程)，map 将一直对堆上的 `ThreadLocal` 对象保持引用。假设 map 持有的是强引用，那么 `ThreadLocal` 对象将一直不会被 GC，从而引发内存泄露；而如果这是个弱引用，那么堆上的 `ThreadLocal` 对象将会在原有强引用断开连接后被 GC。

一个例子。在这里，我实现了自己的 `ThreadLocal` 类，主要是重写了 `finalize()` 函数以观察 `ThreadLocal` 对象被 GC 的时机：

```java
class MyThreadLocal<T> extends ThreadLocal<T> {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("Thread local object GC happened.");
    }
}

class TestReference {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("Value object GC happened.");
    }
}
```

执行以下代码。将 `ThreadLocal` 对象设置到 `ThreadLocalMap` 中后，断开程序中对它的强引用，只剩下 `ThreadLocalMap` 中的弱引用，看看 `ThreadLocal` 对象会不会被 GC。

```java
MyThreadLocal<TestReference> threadLocal = new MyThreadLocal<>();
TestReference r = new TestReference();
threadLocal.set(r);
r = null; // No strong reference to value anymore.
System.out.println("First GC trial.");
System.gc();
threadLocal = null; // No strong reference to thread local anymore.
System.out.println("Second GC trial.");
System.gc();
System.in.read();
```

得到的运行结果，`ThreadLocal` 对象被 GC 了。

```
First GC trial.
Second GC trial.
Thread local object GC happened.
```

这里有件很蛋疼的事：虽然 map 中的 key 引用的堆上对象 (`ThreadLocal`) 已经被 GC 了而成为了 `null`，但是 value 对象并没有被 GC，依旧被 map 强引用 - 这样也会产生内存泄漏。`ThreadLocalMap` 的实现中其实已经考虑到了这个问题，在调用成员函数 `set()` / `get()` / `remove()` 时，会顺便对 map 中所有 key 为 `null` 的 value 进行清理。然而，极端情况下，如果这几个函数之后一直没有被调用，那么内存泄漏实际上一直存在。我们还是应当要有把任何不合理的事情扼杀在摇篮里的基本修养。当不再显式使用一个 `ThreadLocal` 对象时，主动调用 `remove()` 将其从当前线程的 map 中清除掉：

```java
MyThreadLocal<TestReference> threadLocal = new MyThreadLocal<>();
TestReference r = new TestReference();
threadLocal.set(r);
r = null; // No strong reference to value anymore.
System.out.println("First GC trial.");
System.gc();
threadLocal.remove(); // Remove the value from the thread local map.
threadLocal = null; // No strong reference to thread local anymore.
System.out.println("Second GC trial.");
System.gc();
System.in.read();
```

得到结果如下：

```
First GC trial.
Second GC trial.
Thread local object GC happened.
Value object GC happened.
```

## Phantom References

虚引用的构造函数至少需要两个参数：除了被引用的对象外，另一个参数是一个 **引用队列**。当引用的对象要被 GC 时 (`finalize()` 被调用后)，JVM 将会把引用放进队列中。如果在这个队列中检测到了变动，说明对象被 GC 了。对虚引用调用 `get()` 是取不到值的。

写不出实验代码了。虚引用主要用于管理堆外内存，也就是不在 GC 管理范围以内的内存。当 GC 发生后，通过检测引用队列，相当于可以通知程序显式释放堆外内存。

## References

马士兵 - 多线程与高并发 (2020 年第一版)

[GeeksforGeeks - Types of References in Java](https://www.geeksforgeeks.org/types-references-java/)

[CSDN - ThreadLocalMap 里的弱引用](https://blog.csdn.net/vicoqi/article/details/79743112)

---
