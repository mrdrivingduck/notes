# Python - OOP

Created by : Mr Dk.

2018 / 12 / 25 15:44

Nanjing, Jiangsu, China

---

### About

```python
class Mysocket(object):
    pass
```

* 若不继承自任何类，则 `()` 中写入 `object`，所有类最终都会继承自 `object` 类

---

### Constructor

在对象创建完成后，可动态为其绑定属性

* 为了使类起到模板的作用，在类创建时，将一些必须绑定的属性强制绑定
* 相当于构造函数的作用
* 使用 `__init__` 函数
  * 第一个参数永远为 `self`，表示对象本身
  * 在调用时，`self` 由 _Python_ 解释器自动传入
* 其余成员函数，第一个参数必须为 `self`，其余部分和普通函数没有区别

```python
class Mysocket(object):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def print(self):
        print("%s:%d" % (self.host, self.port))
        
sock = Mysocket("192.168.1.100", 8080)
print(sock.host)
print(sock.port)
```

---

### Access Control

* _Private_
  * 对于属性或方法，若它们以双下划线 `__` 开头，则不能在类外被访问
  * 其实可以通过别的方式访问，因为它们被重命名成为了别的变量名，但没必要
* _Protected_
  * 若以单下划线 `_` 开头，则可以被访问，但约定俗成的规矩是不要随意访问
* _Public_
  * 若没有下划线开头，在类外可以被随意访问
* _Python_ 不提供机制阻止干坏事，全凭自觉

```python
class Mysocket(object):
    
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        
    def getHost(self):
        return self.__host
    
    def getPort(self):
        return self.__port
    
    def print(self):
        print("%s:%d" % (self.__host, self.__port))
        
sock = Mysocket("192.168.1.100", 8080)
print(sock._Mysocket__host)    # Private variable still can be accessed
print(sock._Mysocket__port)    # But do not do that
```

---

### Multi-file Organization

若需要使用另一个 `.py` 文件中的某个类，比如 `mysocket.py` 中的 `Mysocket` 类：

```python
from mysocket import Mysocket

sock = Mysocket("192.168.1.100", 8080)
# ...
```

---

### Inheritance & Polymorphism

总体原理与 `C++`、`Java` 类似

__特殊点：鸭子类型__

* 一个对象只要 __看起来像鸭子，走起路来像鸭子__，那它就可以被看做是鸭子
* 不要求严格的继承体系

代码层理解：

* 定义了一个函数，接收一个基类 `Animal` 类对象，调用 `Animal` 类的 `eat()` 方法
* 对于静态语言而言，该函数只能传入 `Animal` 类及其派生类的对象
  * 因为这些类已经有 `eat()` 方法
* 对于 _Python_ 来说，一个不继承 `Animal` 类的类，只要有 `eat()` 方法，也可以被传入该函数中

---

### Object Information

`type()` 函数用于判断对象类型

* 返回 `class` 类型
* 使用内置 `types` 模块中定义的常量判断函数类型

```python
import types

def fn():
    pass

print(type(666) == int)
print(type("mrdrivingduck") == str)
print(type(fn) == types.FunctionType)
```

`isinstance()` 函数也用于判断对象类型，尤其是有 __继承关系__ 的类

* 子类对象属于子类，同时也属于父类
* 父类对象属于父类，但不属于子类

`dir()` 函数获得一个对象的所有属性和方法

---

### Class Attribute

在类中，实例属性属于一个实例（对象）

同时，也可以为类定义属性，该属性属于类

* 调用时，需要直接使用 `类型.变量名`

```python
class Student(object):
    introduction = "I am a Student."
    
print(Student.introduction)
```

---

### Slots

动态语言的灵活性：

* 在创建一个实例后，可以给实例绑定任何属性或函数

绑定函数：

* 给实例绑定函数后，只有该实例可以调用该函数，其它实例不行
* 若要使所有实例都可以调用该函数，需要将该函数绑定到类上

若想要限制实例的属性绑定 - 使用 `__slot__` 变量

```python
class Mysocket(object):
    __slots__ = ("host", "port")    # Use a tuple
    
sock = Mysocket()
sock.host = "192.168.1.100"
sock.port = 8080
# sock.timeout = 3000    # Error
```

---

### Getter & Setter

在绑定属性后，相当于直接把属性暴露出去随意修改

* 定义 `getXXX()` 和 `setXXX()`，可以在 `setXXX()` 中检查参数合法性
* 需要调用函数，没有直接引用属性简单 - `类型.xxx = xxx`

_Python_ 的内置装饰器 `@property` 负责将方法变为属性调用

- 只使用 `@property`
  - 相当于只定义了 _getter_，没有定义 _setter_
  - 可以用于定义一个 __只读属性__

```python
class Mysocket(object):
    
    @property
    def host(self):
        return self._host
    
    @host.setter
    def host(self, host):
        if not isinstance(host, str):
            raise ValueError("Host must be a string.")
        self._host = host
        
    @property
    def port(self):
        return 8080
    
sock = Mysocket()
sock.host = "192.168.1.100"
# sock.port = 9090    # Error, read only
print(sock.host)
print(sock.port)
```

---

### Class Customization

在 _Python_ 中，形似 `__xxx__` 的变量或函数名是由特殊用途的

* 如 `__init__()`、`__slots__` 等

`__str__()`

* 相当于 _Java_ 中的 `toString()`，返回一个较为好看的字符串
* 服务于 `print()` 函数 - `print(obj)` 即可打印该字符串

`__repr__()`

* 作用与 `__str__()` 类似
* 但不服务于 `print()` 函数，而是服务于直接输入变量名，为调试服务
* 可偷懒：`__repr__ = __str__`

`__iter__()` & `__next__()`

* 服务于 `for ... in`
* `__iter__()` 返回一个迭代对象
* `for` 循环不断调用该迭代对象的 `__next__()` 方法拿到循环的下一个值，直到遇到 `StopIteration` 错误

`__getitem__()`

`__getattr__()`

`__call__()`

* 对实例本身进行调用
* `instance.method()` &rarr; `instance()`
* 通过 `callalbe()` 函数，可判断一个对象是否是 __可调用对象__（实现了 `__call__()` 函数的对象）

---

### Summary

这部分真特么多

要完全消化和其它语言的区别还是有难度

以后实战时才回来查阅吧

---

