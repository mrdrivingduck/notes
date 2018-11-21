# Java - Collection - HashMap

Created by : Mr Dk.

2018 / 11 / 21 17:31

Nanjing, Jiangsu, China

---

### Collection Interface

_Java_ 中的集合类分为两组：

* `java.util.Collection`，包括子类：
  * `java.util.Set`
  * `java.util.SortedSet`
  * `java.util.NavigableSet`
  * `java.util.Queue`
  * `java.util.concurrent.BlockingQueue`
  * `java.util.concurrent.TranferQueue`
  * `java.util.Deque`
  * `java.util.concurrent.BlockingDeque`
* `java.util.Map`，不是真正的集合，包括子类：
  * `java.util.SortedMap`
  * `java.util.NavigableMap`
  * `java.util.concurrent.ConcurrentMap`
  * `java.util.concurrent.ConcurrentNavigableMap`

### Collection Implementaions

| Interface | Hash Table | Resizable Array | Balanced Tree | Linked List  | Hash Table + Linked List |
| --------- | ---------- | --------------- | ------------- | ------------ | ------------------------ |
| `Set`     | `HashSet`  |                 | `TreeSet`     |              | `LinkedHashSet`          |
| `List`    |            | `ArrayList`     |               | `LinkedList` |                          |
| `Deque`   |            | `ArrayDeque`    |               | `LinkedList` |                          |
| `Map`     | `HashMap`  |                 | `TreeMap`     |              | `LinkedHashMap`          |

### Map

```
Interface Map<K, V>
K - the type of keys maintained by this map
V - the type of mapped values
```

将 _key_ 和 _value_ 做映射的对象

* _Map_ 中的 _key_ 不能重复
* 每个 _key_ 最多只能映射一个 _value_

_Map_ 接口提供集合视角，可将其内容分别视为 _key_ 的集合，_value_ 的集合和 _key - value_ 集合

_Map_ 的顺序取决于 `iterator` 返回元素的顺序

* _TreeMap_ 对顺序有特殊规定
* _HashMap_ 对顺序没有特殊规定

### HashMap

基于 _HashTable_ 的 _Map_ 接口实现

* 非同步 - 线程不安全
* 允许 `null` 的 _key_
* 允许 `null` 的 _value_
* 不保证 _Map_ 的顺序一直相同

基本操作 `get` 和 `put` 的性能是固定

* 前提是 _hash_ 函数将所有元素都分散到了桶中 - _哈希表原理_

迭代性能与 `capacity` 和 `size` 成正比

* 如果追求迭代性能，`capacity` 不宜设得过大，`load factor` 不宜设得过小
  * `capacity` 是指 __桶__ 的个数
  * `load factor` 用于衡量 _Map_ 的装满程度
* 如果 _Entry_ 超过了 `load factor` 且超过了 `capacity`，_HashMap_ 会被 __rehash__
  * 内部数据结构重组
  * `capacity` 大约扩大一倍

### Thread Safety

如果多个线程并发使用 _HashMap_，且至少一个线程修改了 _HashMap_ 的结构 - 必须在外部同步

* __修改结构__ 指 __增加__ 或 __删除__ 一个或多个结点
* 修改 _key_ 关联的某个值 __不算修改结构__
* 如果不使用同步锁，则需要声明 `Map m = Collections.synchronizedMap(new HashMap(...));`

### Iteration

从 _HashMap_ 的集合视角中获取集合及其迭代器

如果集合的结构发生了变化（除非用 `Iterator` 自身的 `remove()` 函数）

迭代器将会抛出 `ConcurrentModificationException`

---

### Constructor

```java
HashMap();
HashMap(int initialCapacity);
HashMap(int initialCapacity, float loadFactor);
HashMap(Map<? extends K, ? extends V> m);
```

### Basic Operations

```java
boolean isEmpty();
boolean containsKey(Object key);
boolean containsValue(Object value);
int size();
```

```java
V put(K key, V value);
void putAll(Map<? extends K, ? extends V> m);
```

* `put()` - 如果旧值已经存在，将被替换为新值，旧值被返回
* `putAll()` - 新的集合中的元素将替换原集合中已存在的 _key_ 对应的 _value_

```java
V remove(Object key);
boolean remove(Object key, Object value);
void clear();
```

* `remove(Object key)` - 删除 _key_ 对应的 _value_ 并返回
* `remove(Object key, Object value)` - 删除 _key-value_ 对，并返回操作是否成功
* `clear()` - 清空

### Collection View

* 获取所有的 _key_

  ```java
  Set<K> keySet();
  ```

* 获取所有的 _value_

  ```java
  Collection<V> values();
  ```

* 获取所有的 _key-value_ 对

  ```java
  Set<Map.Entry<K, V>> entrySet();
  ```

* __如果需要边遍历边修改集合，则必须使用 Iterator 自身的 remove()__

  ```java
  Iterator<Map.Entry<String, Object>> iter = map.entrySet().iterator();
  while (iter.hasNext()) {
      Map.Entry<String, Object> entry = (Map.Entry<String, Object>) iter.next();
      String key = entry.getKey();
      Object value = entry.getValue();
      
      // iter.remove();
  }
  ```

  否则将会抛出 `ConcurrentModificationException` 异常

---

### Summary

自以为很了解这些数据结构了

因为对 _C++_ 的 _STL_ 用得很熟

结果今天在程序中遍历 _HashMap_ 的时候出现了异常

经过学习

_Java_ 与 _C++_ 还是很不一样的

对 _HashMap_ 的了解更加深入了

---

