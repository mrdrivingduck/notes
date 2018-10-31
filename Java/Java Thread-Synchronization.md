# Java - 线程同步

Created by : Mr Dk.

2018 / 10 / 28 19:59

Nanjing, Jiangsu, China

---

### 1. About

使用 `synchronized` 关键字，可以对目标进行 __加锁__，从而实现 __线程同步__

### 2. Usage

#### 2.1 For code block

* 对 __当前对象__ 加锁

```java
synchronized(this) {
    // TO DO ...
}
```

* 对某一对象加锁

```java
synchronized(obj) {
    // TO DO ...
}
```

* 当多个线程访问 __同一个对象__ 的 `synchronized` 代码块时，同一时刻只有一个线程得到执行
* 当一个线程正在访问某对象的 `synchronized` 代码块时，别的线程可以访问该对象的非 `synchronized` 代码块而不受阻塞

#### 2.2 For function

* 对 __当前对象__ 加锁

```java
public synchronized void Function() {
    // TO DO ...
}

// 等价于
public void Function() {
    synchronized(this) {
        // TO DO ...
    }
}
```

__Attention__：

* `synchronized` 关键字不能被继承
  * 子类 _override_ 父类的 `synchronized` 函数时，默认是不同步的
  * 必须显式声明子类的函数为 `synchronized`，或调用父类的 `synchronized` 函数
* 定义 `Interface` 函数时不能使用 `synchronized` 关键字
* 构造函数不能使用 `synchronized` 关键字，但可以用 `synchronized` 修饰代码块进行同步

#### 2.3 For static function

* 对当前类的 __所有对象__ 加锁
* 相当于对 __类__ 加锁 - 类的所有对象都用这一把锁
  * 因为 `static` 函数属于 __类__ 而不属于 __对象__

```java
public synchronized static void Function() {
    // TO DO ...
}
```

#### 2.3 For class

* 对 __类__ 加锁 - 类的所有对象都用这一把锁

```java
class Test {
    public void Function() {
        synchronized(Test.class) {
            // TO DO ...
        }
    }
}
```

### 3. Summary

* 若 `synchronized` 关键字作用于 __类__ 或 __静态函数__，则取得 __类锁__，即类的所有对象共用同一把锁
* 其余情况，使用 `synchronized` 关键字取得的是 __对象锁__，每个对象都有一把锁
* 实现同步需要很大系统开销，甚至可能死锁 - 尽量避免无谓的同步控制

---

