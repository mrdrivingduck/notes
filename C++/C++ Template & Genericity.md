# C++ - Template & Genericity

Created by : Mr Dk.

2021 / 03 / 29 23:00

Nanjing, Jiangsu, China

---

## Function Template

现代 C++ 编译器实现了 C++ 新增的特性：函数模板。允许 **使用类型作为参数** 来定义函数，使得编译器自动生成该类型的函数。这一特性也被称为 *参数化类型 (parameterized types)*。一个最经典的例子：实现一个 `swap()` 函数交换两个变量。显然，需要对不同的数据类型实现不同的函数，而函数主体中的内容完全相同：

```c++
void swap(int &a, int &b) {
    int temp = a;
    a = b;
    b = temp;
}

void swap(double &a, double &b) {
    double temp = a;
    a = b;
    b = temp;
}
```

模板提供了一种抽象，能够将 **数据类型** 作为参数。这样，只需要实现一个抽象的函数主体即可：

```c++
template <typename T>
void swap(T &a, T &b) {
    T temp = a;
    a = b;
    b = temp;
}
```

有了这个模板，编译器在遇到对 `swap()` 的调用时，根据其 **实际参数类型**，自动生成一个相应类型的函数。比如：

```c++
int a = 3;
int b = 5;
swap(a, b);
```

编译器发现 `swap()` 的实际参数类型为 `int`，那么就会根据 `swap()` 的模板，将类型 `T` 替换为 `int`，并产生一个 `int` 版本的 `swap()`。这个 **根据模板生成函数定义** 的过程由编译器自动完成，不需要开发人员介入。这个过程被称为模板的 **实例化 (instantiation)**。实例化特指从一个抽象的函数定义模板，产生具有实际意义的函数定义的过程。

基于上述过程可知，模板本身不会产生函数，模板仅用于告诉编译器应当如何产生函数定义。说白了，**模板只是产生函数定义的方案**。如果说整个程序内没有任何一处对 `swap()` 的实际调用，那么可执行文件内不会有任何实际的 `swap()` 版本。另外，模板并不能缩短可执行文件的长度：程序内使用了多少种 `swap()` 的实例化版本，可执行文件内就会有多少种 `swap()` 的函数定义。

实例化的过程可被分为：

* 隐式实例化：编译器根据实际参数的类型，隐式获得类型参数，并根据模板产生函数的实际定义
* 显式实例化：编程人员直接显式指定要产生的函数定义

同样以上述 `swap()` 模板为例。当编译器识别到 `swap(a, b)` 时，能够自动获知 `a` 和 `b` 的类型为 `int`。此时，不需要人为干预，编译器就可以自动生成 `swap(int, int)` 的函数定义，这就是隐式实例化。而如果代码中出现了显式指定的模板实例化：

```c++
template void swap<char>(char &, char &);
```

那么编译器将直接为 `char` 类型生成实际的函数定义 (哪怕该版本的函数定义从未被使用过？)。

> 注意，不管是隐式 / 显式实例化，用的都是模板的函数体定义，并不需要重新实现一个函数体。

## Class Template

对于一个类来说，也可以定义模板，用于抽象具有相似功能，但是数据类型不确定的类。一个最经典的例子就是 **容器**。比如实现一个 `stack` 类及其最基本的入栈、出栈操作，但是栈内盛放的数据类型是不确定的。`int` 元素可以出入栈，`bool` 元素也可以。此时，可以使用模板来定义一个类，该类被称为 **模板类**。同样，模板类也只提供 **产生一个实际类的方案**，但不是一个实际的类。

在类定义上使用 `template` 来声明模板，相应的类型名称可以在类内使用。类外的成员函数定义中也要使用泛型。

```c++
template <typename T>
class stack
{
private:
    enum { MAX = 10 };
    T items[MAX]; // abstract
    int top;
public:
    stack();
    bool is_empty();
    bool is_full();
    bool push(const T &item); // abstract
    bool pop(T *item); // abstract
};

template <typename T>
stack<T>::stack()
{
    top = 0;
}

template <typename T>
bool stack<T>::push(const T &item)
{
    if (top < MAX) {
        items[top++] = item;
        return true;
    }
    return false;
}

// ...
```

与函数模板类似，编译器在看到程序中使用了实际的类模板后，将会根据类型参数 `T` 的实际类型产生 `T` 类型的 `stack` 类。比如，程序中的 `stack<int>` 将会使编译器根据 `stack` 的类定义将 `T` 全部替换为 `int`，从而产生 `stack<int>` 的类定义。

除了抽象的类型参数外，模板也支持具体的 **非类型参数** 或 **表达式参数**：

```c++
template <typename T, int n>
class pair {

}
```

这样也是允许的。在实际程序中，可以使用 `pair<char, 12>` 或 `pair<string, 19>`，使编译器根据模板产生相应的类定义。注意，这里将会产生两个完全不同的类，因为类定义将会因为类型参数和非类型参数而完全不同。表达式参数只支持几种类型：

* 整形
* 枚举
* 引用
* 指针

并且用作表达式参数的值必须是 **常量表达式**，模板代码内不允许对表达式参数进行修改。

> 在 C++ 98 中，要求至少用一个空白字符将两个 `>` 隔开，以区别 `>>` 运算符。比如 `stack<array<int>>` 就是错误的。C++ 11 中不要求这么做。
>
> 另外，C++ 98 中使用 `class` 关键字来声明模板类型参数：
>
> ```c++
> template <class T>
> ```
>
> C++ 11 引入 `typename` 关键字完成相同的功能。但是 `class` 依旧用于向下兼容。

## Specialization

模板函数或模板类在满足了通用性的同时，也带来了一个问题：并不是所有数据类型都能完全符合模板内实现的程序语义。假设定义一个用于比较两个元素大小关系的模板，模板内使用 `<` 运算符进行比较：

```c++
template <typename T>
bool compare(T &a, T &b)
{
    return a < b;
}
```

对于 `int` 来说，实例化后的函数定义是符合语义的；对于 `string` 来说，由于其 `operator<` 已经被重载为比较两个字符串大小的语义，因此也是符合的；然而，对于 `const char *` (常量字符串) 来说，其语义就变成了比较两个指针的地址大小，而不是其指向的字符串的大小。显然，我们需要对 `const char *` 类型定制一套更具体的模板定义，避免使用默认模板：

```c++
template <>
// bool compare(const char *a, const char *b) {
bool compare<const char *>(const char *a, const char *b) {
    return strcmp(a, b);
}
```

具体化的类模板也是类似。上述行为被称为模板的 **显式具体化 (explicit specialization)**。可以看出，与 **实例化** 的区别在于，具体化需要提供一个新的模板函数体，实现与模板函数不同的逻辑，从而体现特殊化。当编译器发现函数或类与具体化的模板和抽象化的模板同时匹配时，将会优先选择更加具体化的模板。

C++ 还允许限制部分模板的通用性，即 **部分具体化 (partial specialization)**。部分具体化可以给类型参数指定具体的类型：

```c++
template <typename T1, typename T2> class Pair {};
template <typename T1> class Pair<T1, int> {};
```

可以看出，`template <>` 内声明了所有的抽象类型参数，而之后的 `<>` 声明了具体类型参数。由此可见，显式具体化其实是部分具体化的一个特殊情况。如果在部分具体化中为所有的类型参数指定了具体类型，那么就成了显式具体化，`template <>` 中将没有任何抽象类型参数了：

```c++
template <> class Pair<string, int> {};
```

## Priority

如果程序中的某个函数同时匹配多个模板，编译器将根据优先级选择相应函数。这个过程被称为 *重载解析 (overloading resolution)*。优先级为：

1. 常规函数 (非模板函数)
2. 显式具体化模板函数
3. 部分具体化模板函数
4. 抽象模板函数

显而易见，越具体的函数定义越会被优先匹配。

---

