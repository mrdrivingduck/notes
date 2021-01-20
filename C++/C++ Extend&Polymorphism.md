# Extend and Polymorphism of C++

Created by : Mr Dk.

2018 / 07 / 11 23:12

Hangzhou, Zhejiang, China

---

## 构造函数 - Constructor

* 构造函数与类同名
* 构造函数没有返回值类型
* 若未声明构造函数，则系统自动产生一个 *缺省构造函数*
* 对象创建时系统 **自动调用** 构造函数
* 构造函数没有参数，则成为 *缺省构造函数*，替换系统自动产生的构造函数
* **Overload**

## 拷贝构造函数 - Copy Constructor

* 一种特殊的构造函数
* 采用同类型的另一个对象初始化时自动调用
* 缺省拷贝构造函数：按位拷贝

```c++
// 若构造函数中有缺省参数
// 则只需在函数声明时加入缺省参数即可

class Date
{
private:
    int year;
    int month;
    int date;
    
public:
    Date(int _year = 2018, int _month = 7, int _date = 8);
    Date(const Date & d);
}

// 构造函数的实现可以有两种写法
```

第一种写法：

```c++
// Constructor
Date::Date(int _year, int _month, int _date)
{
    year = _year;
    month = _month;
    date = _date;
    // Other works ...
}

// Copy Constructor
Date::Date(const Date & d)
{
    year = d.year;
    month = d.month;
    date = d.date;
    // Other works ...
}
```

第二种写法：

```c++
// Constructor
Date::Date(int _year, int _month, int _date)
    : year(_year), month(_month), date(_date)
{
    // Other works ...
}

// Copy Constructor
Date::Date(const Date & d)
    : year(d.year), month(d.month), date(d.date)
{
    // Other works ...
}

// 注意参数顺序最好不变
// 不然编译器会报 Warning
```

## 析构函数 

* 与类同名，前面多一个 `~`
* 对象终止时被自动调用（隐式调用）
* 功能：清理，释放内存
* 没有返回值类型
* 不接受参数

## 继承 - Extend

A new class (派生类) based on an existing class (基类)。派生类继承基类所有的 *成员变量* 和 *成员函数*：

* **继承**：保持已有类的特性而构造新类的过程
* **派生**：在已有类的基础上新增自己的特性的过程

继承方式：

* public
  * 基类的 private 成员对于派生类 **不可访问**
  * 基类的 protected 成员成为派生类的 protected 成员
  * 基类的 public 成员成为派生类的 public 成员
* protected
  * 基类的 private 成员对于派生类 **不可访问**
  * 基类的 protected 成员成为派生类的 protected 成员
  * 基类的 public 成员成为派生类的 protected 成员
* private
  * 基类的 private 成员对于派生类 **不可访问**
  * 基类的 protected 成员成为派生类的 private 成员
  * 基类的 public 成员成为派生类的 private 成员

继承声明：

```c++
#include "Date.h"

class Time : public Date	// 继承方式与基类
{
private:
    int hour;
    int minute;
    int second;

public:
    Time(int _hour = 0, int _minute = 0, int _second = 0);
    Time(Date &date, int _hour = 0, int _minute = 0, int _second = 0);
    Time(int _year, int _month, int _date, int _hour = 0, int _minute = 0, int _second = 0);
    void Print();
};
```

构造函数与析构函数：

* 派生类的构造函数需要调用基类的构造函数
* 基类的构造函数 **先于** 派生类的构造函数执行
* 派生类的构造函数需要传递参数给基类的构造函数
* 析构函数的调用顺序 **相反**

```c++
// 调用基类的缺省构造函数
Time::Time(int _hour, int _minute, int _second)
    : hour(_hour), minute(_minute), second(_second)
{
    // Initialize of this class
}

// 调用基类的拷贝构造函数
Time::Time(Date &date, int _hour, int _minute, int _second)
    : Date(date), hour(_hour), minute(_minute), second(_second)
{
    // Initialize of this class
}

// 调用基类的构造函数
Time::Time(int _year, int _month, int _date,
            int _hour, int _minute, int _second)
    : Date(_year, _month, _date), hour(_hour), minute(_minute), second(_second)
{
    // Initialize of this class
}

// 参数顺序最好不要错乱
```

派生类对象与基类对象的关系：

* 派生类对象可以向基类对象赋值 （舍弃派生类自己的成员）
* 基类的指针或引用可以指向派生类对象

派生类对象的访问权限：

* 派生类不能访问基类的 `private` 成员
* 派生类可以访问基类的 `public` 成员和 `protected` 成员

```c++
void Time::Print()
{
    Date::Print();
    cout << hour << " " << minute << " " << second << endl;
}
```

## 多态 - Polymorphism 

联编：确定程序中调用和代码之间的关系

* 静态联编：在编译阶段完成，用对象名或类名限定要调用的函数，如 `Date::Print()` 与 `Time::Print()`
* 动态联编：联编工作在程序执行时进行，程序执行时才确定将要调用的函数

虚函数：

* 动态联编的基础
* **非静态** 成员函数
* `virtual Function_Declaration();`
* 声明中加入 `virtual` 关键字即可，实现中不需要

```c++
Class Date
{
    ...
    // Declaration
    virtual void Print();
    ...
}

void Date::Print()
{
    // Implementation
}
```

继承性：基类中声明为虚函数，派生类中无论是否说明，同原型函数自动为虚函数。其本质是 Override (同名覆盖)，而非 Overload (重载)。使用方式：

* 通过基类指针或引用
* 执行时，根据指针指向的类，决定调用哪个类的函数

纯虚函数与抽象类：

* 在基类中声明的虚函数
* 无函数体
* 要求派生类必须 override 该函数

声明方式：

```c++
class Date
{
    ...
    virtual void Print() = 0;
    ...
}
```

包含 **纯虚函数** 的类即为抽象类

* 抽象类不能实例化
* 抽象类的派生类必须 override 抽象类的纯虚函数才可以实例化

重要概念：

* 派生类对象可以赋值给基类对象
* 基类指针或引用可以指向派生类对象
* 若虚函数已有实现，派生类若不覆盖虚函数，则直接继承基类的虚函数
* 若派生类不覆盖基类的纯虚函数，则派生类也为抽象类，无法实例化

---

