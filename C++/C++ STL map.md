# C++ STL map

Created by : Mr Dk.

2018 / 03 / 27 09:41

Nanjing, Jiangsu, China

---

## Definition

```cpp
template < class Key,
           class T,
           class Compare = less<Key>,
           class Alloc = allocator<pair<const Key,T> >
           > class map;
```

Map 提供 key-value 的映射，底层实现是红黑树 (Red-Black Tree)，是一种非严格意义上的 _AVL_ 树，自带排序的功能。Key 必须能够被比较，所有元素根据 key 的大小排序 - 若 key 为自定义对象，必须 overload `<` 运算符。Map 中不会出现重复的 key，若 key 已存在，则插入失败。

根据 key 可以快速查找节点及其 value，查找的时间复杂度基本为 log(n)：

- 快速插入 key-value pair
- 快速删除 key-value pair
- 快速根据 key 修改对应的 value
- 插入、删除结点对其它结点没有影响

```cpp
#include <map>
using namespace std;

// using std::map;
// using std::pair;
// using std::make_pair;
```

## Constructor

```cpp
map<key_Type, value_Type> map;
```

## Attribute

```cpp
int size = map.size(); // 返回 map 中的元素个数
bool empty = map.empty(); // 返回 map 是否为空
```

## Iterator

```cpp
map<key_Type, value_Type>::iterator iter; 正向迭代器
iter = map.begin(); // 指向第一个元素的迭代器
iter = map.end(); // 指向最后一个元素的下一个位置的迭代器

map<key_Type, value_Type>::reverse_iterator r_iter; // 反向迭代器
r_iter = map.rbegin(); // 指向最后一个元素的迭代器
r_iter = map.rend(); // 指向第一个元素前一个位置的迭代器

key_Type key = iter->first; // 取得 key 值
value_Type value = iter->second; // 取得 value 值

// 遍历
for (iter = map.begin(); iter != map.end(); iter++) {
    cout << iter->first << " ";
    cout << iter->second << endl;
}
```

## Search

```cpp
iter = map.find(key);

// 若没有找到 key ，则返回指向超尾元素的迭代器
// 若找到 key ，则返回指向该 node 的迭代器
// 时间复杂度基本为 Log(map.size())
if (iter == map.end()) {
    // Not Found
} else {
    // Found
    cout << iter->first << " ";
    cout << iter->second << endl;
}
```

## Insert

```cpp
// 若 key 已存在，则插入失败，新值不会覆盖旧值
map.insert(pair<key_Type, value_Type> (key, value));

// 若想要查看插入是否成功
// 可采用如下插入方式
pair<map<key_Type, value_Type>::iterator, bool> inserted
	= map.insert(pair<key_Type, value_Type> (key, value));

if (inserted.second == true) {
    // Insert success
    // TO DO ...
} else {
    // Insert unsuccess
    // TO DO ...
}
```

## Deletion

```cpp
map.erase(iter); // 删除迭代器指向的 node
map.erase(key); // 删除指定的 key 值所对应的 node
map.erase(iter1, iter2); // 删除一个范围内的 node
map.clear(); // 删除所有元素
```

## Object as Key

```cpp
// 由于 map 本身是有序的，因此需要 key 的类型是可比较的。
// 当使用自定义的 class 作为 key 时，需要 overload < 运算符
// 在 overload 的写法上需要注意，千万不能漏掉 {} 之前的 const

class Class {
public:
    // ...
    // ...
    // Constructor
    // Copy_Constructor (VERY IMPORTANT!!!)
    bool operator < (const Class &c) const {
        // TO DO ...
        // return true | return false;
    }
};
```

---

## Summary

可以通过 map 方便地关联两个或多个属性。
