## C++ STL multimap

Created by : Mr Dk.

2018 / 09 / 15 20:16

Nanjing, Jiangsu, China

---

##### 1. Feature

```C++
template < class Key,                                   // multimap::key_type
           class T,                                     // multimap::mapped_type
           class Compare = less<Key>,                   // multimap::key_compare
           class Alloc = allocator<pair<const Key,T> >  // multimap::allocator_type
           > class multimap;
```

* 提供 `key` - `value` 的映射
  * `key` 必须能够被比较
    * 使用 `<` 运算符进行比较
    * 若 `key` 为自定义类型，则需要重载 `<` 运算符
  * `key` 不会重复出现 - `value` 可以重复出现
  * 根据 `key` 的大小排序 - 默认从小到大
  * 通过 `key` 快速查找 `value`
  * `key` 可被修改，`value` 不可被修改
* 底层由 __红黑树__ 实现
* 插入、删除操作后，其余迭代器 __不会失效__

---

##### 2. Dependency

```C++
#include <map>
using namespace std;	// using std::map;
```

---

##### 3. Usage

* Constructor

  * ```C++
    // Empty Container (Default)
    multimap <key_Type, value_Type> MultiMap;
    // Copy Constructor
    multimap <key_Type, value_Type> MultiMap(AnotherMap);
    // Range Constructor
    multimap <key_Type, value_Type> MultiMap(AnotherMap.begin(), AnotherMap.end());
    ```

* Destructor

* Operator `=`

  * __Copy__ a container

  * ```C++
    multimap <key_Type, value_Type> A;
    multimap <key_Type, value_Type> B;
    A = B;
    ```

* Iterators

  * ```C++
    // 返回指向第一个元素的迭代器
    multimap <key_Type, value_Type>::iterator iter_begin
    	= MultiMap.begin();
    // 返回指向最后一个元素的下一个位置的迭代器
    multimap <key_Type, value_Type>::iterator iter_end
    	= MultiMap.end();
    // 返回指向最后一个元素的迭代器
    multimap <key_Type, value_Type>::reverse_iterator iter_rbegin
    	= MultiMap.rbegin();
    // 返回指向第一个元素的前一个位置的迭代器
    multimap <key_Type, value_Type>::reverse_iterator iter_rend
    	= MultiMap.rend();
    ```

* Capacity

  * ```C++
    // 返回容器是否为空
    if (MultiMap.empty() == FALSE)
    {
        // 返回容器中的元素个数
        cout << MultiMap.size() << endl;
        // 返回容器可容纳的最大容量
        cout << MultiMap.max_size() << endl;
    }
    ```

* Modifiers

  * ```C++
    /*
     * 插入
     */
    MultiMap.insert(pair <key_Type, value_Type> (key, value));
    
    /*
     * 删除
     */
    multimap <key_Type, value_Type>::iterator mapIter = MultiMap.find(key);
    MultiMap.erase(mapIter);                            // 删除单个元素
    MultiMap.erase(key);                                // 删除 key 的所有元素
    MultiMap.erase(MultiMap.begin(), MultiMap.end());   // 删除范围内的元素
    MultiMap.clear();                                   // 删除全部元素
    
    /*
     * 交换
     */
    MultiMap.swap(AnotherMap);	// 交换两个容器中的内容
    ```

* __Query__

  * ```C++
    /*
     * find() - 返回第一次出现 key 的迭代器
     */
    multimap <key_Type, value_Type>::iterator mapIter = MultiMap.find(key);
    if (mapIter == MultiMap.end())
    {
        // NOT FOUND
    }
    
    /*
     * count() - 返回 key 出现的次数
     */
    cout << MultiMap.count(key) << endl;
    
    /*
     * lower_bound() - 返回指向第一个不小于 key 的元素的迭代器 （>=）
     * upper_bound() - 返回指向第一个大于 key 的元素的迭代器 （>）
     */
    typedef multimap <key_Type, value_Type>::iterator Iter;
    Iter low = MultiMap.lower_bound(key);
    Iter high = MultiMap.upper_bound(key);
    
    /*
     * equal_range() - 返回指向 key 的首尾范围的迭代器
     * 返回形式为 pair - 
     *     第一个成员为 lower_bound() 的结果
     *     第二个成员为 upper_bound() 的结果
     *     ['>=', '>') 等价于 '='
     */
    pair <Iter, Iter> range = MultiMap.equal_range(key);
    for (Iter iter = range.first; iter != range.second; iter++)
    {
        cout << iter -> first << " " << iter -> second << endl;
    }
    ```

---

##### 4. Doubt

`multimap <key, value>` & `map <key, set <value> >`

* Differences in:
  * Feature
  * Situation
  * Performance

---

##### 5. Reference

* [http://www.cplusplus.com/reference/map/multimap/](http://www.cplusplus.com/reference/map/multimap/)

---

