# C++ STL algorithm

Created by : Mr Dk.

2021 / 01 / 20 16:58

Ningbo, Zhejiang, China

---

STL 的 `<algorithm>` 中定义了专门用于对一个范围内的元素进行操作的各种算法。实现上肯定十分高效，熟悉这些算法肯定能够极大提升刷题效率。

```cpp
#include <algorithm>
```

## Non-Modifying Sequence Operations

## Modifying Sequence Operations

### std::unique

在一个范围内去除重复元素，只保留相同元素中第一个出现的元素。`==` 运算符用于进行比较，但是可以自行实现比较函数。

在具体的实现中，算法是将与当前迭代器不同的元素复制到前面来，实现去重。所以数组必须先进行排序后，再调用 `unique()`，才能真正实现去重的效果。

返回去重区间的结尾位置。

```cpp
template <class ForwardIterator>
  ForwardIterator unique (ForwardIterator first, ForwardIterator last);
template <class ForwardIterator, class BinaryPredicate>
  ForwardIterator unique (ForwardIterator first, ForwardIterator last,
                          BinaryPredicate pred);
```

### std::unique_copy

与上述功能相同，只需另外提供一个保存输出结果的迭代器即可。去重操作将不会影响原有数组。

```cpp
template <class InputIterator, class OutputIterator>
  OutputIterator unique_copy (InputIterator first, InputIterator last,
                              OutputIterator result);
template <class InputIterator, class OutputIterator, class BinaryPredicate>
  OutputIterator unique_copy (InputIterator first, InputIterator last,
```

### std::reverse

逆置。具体实现方式是从头部和尾部开始交换元素。

```cpp
template <class BidirectionalIterator>
  void reverse (BidirectionalIterator first, BidirectionalIterator last);
```

### std::reverse_copy

逆置，将结果复制到一个迭代器指向的空间中。从结尾开始复制元素到结果空间的开头。

```cpp
template <class BidirectionalIterator, class OutputIterator>
  OutputIterator reverse_copy (BidirectionalIterator first,
                               BidirectionalIterator last, OutputIterator result);
```

### std::copy / std::copy_backward

复制一段范围的元素到另一个空间中 (从头开始拷贝或从尾开始拷贝)。

- 一对输入迭代器指示范围
- 一个输出迭代器指向目标空间开始的位置

```cpp
template <class InputIterator, class OutputIterator>
  OutputIterator copy (InputIterator first, InputIterator last, OutputIterator result);
```

```cpp
template <class BidirectionalIterator1, class BidirectionalIterator2>
  BidirectionalIterator2 copy_backward (BidirectionalIterator1 first,
                                        BidirectionalIterator1 last,
                                        BidirectionalIterator2 result);
```

### std::copy_n

复制某个位置开始的 n 个元素到目标空间中。

- 一个输入迭代器指示起始位置
- 整数 `n` 指示元素个数
- 一个输出迭代器指示目标位置

```cpp
template <class InputIterator, class Size, class OutputIterator>
  OutputIterator copy_n (InputIterator first, Size n, OutputIterator result);
```

### std::copy_if

复制一段范围中满足条件的元素到另一个空间中。

- 一对输入迭代器指示范围
- 一个输出迭代器指示目标空间起始位置
- 一元表达式判断每个元素是否符合条件

```cpp
template <class InputIterator, class OutputIterator, class UnaryPredicate>
  OutputIterator copy_if (InputIterator first, InputIterator last,
                          OutputIterator result, UnaryPredicate pred);
```

### std::move / std::move_backward

将指定范围内的元素移动到目标空间中 (从头移动或从尾移动)。移动后，原范围内的元素将处于 **未确定但合法** 的状态。

```cpp
template <class InputIterator, class OutputIterator>
  OutputIterator move (InputIterator first, InputIterator last, OutputIterator result);
```

```cpp
template <class BidirectionalIterator1, class BidirectionalIterator2>
  BidirectionalIterator2 move_backward (BidirectionalIterator1 first,
                                        BidirectionalIterator1 last,
                                        BidirectionalIterator2 result);
```

### std::swap / std::swap_ranges / std::iter_swap

交换两个对象的值。

```cpp
template <class T> void swap (T& a, T& b);
```

交换两个对象中指定长度范围内的元素。

```cpp
template <class ForwardIterator1, class ForwardIterator2>
  ForwardIterator2 swap_ranges (ForwardIterator1 first1, ForwardIterator1 last1,
                                ForwardIterator2 first2);
```

交换两个迭代器指向的值。

```cpp
template <class ForwardIterator1, class ForwardIterator2>
  void iter_swap (ForwardIterator1 a, ForwardIterator2 b);
```

### std::transform

对一段范围内的元素应用指定的一元或二元操作后，将结果保存到一个指定的空间中。

一元操作：

```cpp
template <class InputIterator, class OutputIterator, class UnaryOperation>
  OutputIterator transform (InputIterator first1, InputIterator last1,
                            OutputIterator result, UnaryOperation op);
```

二元操作：

```cpp
template <class InputIterator1, class InputIterator2,
          class OutputIterator, class BinaryOperation>
  OutputIterator transform (InputIterator1 first1, InputIterator1 last1,
                            InputIterator2 first2, OutputIterator result,
                            BinaryOperation binary_op);
```

### std::replace / std::replace_copy / std::replace_if / std::replace_copy_if

对一段范围内的元素将与指定值相等的值替换为新值，使用 `==` 操作符进行比较。

```cpp
template <class ForwardIterator, class T>
  void replace (ForwardIterator first, ForwardIterator last,
                const T& old_value, const T& new_value);
```

将一段范围内的元素替换后的结果复制到一个独立的空间中：

```cpp
template <class InputIterator, class OutputIterator, class T>
  OutputIterator replace_copy (InputIterator first, InputIterator last,
                               OutputIterator result,
                               const T& old_value, const T& new_value);
```

对一段范围内满足指定条件的元素替换为新值，使用自定义的一元函数进行判断。

```cpp
template <class ForwardIterator, class UnaryPredicate, class T>
  void replace_if (ForwardIterator first, ForwardIterator last,
                   UnaryPredicate pred, const T& new_value );
```

将一段范围内的元素替换后的结果复制到一个独立的空间中：

```cpp
template <class InputIterator, class OutputIterator, class UnaryPredicate, class T>
  OutputIterator replace_copy_if (InputIterator first, InputIterator last,
                                  OutputIterator result, UnaryPredicate pred,
                                  const T& new_value);
```

## Sorting

### std::sort

不稳定排序。必须指定的是排序的起始范围 (迭代器)，作用范围为 `[first, last)`。可选的参数是排序要使用到的比较函数，如不指定比较函数，那么使用 `<` 运算符进行比较。

```cpp
template <class RandomAccessIterator>
  void sort (RandomAccessIterator first, RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void sort (RandomAccessIterator first, RandomAccessIterator last, Compare comp);
```

时间复杂度为 O(nlog(n))。实现逻辑如下：

- 默认使用快速排序 (相比于堆排序，数据是连续访问的，对 cache 友好)，将数据分段归并
- 如果分段内数据小于阈值 (16)，则改用插入排序，避免快速排序的递归开销
- 如果递归层次过深，则使用堆排序 (复杂度相同，但无需更多递归)

### std::stable_sort

稳定排序。必须指定的是排序的起始范围 (迭代器)，作用范围为 `[first, last)`。可选的参数是排序要使用到的比较函数，如不指定比较函数，那么使用 `<` 运算符进行比较。

稳定排序会维持序列中相等元素的相对顺序。

```cpp
template <class RandomAccessIterator>
  void stable_sort ( RandomAccessIterator first, RandomAccessIterator last );

template <class RandomAccessIterator, class Compare>
  void stable_sort ( RandomAccessIterator first, RandomAccessIterator last,
                     Compare comp );
```

### std::partial_sort

输入三个参数，作用范围在 `[first, last)` 之间。执行算法后，`[first, middle)` 区间将包含整个区间中升序排列的前 `middle - first` 个元素，`[middle, last)` 区间将不包含顺序。

默认使用 `<` 运算符进行比较，可选自实现的比较函数覆盖默认行为。

```cpp
template <class RandomAccessIterator>
  void partial_sort (RandomAccessIterator first, RandomAccessIterator middle,
                     RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void partial_sort (RandomAccessIterator first, RandomAccessIterator middle,
                     RandomAccessIterator last, Compare comp);
```

### std::partial_sort_copy

原理同上，只是将结果复制到另一块空间 `[result_first, result_last)` 中，原空间保持不变。`middle` 参数变为返回结果集中的首尾范围，显然内部是通过结果集的首尾范围隐式指定了 `middle` 的位置。

```cpp
template <class InputIterator, class RandomAccessIterator>
  RandomAccessIterator
    partial_sort_copy (InputIterator first,InputIterator last,
                       RandomAccessIterator result_first,
                       RandomAccessIterator result_last);
template <class InputIterator, class RandomAccessIterator, class Compare>
  RandomAccessIterator
    partial_sort_copy (InputIterator first,InputIterator last,
                       RandomAccessIterator result_first,
                       RandomAccessIterator result_last, Compare comp);
```

### std::is_sorted

返回指定范围内的元素是否是排序的：

```cpp
template <class ForwardIterator>
  bool is_sorted (ForwardIterator first, ForwardIterator last);
template <class ForwardIterator, class Compare>
  bool is_sorted (ForwardIterator first, ForwardIterator last, Compare comp);
```

### std::is_sorted_until

返回序列中第一个不符合排序要求的元素的迭代器：

```cpp
template <class ForwardIterator>
  ForwardIterator is_sorted_until (ForwardIterator first, ForwardIterator last);
template <class ForwardIterator, class Compare>
  ForwardIterator is_sorted_until (ForwardIterator first, ForwardIterator last,
                                   Compare comp);
```

### std::nth_element

对指定范围内的数据进行重排序，并指定一个位置，这个位置之前的元素全都小于这个位置之后的元素 (等价于序列中最小的 n 个元素)。默认使用 `<` 运算符，可选使用自定义的比较函数。

```cpp
template <class RandomAccessIterator>
  void nth_element (RandomAccessIterator first, RandomAccessIterator nth,
                    RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void nth_element (RandomAccessIterator first, RandomAccessIterator nth,
                    RandomAccessIterator last, Compare comp);
```

## Partitions

### std::partition

对指定范围内的元素进行重排序，满足特定条件为 `true` 的所有元素全部排列在特定条件为 `false` 的元素之前，返回指向后一组 (指定条件为 `false`) 元素第一个元素的迭代器。

不稳定分治：序列中元素的相对顺序不一定维持不变。

```cpp
template <class BidirectionalIterator, class UnaryPredicate>
  BidirectionalIterator partition (BidirectionalIterator first,
                                   BidirectionalIterator last,
                                   UnaryPredicate pred);
```

其中 `UnaryPredicate` 是一个一元参数返回值为 `bool` 类型的函数。内部等价实现：

```cpp
template <class BidirectionalIterator, class UnaryPredicate>
  BidirectionalIterator partition (BidirectionalIterator first,
                                   BidirectionalIterator last, UnaryPredicate pred)
{
    while (first!=last) {
        while (pred(*first)) {
            ++first;
            if (first==last) return first;
        }
        do {
            --last;
            if (first==last) return first;
        } while (!pred(*last));
        swap (*first,*last);
        ++first;
    }
    return first;
}
```

> 这里也可以看出为什么是不稳定的：原本排在前面的元素被 swap 到后面去了。

### std::stable_partition

同上，但是分治是稳定的：`pred` 返回结果相同的元素之间的相对顺序不变。内部实现上使用了一个 **临时缓冲区** (来从头存放 `false` group 中的元素)。

```cpp
template <class BidirectionalIterator, class UnaryPredicate>
  BidirectionalIterator stable_partition (BidirectionalIterator first,
                                          BidirectionalIterator last,
                                          UnaryPredicate pred);
```

### std::partition_copy

不修改原有序列，将满足条件为 `true` 的元素放入 `result_true` 迭代器开始的空间中，将满足条件 `false` 的元素放入 `result_false` 迭代器开始的空间中。

```cpp
template <class InputIterator, class OutputIterator1,
          class OutputIterator2, class UnaryPredicate pred>
  pair<OutputIterator1,OutputIterator2>
    partition_copy (InputIterator first, InputIterator last,
                    OutputIterator1 result_true, OutputIterator2 result_false,
                    UnaryPredicate pred);
```

### std::partition_point

在一个 **已经被划分好的序列中**，寻找划分点，也就是第一个使 `pred()` 返回 `false` 的迭代器位置。基于已经被划分好的假设，可以通过二分查找的方式进行优化。

```cpp
template <class ForwardIterator, class UnaryPredicate>
  ForwardIterator partition_point (ForwardIterator first, ForwardIterator last,
                                   UnaryPredicate pred);
```

## Binary Search

### std::lower_bound

返回序列中第一个 **大于等于** 指定值的元素，前提是序列已经有序。默认使用 `<` 运算符，可选使用自定义的比较函数。

```cpp
template <class ForwardIterator, class T>
  ForwardIterator lower_bound (ForwardIterator first, ForwardIterator last,
                               const T& val);
template <class ForwardIterator, class T, class Compare>
  ForwardIterator lower_bound (ForwardIterator first, ForwardIterator last,
                               const T& val, Compare comp);
```

### std::upper_bound

返回序列中第一个 **大于** 指定值的元素，前提是序列已经有序。

```cpp
template <class ForwardIterator, class T>
  ForwardIterator upper_bound (ForwardIterator first, ForwardIterator last,
                               const T& val);
template <class ForwardIterator, class T, class Compare>
  ForwardIterator upper_bound (ForwardIterator first, ForwardIterator last,
                               const T& val, Compare comp);
```

### std::equal_range

寻找序列中等于某个值的数据范围，前提是序列已经有序。如果序列中不存在该值，则返回两个范围为 0 的迭代器，迭代器指向距离指定值最接近的值。

```cpp
template <class ForwardIterator, class T>
  pair<ForwardIterator,ForwardIterator>
    equal_range (ForwardIterator first, ForwardIterator last, const T& val);
template <class ForwardIterator, class T, class Compare>
  pair<ForwardIterator,ForwardIterator>
    equal_range (ForwardIterator first, ForwardIterator last, const T& val,
                  Compare comp);
```

### std::binary_search

寻找序列中是否存在指定的值，前提是序列已经有序。二分查找。

```cpp
template <class ForwardIterator, class T>
  bool binary_search (ForwardIterator first, ForwardIterator last,
                      const T& val);
template <class ForwardIterator, class T, class Compare>
  bool binary_search (ForwardIterator first, ForwardIterator last,
                      const T& val, Compare comp);
```

## Heap

### std::make_heap

参数给定一个范围，对该范围内的数据建立堆序。默认使用 `<` 运算符构造大顶堆，可选自定义的比较函数。

```cpp
template <class RandomAccessIterator>
  void make_heap (RandomAccessIterator first, RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void make_heap (RandomAccessIterator first, RandomAccessIterator last,
                  Compare comp );
```

### std::push_heap

给定一个已经满足堆序的范围 `[first, last - 1)`，将最后一个元素 `last - 1` 加入到这个堆中，使 `[first, last)` 满足堆序。可选自定义的比较函数维护堆序。

> 通常在容器的 `push_back()` 函数之后使用。

```cpp
template <class RandomAccessIterator>
  void push_heap (RandomAccessIterator first, RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void push_heap (RandomAccessIterator first, RandomAccessIterator last,
                   Compare comp);
```

### std::pop_heap

给定一个满足堆序的范围 `[first, last)`，将堆顶元素弹出到 `last - 1` 位置上，并重新维护剩余元素的堆序。导致的效果是 `[first, last - 1)` 是一个堆，最后一个元素是原堆顶元素。

> 通常在容器的 `pop_back()` 函数之前使用。

```cpp
template <class RandomAccessIterator>
  void pop_heap (RandomAccessIterator first, RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void pop_heap (RandomAccessIterator first, RandomAccessIterator last,
                 Compare comp);
```

### std::sort_heap

对一个堆序范围进行堆排序。

```cpp
template <class RandomAccessIterator>
  void sort_heap (RandomAccessIterator first, RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  void sort_heap (RandomAccessIterator first, RandomAccessIterator last,
                  Compare comp);
```

### std::is_heap

返回给定的序列范围是否满足堆序。

```cpp
template <class RandomAccessIterator>
  bool is_heap (RandomAccessIterator first, RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  bool is_heap (RandomAccessIterator first, RandomAccessIterator last,
                Compare comp);
```

### std::is_heap_until

返回给定序列中第一个不满足堆序的位置。

```cpp
template <class RandomAccessIterator>
  RandomAccessIterator is_heap_until (RandomAccessIterator first,
                                      RandomAccessIterator last);
template <class RandomAccessIterator, class Compare>
  RandomAccessIterator is_heap_until (RandomAccessIterator first,
                                      RandomAccessIterator last
                                      Compare comp);
```

## Merge

## Min / Max

### std::min

返回两个元素中较小的那个。如果两者相同，则返回前一个。默认使用 `<` 运算符。

```cpp
template <class T> const T& min (const T& a, const T& b);
template <class T, class Compare>
  const T& min (const T& a, const T& b, Compare comp);
```

### std::max

返回两个元素中较大的那个，如果两者相同，则返回前一个。默认使用 `<` 运算符。

```cpp
template <class T> const T& max (const T& a, const T& b);
template <class T, class Compare>
  const T& max (const T& a, const T& b, Compare comp);
```

### std::minmax

以 `<min, max>` 的形式返回最大值和最小值。

```cpp
template <class T>
  pair <const T&,const T&> minmax (const T& a, const T& b);
template <class T, class Compare>
  pair <const T&,const T&> minmax (const T& a, const T& b, Compare comp);
initializer list (3)
template <class T>
  pair<T,T> minmax (initializer_list<T> il);
template <class T, class Compare>
  pair<T,T> minmax (initializer_list<T> il, Compare comp);
```

### std::min_element

返回指定范围内的最小值。

```cpp
template <class ForwardIterator>
  ForwardIterator min_element (ForwardIterator first, ForwardIterator last);
template <class ForwardIterator, class Compare>
  ForwardIterator min_element (ForwardIterator first, ForwardIterator last,
                               Compare comp);
```

### std::max_element

返回指定范围内的最大值。

```cpp
template <class ForwardIterator>
  ForwardIterator max_element (ForwardIterator first, ForwardIterator last);
template <class ForwardIterator, class Compare>
  ForwardIterator max_element (ForwardIterator first, ForwardIterator last,
                               Compare comp);
```

### std::minmax_element

返回指定范围内的最小值和最大值。如果包含多个相同值：

- 返回第一个最小值
- 返回最后一个最大值

```cpp
template <class ForwardIterator>
  pair<ForwardIterator,ForwardIterator>
    minmax_element (ForwardIterator first, ForwardIterator last);
template <class ForwardIterator, class Compare>
  pair<ForwardIterator,ForwardIterator>
    minmax_element (ForwardIterator first, ForwardIterator last, Compare comp);
```

## Other

---

## References

[CPlusPlus.com](http://www.cplusplus.com/reference/algorithm/)
