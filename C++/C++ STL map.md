# C++ STL map

Created by : Mr Dk.

2018 / 03 / 27 09:41

Nanjing, Jiangsu, China

---

## 1. 原型 特性

```c++
template < class Key,
           class T,
           class Compare = less<Key>,
           class Alloc = allocator<pair<const Key,T> >
           > class map;
```

 * 提供 `key` - `value` 的映射
 * 底层实现：红黑树 （Red-Black Tree）
    * 一种非严格意义上的 _AVL_ 树
    * 自带排序的功能
 * `key` 必须能够被比较 所有元素根据 `key` 的大小排序
    * `key` 为自定义对象，必须 _overload_ __<__ 运算符
 * _map_ 中不会出现重复的 `key` ，若 `key` 已存在，则插入失败
 * 根据 `key` 快速查找节点及其 _value_
 * 查找的时间复杂度基本为 _log ( N )_ 
* 快速插入 `key` - `value` 对
 * 快速删除 `key ` - `value` 对
* 快速根据 `key` 修改对应的 `value` 
 * 插入、删除结点对其它结点没有影响

---

## 2. 引用头文件

```C++
#include <map>
using namespace std;	// OR : std::map
```

---

## 3. 构造函数

```c++
map <key_Type, value_Type> Map;
```

---

## 4. 基本属性

```c++
// 返回 map 中的元素个数
int size = Map.size();

// 返回 map 是否为空
bool empty = Map.empty();
```

---

## 5. 迭代器的声明和使用 （遍历）

```C++
// 声明一个正向迭代器
map <key_Type, value_Type>::iterator mapIter;
// 返回指向第一个元素的迭代器
mapIter = Map.begin();
// 返回指向最后一个元素的下一个位置的迭代器
mapIter = Map.end();

// 声明一个反向迭代器
map <key_Type, value_Type>::reverse_iterator revIter;
// 返回指向最后一个元素的迭代器
revIter = Map.rbegin();
// 返回指向第一个元素前一个位置的迭代器
revIter = Map.rend();

// 取得 key 值
key_Type key = mapIter -> first;
// 取得 value 值
value_Type value = mapIter -> second;

// 遍历
for (mapIter = Map.begin();
     mapIter != Map.end();
     mapIter++) {
    cout << mapIter -> first << " ";
    cout << mapIter -> second << endl;
}
```

---

## 6. 查找

```c++
mapIter = Map.find (key);

// 若没有找到 key ，则返回指向超尾元素的迭代器
// 若找到 key ，则返回指向该 node 的迭代器
// 时间复杂度基本为 Log(Map.size())
if (mapIter == Map.end()) {
    // Not Found
} else {
    // Found
    cout << mapIter -> first << " ";
    cout << mapIter -> second << endl;
}
```

---

## 7. 插入

```C++
// 若 key 已存在，则插入失败，新值不会覆盖旧值
Map.insert (pair <key_Type, value_Type> (key, value));

// 若想要查看插入是否成功
// 可采用如下插入方式
pair <map <key_Type, value_Type>::iterator, bool> Inserted 
	= Map.insert (pair <key_Type, value_Type> (key, value));

if (Inserted.second == true) {
    // Insert success
    // TO DO ...
} else {
    // Insert unsuccess
    // TO DO ...
}
```

---

## 8. 删除

```C++
// 删除迭代器指向的 node
Map.erase (mapIter);

// 删除指定的 key 值所对应的 node
Map.erase (key);

// 删除一个范围内的 node
Map.erase (Iter1, Iter2);

// 删除所有元素
Map.clear();
```

---

## 9. 自定义对象作为 key 时需要注意

```C++
// 由于 map 本身是有序的
// 因此需要 key 的类型是可比较的
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

## 总结

很便捷、高效的数据结构

可以用来作为  _树_  的具体实现

也在一些复杂的数据结构题中使用

可以通过 _map_ 方便地关联两个或多个属性

并且查找、插入、删除的效率都极高

在 _PAT_ 的练习和考试中对我的帮助相当大

---