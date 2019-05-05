# Python - Data Structure

Created by : Mr Dk.

2018 / 12 / 23 0:36

Nanjing, Jiangsu, China

---

## List

列表 - 一种 __有序__ 的集合，可以随时 __增加__ 或 __删除__ 其中的元素

* _list_ 中的元素可以是不同类型的
* _list_ 中的元素也可以是另一个 _list_ （递归定义）

使用 `[]` 初始化：

```python
fruits = ["apple", "banana", "orange"]
```

* 使用 `len()` 可以获得元素个数
* 使用索引 `fruits[i]` 可以访问每个位置的元素
  * 范围从 `0` 到 `len(fruits) - 1`
* 可以使用 `-1` 作为索引，直接获取最后一个元素
  * `-2`、`-3` ... 依次类推
* 使用 `append()` 函数可追加元素到末尾
* 使用 `insert()` 函数可将元素插入到指定位置

```python
fruits.insert(2, "grape")
```

* 使用 `pop()` 函数删除指定位置的函数或末尾元素
* 直接赋值给索引位置，替换元素
* 对于 _list_ 中的 _list_，可使用类似多维数组的访问方式访问

---

## Tuple

元组 - 有序列表

* __一旦初始化后就不能修改__
* 不能增加、删除、修改元素
* 代码更为安全

使用 `()` 初始化：

```python
t = (1, 2, 3)
t = ()
t = (1,)
```

* 定义 __只有一个元素__ 的 _tuple_ 时，为避免和 `t = (1)` 产生歧义，必须加入一个 `,`
* _tuple_ 不可变指的是元素指向不变，但若元素指向一个 _list_，_list_ 的内容是可以改变的

---

## Dict

字典 - _key-value_ 存储，查找速度极快，但占用空间多

* 根据 _key_ 算出 _value_ 的 _hash_ 位置
* 内部存放顺序和插入顺序无关
* _key_ 必须是不可变对象（_list_ 不行）

使用 `{}` 初始化：

```python
grade = {"Tim": 100, "Sam": 80, "Lewis": 90}
grade["Tom"] = 89
```

* 多次对 _key_ 对应的 _value_ 赋值，后面的值会把前面的值冲掉

判断 _key_ 是否存在：

* 返回 `True` 或 `False`

```python
judge = "Alice" in grade
```

* 使用 `get()` 方法，_key_ 不存在则返回 `None`，或自己指定的值

```python
grade.get("Alice")
grade.get("Alice", -1)
```

删除一个 _key_，使用 `pop(key)` 方法

---

## Set

_set_ 与 _dict_ 类似，但只存储 _key_，不存储 _value_

* 无序无重复的集合
* 不可以放入可变对象（无法比较它们是否相等）

初始化：

```python
s = set([1, 2, 3])
```

增/删元素 - `add(key)` / `remove(key)`

---

## Summary

感觉和 _R_ 语言比较类似

但是我居然先学的是 _R_ 而不是 _Python_ ...

睡了 起床读完论文继续

---

