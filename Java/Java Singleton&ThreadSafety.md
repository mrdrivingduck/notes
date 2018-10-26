## Java - 单例模式及其线程安全

Created by : Mr Dk.

2018 / 10 / 26 13:15

Nanjing, Jiangsu, China

---

### Concept

* 一种常用的 __软件设计模式__
* 核心结构只包含一个被称为 __单例__ 的特殊类
* 模式保证整个系统中单例类 __只有一个实例化对象__

### Points & Ideas

* 该类只能有一个实例化对象
  * 只提供 __私有构造函数__ （类外部无法用 `new` 实例化对象）
* 该类的实例化对象必须自行创建
  * 该类内部维护一个 __静态私有__ 的实例化对象
* 该类必须能向整个系统提供这个实例化对象
  * 该类提供一个 __静态公有__ 的函数用于获取类内的实例化对象

#### 一种可能的实现：

```java
public class Single {
    // 唯一的实例化对象
    private static Single single = new Single();
    // 私有构造函数
    private Single() {}
    // 获取对象的唯一途径
    public static Single getInstance() {
        return single;
    }
}
```

```java
public class Test {
    public static void main(String[] args) {
        // 在系统中获取该类对象
        Single single = Single.getInstance();
    }
}
```

### Build Method

* 懒汉模式

  * 单例对象在 __第一次使用时__ 实例化

  * 在 `getInstance()` 函数中判断实例是否为 `null`

    * 实例不为 `null`，则直接返回实例
    * 实例为 `null`，则先实例化再返回

    ```java
    public static Single getInstance() {
        if (single == null) {
            // Instantiation
        }
        return single;
    }
    ```

* 饿汉模式

  * 单例实例在 __类装载时__ 实例化

  * 在内部单例对象声明时直接调用构造函数实例化

    ```java
    private static Single single = new Single();
    
    public static Single getInstance() {
        return single;
    }
    ```

  * _为何可以这样实现？_

    ```
    Java 类的生命周期：
    加载 -> 链接 -> 初始化 -> 使用 -> 卸载
    
    加载：
        JVM 识别 .class 文件
    链接：
        验证 - 确定该类是否符合 Java 语言规范
        准备 - 为 static 成员变量分配内存，并初始化为默认值
            基本类型默认初始化为 0
            引用类型默认初始化为 null
            由 static final 修饰的变量 直接赋值
        解析 - JVM 将所有符号引用转换为直接引用
    初始化：
        静态变量赋值
        顺序：
            先静态方法，后静态属性 ---> 这一特性支持了上述实现
            先父类，后子类
    使用：
        实例化
        垃圾收集
        对象终结
    卸载：
        类被 JVM 执行垃圾回收
    ```

### Situation

多线程（Multithread）场景

* 单例模式被多个线程使用时是否会出现问题？

#### Situation1 - Database 

希望使用同一个数据库连接 `java.sql.Connection conn`，进行多次的 `SQL` 查询

* 经过资料查阅，存在线程安全问题
* 需要使用 _数据库连接池_
* 之前 _cnsoft_ 项目中的写法可能有问题！
* 下次开发有关应用时再详细研究

#### Situation2 - HTTP Client

即将准备开发一个 _client_，不断向 `localhost` 上的 _Kismet server_ 上通过 `HTTP` 请求获取数据

* `Get` & `POST` 请求都有
* 请求频率会很高
* 每次实例化 `HttpClient` 影响性能，且没有必要

希望每次使用同一个 `HttpClient`，进行多次的 `GET` 和 `POST` 请求

* `Apache HTTP Components 4.5.2` 的文档指出，`HttpClient` 是线程安全的

```
HttpClient implementations are expected to be thread safe.
It is recommended that the same instance of this class is reused for multiple request executions.
```

* 思路
  * 在单例类中实例化一个 `HttpClient` 并初始化
  * 在系统中通过 `getInstance()` 获取到 `HttpClient` 实例，并执行 `HttpGet` 或 `HttpPost`

---

