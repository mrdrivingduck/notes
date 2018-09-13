## C++ STL set

Created by : Mr Dk.

2018 / 03 / 30 23:27

Nanjing, Jiangsu, China

---

##### 1. 原型 特性

```C++
template < 
		class T,
        class Compare = less<T>,
        class Alloc = allocator<T>
> class set;
```

 * 集合容器
 * *key* 就是 *value*
 * 容器中 *key* 值唯一，按照 *key* 值从小到大排列
 * 底层实现为 *红黑树*
 * 插入元素时不破坏顺序
 * 若元素已存在，则插入失败

---

##### 2. 引用头文件

```C++
#include <set>
using namespace std;	// OR : std::set
```

---

##### 3. 构造函数

```C++
set <key_type> Set;
```

---

##### 4. 基本属性

```C++
// 返回 set 中的元素个数
int size = Set.size();

// 返回 set 是否为空
bool empty = Set.empty();

// 返回 set 的最大容量
int max_size = Set.max_size();
```

---

##### 5. 迭代器的声明和使用 （遍历）

```C++
// 声明正向迭代器
set <key_type>::iterator setIter;
// 返回指向第一个元素的迭代器
setIter = Set.begin();
// 返回指向最后一个元素下一个位置的迭代器
setIter = Set.end();

// 声明反向迭代器
set <key_type>::reverse_iterator reverseIter;
// 返回指向最后一个元素的迭代器
reverseIter = Set.rbegin();
// 返回指向第一个元素前一个位置的迭代器
reverseIter = Set.rend();

// 取得 key 值
key_type key = *setIter;

// 遍历
for (setIter= Set.begin();
     setIter != Set.end();
     setIter++) {
    // *setIter
    // TO DO ...
}
```

---

##### 6. 查找

```C++
setIter = Set.find(key);

// 若没有找到 key ，则返回指向超尾元素的迭代器
// 若找到 key ，则返回指向该 node 的迭代器
// 时间复杂度基本为 Log(Map.size())
if (setIter == Set.end()) {
    // Not Found
} else {
    // Found
}
```

---

##### 7. 插入

```C++
// 若 key 已存在，则插入失败
// 新值不会覆盖旧值
// 调用拷贝构造函数
Set.insert (key);

// 若需要获得插入状态
// 返回的迭代器指向 set 中已存在的 key
// 返回的 bool 表示插入是否成功
pair <set <key_type>::iterator, bool> res = Set.insert(key);
if (res.second == false)
{
    // Insert failure
    // TO DO ...
}
```

---

##### 8. 删除

```C++
// 删除迭代器指向的 node
Set.erase (setIter);

// 删除指定的 key 值所对应的 node
Set.erase (key);

// 删除一个范围内的 node
Set.erase (Iter1, Iter2);

// 删除所有元素
Set.clear();
```

---

##### 9. 自定义对象作为 key 时需要注意

```C++
// 由于 set 本身是有序的
// 因此需要 key 类型是可比较的
// 当使用自定义的 class 作为 key 时
// 需要 overload < 运算符
// 在 overload 的写法上需要注意
// 千万不能漏掉 {} 之前的 const

class Class {
    public:
    	// ...
    	// ...
    	// Constructor
    	// Copy_Constructor (VERY IMPORTANT!!!)
        bool operator < (const Class &C) const {
            // TO DO ...
            // return true | return false;
        }
};
```

---

### *总结*

便捷、高效的数据结构

在 *key* 本身也具有数据属性的情况下代替 *map* 使用

查找、插入、删除的效率都很高

在 *并查集* 题目中经常使用

---

