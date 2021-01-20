# C++ - Template & Genericity

Created by : Mr Dk.

2018 / 09 / 13 23:42

Nanjing, Jiangsu, China

---

## About Template - 模板

目的：**重用代码**。例子：容器类。

* Used for storing other objects or types
* For different data types, codes are the same **except types**

Why not create a generic class?

* Independent from **types**
* Use **types** as parameters to this class

## 常用模板类

比如 *STL* 中的 `vector` `map` 等。`vector <int>` / `vector <double>` / `vector <string>` 共用模板类 `std::vector`。

## 使用方式

1. 在类声明代码块前声明 `template <class T>` 或 `template <typename T>`
2. 在类中直接使用 `T` 作为数据类型
3. 若类成员函数的实现在类外
  * 在每一个使用泛型的成员函数代码块前声明 `template <class T>` 或 `template <typename T>`
  * ```c++
    返回值类型 类名 <T>:: 类成员函数 (参数列表)
    {
        // 函数实现
        // TO DO ...
    }
    ```

4. 使用时，在 `<>` 内指定特定的数据类型即可使用模板
  * 数据类型相当于变量
  * 必须显式指定数据类型，使编译器可以确定要生成的函数
  * 数据类型必须实现模板类限定的方法，如 *STL* 中的重载 `<` 运算符

## 4. 应用实例

使用 *STL* 封装一个 MultiMap
  * 一个 key 可以对应多个 value
  * value 不可重复
  * 实现 *STL* 中 map 的基本操作

核心思路
  * 底层使用 *STL* 中的 map 和 set：`map <key_type, set <value_type> >`
  * 对外封装为：`MultiMap <key_type, value_type>`

```c++
#include <iostream>
#include <map>
#include <set>
using std::cout;
using std::endl;
using std::set;
using std::map;
using std::pair;

template <class K, class S>
class MultiMap
{
private:
    map <K, set <S> > multimap;
public:
    // Constructor
    MultiMap <K, S> () {}
    // Copy Constructor
    MultiMap <K, S> (MultiMap <K, S>& M);
    typename map <K, set <S> >::iterator find(const K &k);
    pair <typename map <K, set <S> >::iterator, bool> insert(const K &k, const S &s);
    int size() {return multimap.size();}
    int size(const K &k);
};

template <class K, class S>
MultiMap <K, S>::MultiMap(MultiMap <K, S>& M)
{
    multimap = M.multimap;
}

template <class K, class S>
typename map <K, set <S> >::iterator
    MultiMap <K, S>::find(const K &k)
{
    return multimap.find(k);
}

template <class K, class S>
pair < typename map <K, set <S> >::iterator, bool>
    MultiMap <K, S>::insert(const K &k, const S &s)
{
    typename map <K, set <S> >::iterator mapIter = multimap.find(k);
    if (mapIter == multimap.end())
    {
        set <S> temp;
        temp.insert(s);
        return multimap.insert(pair <K, set <S> > (k, temp));
    }
    set <S>& Set = mapIter->second;
    pair <typename set <S>::iterator, bool> res = Set.insert(s);
    return pair <typename map <K, set <S> >::iterator, bool> (mapIter, res.second);
}

template <class K, class S>
int MultiMap <K, S>::size(const K &k)
{
    typename map <K, set <S> >::iterator mapIter = multimap.find(k);
    if (mapIter == multimap.end())
    {
        return 0;
    }
    else
    {
        return (mapIter->second).size();
    }
}

int main()
{
    // Testing
    MultiMap <int, double> Mul;
    
    Mul.insert(1, 2.5);
    Mul.insert(1, 2.7);
    Mul.insert(2, 2.6);
    Mul.insert(2, 2.6);
    Mul.insert(3, 2.4);

    cout << Mul.size() << endl;
    cout << Mul.size(1) << endl;
    cout << Mul.size(2) << endl;

    return 0;
}
```

---

