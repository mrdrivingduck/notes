# C++ - Operator Overload

Created by : Mr Dk.

2021 / 03 / 05 20:14

Nanjing, Jiangsu, China

---

## About

运算符重载是一种形式的 C++ 多态，根据操作数的 **数目** 和 **类型** 来决定采用哪种操作。其一般形式为：

```cpp
operatorop(args)
```

其中，后一个 `op` 可被替换为 C++ 中已经存在的且可以被重载的运算符，比如加法运算符 `+`：

```cpp
operator+(args)
```

重载后，编译器能够对运算符进行等价的替换：

```cpp
A = B + C;
A = B.operator+(C);
```

上述运算符重载方式只能由运算符左侧的操作数通过 **成员函数** 实现。另外可以通过 **友元函数** 实现运算符右侧操作数的运算符重载。

## Limits

C++ 的运算符重载又如下限制：

1. 运算符重载至少要有一个操作数是用户定义的类型 (防止用户为原生类型重载运算符)
2. 不能违反运算符的句法规则 (原来是双目，那就还得是双目)
3. 不能修改运算符优先级
4. 不能创建新的运算符
5. 不能重载如下运算符：
   - `sizeof`
   - `.`
   - `.*`
   - `::`
   - `?:`
   - `typeid`
   - `const_cast`
   - `dynamic_cast`
   - `reinterpret_cast`
   - `static_cast`
6. 某些运算符只能以成员函数的形式重载 (不能以友元函数)：
   - `=`
   - `()`
   - `[]`
   - `->`

## Implementation

### Member Function

以成员函数实现运算符重载，默认了运算符左侧的操作数是当前对象，因此只需要传递一个右操作数作为参数即可。编译器负责将重载后的运算符替换为成员函数调用：

```cpp
T::T operator*(const double &d) {
    // ...
}
```

```cpp
A = B * 2.75;
A = B.operator*(2.75);
```

那么，这种情况怎么办呢？

```cpp
A = 2.75 * B;
```

## Friend Function

如果说将运算符的重载不重载为成员函数，而是重载为一个普通函数，通过传入两个参数，就可以实现按照需要获取操作数顺序。

```cpp
T operator*(const double &d, T obj) {
    // ...
}
```

```cpp
A = 2.75 * B;
A = operator*(2.75, B);
```

这时出现了一个问题：如果这个函数的实现需要访问类的 **私有成员变量** 该怎么办？由于非成员函数不是由对象调用，因此不能访问类内部的私有成员变量。这时候就需要类的 **友元函数** 出马。类的友元函数是非成员函数，但是访问权限与成员函数相同 - 可以访问类的私有成员变量。

创建友元函数的方式是将函数声明在类内，并在原型前加上 `friend` 关键字 (不需要类限定符 `::`)：

```cpp
friend T operator*(const double &d, T obj) {
    // T.xxx;
}
```

> 总结，如果要为类重载运算符，并且不是用类对象作为第一个参数，可以使用友元函数反转操作数顺序。当然，具体用不用友元取决于 **是否要访问类内的私有成员变量**：如果只是将对象作为一个整体使用，不用友元也一样。

## Example: Overload <<

对于一个自定义的类，用户希望能够通过 `cout << obj` 直接打印对象信息。对于该运算符来说，显然用户不会去修改 `iostream` 的头文件来为 cout 对象重载 `<<` 运算符。所以，需要通过友元 (如果需要打印类内私有变量的值) 的方式为该类对象重载 `<<` 运算符。

```cpp
friend void operator<<(ostream &os, const T &t) {
    os << t.xxx;
}
```

由于要操作 cout 对象本身，所以这里传入的参数是引用。编译器会将代码转换为：

```cpp
cout << obj;
operator<<(cout, obj);
```

但是这样还是有个问题：没法适用于连续的 `<<` 运算符：

```cpp
cout << "Hello" << obj << "hhh";
// (cout << "Hello") << obj << "hhh";
// cout << obj << "hhh";
// (void) << "hhh";
```

所以重载函数的返回值也应当是 `ostream` 对象，并且是一个引用：

```cpp
friend ostream & operator<<(ostream &os, const T &t) {
    os << t.xxx;
    return os;
}
```

这样就可以实现如下的效果：

```cpp
cout << "Hello" << obj << "hhh";
// (cout << "Hello") << obj << "hhh";
// cout << obj << "hhh";
// cout << "hhh";
```

## Example: STL

由于 STL 中的容器基本实现了泛型，因此用户可以将自定义类型的对象放进 STL 容器中。在对 STL 容器内元素进行排序时，算法默认使用 `<` 运算符。因此，如果要对自定义类型的对象进行排序，需要为类重载 `<` 运算符。函数原型如下：

```cpp
bool operator<(const T &t) const;
```

这里为什么要使用 `const` 呢？STL 底层的比较函数实现类似如下：

```cpp
bool operator<(const T &__x, const T &__y) {
    return __x < __y;
}
```

只有 `const` 函数才可以访问 `const` 对象中的数据。
