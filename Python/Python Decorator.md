# Python - Decorator

Created by : Mr Dk.

2018 / 12 / 27 23:32

Nanjing, Jiangsu, China

---

### Higher-order Function

在 _Python_ 中，函数本身也可以赋值给变量

* 如果一个变量指向一个函数，可以通过该变量调用函数

在 _Python_ 中，函数名也是变量

* 也就是说某一函数名可以用来指向别的函数
* 当然实际中不会这样做

高阶函数 - 高度抽象化

* 变量可以指向函数
* 函数参数能够接收变量
* 一个函数能够接收另一个函数作为参数，这种函数就被称为高阶函数

### Decorator

函数也是一个对象，每个函数对象都有一个 `__name__`，存储函数的名字

如果想要在代码运行期间动态增强某个函数的功能，就可以使用 “装饰器” _Decorator_

实例：在某一个函数调用前增加一个打印日志的功能，但不修改函数定义

```python
def log(func):
    def wrapper(*args, **kw):
        print("called:", func.__name__)
        return func(*args, **kw)
    return wrapper

@log
def date():
    print("2018.12.27")

date()
```

定义一个 `log()` 函数作为装饰器，将 `@log` 置于要打印日志的函数之前，然后调用该函数

这里相当于 `date = log(date)`

---

### Summary

暂时简单地记录一下

因为还没有发现装饰器到底有什么用

以后万一需要用的话再去看看专门讲装饰器的文章吧

---

