# JVM - Volatile

Created by : Mr Dk.

2020 / 05 / 15 11:56

Nanjing, Jiangsu, China

---

## Volatile 的基本功能

* 线程可见性
* 禁止指令重排序

### 线程可见性

JVM 有主内存与线程私有内存之分。线程 A 在访问内存时，从主内存中将值拷贝到线程私有内存中，并访问线程私有内存中的值。如果中途有另一个线程 B 修改了主内存中的值，线程 A 依旧访问线程私有内存，而不是主内存中的新值。

`volatile` 修饰主内存中的值，保持该值的线程可见性。该关键字使得线程每次访问该值时，都需要将值从主内存中读到私有内存才能访问；当线程修改该值后，也立刻将其刷新到主内存中。

### 禁止指令重排序

为什么会有指令重排序？当 CPU 在进行一些相对较慢的操作 (访问内存) 时，在等待内存响应的过程中，可以先执行之后的一些无关指令，从而提升一些效率。如果在某些场合下没有禁止指令重排序，可能会带来问题。JVM 规范中，有八种需要禁止指令重排序的场景 (happens-before)，除这八个场景外，指令可以重排序。

#### 对象的创建过程 (字节码)

* `new` (分配对象占用的内存) (**成员变量被赋值为默认值**)
* `dup`
* `invokespecial <T.<init>>` (调用对象构造函数) (**成员变量被赋值为指定值**)
* `astore_1` (将对象的引用与对象的内存建立关系 (`Object o != null`))
* `return`

#### 单例模式

饿汉式单例模式：(不管实例会不会被使用都会被实例化)

```java
public class Single {
    private static final Single INSTANCE = new Single();

    private Single() {}

    public static Single getInstance() {
        return INSTANCE;
    }

    /**
     * ......
     */
}
```

懒汉式单例模式：(实例不被使用就不会被实例化)

```java
public class Single {
    private static Single INSTANCE;

    private Single() {}

    public static Single getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new Single();
        }
        return INSTANCE;
    }
}
```

对于懒汉式的单例模式，在多线程场景下，如何保证创建的对象唯一？或许可以给 `getInstance()` 加 `synchronized` 关键字，但是锁的粒度太粗 (万一该函数中除了实例化对象以外，还有一些不需要同步的业务逻辑呢？)。改进：

```java
public static Single getInstance() {
    if (INSTANCE == null) {
        synchronized (Single.class) {
            INSTANCE = new Single();
        }
    }
    return INSTANCE;
}
```

但是这种情况还是会有问题。当线程 A 通过了 `INSTANCE == null` 的条件后，线程 B 也通过了该条件并成功获得锁创建了对象，并释放了锁；此时线程 A 又会获得锁并创建一个新的实例。

显然，在进入临界区以后，需要再次判断实例是否为空，如果还是为空，再进行实例化。因此最终的改进版又被称为 Double Check Lock (DCL)：

```java
public static Single getInstance() {
    if (INSTANCE == null) {
        synchronized (Single.class) {
            if (INSTANCE == null) {
                INSTANCE = new Single();
            }
        }
    }
    return INSTANCE;
}
```

其中，外面的 `INSTANCE == null` 可以防止在每次调用 `getInstance()` 时都进入 `synchronized` 块进行同步，损失性能 (试想如果没有外面这个 `if` 的情况)；内部的 `INSTANCE == null` 用于保证只实例化一个对象。那么，`INSTANCE` 是否需要加 `volatile` 呢？如果要，为什么呢？

```java
public class Single {
    private static volatile Single INSTANCE; // ?

    private Single() {}

    public static Single getInstance() {
        if (INSTANCE == null) {
            synchronized (Single.class) {
                if (INSTANCE == null) {
                    INSTANCE = new Single();
                }
            }
        }
        return INSTANCE;
    }
}
```

此时，只关注对象创建过程中的三条字节码：

1. `new`
2. `invokespecial <T.<init>>`
3. `astore_1`

假设发生了如下形式的重排序：

1. `new`
2. `astore_1`
3. `invokespecial <T.<init>>`

当进行对象实例化的线程 A 执行完 2 时，另一个线程 B 在判断 `INSTANCE == null` 时会发现此时 `INSTANCE` 不为空了，那么线程 B 就认为对象已经实例化完毕，可以直接使用了。而实际上此时对象的构造函数还没有被调用，对象中的成员变量全部都是默认值 `0`，如果直接使用这个半初始化的对象会有问题。因此，`INSTANCE` 对象需要修饰为 `volatile`，禁止对这段内存的访问进行指令重排序，从而保证实例被初始化完成后才能被使用。

## Volatile 的底层实现

Volatile 底层通过 **内存屏障 (Memory Barrier)** 来实现。内存屏障是用于禁止指令重排序的指令。JVM 级别的内存屏障与 CPU 级别的内存屏障是不一样的。JVM 规定需要实现的内存屏障包含：

* Load-Load 屏障 - 两条 Load 指令不可以重排序
* Store-Store 屏障 - 两条 Store 指令不可以重排序
* Load-Store 屏障 - 一条 Load 指令与一条 Store 指令不可以重排序
* Store-Load 屏障 - 一条 Store 指令与一条 Load 指令不可以重排序 (保证 Store 指令对所有 CPU 可见)

对于 `volatile` 内存的 **写** 操作，在其之前加入 Store-Store 屏障，在其之后加入 Store-Load 屏障；对于 `volatile` 内存的 **读** 操作，在其之前加入 Store-Load 屏障，在其之后加入 Load-Store 屏障。

HotSpot JVM 使用 `lock addl` 指令实现了所有功能。因为这条指令的行为能够实现上述的屏障功能。当然，也可以通过其它指令来实现屏障。

## C 语言级别 (CPU 级别) 的 volatile

与 Java 的 `volatile` 无关。

### MESI Cache (Intel x86)

* Modified
* Exclusive
* Shared
* Invalid

使得不同的 CPU 核心之间能够互相通知缓存状态变化的缓存一致性协议。

## Cache Line

根据程序和数据的 **局部性原理**，CPU 一次性将一块数据读入 cache，这种块单位被称为 cache line，大小为 64 B (工业实践经验)。

### 消除伪共享

两个线程在访问同一 cache line 中的非共享数据时，会导致彼此的 cache line 不停地失效，因此两个线程需要不断从内存中重新拷贝新的 cache line，影响了性能。如果强行使两个线程要访问的数据位于不同的 cache line 中，就能避免这种情况了。比如，对于一个 RingBuffer，假设 head 与 tail 位于同一个缓存行中，生产者线程在 tail 产生资源，消费者线程在 head 消费资源，两个线程就会频繁使得对方的 cache line 失效。

有一种很牛啤的代码写法：

```java
protected long p1, p2, p3, p4, p5, p7, p7;
public long xxx;
protected long p9, p10, p11, p12, p13, p14, p15;
```

这样就使得中间的数据在任何情况下都不会与其它的数据共存于同一个缓存行中，从而消除了伪共享。在 JDK 1.8 中，用 `@sun.misc.Contended` 注解修饰一个类时，会使这个类的成员变量位于不同的 cache line，从而省略了上述的写法。

> 使用上述注解需要打开 JVM 的 `-XX:-RestrictContended` 选项。

---

