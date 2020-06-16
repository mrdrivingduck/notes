# Vue.js - Lifecycle

Created by : Mr Dk.

2019 / 05 / 22 17:01

Nanjing, Jiangsu, China

---

## Lifecycle Mounts

![vue-lifecycle](../img/vue-lifecycle.png)

1. 实例化 Vue - `new Vue()`
2. 初始化 Event & Lifecycle
3. 调用 `beforeCreate()` 钩子
   * 此时数据未被挂载，无法访问 `data` 和 DOM
4. 挂载数据、绑定事件
5. 调用 `created()` 钩子
   * 可以访问数据，也可以修改数据，且修改数据不触发 `updated()`
6. 找到实例或组件对应的 `<template></template>`，编译模板为虚拟 DOM
7. 调用 `beforeMount` 钩子
   * 此时虚拟 DOM 创建完成，马上就要渲染
8. 渲染出真实 DOM
9. 调用 `mounted()` 钩子
   * 组件渲染完成，可以操作真实 DOM（响应式操作）
10. 组件或实例的数据修改后，立刻调用 `beforeUpdate()` 钩子
11. 重新构建虚拟 DOM，利用 diff 算法对比，重新渲染
12. 调用 `updated()` 钩子
13. 当调用 `vm.$destroy()` 函数后，立刻调用 `beforeDestory()` 钩子
14. 清除计时器、子组件、事件监听器等善后工作
15. 调用 `destroyed()` 钩子

---

## Lifecycle of Parent & Child Components

### Loading & Rendering

```
parent -> beforeCreate()
parent -> created()
parent -> beforeMount()
child  -> beforeCreate()
child  -> created()
child  -> beforeMount()

child  -> mounted()
parent -> mounted()
```

### Updating

```
parent -> beforeUpdate()
child  -> beforeUpdate()
child  -> updated()
parent -> updated()
```

### Destroying

```
parent -> beforeDestory()
child  -> beforeDestory()
child  -> destroyed()
parent -> destroyed()
```

---

## Summary

父子组件的生命周期关系，可以类比 C++ 的子类构造函数调用顺序。把这个理清楚以后，就不会出现父子组件之间诡异的渲染失败了。

---

