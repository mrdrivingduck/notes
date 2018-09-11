## C++ static & friend members of class

---

Created by : Mr Dk.

2018 / 09 / 11 23:03

Nanjing, Jiangsu, China

---

##### 1. 基本概念

* 一般的成员函数
  * 能够访问类的 _private_ 部分
  * 函数位于类的作用域之中
  * 函数由一个对象激活
* `static` 成员函数
  * 能够访问类的 _private 且 static_ 部分
  * 函数位于类的作用域之中
  * __函数不由对象激活__
* `friend` 成员函数
  * 能够访问类的 _private_ 部分
  * 函数不位于类的作用域之中

---

##### 2. 静态成员

* 由 `static` 关键字声明
* 是 __类__ 的一部分，而不是 __对象__ 的一部分 - 因此只有 __一个副本__
* 因此不需要使用特定对象调用，直接使用 __类名__ 和 __::__ 即可调用
* 不能使用 `this` 指针
* 静态成员变量
  * __必须在类外定义和初始化，用 :: 指明所属的类__
* 静态成员函数
  * 只能引用该类的 __静态__ 成员变量和 __静态__ 成员函数

```C++
#include <iostream>
using namespace std;

class Test
{
    private:
    	static int value;
    public:
    	static int getValue()；
};

// 类外初始化静态成员变量
int Test::value = 0;
// 类外添加静态成员函数的实现
int Test::getValue() {
    return value;
}
// ATTENTION : 类外不需要写 static 关键字

int main()
{
	// 直接使用类名和作用域解析运算符调用
    // 不需要实例化对象
    cout << Test::getValue() << endl;
    
    return 0;
}
```

---

##### 3. 友元成员

* 用 `friend` 关键字声明
* 友元函数不是类的成员，但可以访问类的 `private` 变量
* 友元可以是
  * 一个独立的函数
  * 其它类的成员函数
  * 其它类本身 _友元类_
* 友元用于处理 __同一个类 多个对象之间的关系__，该关系不为单个对象所有

```C++
#include <iostream>
using namespace std;

class Test
{
	private:
    	int a;
    	int b;
    public:
    	Test (int a, int b)
        {
            this -> a = a;
            this -> b = b;
        }
    	friend int distance(const Test &t1, const Test &t2);
};

// 类外不需要使用 friend 关键字
// 不属于类，不需要使用类名
int distance(const Test &t1, const Test &t2)
{
    // 直接访问 private 变量
    return t1.a - t2.a;
}

int main()
{
    Test t1(1, 2);
    Test t2(3, 4);
    cout << distance(t1, t2) << endl;
    
    return 0;
}
```

---

##### 4. 总结

静态成员已经在暑期实习中使用过了

由于马上要复习运算符重载

所以把友元也给一起复习了

---

