## C++ STL vector

---

Created by : Mr Dk.

2018 / 03 / 21 23:03

Nanjing, Jiangsu, China

---

##### 1. 原型 特性

```C++
template < class T, class Alloc = allocator<T> > class vector;
```

 * 顺序存储容器
 * 动态大小数组​

---

##### 2. 引用头文件

```c++
#include <vector>
using namespace std;	// OR : std::vector
```

---

##### 3. 声明 / 定义

```C++
// 声明一个空的 vector
vector <int> Vector;

// 声明一个含有 N 个元素的 vector
// 若 <> 内为对象，则调用构造函数初始化
vector <int> Vector (N);

// 声明一个含有 N 个元素的 vector，并赋值为 number
vector <int> Vector (N, number);
```

---

##### 4. 内存分配

​	4.1 预留 N 个元素的内存 但不构造对象

```C++
// 访问预留的空间是非法的
Vector.reserve (N);

// 可以与 push_back () 方法配合使用
Vector.push_back (1);
```

​	4.2 分配 N 个元素的内存 并构造对象

```C++
// 分配 N 个元素的内存
Vector.resize (N);

// 分配 N 个元素的内存，并赋值
Vector.resize (N, 0);
```

---

##### 5. 基本属性

```C++
// 返回 vector 的长度 （元素个数）
int size = Vector.size();

// 返回 vector 是否为空
bool empty = Vector.empty();

// 声明一个正向迭代器
vector <int>::iterator vectorIter;
// 返回指向头一个元素的迭代器
vectorIter = Vector.begin();
// 返回指向最后一个元素的下一个位置的迭代器
vectorIter = Vector.end();

// 声明一个反向迭代器
vector <int>::reverse_iterator reverseIter;
// 返回指向最后一个元素的反向迭代器
reverseIter = Vector.rbegin();
// 返回指向第一个元素前一个位置的反向迭代器
reverseIter = Vector.rend();
```

---

##### 6. 迭代器的声明与使用

```C++
// 正向迭代器
vector <int>::iterator vectorIter;

// 遍历
for (vectorIter = Vector.begin(); 
	 vectorIter != Vector.end(); 
	 vectorIter++) {
    cout << *vectorIter << endl;
}

// 反向迭代器
vector <int>::reverse_iterator reverseIter;

// 遍历
for (reverseIter = Vector.rbegin();
	 reverseIter = Vector.rend();
	 reverseIter++) {
    cout << *reverseIter << endl;
}
```

---

##### 7. 添加 / 删除元素

​	7.1 在尾部插入

```C++
// 若超出内存范围
// 自动重新分配内存
Vector.push_back (1);

// 在知道插入数量的情况下
// 提前使用 reserve 函数预留内存
// 避免内存重新分配 效率更高
```

​	7.2 在尾部删除

```C++
Vector.pop_back();
```

​	7.2 在指定位置插入

```C++
// 在 vectorIter 的位置前插入元素
Vector.insert (vectorIter, 1);

// 在 vectorIter 的位置前插入 N 个元素
Vector.insert (vectorIter, N, 1);

// 在 vectorIter 的位置前插入 [begin, end) 的元素
Vector.insert (vectorIter, Iter_begin, Iter_end);
```

​	7.3 在指定位置删除

```C++
// 删除 vectorIter 指向的元素
Vector.erase (vectorIter);

// 删除 [begin, end) 中的元素
Vector.erase (Iter_begin, Iter_end);
```

​	7.4 删除全部

```C++
Vector.clear();
```

---

##### 8. vector 赋值

​	8.1 已重载 = 运算符

```C++
vector <int> Vector1 = Vector2;
```

​	8.2 assign 函数

```C++
Vector1.assign (Vector2.begin(), Vector2.end());
```

---

##### 9. 数据访问

```C++
// 第一个元素
cout << Vector.front() << endl;

// 最后一个元素
cout << Vector.back() << endl;

// 随机访问
cout << Vector.at (pos) << endl;
cout << Vector [pos] << endl;
```

---

##### 10. 算法相关

```C++
// 需要引用头文件
#include <algorithm>

// 排序
sort (Vector.begin(), Vector.end());
sort (Vector.begin(), Vector.end(), greater <int> ());
sort (Vector.begin(), Vector.end(), Comp);
// 比较函数 bool Comp() 需要自己实现

// 逆置
reverse (Vector.begin(), Vector.end());
```

---

##### 11. 堆操作

```C++
// 建堆 （默认为大顶堆）
make_heap (Vector.begin(), Vector.end());
// 小顶堆
make_heap (Vector.begin(), Vector.end(), greater <int> ());

// 堆中添加元素
Vector.push_back (1);
push_heap (Vector.begin(), Vector.end());

// 堆中删除元素
pop_heap (Vector.begin(), Vector.end());
Vector.pop_back ();

// 堆排序
sort_heap (Vector.begin(), Vector.end());
```

---

##### 12. 二维数组

​	（一般用于表示图的邻接矩阵）

```C++
vector <vector <int> > Graph;
```

---

### *总结*

这个数据结构相当好用。

是我在 PAT 考试中用到的最多的数据结构之一。

适合需要大量随机访问的场合。

也可作为已知规模数据的静态存储方式。