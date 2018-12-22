# Python - Type Definition

Created by : Mr Dk.

2018 / 12 / 22 23:36

Nanjing, Jiangsu, China

---

### Integer

_Python_ 可以处理任意大小、任意符号的整数

* 用 __十六进制__ 表示整数 - 使用 `0x` 前缀和 `0-9`，`a-f` 
* 没有大小限制

### Floating Number

* 可以使用数学写法
* 也可以使用科学计数法（用 `e` 代替 `10`，`1.23e-5`）

### String

由 `''` 或 `""` 包围起来的任意文本

字符串内部换行：`'''...'''`

#### Encoding

美国的 _ASCII_，中国的 _GB2312_，日本的 _Shift_JIS_ ......

编码不统一导致乱码

__Unicode__ 将所有语言统一编到一套编码里，通常使用两个字节

由于 __存储__ 和 __传输__ 的开销，出现了可变长编码 _UTF-8_，将所有字符编码为 _1-6_ 个字节

在计算机 __内存__ 中，统一使用 __Unicode__ 编码；当保存至 __硬盘__ 或 __传输__ 时，转换为 __UTF-8__ 编码

在 _Python 3_ 中，字符串以 _Unicode_ 编码

`ord()` 函数获取字符的整数表示，`chr()` 函数将编码转换为字符

#### Parsing

将内存中的 _Unicode_ 字符串转换为字节流 - 用带 `b` 前缀的 `''` 或 `""` 表示

```python
x = b'ABC'
```

可以通过 `encode()` 函数将字符串转换为字节流

* 中文编码为 _ASCII_ 时会报错

```python
"CBC".encode("ascii")
"喇叭".encode("utf-8")
```

反之，使用 `decode()` 函数将字节流编码为字符串

```python
x = b'ZJT'.decode("ascii")
```

#### Length

使用 `len()` 函数计算长度

* 若 `len()` 中的是字符串，则计算字符个数
* 若 `len()` 中的是字节流，则计算字节个数

#### Formating

与 _C_ 语言类似

| Pattern | Replacement  |
| ------- | ------------ |
| %d      | 整数         |
| %f      | 浮点数       |
| %s      | 字符串       |
| %x      | 十六进制整数 |

```python
print("Hi %s, your score is %d" % ("Tim", 100))
```

* 需要对应好顺序
* 还可以指定浮点数精确到的位数和整数是否补零

或使用 `format()` 函数

```python
pattern = "Hi {0}, your score improves {1:.2f}%"
print(pattern.format("Tim", 12.5688))
```

### Boolean

值：`True` 和 `False` （注意大小写）

计算：`and`、`or`、`not`

### Null Value

`None` （注意大小写）

### Variable

_Python_ 中，`=` 用于赋值：

* 可将任意数据类型赋值给变量
* 同一个变量可以被不同类型的变量反复赋值
* 因此 _Python_ 是一种 __动态语言__

内存透视：对于 `x = "ABC"`

* 在内存中创建了一个值为 `ABC` 的字符串
* 在内存中创建了一个 `x` 变量，并指向该字符串

### Constant

通常用全部大写的变量名表示常量（习惯用法）

常量其实也是变量，_Python_ 没有任何机制保证常量不会被改变

常量的值实际上是可以被改变的（但没有必要）

### Division

精确除法 - `/`

* 计算结果为浮点数（哪怕恰好整除）

保留整数除法 - `//`

* 计算结果永远为整数
* 只取结果的整数部分

取余数除法 - `%`

* 计算结果永远为整数
* 只取结果的余数部分

---

### Summary

好像有点理解为什么都说 _Python_ 简单了

因为很多函数都已经 _out of the box_ :ok_hand:

好吧 继续 :muscle:

---

