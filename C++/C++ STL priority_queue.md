# C++ STL priority_queue

Created by : Mr Dk.

2020 / 11 / 22 16:43

Chongqing, China

---

## Definition

```cpp
template <class T,
          class Container = vector<T>,
          class Compare = less<typename Container::value_type>
          > class priority_queue;
```

提供对指定容器类型的组织方式。将容器内元素组织为一个堆，每次保证优先级最高的元素出队列。其中，三个模板参数的含义分别为：

- 泛型类型 T
- 底层容器的实现类型 container，只支持 `vector` 或 `deque`，默认为 `vector`，底层容器需要支持 _随机访问迭代器_ 的如下操作：
  - `empty()`
  - `size()`
  - `front()`
  - `push_back()`
  - `pop_back()`
- 第三个参数是比较函数 compare，默认为 `less<T>`，堆化后每次出队的是优先级最高的元素 (大顶堆)

> ### T
>
> Type of the elements.
> Aliased as member type `priority_queue::value_type`.
>
> ### Container
>
> Type of the internal _underlying container_ object where the elements are stored.
> Its `value_type` shall be `T`.
> Aliased as member type `priority_queue::container_type`.
>
> ### Compare
>
> A binary predicate that takes two elements (of type `T`) as arguments and returns a `bool`.
> The expression `comp(a,b)`, where comp is an object of this type and a and b are elements in the container, shall return `true` if a is considered to go before b in the _strict weak ordering_ the function defines.
> The priority_queue uses this function to maintain the elements sorted in a way that preserves _heap properties_ (i.e., that the element popped is the last according to this _strict weak ordering_).
> This can be a function pointer or a function object, and defaults to `less<T>`, which returns the same as applying the _less-than operator_ (`a<b`).
>
> 另外，可以自行使用 `#include <algorithm>` 中的 `make_heap()` 等函数手动对 `vector` 等容器建堆，效果一致。

```cpp
#include <queue>
using namespace std;
// using std::priority_queue;
```

## Constructor

```cpp
priority_queue<int> pq;
priority_queue<int, vector<int>, std::greater<int>> pq;
```

## Member Functions

- `empty()`
- `size()`
- `top()`
- `push()`
- `pop()`
- `emplace()`: construct and insert element
- `swap()`

## Self-Defined Comparison

如果想要自定义比较函数，需要自行定义一个结构体，并重载 `()` 运算符：

```cpp
struct comp {
    bool operator()(vector<int> &flight1, vector<int> &flight2) {
        return flight1[1] > flight2[1];
    }
};

priority_queue<vector<int>, vector<vector<int>>, comp> heap;
```

---

## References

[cplusplus.com - priority_queue](http://www.cplusplus.com/reference/queue/priority_queue/)

[STL priority_queue 底层实现 (深度剖析)](http://c.biancheng.net/view/7010.html)
