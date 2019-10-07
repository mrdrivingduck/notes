# Java - Deep Copy

Created by : Mr Dk.

2019 / 10 / 07 20:12

Nanjing, Jiangsu, China

---

## About

最近在用 Java 实现一个 Fuzzer 时

其中的一些算法需要对对象进行拷贝

之前写 Vue 的时候，都是直接 `JSON.parse()` + `JSON.stringfy()` 完事了

对于 Java 应该怎么处理不是太了解

于是搜索了一波 🙄 名堂还真不少

但至少可以明确的一点是，`JSON` 不是 Java 的原生支持

所以方法显然不是转成 JSON 字符串再转回来

---

## Clone Function

首先，Java 中的所有对象全部继承自 `java.lang.Object`

在这个 root superclass 中，定义了一个 `clone()` 函数

因此任何派生类都可以 override 这一个 `clone()` 函数

该函数的默认行为是 - 返回一个对象的浅拷贝

* 即，复制该对象中的每一个 field
* 对于 __原始数据类型__ (`int`, `float`) 或 __不可改变的类型__ (`String`) 来说，复制的是值
* 对于对象来说，复制的是引用 - (我宁愿把它理解为，复制的是指针) - 就是说，只是复制了指针，指针变成了两个，但指向的区域还是同一个

浅拷贝的问题显而易见，如果 __修改__ (只读应该不会有问题) 这个复制后的对象中的对象引用，相当于被复制对象中的该引用也有问题

例子：

```java
Vector original = new Vector();
StringBuffer text = new StringBuffer("A");
original.addElement(text);

Vector clone = (Vector) original.clone();
```

实例化一个 `Vector` 对象，并将一个 `StringBuffer` 对象作为元素加入到该对象中 (引用传递)

然后浅拷贝一个 `Vector` 对象

显然，通过两个对象都可以访问到 `StringBuffer` 对象，克隆看起来是成功的

```java
clone.addElement(new Integer(5));
```

此时，访问这两个对象， `clone` 可以访问到 `Integer`，而 `original` 不行

因为这两个 `Vector` 现在确实是两个独立的对象了

`clone` 对象持有对 `Integer` 对象的引用，而 `original` 对象没有

```java
text.append("EMMM");
```

此时，通过两个 `Vector` 对象访问 `text`

发现两个对象中的 `text` 对象都变了

因为这两个 `Vector` 对象持有对同一个 `StringBuffer` 对象的引用

> 也就是说，浅拷贝只是复制了 "指针"，而指针指向的对象没有被复制
>
> 因此，通过 `origin` 对象修改了 `StringBuffer` 对象后
>
> 通过 `clone` 对象访问 `StringBuffer` 对象时，能够看到修改

so. 如果业务逻辑需要的是把 `StringBuffer` 对象也复制两份

即需要进行所谓的 __deep copy__ ，how to do it?

---

## Issues

或许可以自己实现一个 `deepCopy()` 函数，以完成复杂的深拷贝功能？

1. 必须有这个类的源代码才行
   * 如果想复制一个第三方的类，或许可能被声明为 `final` - Well...GG 😥
2. 必须能够访问这个类的基类的所有 field
   * 如果基类的 field 被声明为 `private` - Well...GG again 😥
3. 必须能够拷贝该类引用的所有类型的对象才行
   * 但有些类型只有在运行时才能被明确
4. 很容易出错，难于维护
   * 一旦这个类的结构被改动了，都要检查一遍这个函数

此外，覆盖 `clone()` 函数在 _StackOverFlow_ 上也不被推荐

* 深度复制应当是一个递归的过程
* 至少，在实现 `clone()` 函数时，该对象引用的所有类型的对象也应当都覆盖 `clone()`
* 不然总会有被该类引用的对象是浅拷贝

> emm... 🤔 有道理啊

---

## Solution

所以常用的解决方案是使用 _Java Object Serialization (JOS)_

即，序列化和反序列化

从字节层面，把整个对象复制一份

更重要的是，JOS 负责其中的所有细节：

* 父类中的 field
* 跟随 object graphs 并能够递归地复制引用的所有对象

> 意思是只管序列化 / 反序列化就行，不用管嵌套对象的问题？

```java
Object orig;
Object obj = null;

ByteArrayOutputStream bos = new ByteArrayOutputStream();
ObjectOutputStream out = new ObjectOutputStream(bos);
out.writeObject(orig);
out.flush();
out.close();

ObjectInputStream in = new ObjectInputStream(
    new ByteArrayInputStream(bos.toByteArray()));
obj = in.readObject();
```

但也存在问题：

* 被拷贝的对象 (包括嵌套在内的) 必须实现 `java.io.Serializable` - 即，必须是可序列化的

  > 那第三方的对象万一无法被序列化咋办呢？
  >
  > 它没有实现 `java.io.Serializable` 接口
  >
  > 我还要修改它的源代码不成？？

* JOS 比较慢

* Byte array stream 的实现是 __线程安全__ 的，因此会有一些额外的开销

可能的优化方式：

1. `ByteArrayOutputStream` 默认会初始化 32 字节的数组，然后动态增长
   * 可以用更大的值初始化
2. `ByteArrayOutputStream` 的所有函数都是 `synchronized` 的 - 由于我们确保是在单线程中执行，同步关键字可以去掉
3. `toByteArray()` 会返回 stream 的字节数组的一份拷贝 - 浪费空间和时间

---

## Reference

http://javatechniques.com/blog/faster-deep-copies-of-java-objects/

---

## Summary

还是需要多读读 JDK 源码

不知道有没有什么好的书籍

---

