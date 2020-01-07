# Python - Control Flow

Created by : Mr Dk.

2018 / 12 / 24 0:03

Nanjing, Jiangsu, China

---

## Conditional

```python
salary = 10000

if salary >= 200000:
    print("nb")
elif salary >= 100000:
    print("666")
else:
    print("laji")
```

* 注意不要少了冒号 `:`
* 注意 _Python_ 的缩进代码块规则 - 若条件满足，则执行缩进部分的代码

---

## Loops

### For Loops

```python
sum = 0
for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    sum = sum + i
print(sum)
```

* 可用于迭代 _list_ 或 _tuple_ 中的每一个元素
* 每个元素会被分别赋值给 `i`，然后执行缩进代码块中的语句
* 不要忘了冒号 `:`

_Python_ 提供 `range()` 函数用于生成一个整数序列：

* 如 `range(16)` 可以生成 `0` 到小于 `16`（`15`）的整数序列
* 整数序列可以通过 `list()` 函数转换为 _list_，并写在循环条件中

### While Loops

```python
sum = 0
while sum < 100:
    sum = sum + 1
print(sum)
```

* 条件满足时继续循环，条件不满足是退出循环

### Break

使用 `break` 跳出循环

### Continue

使用 `continue` 跳过当前循环，直接进行下一次循环

---

## Summary

睡前争分夺秒学一点

这些都与已经掌握的语言类似

使用时在细节上注意即可，比如不要少了 `:`

---

