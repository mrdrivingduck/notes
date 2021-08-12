# C++ STL multimap

Created by : Mr Dk.

2018 / 09 / 15 20:16

Nanjing, Jiangsu, China

---

## Feature

```c++
template < class Key,                                   // multimap::key_type
           class T,                                     // multimap::mapped_type
           class Compare = less<Key>,                   // multimap::key_compare
           class Alloc = allocator<pair<const Key,T> >  // multimap::allocator_type
           > class multimap;
```

Multimap 提供 key - value 的映射。

- key 必须能够被比较，默认使用 `<` 运算符进行比较
- 若 key 为自定义类型，则需要重载 `<` 运算符
- key 不会重复出现，value 可以重复出现
- 根据 key 的大小排序，默认从小到大

通过 key 快速查找 value，key 可被修改，value 不可被修改。底层由 **红黑树** 实现。插入、删除操作后，其余迭代器 **不会失效**。

```c++
#include <map>
using namespace std;

// using std::multimap;
// using std::pair;
// using std::make_pair;
```

## Constructor

```c++
multimap<key_Type, value_Type> multimap; // Empty container (default)
multimap<key_Type, value_Type> multimap(another_map); // Copy constructor
multimap<key_Type, value_Type> multimap(another_map.begin(), another_map.end()); // Range constructor
```

## Operator `=`

**Copy** a container.

```c++
multimap<key_Type, value_Type> A;
multimap<key_Type, value_Type> B;
A = B;
```

## Iterators

```c++
multimap<key_Type, value_Type>::iterator iter_begin = multimap.begin(); // 指向第一个元素的迭代器
multimap<key_Type, value_Type>::iterator iter_end = multimap.end(); // 指向最后一个元素的下一个位置的迭代器
multimap<key_Type, value_Type>::reverse_iterator iter_rbegin = multimap.rbegin(); // 指向最后一个元素的迭代器
multimap<key_Type, value_Type>::reverse_iterator iter_rend = multimap.rend(); // 指向第一个元素的前一个位置的迭代器
```

## Capacity

```c++
// 返回容器是否为空
if (multimap.empty() == FALSE)
{
    // 返回容器中的元素个数
    cout << multimap.size() << endl;
    // 返回容器可容纳的最大容量
    cout << multimap.max_size() << endl;
}
```

## Modification

```c++
multimap.insert(pair<key_Type, value_Type> (key, value)); // 插入

// 删除
multimap<key_Type, value_Type>::iterator iter = multimap.find(key);
multimap.erase(iter);                               // 删除单个元素
multimap.erase(key);                                // 删除 key 的所有元素
multimap.erase(multimap.begin(), multimap.end());   // 删除范围内的元素
multimap.clear();                                   // 删除全部元素

multimap.swap(another_map);	// 交换两个容器中的内容
```

## Search

```c++
// find() - 返回第一次出现 key 的迭代器
multimap<key_Type, value_Type>::iterator iter = multimap.find(key);
if (iter == multimap.end())
{
    // NOT FOUND
}

// count() - 返回 key 出现的次数
cout << multimap.count(key) << endl;

/*
 * lower_bound() - 返回指向第一个不小于 key 的元素的迭代器 （>=）
 * upper_bound() - 返回指向第一个大于 key 的元素的迭代器 （>）
 */
typedef multimap<key_Type, value_Type>::iterator Iter;
Iter low = multimap.lower_bound(key);
Iter high = multimap.upper_bound(key);

/*
 * equal_range() - 返回指向 key 的首尾范围的迭代器
 * 返回形式为 pair - 
 *     第一个成员为 lower_bound() 的结果
 *     第二个成员为 upper_bound() 的结果
 *     ['>=', '>') 等价于 '='
 */
pair<Iter, Iter> range = multimap.equal_range(key);
for (Iter iter = range.first; iter != range.second; iter++) {
    cout << iter->first << " " << iter->second << endl;
}
```

## Reference

* [CPlusPlus.com - std::multimap](http://www.cplusplus.com/reference/map/multimap/)

