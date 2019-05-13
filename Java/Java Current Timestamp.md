# Java - Current Timestamp

Created by : Mr Dk.

2019 / 01 / 06 18:07

Nanjing, Jiangsu, China

---

## About

在 _Java_ 中获取当前时间戳的几种方式

---

## 1. `java.lang.System`

```java
long timestamp = System.currentTimeMillis();
```

---

## 2. `java.util.Date`

```java
long timestamp = new Date().getTime();
```

看其源代码：

```java
/**
 * Allocates a <code>Date</code> object and initializes it so that
 * it represents the time at which it was allocated, measured to the
 * nearest millisecond.
 *
 * @see     java.lang.System#currentTimeMillis()
 */
public Date() {
    this(System.currentTimeMillis());
}
```

所以说，还不如使用第一种方式

---

## 3. `java.util.Calendar`

```java
long timestamp = Calendar.getInstance().getTimeInMillis();
```

效率最低，没有必要

---

## Summary

不知道为啥

到目前为止也写了那么多的 _Java_ 了

但是第一种效率最高的方式是最后才知道的

---

