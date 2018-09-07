## Extend and Polymorphism of C++

Created by : Mr Dk.

2018 / 07 / 11 23:12

Hangzhou, Zhejiang, China

---

#### 1. 构造函数 - Constructor

 * 构造函数与类同名
 * 构造函数没有返回值类型
 * 若未声明构造函数，则系统自动产生一个 _缺省构造函数_
 * 对象创建时系统 __自动调用__ 构造函数
 * 构造函数没有参数，则成为 _缺省构造函数_ ，替换系统自动产生的构造函数
 * __Overload__

#### 2. 拷贝构造函数 - Copy Constructor

* 一种特殊的构造函数

* 采用同类型的另一个对象初始化时自动调用

* 缺省拷贝构造函数：按位拷贝

  ```C++
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

* 第一种写法

  ```C++
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

* 第二种写法

  ```C++
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

---

#### 3. 析构函数 

* 与类同名，前面多一个 `~`
* 对象终止时被自动调用（隐式调用）
* 功能：清理，释放内存
* 没有返回值类型
* 不接受参数

---

#### 4. 继承 - Extend

* A new class（派生类） based on an existing class（基类）

* 派生类继承基类所有的 _成员变量_ 和 _成员函数_

* __继承__ - 保持已有类的特性而构造新类的过程

* __派生__ - 在已有类的基础上新增自己的特性的过程

* 继承方式

  * public
    * 基类的 private 成员对于派生类 __不可访问__
    * 基类的 protected 成员成为派生类的 protected 成员
    * 基类的 public 成员成为派生类的 public 成员
  * protected
    * 基类的 private 成员对于派生类 __不可访问__
    * 基类的 protected 成员成为派生类的 protected 成员
    * 基类的 public 成员成为派生类的 protected 成员
  * private
    * 基类的 private 成员对于派生类 __不可访问__
    * 基类的 protected 成员成为派生类的 private 成员
    * 基类的 public 成员成为派生类的 private 成员

* 声明

  ```C++
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

* 构造函数与析构函数

  * 派生类的构造函数需要调用基类的构造函数
  * 基类的构造函数 __先于__ 派生类的构造函数执行
  * 派生类的构造函数需要传递参数给基类的构造函数
  * 析构函数的调用顺序 __相反__

  ```C++
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

* 派生类对象与基类对象的关系

  * 派生类对象可以向基类对象赋值 （舍弃派生类自己的成员）
  * 基类的指针或引用可以指向派生类对象

* 派生类对象的访问权限

  * 派生类不能访问基类的 private 成员
  * 派生类可以访问基类的 public 成员和 protected 成员

  ```C++
  void Time::Print()
  {
      Date::Print();
      cout << hour << " " << minute << " " << second << endl;
  }
  ```

---

#### 5. 多态 - Polymorphism 

* 联编：确定程序中调用和代码之间的关系

  * 静态联编：在编译阶段完成，用对象名或类名限定要调用的函数

    * `Date::Print()` 与 `Time::Print()`

  * 动态联编：联编工作在程序执行时进行，程序执行时才确定将要调用的函数

* 虚函数

  * 动态联编的基础

  * __非静态__ 成员函数

  * `virtual Function_Declaration();`

  * 声明中加入 `virtual` 关键字即可，实现中不需要

    ```C++
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

  * 继承性：基类中声明为虚函数，派生类中无论是否说明，同原型函数自动为虚函数

  * 本质：__Override__ ！！！（同名覆盖），而非 __Overload__ （重载）

  * 使用方式

    * 通过基类指针或引用
    * 执行时，根据指针指向的类，决定调用哪个类的函数

* __注意重要概念__

  * __派生类对象可以赋值给基类对象__
  * __基类指针或引用可以指向派生类对象__

* 纯虚函数与抽象类

  * 纯虚函数是在基类中声明的虚函数

    * 无函数体

    * 要求派生类必须 __Override__ 该函数

    * 声明方式

      ```C++
      class Date
      {
          ...
          virtual void Print() = 0;
          ...
      }
      ```

  * 包含 __纯虚函数__ 的类即为抽象类

    * 抽象类不能实例化
    * 抽象类的派生类可以实例化
    * 抽象类的派生类必须 override 抽象类的纯虚函数

---



