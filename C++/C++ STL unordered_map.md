# C++ STL unordered_map

Created by : Mr Dk.

2020 / 11 / 27 20:08

Nanjing, Jiangsu, China

---

## Template

`unordered_map` 容器与 `map` 都是以 key 为唯一标识符的，区别在于底层实现。`map` 底层使用 *红黑树* 实现，因此维护了 key 值之间的顺序关系，对 `map` 的遍历将会是有序的。而 `unordered_map` 底层使用 hash table 实现。在遍历时，会按照 bucket 来遍历，元素并不是有序的。

模板定义：

```c++
template < class Key,                                    // unordered_map::key_type
           class T,                                      // unordered_map::mapped_type
           class Hash = hash<Key>,                       // unordered_map::hasher
           class Pred = equal_to<Key>,                   // unordered_map::key_equal
           class Alloc = allocator< pair<const Key,T> >  // unordered_map::allocator_type
           > class unordered_map;
```

需要引用的头文件与命名空间：

```c++
#include <unordered_map>
using std::unordered_map;

// using std::pair;
// using std::make_pair;
```

## Declaration

```c++
unordered_map<string, int> map;
```

## Insert

有如下几种插入方式：

- 该容器重载了 `[]` 运算符，可以以类似字典的方式插入元素
    - 如果容器中已有 key 的对应元素，则直接返回该元素的引用
    - 如果容器中没有 key 的对应元素，则创建新元素插入容器中，并返回该元素的引用
- 通过构造 `pair<>` 来插入元素

```c++
map["Tom"] = 1;

map.insert(make_pair("Tom", 1));
map.insert(pair<string, int> ("Tom", 1));

pair<unordered_map<string, int>::iterator, bool> inserted 
	= map.insert(pair<string, int> ("Tom", 1));
```

插入操作返回指向插入元素的迭代器，以及插入是否成功。

## Erase

以迭代器作为参数，删除元素；也可以直接用 key 来删除元素。

由于本容器无序，所以 **范围删除** 的结果不可预测。

```c++
map.erase("Tom");
map.erase(map.find("Tom"), map.end()); // 范围删除
```

## Search

以 key 为元素查找。

```c++
unordered_map<string, int>::const_iterator iter = map.find("Tom");

if (iter == map.end()) {
    // FOUND
} else {
    // cout << iter->first << " " << iter->second;
}
```

另外，还可以计算 key 元素的个数。对于该容器来说，要么是 1，要么是 0。含义上相当于 `exist()`：

```c++
int count = map.count("Tom");
```

## Element Access

两种方式可以访问 value 的引用，与 `string` 类似：

- `[]` 运算符
- `at()` 函数

```c++
map["Tom"] = 1;
map.at("Tom") += 2;
```

## Bucket

传统的容量操作只体现容器内被用户操作的元素个数，而 `unordered_map` 内部维护的 hash 桶容量通过这组 API 返回。

```c++
int bucket_count = map.bucket_count();         // 取得桶的个数
int bucket_size = map.bucket_size(0);          // 第 0 个桶中的元素数量
int max_bucket_count = map.max_bucket_count(); // 桶的最大个数
int bucket_id = map.bucket("Tom");             // Tom 位于第几个 bucket 中，参数为 key_type
```

## Hash

与 hash 算法相关的量：

```c++
float load_factor = map.load_factor();         // 计算公式为 size / bucket_count，衡量容器的填充程度
float max_load_factor = map.max_load_factor(); // get
map.max_load_factor(max_load_factor / 2.0);    // set
map.rehash(20);                                // 设置 hash 桶数量的最小值
map.reserve(20);                               // 设置 hash 桶的数量至最适合存放至少 n 个元素
```

---

## References

[cplusplus.com - unordered_map](http://www.cplusplus.com/reference/unordered_map/unordered_map/)

[GeeksforGeeks - unordered_map in C++ STL](https://www.geeksforgeeks.org/unordered_map-in-cpp-stl/)

