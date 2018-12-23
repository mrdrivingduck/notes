# Python - Function

Created by : Mr Dk.

2018 / 12 / 24 01:06

Nanjing, Jiangsu, China

---

### Invoke

* 若传入的参数数量和参数类型不对，会报出 `TypeError` 的错误
* 内置常用函数：`abs()`、`min()`、`max()`
* 数据类型转换：`int()`、`float()`、`str()`、`bool()`、`hex()`

---

### Define

* 使用 `def` 语句定义函数
* 随后写出函数名
* 随后写出括号 `()` 和括号中的参数列表
* 随后写出 `:`
* 随后在缩进的代码块中实现函数具体逻辑
* 在函数中使用 `return` 返回
  * 如果没有 `return` 语句，函数返回结果为 `None`
  * `return None` 和 `return` 等价

```python
def my_abs(x):
    if x >= 0:
        return x
    else:
        return -x
```

#### Empty Statement

使用 `pass` 语句 - 可用于占位，使程序先可以运行起来

```python
def nop():
    pass
```

```python
if salary >= 100000:
    pass
```

#### Parameter Check

使用内置函数 `isinstance()` 实现类型检查

```python
def my_abs(x):
    if not isinstance(x, (int, float)):
        raise TypeError("Type not support.")
    if x >= 0:
        return x
    else:
        return -x
```

#### Multiple Return

返回值可以是一个 _tuple_：

* 在语法上，返回一个 _tuple_ 可以省略括号 `()`
* 多个变量可以同时接收一个 _tuple_，按位置赋对应的值

```python
def mul_param(x, y):
    return x, y

a, b = mul_param(1, 2)
# tup = mul_param(1, 2)
```

---

### Parameters

#### Default Parameters

```python
def test(x, a = 2, b = 3, c = 4):
    return x, a, b, c
```

* 必传参数在前，缺省参数在后，否则将会报错
* 调用时可以不按顺序提供部分默认参数
  * 需要显式声明参数名 - `test(1, b="hello")`
* 默认参数也是一个变量
  * 若调用函数时改变了该变量的内容，则下次调用时默认参数将被改变
  * 因此，__默认参数必须指向不变对象！！！__

#### Random Length Parameters

在参数声明前添加 `*` 号

```python
def sum_rand(*numbers):
    sum = 0
    for i in numbers:
        sum = sum + i
    return sum

l = [1, 2, 3]
print(sum_rand(*l))
```

* 在函数内部，`numbers` 实际上收到的是 _tuple_
* 在外部调用时，使用 `*` 可将 _list_ 或 _tuple_ 转换为可变参数

#### Key Word Parameters

在参数声明前添加 `**` 号

```python
def kwd_param(name, age, **kw):
    print("name:", name, "age:", age, "other:", kw)
    
kwd_param("Tim", 21)
kwd_param("Tim", 22, school="NUAA", emotion="single")
```

* 在函数内部，`kw` 实际上收到的是 _dict_
* 在外部调用时，使用 `**` 可将 _dict_ 转换为可变参数

#### Named Key Word Parameters

在普通的位置参数和关键字参数之间用 `*` 隔开

```python
def test(name, age, *, city, job):
    print(name, age, city, job)	
    
test("Tim", 21, city="Nanjing", job="student")
test("Tim", 21, "Nanjing", "student")  # ERROR
```

* 命名关键字必须传入参数名，否则将报错
* 命名关键字可以有缺省值
* 如果函数定义中已有一个可变参数，则后面跟着的命名关键字参数不再需要 `*` 分隔符

#### Parameters Order

参数定义的顺序必须是：__必选参数、默认参数、可变参数、命名关键字参数和关键字参数__

---

### Summary

有几个没见过的高级用法还是需要好好想一想 :sweat_smile:

---

