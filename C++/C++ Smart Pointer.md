# C++ - Smart Pointer

Created by : Mr Dk.

2021 / 09 / 19 20:00

Ningbo, Zhejiang, China

---

学习一下 C++ 中四种常见智能指针的用法、行为和具体实现。它们的定义位于：

```c++
#include <memory>
using namespace std;
```

## auto_ptr (deprecated in C++ 11)

Automatic Pointer，已经在 C++ 11 标准中过时。

智能指针本身也是一个对象，在内部维护了实际的指针。当 `auto_ptr` 对象的生命周期结束时，在对象的 **析构函数** 中实现对指针的销毁 (通常为 `operator delete`)。

该指针提供了对一个指针的全周期生命管理，语义上类似于 **独占** 一个指针，维护着对内部指针的 **控制权**。对指针拥有控制权的 `auto_ptr` 负责对内部指针进行销毁。因此，不可能有多于两个 `auto_ptr` 对象在内部维护着同一个指针。当两个 `auto_ptr` 对象之间发生赋值时，将会涉及到控制权的转移。控制权转移之后，原指针将失效。

另外，可以看到构造函数都带有 `throw`，保证是 *异常安全* 的。

```c++
explicit auto_ptr (X* p=0) throw();

auto_ptr (auto_ptr& a) throw();
template<class Y>
  auto_ptr (auto_ptr<Y>& a) throw();

auto_ptr (auto_ptr_ref<X> r) throw();
```

```c++
~auto_ptr() throw();
```

常规指针行为：

```c++
X* get() const throw();        // 获取内部指针
X& operator*() const throw();  // 通过 operator* 对内部指针解引用
X* operator->() const throw(); // 通过 operator-> 返回内部指针的成员变量
```

控制权管理：

```c++
// 指针赋值，左边的 auto_ptr 对象接管控制权，右边的 auto_ptr 对象置空
auto_ptr& operator= (auto_ptr& a) throw();
template <class Y>
  auto_ptr& operator= (auto_ptr<Y>& a) throw();
auto_ptr& operator= (auto_ptr_ref<X> r) throw();

// 放弃控制权，将 auto_ptr 内部指针置空，但不销毁指针指向的空间
X* release() throw();

// 放弃控制权，并销毁内部指针指向的空间
// 然后内部指针被重新初始化 (或置空)
void reset (X* p=0) throw();
```

> `auto_ptr` 使用了 copy 语义来实现转移指针，但其行为并不与 copy 语义一致。因为原对象释放了所有权。因此在 C++ 11 中被 `unique_ptr` 替代，因为它实现了 move 语义。

## unique_ptr

它的语义如其名称所述，表示独占一个资源。一旦它对一个指针资源拥有控制权，就需要在析构函数中负责对这个指针进行销毁。被赋值或主动放弃控制权时也是如此。unique_ptr 在语义上独占了指针，因此在销毁指针时并不考虑这个指针是否被其它对象持有。

其内部元素包含：

- Pointer：在构造时被赋值，在赋值 / reset 时可被替换，也可以被独立访问
- Deleter：一个 **可调用对象**，接收参数为相同指针类型，在构造时被设置，可以通过赋值替换，用于销毁其管理的指针

构造函数：

```c++
// 空构造函数，内部指针被设置为 nullptr
constexpr unique_ptr() noexcept;	
constexpr unique_ptr (nullptr_t) noexcept : unique_ptr() {}

// 从指针构造
explicit unique_ptr (pointer p) noexcept;
// 从指针构造，并复制一份输入 deleter
unique_ptr (pointer p,
    typename conditional<is_reference<D>::value,D,const D&> del) noexcept;	
// 从指针构造，并使用输入 deleter
unique_ptr (pointer p,
    typename remove_reference<D>::type&& del) noexcept;

// move 语义构造：接管指针，复制一份 deleter
unique_ptr (unique_ptr&& x) noexcept;
template <class U, class E>
  unique_ptr (unique_ptr<U,E>&& x) noexcept;
template <class U>
  unique_ptr (auto_ptr<U>&& x) noexcept;

// !!! 拷贝构造函数被禁用，因为指针是被独占的
unique_ptr (const unique_ptr&) = delete;
```

析构函数：

```c++
~unique_ptr();  // 以内部指针为参数，调用 deleter
```

指针行为：

```c++
// 判空，不再需要先通过 get 获取到内部指针，再对内部指针进行判空
explicit operator bool() const noexcept;

// 重载 operator* 和 operator->
typename add_lvalue_reference<element_type>::type operator*() const;
pointer operator->() const noexcept;
```

控制权管理：

```c++
// 放弃指针控制权，内部指针置空
pointer release() noexcept;

// 放弃指针控制权并销毁
// (可选) 接管输入参数中的指针控制权
void reset (pointer p = pointer()) noexcept;

// 与另一个 unique_ptr 对换控制权
void swap (unique_ptr& x) noexcept;
```

## shared_ptr

该对象允许与其它 shared_ptr 对象共享对一个指针的控制权。这一组共享者中最后一个释放控制权的对象负责销毁该指针。共享控制权的唯一方式是复制内部指针，并维护引用计数。

内部的指针：

- Stored pointer：指向需要被管理的对象
- Owned pointer：指向控制权对象组用于管理何时销毁 stored pointer 的数据

构造函数：

```c++
// 空构造函数，不管理任何指针，引用计数为 0
constexpr shared_ptr() noexcept;
constexpr shared_ptr(nullptr_t) : shared_ptr() {}

// 默认构造函数，可选指针、deleter、allocator
template <class U> explicit shared_ptr (U* p);
template <class U, class D> shared_ptr (U* p, D del);
template <class D> shared_ptr (nullptr_t p, D del);
template <class U, class D, class Alloc> shared_ptr (U* p, D del, Alloc alloc);
template <class D, class Alloc> shared_ptr (nullptr_t p, D del, Alloc alloc);

// 拷贝构造函数
// 如果输入参数不为空，则共享控制权，并增加 ref count
// 如果输入参数为空，那么创建一个空的对象
shared_ptr (const shared_ptr& x) noexcept;
template <class U> shared_ptr (const shared_ptr<U>& x) noexcept;
// 从 weak_ptr 构造：如果输入参数过期，那么抛出 bad_weak_ptr 异常
template <class U> explicit shared_ptr (const weak_ptr<U>& x);

// 移动构造函数
// 构造完毕后，输入参数被置空
shared_ptr (shared_ptr&& x) noexcept;
template <class U> shared_ptr (shared_ptr<U>&& x) noexcept;

// 从 auto_ptr 或 unique_ptr 转移控制权，入参丢失控制权而被置空
template <class U> shared_ptr (auto_ptr<U>&& x);
template <class U, class D> shared_ptr (unique_ptr<U,D>&& x);

// 别名构造函数
// 对象不管理 p 指向的存储，而是共享 x 的数据并累加引用计数
// 通常被用于指向已经被纳入管理的 object member
template <class U> shared_ptr (const shared_ptr<U>& x, element_type* p) noexcept;
```

析构函数：

- 如果引用计数大于 1，那么引用计数--
- 如果引用计数等于 1，那么使用 deleter 或 `operator delete` 销毁指针
- 如果引用计数为 0，那么没有任何效果

```c++
~shared_ptr();
```

重置：

```c++
// 当前对象被自销毁
void reset() noexcept;
// (可选) 然后对一个新指针建立控制权
template <class U> void reset (U* p);
template <class U, class D> void reset (U* p, D del);
template <class U, class D, class Alloc> void reset (U* p, D del, Alloc alloc);
```

引用计数相关：

```c++
long int use_count() const noexcept;  // 返回引用计数
bool unique() const noexcept;         // 返回控制权是否唯一
```

其余与 unique_ptr 类似。

## weak_ptr

shared_ptr 互相引用时，引用计数永远不会减至 0。weak_ptr 用于解决这个问题。它可以被 shared_ptr 赋值，但不增加引用计数。

构造函数：

```c++
// 成为共享组的一部分，但不持有控制权 (不增加引用计数)
constexpr weak_ptr() noexcept;

weak_ptr (const weak_ptr& x) noexcept;
template <class U> weak_ptr (const weak_ptr<U>& x) noexcept;

template <class U> weak_ptr (const shared_ptr<U>& x) noexcept;
```

析构函数无任何作用。

引用计数相关：

```c++
// 返回共享内部指针控制权的指针数量
long int use_count() const noexcept;
// 返回当前 weak_ptr 是否过期 (use_count()==0)
bool expired() const noexcept;
// 返回当前 weak_ptr 对应的 shared_ptr (如果没有过期)
shared_ptr<element_type> lock() const noexcept;
```

weak_ptr 没有重载 `operator*` 和 `operator->`，因此只能通过 shared_ptr 访问堆空间。

> 没太搞懂它的具体使用场景。

---

## References

[cplusplus.com - auto_ptr](http://www.cplusplus.com/reference/memory/auto_ptr/)

[cplusplus.com - unique_ptr](http://www.cplusplus.com/reference/memory/unique_ptr/)

[cplusplus.com - shared_ptr](http://www.cplusplus.com/reference/memory/shared_ptr/)

[cplusplus.com - weak_ptr](https://www.cplusplus.com/reference/memory/weak_ptr/)

