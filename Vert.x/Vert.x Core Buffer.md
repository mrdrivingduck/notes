# Vert.x Core - Buffer

Created by : Mr Dk.

2018 / 11 / 04 19:51

Nanjing, Jiangsu, China

---

## About

_Buffer_ - a sequence of zero or more bytes that can read from or written to and which expands automatically as necessary to accommodate any bytes written to it. You can perhaps think of a buffer as smart byte array.

## Creating

提供几个静态的函数：`Buffer.buffer`

* 创建一个新的空 _buffer_

  ```java
  Buffer buf = Buffer.buffer();
  ```

* 用字符串创建一个 _buffer_，并指定 __编码方式__

  ```java
  Buffer buf = Buffer.buffer("string");              // Default encoding: UTF-8
  Buffer buf = Buffer.buffer("string", "UTF-16");    // Encoding: UTF-16
  ```

* 用 _byte array_ 创建一个 _buffer_

  ```java
  byte[] bytes = new byte[] {1, 3, 5};
  Buffer buf = Buffer.buffer(bytes);
  ```

* 创建指定大小的空 _buffer_

  ```java
  Buffer buf = Buffer.buffer(1024);
  ```

## Writing to Buffer

_buffer_ 会自动增长以容纳字节 - 永远不会报 `IndexOutOfBoundException`

两种写入方式：

* Appending

  * 使用 `appendXXX` 函数族

  * 该函数族返回 _buffer_ 本身，因此可以使用 `fluent API` 的方式链式调用

    ```java
    Buffer buf = Buffer.buffer();
    buf.appendInt(16).appendString("I love u");
    ```

* Random Access

  * 使用 `setXXX` 函数族

  * 该函数族的第一个参数为 `int index`，指示想要写入 _buffer_ 的位置

  * 必要时，_buffer_ 会自动增长以容纳数据

    ```java
    Buffer buf = Buffer.buffer();
    buf.setInt(0, 16);
    buf.setString(1000, "I love u");
    ```

## Reading from Buffer

* 使用 `getXXX` 函数族
* 该函数族的第一个参数为 `int index`，指示想要开始读取 _buffer_ 的位置

## Working with unsigned numbers

_Vert.x_ 支持无符号的 `getUnsignedXXX`、`setUnsignedXXX`、`appendUnsignedXXX`

## Others

`length()` - 得到 _buffer_ 的长度

`copy()` - 得到 _buffer_ 的拷贝

`sclice()` - 得到 _buffer_ 的片段 __不拷贝底层数据__

## Buffer Re-use

"After writing a buffer to a socket or other similar place, they cannot be re-used."

---

## Summary

在实现 `MessageCodec` 时需要用到 _buffer_

---

