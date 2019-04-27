# Vue.js - Reactivity

Created by : Mr Dk.

2019 / 04 / 27 17:26

Nanjing, Jiangsu, China

---

## What is Reactivity

Vue 最独特的特性：非侵入性的响应式系统

* 数据模型 - JavaScript 对象
* 修改数据模型，视图会进行更新

---

## Tracing Changes

将一个 JavaScript 对象传入 Vue 实例作为 `data`

Vue 将遍历该对象的所有属性

* 使用 `Object.defineProperty` 将属性转换为 `getter/setter`
* `Object.defineProperty` 不支持 IE8 以及更低版本浏览器
* `getter/setter` 能够使 Vue 追踪依赖（被访问和修改时通知变更）

每个组件实例对应一个 __watcher__ 实例

* 在 __组件渲染__ 的过程中把接触过的数据记录为 __依赖__
* 当依赖的 `setter` 触发时，通知 __watcher__，从而触发重新渲染

![vue-reactive](../img/vue-reactive.png)

---

## Attention

### Object

Vue __无法检测到对象属性的增加或删除__

* Vue 是在实例初始化时，进行属性的 _getter/setter_ 转化
* 所以属性必须在 `data` 上初始化，才能被 Vue 转换为响应式
* 对于已经创建的实例，Vue 不允许动态添加根级别的响应式属性
* 必须在初始化实例前声明所有根级响应式属性，哪怕只是一个空值
* 否则，Vue 将警告渲染函数正在试图访问不存在的属性

只能通过 Vue 提供的 API 动态添加响应式属性：

```javascript
Vue.set(vm.userProfile, 'age', 27)
// OR
// vm.$set() is an alias of Vue.set()
vm.$set(vm.userProfile, 'age', 27)
```

如果想为已有对象赋予多个新属性

需要用 __原对象__ 和 __新属性对象__ 混合创建一个新的对象：

```javascript
// Instead of `Object.assign(this.someObject, { a: 1, b: 2 })`
this.someObject = Object.assign({}, this.someObject, { a: 1, b: 2 })
```

### Array

Vue 包含一组观察数组的变异方法

调用这些方法将会触发视图更新：

* `push()`
* `pop()`
* `shift()`
* `unshift()`
* `splice()`
* `sort()`
* `reverse()`

数组更新方式：

* 变异方法：改变被方法调用的原始数组
* 非变异方法：不改变原始数组，但返回一个新数组，用新数组替换旧数组
  * Vue 实现了一些智能的、启发式的方法，因此替换数组是高效的操作

受到 JavaScript 的限制，Vue 不能检测以下变动的数组：

* 利用索引直接设置一个项：`vm.items[indexOfItem] = newValue`
* 直接修改数组长度：`vm.items.length = newLength`

为了实现相同的效果，同时触发状态更新 - 

* 设置或删除某项：

  ```javascript
  Vue.set(vm.items, indexOfItem, newValue)
  // OR
  vm.$set(vm.items, indexOfItem, newValue)
  
  vm.items.splice(indexOfItem, 1, newValue)
  ```

* 操作数组长度：

  ```javascript
  vm.items.splice(newLength)
  ```

---

## Async Update Queue

Vue 更新 DOM 时是 __异步执行__ 的

* 侦听到数据变化，Vue 将开启一个队列
* 缓冲在同一 __事件循环__ 中发生的所有数据变更
* 同一个 __watcher__ 被多次触发，只会被推入到队列一次（避免重复操作）
* 在下一事件循环的 `tick` 中，Vue 刷新队列并执行实际工作（修改 DOM）

因此，在设置响应对象后，组件不会立刻重新渲染

* 队列刷新后，组件会在下一个 `tick` 中更新
* 为了在更新 DOM 完成后做点什么，可以调用
  * `Vue.nextTick(callback)`
  * `vm.$nextTick()`

---

## Summary

这里面的问题在开发中有涉及到

幸亏有一次看了相关的 Vue 官方文档

才迅速找到了出问题的地方

第一次的问题出现在添加对象属性没有被 watch 到

第二次的问题出现在别人的代码通过 index 直接向数组中插值

导致也无法被 watch 到

今天算是稍微了解了一些 Vue 的底层原理

虽然依旧没有看源码。。。。。。

以后如果想深入了解一个东西

还是应该读一读源码

---

