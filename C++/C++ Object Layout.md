# C++ - Object Layout

Created by : Mr Dk.

2021 / 03 / 06 16:17

Nanjing, Jiangsu, China

---

## About

一个 C++ 对象的内存布局是什么样的？

程序在运行时会有几个内存区：

* 数据段
* BSS 段
* 代码段
* 栈
* 堆

一个 C++ 对象的各部分分别在哪个位置上呢？

## Original

首先明确一点，在 C 语言中：

* 全局变量和静态变量存储在数据段 (已被初始化) 和 BSS 段 (未被初始化) 中
* 代码 (函数) 全部保存在代码段中
* 函数内的局部变量位于栈上 (在编译时已经可以确定空间大小)
* 在代码中动态分配的内存位于堆上 (不确定空间大小，动态分配)

## C++ Object

根据上述思路，以一个位于函数内的局部变量对象为例。在对象被声明后，肯定会在栈内占用内存空间。栈内占用内存的大小在编译时已经可以确定，包含：

* 非静态成员变量
* (如果有虚函数) 虚函数表指针

其它部分去哪了呢？以下内容参考自 *Vishal Chovatiya* 的博客：

* [Memory Layout of C++ Object in Different Scenarios](http://www.vishalchovatiya.com/memory-layout-of-cpp-object/)
* [Inside the C++ Object Model](http://www.vishalchovatiya.com/inside-the-cpp-object-model/)

```c++
class X {
    int         x;
    float       xx;
    static int  count;
public:
    X() {}
    virtual ~X() {}
    virtual void printAll() {}
    void printInt() {}
    void printFloat() {}
    static void printCount() {}
};
```

对象布局：

```
      |                        |          
      |------------------------| <------ X class object memory layout
      |        int X::x        |
stack |------------------------|
  |   |       float X::xx      |                      
  |   |------------------------|      |-------|--------------------------|
  |   |         X::_vptr       |------|       |       type_info X        |
 \|/  |------------------------|              |--------------------------|
      |           o            |              |    address of X::~X()    |
      |           o            |              |--------------------------|
      |           o            |              | address of X::printAll() |
      |                        |              |--------------------------|
      |                        |
------|------------------------|------------
      |  static int X::count   |      /|\
      |------------------------|       |
      |           o            |  data segment           
      |           o            |       |
      |                        |      \|/
------|------------------------|------------
      |        X::X()          | 
      |------------------------|       |   
      |        X::~X()         |       |
      |------------------------|       | 
      |      X::printAll()     |      \|/ 
      |------------------------|  text segment
      |      X::printInt()     |
      |------------------------|
      |     X::printFloat()    |
      |------------------------|
      | static X::printCount() |
      |------------------------|
      |                        |
```

### Member Function

成员函数去哪了？C++ 把所有的成员函数转换成了普通函数。编译器为函数加上类名作用域解析，以表示该函数属于哪个类；并为每个类成员函数 **隐式传入一个参数**：`this` 指针，指向调用成员函数的对象地址，这样成员函数内就可以访问成员变量了。以下面的类为例：

```c++
class foo {
    int m_var;
public:
    void print() {
        cout << m_var << endl;
    }
};
```

编译器将会对成员变量和成员函数分别对待。把成员变量留在类内，占用对象内存；把成员函数加上作用域解析，隐式传入 `this` 指针后，放进代码段中：

```c++
class foo {
    int m_var;
};

void foo::print(foo *this) {
    std::cout.operator<<(this->m_var).operator<<(std::endl);
}
```

### Static Member Function

对于类内的静态成员函数，编译器同样对其加上作用域解析后，放进了代码段中。区别在于 **不会将 `this` 指针作为隐式参数**，因为这个函数不会被某个对象调用。

### Static Member Variable

由于静态成员变量也不可能在每个对象实例中都有一个副本，因此不会与非静态成员变量一样放在栈上。被加上作用域解析后，被放进了数据段中。

### Virtual Function

编译器自动为每个类内的所有虚函数生成一个 **虚函数表**，通常会放置在数据段中 (但具体取决于编译器的具体实现)。虚函数表中放置了指向代码段中相应函数入口的指针。表内的第一个条目是一个指向 `type_info` 对象的指针，该对象内包含了与当前类相关的继承信息。

编译器自动为每个带有虚函数的对象添加了一个成员变量 `_vptr`，该指针指向类的虚函数表。

## Differences between Structure and Class

在 C++ 中对 `struct` 进行了扩展，`struct` 与 `class` 的使用无异，除了一点：

* `struct` 默认所有成员为 `public`；同样，在继承方式上，默认为公有继承
* `class` 默认所有成员为 `private`；同样，在继承方式上，默认为私有继承

但是具体使用 `struct` 和 `class` 一般遵循约定：

* 如果只是为了将一些元素捆为一个整体，那么可以使用 `struct`
* 如果是为了高层次的建模、抽象，或者提供一种接口，那么就使用 `class`

参考：[Fluent C++ - The real difference between struct and class](https://www.fluentcpp.com/2017/06/13/the-real-difference-between-struct-class/)

---

