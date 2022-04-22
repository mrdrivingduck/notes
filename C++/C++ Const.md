# C++ - Const

Created by : Mr Dk.

2021 / 03 / 05 23:22

Nanjing, Jiangsu, China

---

## About

`const` 是一个 C++ 限定符，用于指出 **常量** 的符号内容。创建常量的通用格式如下：

```cpp
const type name = value;
```

应当尽量在声明时直接对常量进行初始化。

与 `#define` 的区别：

- `const` 能够明确指明常量数据类型
- C++ 的作用域规则能将 `const` 的定义限制在特定的函数或文件中
- 可以用于数组或结构体等复杂类型

## Const with Pointers

`const` 关键字能够与指针组合出两种用法：

- 指向常量的指针：指针认为指向的值是常量，因此不允许用指针修改值
- 常量指针：指针自身是一个常量，指针的值无法被修改

### 指向常量的指针

对于一个 _指向常量的指针_，其真正指向的数据不一定是一个常量，只是指针这么认为。所以想通过这个指针去修改数据是不行的，但是可以绕开指针去修改数据。

```cpp
int age = 24;
const int *pt = &age;

age = 25; // ojbk
// (*pt)++; NO!
```

可以看到，`const` 与 `int` 结合为 `const int`，表示了指针的类型。指针认为它指向了一个不能被修改的常量。由于 **指向的对象是否能被修改** 的认知方在指针，就有了如下很有意思的性质：

- 一个 `const` 指针可以被非 `const` 指针赋值 (自然也可以被 `const` 指针赋值)
- 一个非 `const` 指针不能被 `const` 指针赋值

> 通俗地说，`const` 指针有点像一个 _暖男_：
>
> - 毫不在意过去：无论是 `const` 指针还是非 `const` 指针，都可以赋值给它
> - 固执的保护欲：只要它认定了指向的数据是 `const`，那么它是不会把它交 (赋值) 给非 `const` 指针的

基于这个性质，对于下面的函数声明，参数传递将会失败。因为一个 `const` 指针不能赋值给非 `const` 的形参：

```cpp
const int months[12] = { 31,28,31,30,31,30,31,31,30,31,30,31 };

int sum(int arr[], int n); // int sum(const int arr[], int n);

cout << sum(months, 12); // NOT ALLOWED
```

通常将指针作为函数参数传递时，使用 `const` 指针来保护参数数据不被修改。在函数声明中，应当尽量使用 `const`：

- 避免无意间修改数据导致程序错误
- `const` 使得函数可以接收 `const` 和非 `const` 实参，否则只能接受非 `const`

### 指针常量

- 数据类型为 `int *` 表示该指针指向的对象可以被修改 (非 `const`)
- `const` 与指针变量名结合，表示该变量的值不可修改

```cpp
int sloth = 3;
int * const finger = &sloth;
```

上述声明使得该指针只能指向 `sloth` 所在地址。

## Const Member Function

保证声明的函数 **不会修改** 调用它的对象。

```cpp
void Stock::show() const;
```

```cpp
const Stock s;
s.show(); // NOT ALLOWED if not const
```
