# C++ - Polymorphism with unknown type

Created by : Mr Dk.

2018 / 07 / 15 14:32

Hangzhou, Zhejiang, China

---

### 1. 问题描述

* 返回的数据类型不确定，在 `C++` 中使用一般方法无法实现
* 因为 `C++` 中，函数的返回值类型必须是确定的

### 2. 解决方法

#### 2.1 基类与派生类的定义

* 指定一个基类，在主程序中保留一个基类指针
* 基类中定义派生类需要 `override` 的虚函数或纯虚函数
* 虚函数或纯虚函数的返回值类型为 `void *`
* 各派生类的成员变量储存相应数据类型的值
* 各派生类返回相应数值的 `override` 函数的返回值全部为 `void *`

```C++
#include <string>
using namespace std;

// 基类 抽象类 不实例化
class Base 
{
private:

public:
    virtual ~Base() {}
    virtual void* getValue() = 0;
};

class ChildInt : public Base 
{
private: 
    int value;
public: 
    ChildInt(int i) {value = i;}
    ~ChildInt() {}

    void* getValue() {return (void *)(&value);}
};

class ChildDouble : public Base 
{
private: 
    double value;
public:
    ChildDouble(double i) {value = i;}
    ~ChildDouble() {}

    void* getValue() {return (void *)(&value);}
};

class ChildString : public Base
{
private:
    string value;
public: 
    ChildString(string i) {value = i;}
    ~ChildString() {}

    void* getValue() {return (void *)(&value);}
};
```

#### 2.2 主函数中的使用方式

* 使用基类指针和 `new` 关键字，直接构造派生类对象
* 利用 __多态__，使用基类指针调用派生类的 `override` 函数
* 根据数据类型，将得到的 `void *` 类型的指针强制转换成对应数据类型的指针
* 对指针使用 `*` 运算符取得具体的数值

```C++
#include <iostream>
using namespace std;

int main() 
{
    Base *base;

    base = new ChildInt(5);
    cout << *((int *)(base->getValue())) << endl;
    delete base;
    base = NULL;

    base = new ChildDouble(2.5);
    cout << *((double *)(base->getValue())) << endl;
    delete base;
    base = NULL;

    base = new ChildString("emm");
    cout << *((string *)(base->getValue())) << endl;
    delete base;
    base = NULL;

    return 0;
}
```

### 3.注意

* 如果需要在基类的构造函数中进行一些初始化

  * 在派生类的构造函数中，进行参数传递，先进行基类的初始化
  * __基类的构造函数无法被声明为__`virtual` ，但 __析构函数__ 可以


```C++
Class Child : public Base
{
private:

public:
	Child(int arg)
		: Base(arg)
	{
        // TO DO ...
	}
}
```

* 如果派生类需要在析构函数中做个性化的工作
  *  __基类的析构函数需要显式定义为__  `virtual` ，但 __不能定义为纯虚函数__
  * 这样，在执行 `delete base;` 时
  * 先根据多态特性调用对应派生类的析构函数完成对应类型的析构
  * 再调用基类析构函数（如不需要，则函数体为空）
  * 在派生类的析构函数中，可进行个性化的工作

---

