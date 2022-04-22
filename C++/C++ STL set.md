# C++ STL set

Created by : Mr Dk.

2018 / 03 / 30 23:27

Nanjing, Jiangsu, China

---

## Definition

```cpp
template <
    class T,
    class Compare = less<T>,
    class Alloc = allocator<T>
> class set;
```

Set 为集合容器，key 就是 value。容器中 key 值唯一，按照 key 值从小到大排列。底层实现为 _红黑树_，插入元素时不破坏顺序，若元素已存在，则插入失败。

```cpp
#include <set>
using namespace std; // OR : std::set
```

## Constructor

```cpp
set <key_type> set;
```

## Attributes

```cpp
int size = set.size(); // 返回 set 中的元素个数
bool empty = set.empty(); // 返回 set 是否为空
int max_size = set.max_size(); // 返回 set 的最大容量
```

## Iterator

```cpp
set<key_type>::iterator iter; // 正向迭代器
iter = set.begin(); // 指向第一个元素的迭代器
iter = set.end(); // 指向最后一个元素下一个位置的迭代器

set <key_type>::reverse_iterator r_iter; // 反向迭代器
r_iter = set.rbegin(); // 指向最后一个元素的迭代器
r_iter = set.rend(); // 指向第一个元素前一个位置的迭代器

key_type key = *iter; // 取得 key 值

// 遍历
for (iter= set.begin(); iter != set.end(); iter++) {
    // *iter
    // TO DO ...
}
```

## Search

```cpp
iter = set.find(key);

// 若没有找到 key ，则返回指向超尾元素的迭代器
// 若找到 key ，则返回指向该 node 的迭代器
// 时间复杂度基本为 log(set.size())
if (iter == set.end()) {
    // Not Found
} else {
    // Found
}
```

## Insert

```cpp
// 若 key 已存在，则插入失败
// 新值不会覆盖旧值
// 调用拷贝构造函数
set.insert(key);

// 若需要获得插入状态
// 返回的迭代器指向 set 中已存在的 key
// 返回的 bool 表示插入是否成功
pair<set <key_type>::iterator, bool> res = set.insert(key);
if (res.second == false) {
    // Insert failure
    // TO DO ...
}
```

## Deletion

```cpp
set.erase(iter); // 删除迭代器指向的 node
set.erase(key); // 删除指定的 key 值所对应的 node
set.erase(Iter1, Iter2); // 删除一个范围内的 node
set.clear(); // 删除所有元素
```

## Self-Defined Keys

```cpp
// 由于 set 本身是有序的，因此需要 key 类型是可比较的。
// 当使用自定义的 class 作为 key 时，需要 overload < 运算符。
// 在 overload 的写法上需要注意，千万不能漏掉 {} 之前的 const。

class Class {
public:
    // ...
    // ...
    // Constructor
    // Copy_Constructor (VERY IMPORTANT!!!)
    bool operator < (const Class &cD) const {
        // TO DO ...
        // return true | return false;
    }
};
```

---

## Summary

在 _并查集_ 类算法题目中经常使用。
