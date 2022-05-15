# Java - Equals

Created by : Mr Dk.

2020 / 05 / 19 17:45

Nanjing, Jiangsu, China

---

## About Equals and ==

当编写程序时，我们经常需要判断两个变量是否相等。对于 (尤其是之前有过 C/C++ 经验的) green hand Java coder 来说，一个常犯的错误就是使用了 C/C++ 中常用的 `==` 运算符来进行比较。对于 `int` 等 Java 中的 primitive type 来说，用 `==` 运算符没有任何问题。而对于 reference type (即对象) 来说，用 `==` 就不对了。我记得我当年踩的第一个坑就是用 `==` 去比较两个 `String`。

Java 中具有 **原始类型 (Primitive Type)** 和 **引用类型 (Reference Type)** 两种类型的变量。这两种变量的内存都位于 JVM 栈中，并随着函数的调用和退出进行分配和释放。特别地，引用类型通过 `new` 关键字在 Java heap 上分配内存，存放实例化的对象；堆上的内存由 JVM 的 GC 系统自动回收。引用类型本身的值保存的是 **对应实例对象的内存地址**。这种设计引发了 Java 赋值时值传递、引用传递的区别，也就是深拷贝和浅拷贝的区别。

`==` 的语义其实很简单 - 两个变量相等，当且仅当它们的值相等。而对于引用类型来说，两个变量的值相等，意味着它们 **引用的内存地址相等**，即，两个引用类型变量指向 (可能是 heap 上的) 同一个对象实例。如果两个对象实例的值 (比如说 String) 相同，但它们是两个不同的对象实例，内存地址不同，用 `==` 去比较它们肯定会得到 `false`。

显然，`==` 运算符对于引用类型变量的语义是：两个变量是否指向同一个位置 (对象)。那么如何比较两个引用变量指向的 **内容** (而不是位置) 是否相同呢？这就是 `equals()` 的意义。Java 中的所有对象都继承自 `java.lang.Object`，在这个类中，定义了 `equals()` 函数：

```java
/**
 * Indicates whether some other object is "equal to" this one.
 * <p>
 * The {@code equals} method implements an equivalence relation
 * on non-null object references:
 * <ul>
 * <li>It is <i>reflexive</i>: for any non-null reference value
 *     {@code x}, {@code x.equals(x)} should return
 *     {@code true}.
 * <li>It is <i>symmetric</i>: for any non-null reference values
 *     {@code x} and {@code y}, {@code x.equals(y)}
 *     should return {@code true} if and only if
 *     {@code y.equals(x)} returns {@code true}.
 * <li>It is <i>transitive</i>: for any non-null reference values
 *     {@code x}, {@code y}, and {@code z}, if
 *     {@code x.equals(y)} returns {@code true} and
 *     {@code y.equals(z)} returns {@code true}, then
 *     {@code x.equals(z)} should return {@code true}.
 * <li>It is <i>consistent</i>: for any non-null reference values
 *     {@code x} and {@code y}, multiple invocations of
 *     {@code x.equals(y)} consistently return {@code true}
 *     or consistently return {@code false}, provided no
 *     information used in {@code equals} comparisons on the
 *     objects is modified.
 * <li>For any non-null reference value {@code x},
 *     {@code x.equals(null)} should return {@code false}.
 * </ul>
 * <p>
 * The {@code equals} method for class {@code Object} implements
 * the most discriminating possible equivalence relation on objects;
 * that is, for any non-null reference values {@code x} and
 * {@code y}, this method returns {@code true} if and only
 * if {@code x} and {@code y} refer to the same object
 * ({@code x == y} has the value {@code true}).
 * <p>
 * Note that it is generally necessary to override the {@code hashCode}
 * method whenever this method is overridden, so as to maintain the
 * general contract for the {@code hashCode} method, which states
 * that equal objects must have equal hash codes.
 *
 * @param   obj   the reference object with which to compare.
 * @return  {@code true} if this object is the same as the obj
 *          argument; {@code false} otherwise.
 * @see     #hashCode()
 * @see     java.util.HashMap
 */
public boolean equals(Object obj) {
    return (this == obj);
}
```

可以看到，`Object` 的实现中还是使用了 `==`。但是，任意一个 Java 对象都可以 override 这个函数，从而实现对象自己的 `equals()` 行为。比如，对于 `java.lang.String` 来说，`equals()` 比较的就是字符串的 **内容** 是否相同了 (两个字符串可以位于内存中的不同位置)：

```java
/**
 * Compares this string to the specified object.  The result is {@code
 * true} if and only if the argument is not {@code null} and is a {@code
 * String} object that represents the same sequence of characters as this
 * object.
 *
 * @param  anObject
 *         The object to compare this {@code String} against
 *
 * @return  {@code true} if the given object represents a {@code String}
 *          equivalent to this string, {@code false} otherwise
 *
 * @see  #compareTo(String)
 * @see  #equalsIgnoreCase(String)
 */
public boolean equals(Object anObject) {
    if (this == anObject) {
        return true;
    }
    if (anObject instanceof String) {
        String anotherString = (String)anObject;
        int n = value.length;
        if (n == anotherString.value.length) {
            char v1[] = value;
            char v2[] = anotherString.value;
            int i = 0;
            while (n-- != 0) {
                if (v1[i] != v2[i])
                    return false;
                i++;
            }
            return true;
        }
    }
    return false;
}
```

## Equals of Arrays

对于数组来说，如何定义其是否相等呢？Java 中有原生的数组对象 `Object[]` (`int[]` / `boolean[]` / ...)，还有 JDK 中实现的容器对象 `ArrayList` (以及其它 List)，都具有数组的功能。那么这两个对象的 `equals()` 有什么区别呢？另外，`java.util.Arrays` 工具类中提供的静态函数 `Arrays.equals(Object[] a, Object[] a2)` 又如何呢？

### Java 数组对象的 equals()

Java 原生的数组对象并没有 override `equals()` 函数，也就是说，使用了默认语义 `==`。所以，下面两条语义等价，含义是比较两个引用类型变量 **是否指向同一个数组**：

```java
Object[] o1 = new Object[8];
Object[] o2 = o1;
System.out.println(o1.equals(o2));
System.out.println(o1 == o2);
```

### ArrayList 的 equals()

`java.util.ArrayList` 中并没有实现 `equals()`，所以找到它的父类 `java.util.AbstractList`：

```java
/**
 * Compares the specified object with this list for equality.  Returns
 * {@code true} if and only if the specified object is also a list, both
 * lists have the same size, and all corresponding pairs of elements in
 * the two lists are <i>equal</i>.  (Two elements {@code e1} and
 * {@code e2} are <i>equal</i> if {@code (e1==null ? e2==null :
 * e1.equals(e2))}.)  In other words, two lists are defined to be
 * equal if they contain the same elements in the same order.<p>
 *
 * This implementation first checks if the specified object is this
 * list. If so, it returns {@code true}; if not, it checks if the
 * specified object is a list. If not, it returns {@code false}; if so,
 * it iterates over both lists, comparing corresponding pairs of elements.
 * If any comparison returns {@code false}, this method returns
 * {@code false}.  If either iterator runs out of elements before the
 * other it returns {@code false} (as the lists are of unequal length);
 * otherwise it returns {@code true} when the iterations complete.
 *
 * @param o the object to be compared for equality with this list
 * @return {@code true} if the specified object is equal to this list
 */
public boolean equals(Object o) {
    if (o == this)
        return true;
    if (!(o instanceof List))
        return false;

    ListIterator<E> e1 = listIterator();
    ListIterator<?> e2 = ((List<?>) o).listIterator();
    while (e1.hasNext() && e2.hasNext()) {
        E o1 = e1.next();
        Object o2 = e2.next();
        if (!(o1==null ? o2==null : o1.equals(o2)))
            return false;
    }
    return !(e1.hasNext() || e2.hasNext());
}
```

不管是看注释，还是看代码，不难发现，ArrayList 将会依次遍历每一个元素，并调用每一个元素的 `equals()` 函数。也就是说，ArrayList 的 `equals()` 返回 `true` 当且仅当：

1. 比较对象也是一个 List
2. 两个 List 有着相同的长度
3. List 中的每一对元素的 `equals()` 都返回 `true`

从语义上讲，这个 `equals()` 实现了比较两个数组的 **内容** 是否相同。

### Arrays 中的 equals()

在 `java.util.Arrays` 工具类中，实现了不同数据类型数组的 `equals()`。以 `Object[]` 为例：

```java
/**
 * Returns <tt>true</tt> if the two specified arrays of Objects are
 * <i>equal</i> to one another.  The two arrays are considered equal if
 * both arrays contain the same number of elements, and all corresponding
 * pairs of elements in the two arrays are equal.  Two objects <tt>e1</tt>
 * and <tt>e2</tt> are considered <i>equal</i> if <tt>(e1==null ? e2==null
 * : e1.equals(e2))</tt>.  In other words, the two arrays are equal if
 * they contain the same elements in the same order.  Also, two array
 * references are considered equal if both are <tt>null</tt>.<p>
 *
 * @param a one array to be tested for equality
 * @param a2 the other array to be tested for equality
 * @return <tt>true</tt> if the two arrays are equal
 */
public static boolean equals(Object[] a, Object[] a2) {
    if (a==a2)
        return true;
    if (a==null || a2==null)
        return false;

    int length = a.length;
    if (a2.length != length)
        return false;

    for (int i=0; i<length; i++) {
        Object o1 = a[i];
        Object o2 = a2[i];
        if (!(o1==null ? o2==null : o1.equals(o2)))
            return false;
    }

    return true;
}
```

可以看到，其中也有一个 for 循环对数组中的每对元素调用 `equals()` 进行比较。两个数组相等当且仅当它们以相同的顺序包含了相同的元素。

## Equals of Wrapper Class

为了保证任何变量都具有面向对象的行为，Java 对每一种原始类型都提供了对应的包装类。在包装类的对象中，包含原始类型的值。比如，`Interger` 之于 `int`，`Double` 之于 `double` 等。那么包装类的 `equals()` 又是个什么语义呢？以 `java.lang.Integer` 为例：

```java
/**
 * Compares this object to the specified object.  The result is
 * {@code true} if and only if the argument is not
 * {@code null} and is an {@code Integer} object that
 * contains the same {@code int} value as this object.
 *
 * @param   obj   the object to compare with.
 * @return  {@code true} if the objects are the same;
 *          {@code false} otherwise.
 */
public boolean equals(Object obj) {
    if (obj instanceof Integer) {
        return value == ((Integer)obj).intValue();
    }
    return false;
}
```

显然，`equals()` 对包装类对象内部维护的原始类型变量 `int value` 应用了 `==` 进行比较。因此，语义上，包装类的 `equals()` 本质上相当于原始类型变量的值比较 (内容比较)。

---

## Summary

总结，只需要搞清语义即可。语义有两种：

- 变量位置比较
- 变量内容比较

`==` 比较变量的位置；默认来说，`equals()` 也比较变量的位置，但在经过 override 之后一般体现出比较变量内容的语义。当然也有例外，具体还是要看类型的 `equals()` 是如何实现的。

---

## Exercise

```java
ArrayList<Integer []> a = new ArrayList<>();
ArrayList<Integer []> b = new ArrayList<>();
Integer []g = new Integer[2];
Integer []h = new Integer[2];
g[1] = 1;
h[1] = 1;
a.add(g);
b.add(h);

System.out.println(a == b);
System.out.println(a.equals(b));
System.out.println(Arrays.equals(a.toArray(),b.toArray()));
```

输出结果应为三个 `false`：

- 由于 `a` 和 `b` 是两个不同的对象，显然内存地址不相等
- 由于 `a` 和 `b` 是 ArrayList 对象，`equals()` 会调用其中的每一对元素的 `equals()`，即 `g` 与 `h`
  - 由于 `g` 与 `h` 是 Java 原生数组对象，`g.equals(h)` 等价于 `g == h`，显然它们内存地址不相等
- `a.toArray()` 会将 ArrayList 转换为一个 Java 原生的数组对象
  - `Arrays.equals()` 比较的是数组对象中的每对元素 (`Integer []`) 是否 `equals()`
  - 问题转化为 `g.equals(h)`，同上

```java
ArrayList<List> c = new ArrayList<>();
ArrayList<List> d = new ArrayList<>();
ArrayList<Integer> e = new ArrayList<>();
ArrayList<Integer> f = new ArrayList<>();
e.add(1);
f.add(1);
c.add(e);
d.add(f);

System.out.println(c.equals(d));
```

输出结果为 `true`：

- 由于 `c` 和 `d` 是 ArrayList，比较其中的每对元素是否 `equals()`，问题转化为 `e.equals(f)`
- 由于 `e` 和 `f` 也是 ArrayList，比较其中的每对元素是否 `equals()`，问题转化为 `c.equals(d)`
- 由于 `c` 和 `d` 都是 `Integer` 包装类，将会比较它们内部的值是否相同 - 显然，它们的值都等于 `1`

---

## References

[Stackoverflow - equals vs Arrays.equals in Java](https://stackoverflow.com/questions/8777257/equals-vs-arrays-equals-in-java)

[理解 Java 中的引用传递和值传递](https://www.cnblogs.com/zhangyu317/p/11226105.html)

[Java 中基本数据类型的存储方式和相关内存的处理方式](https://www.cnblogs.com/xiohao/p/4278173.html)

[Wrapper Classes in Java](https://www.geeksforgeeks.org/wrapper-classes-java/)

---
