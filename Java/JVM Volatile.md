# JVM - Volatile

Created by : Mr Dk.

2020 / 05 / 15 11:56

Nanjing, Jiangsu, China

---

## Volatile 的基本功能

* 线程可见性
* 禁止指令重排序

### 线程可见性

Java 的内存模型 (JMM) 规定，堆内存有主内存与线程私有内存之分。线程 A 在访问内存时，从主内存中将值拷贝到线程私有内存中，并访问线程私有内存中的值。如果中途有另一个线程 B 修改了主内存中的值，线程 A 依旧访问线程私有内存，而不是主内存中的新值。私有内存只是 JMM 中的一个抽象概念，并不真实存在，可能涵盖缓存、写缓冲、寄存器等硬件。

`volatile` 修饰主内存中的值，保持该值的线程可见性。该关键字使得线程每次访问该值时，都需要将值从主内存中读到私有内存才能访问；当线程修改该值后，也立刻将其刷新到主内存中。由缓存一致性协议保证。

### 禁止指令重排序

为什么会有指令重排序？当 CPU 在进行一些相对较慢的操作 (访问内存) 时，在等待内存响应的过程中，可以先执行之后的一些无关指令 (没有数据依赖)，从而提升效率。如果在某些场合下没有禁止指令重排序，可能会带来问题。JVM 规范中，有八种需要禁止指令重排序的场景 (happens-before)，除这八个场景外，指令可以重排序以优化性能：

* Load-Load 重排序
* Load-Store 重排序
* Store-Store 重排序
* Store-Load 重排序

不同 CPU 对于重排序的支持不同，不过常用的 CPU 基本上都支持 Store-Load 重排序 (指令先写后读 → 内存先读后写)，不允许数据依赖重排序。

> 现代 CPU 普遍使用 **写缓冲区** 临时保存向内存写入的数据：
>
> * 避免 CPU 停顿等待向内存写入数据
> * 合并写缓冲区对同一内存地址的多次写，减少对内存总线的占用
>
> 但是每个 CPU 核心的写缓冲区只对自身可见，其它核心不可见。因此执行写指令 + 读指令体现为写入写缓冲区 + 从内存中读取 + 写缓冲区写回内存，因此表现为先读后写，即重排序。

为了保证内存的线程可见性，Java 编译器会在生成指令序列的适当位置插入 **内存屏障指令** 以禁止特定类型的指令重排序。JMM 规定的内存屏障包含四类：

| Memory Barrier      | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| Load-Load Barrier   | 确保屏障前 load 指令的装载先于屏障后 load 指令的装载         |
| Store-Store Barrier | 确保屏障前 store 指令刷新到主内存后，屏障后的 store 指令才刷新到主内存 |
| Load-Store Barrier  | 确保屏障前 load 指令先装载，然后屏障后的 store 指令才刷新到主内存 |
| Store-Load Barrier  | 确保屏障前的 store 先刷新到主内存，然后屏障后的 load 指令才装载数据 |

其中，Store-Load 屏障同时具备其它三个屏障的效果，同时有着最昂贵的开销。现在的多核 CPU 基本都支持这个屏障。

> CPU 中的写缓冲区我觉得可以类比为磁盘与内存之间的缓冲区问题，简而言之就是读比写快很多。所以 MySQL 中会有 insert buffer 用于合并对于同一个磁盘页的多次写操作，从而减少 I/O 次数 - 就是因为将脏页写回内存的速度远远慢于从内存读取数据的速度。

### 指令重排序引发的问题

一个对象的创建过程 (字节码)：

* `new` (分配对象占用的内存) (**成员变量被赋值为默认值**)
* `dup`
* `invokespecial <T.<init>>` (调用对象构造函数) (**成员变量被赋值为指定值**)
* `astore_1` (将对象的引用与对象的内存建立关系 (`Object o != null`))
* `return`

单例模式的分类：

* 饿汉式单例模式：(不管实例会不会被使用都会被实例化)

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

* 懒汉式单例模式：(实例不被使用就不会被实例化)

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

Volatile 底层通过 **内存屏障 (Memory Barrier)** 来实现，其内存语义为：

* 写 volatile 变量时，JMM 将线程私有内存中的共享变量刷新到主内存
* 读 volatile 变量时，JMM 将私有内存中的变量置为无效，重新从主内存中读取共享变量

对于 volatile 写操作来说，需要保证的是：

1. 在 volatile 写操作之前，其它写操作已经完成 (不允许其它写操作重排序到 volatile 写之后)
2. 在 volatile 写操作完成之后，之后的读写操作才可以继续进行 (不允许其它读写操作重排序到 volatile 写之前)

由此可以推导出 volatile 写的内存屏障实现方式：

```
Store-Store barrier --> volatile write --> Store-Load barrier
```

对于 volatile 读操作来说，需要保证的是：

1. 在 volatile 读操作之前，其它写操作已经对所有 CPU 可见
2. 在 volatile 读操作之后，其它读写操作才可以继续进行

理论上，第一点需要一个 Store-Load 屏障，第二点需要 Load-Load 屏障 + Load-Store 屏障。但是之前的 volatile 写操作的后面已经加上了 Store-Load 屏障，所以第一点实际上就不需要额外的屏障指令了。

> Store-Load 屏障其实既可以加在 volatile 写操作的后面，也可以加在 volatile 读操作的前面。但是，大部分 `volatile` 的使用场景是一个线程写，多个线程读，所以把屏障加在写操作后面能够带来可观的效率提升。JMM 的实现遵循的原则：尽可能保守，以确保正确；在正确的前提下追求效率。

由此推导出 volatile 读的内存屏障实现方式：

```
[Store-Load barrier] (optional) --> volatile read --> (Load-Store + Load-Load) barrier
```

之后，对于不同的 CPU 提供的不同松紧度的内存模型，内存屏障指令的插入还可以根据具体的 CPU 而继续优化。比如，x86 CPU 只会做 **写 - 读重排序**，那么只需要在 volatile 写操作之后加上 Store-Load 屏障即可。因此，x86 架构下 volatile 写的开销会比 volatile 读的开销大很多。

HotSpot JVM 使用 `lock addl` 指令实现了所有功能。因为这条指令的行为能够实现上述的屏障功能。当然，也可以通过其它指令来实现屏障。

## 缓存一致性协议

当一个共享变量被并发操作时，肯定存在于多个 CPU 核心的 cache 中。如何保证它们的一致性？在 Java 中，被 `volatile` 变量修饰的共享变量进行写操作时会多出汇编代码，完成如下功能：

1. 修改 cache line 中的数据后，将数据写回内存
2. 写回内存的操作使得其它核心的 cache line 中该内存地址的数据 **无效**

从实现上来说，维护共享变量的一致性可以有两种方式：

* 锁总线 - 某个核心独占共享内存，其它核心的操作将被阻塞 - 开销较大，其它核心的无关操作也会被阻塞
* 锁缓存 - 锁定共享内存对应的缓存，强令这块缓存写回内存，同时其它缓存副本无效

锁缓存是由 **缓存一致性协议** 保证的。每个 CPU 核心通过嗅探总线上传播的数据，检查自己 cache 中的数据是否过期。这样，多个 CPU 核心不会同时修改由两个以上 CPU 缓存的内存数据。Intel 系列处理器使用 *MESI* 缓存一致性协议：

* Modified
* Exclusive
* Shared
* Invalid

处理器使用总线嗅探技术保证核心内部缓存、系统内存、其它核心缓存保持一致。

## Cache Line

根据程序和数据的 **局部性原理**，CPU 一次性将一块数据读入 cache，这种块单位被称为 cache line，大小为 64B (工业实践经验)。一般来说一级缓存和二级缓存由每个 CPU 核心独占，三级缓存由多个 CPU 核心共享。

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

这种写法有两个前提：

1. 缓存行大小为 64B
2. 共享变量不会被频繁写 - 因为只有写操作才会锁缓存

---

