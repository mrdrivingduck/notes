## C++ - Operator Overload

Created by : Mr Dk.

2018 / 09 / 11 14:42

Nanjing, Jiangsu, China

---

##### 1. 目标

* 采用领域内习惯性的记述形式
* 必要性：
  * `C++` 中预定义的运算符只能处理 __基本数据类型__
* 使自定义的类可以使用通用的 `C++` 运算符
  * 运算类 -  `+` `-`  等
  * 比较类 - `<` `==` 等
  * 赋值类 - `=`
  * 输入输出类 - `>>` `<<`  等
  * 其它类 - `[]` `()` 等

---

##### 2. 规则与限制

* 实现机制
  * 将指定的 __运算符__ 转化为对 __运算符函数__ 的调用
  * 将 __运算对象__ 转化为 __运算符函数的实参__
  * 编译系统对重载运算符的选择，遵循函数重载的选择原则
* 不能重载的运算符：`.` `*` `::` `?: ` `sizeof`
* 只能重载 `C++` 已有的运算符
* 不能改变运算符的 __优先级__ 和 __结合性__
* 不能改变操作数个数 _（维持相同的语法规则）_
* 重载后的运算符参数中至少要包含一个用户自定义的类型
  * 防止用户对 __标准数据类型__ 定义重载规则

---

##### 3. 实现形式

* 重载为 __类成员函数__

  * ```C++
    #include <iostream>
    using namespace std;
    
    class Test 
    {
    private:
        int value;
    public:
        // Constructor
        Test(int value) {this -> value = value;}
        // 重载为类成员函数
        // 只需一个外部参数即可 另一个参数为对象本身
        // 最好带有 const，以便集成 STL
        bool operator< (const Test &t) const;
    };
    
    bool Test::operator< (const Test &t) const
    {
        return value < t.value;
    }
    
    int main()
    {
        Test t1(7);
        Test t2(6);
        cout << (t1 < t2) << endl;
    
        return 0;
    }
    ```

* 重载为 __友元函数__

  * ```C++
    #include <iostream>
    using namespace std;
    
    class Test 
    {
    private:
        int value;
    public:
        // Constructor
        Test(int value) {this -> value = value;}
        // 重载为友元函数
        // 由于函数不属于类，参数个数发生变化
        friend bool operator< (const Test &t1, const Test &t2);
    };
    
    bool operator< (const Test &t1, const Test &t2) {
        return t1.value < t2.value;
    }
    
    int main()
    {
        Test t1(5);
        Test t2(6);
        cout << (t1 < t2) << endl;
    
        return 0;
    }
    ```

* `C++` 中规定，`=` `[]` `()` `->` 四个运算符只能被重载为 __类成员函数__

  * 因为这四种运算符没有精确匹配参数类型和数目的功能

* `<<` 和 `>>` 用于输入输出时只能被重载为 __友元函数__

  * 因为若重载为 __类成员函数__，则对象本身默认作为第一个参数
  * 那么使用方式将变为：`t << cout`，这会令人迷惑，不可取！

---

##### 4. 几种重载写法

```C++
#include <iostream>
using namespace std;

class Test 
{
private:
    int value;
public:
    Test(int value) {this -> value = value;}
    Test(const Test &t) {this -> value = t.value;}
    int getValue() {return value;}
    
    // 重载 + ，返回一个新的对象
    // Test t3 = t1 + t2;
    // 重载 - 等同理
    Test operator+ (const Test &t)
    {
        return Test(value + t.value);
    }
    
    // 重载 == ，返回一个逻辑值
    // 重载 < > <= >= 等同理
    bool operator== (const Test &t)
    {
        return value == t.value;
    }
    
    // 重载 = ，返回对象本身，因此返回值带引用
    // 重载 += -= 等同理
    Test & operator= (const Test &t)
    {
        value = t.value;
        return *this;
    }
    
    // 重载 ++ ，返回对象本身，因此返回值带引用，无需其它参数
    // 此运算符为 前置 ++
    // ++t;
    // 重载 -- 等同理
    Test & operator++ ()
    {
        value++;
        return *this;
    }
    
    // 重载 ++ ，返回对象本事，因此返回值带引用
    // 此运算符为 后置 ++
    // t++;
    // int 参数为虚设，目的是为了区分前后置，不会被使用，值为0
    // 虚参数不必命名，否则编译器将有警告 - 参数未使用
    // 重载 -- 等同理
    Test & operator++ (int)
    {
        value++;
        return *this;
    }
    
    // 重载 << ，用于通过 cout 直接输出
    // 只能通过 友元函数 的方式实现
    friend ostream & operator<< (ostream &out, const Test &t)
    {
        out << t.value;
        return out;
    }
    
    // 重载 >> ，用于通过 cin 直接输入
    // 只能通过 友元函数 的方式实现
    // 参数中自定义对象不能带 const ，因为该对象不是常量，会被输入改变
    // 应当加入输入格式错误的处理
    friend istream & operator>> (istream &in, Test &t)
    {
        in >> t.value;
        return in;
    }
};
```

* 如果需要使用 `STL`，则最重要的是重载 `<` 
* 且重载声明后一定要加 `const`

---

##### 5. 总结

_运算符重载_ 在 `C++` 中是一项相当重要的技术

在实现完成后 可以使编码更加简洁且易于理解

---

