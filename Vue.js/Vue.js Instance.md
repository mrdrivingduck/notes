# Vue.js - Instance

Created by : Mr Dk.

2019 / 02 / 22 17:46

Nanjing, Jiangsu, China

---

## About

每一个 Vue 应用都是通过 `Vue` 函数创建一个新的 Vue 实例开始的：

```javascript
var vm = new Vue({
    // Options
})
```

`vm` 是 ViewModel 的缩写。创建 Vue 实例时，可以传入选项对象

一个 Vue 应用包括：

* 通过 `new Vue` 创建的 **根实例**
* 可选的嵌套、可复用组件树

所有的 Vue 组件都是 Vue 实例，并接受相同的选项对象。

---

## Data and Methods

当一个 Vue 实例被创建后

它向 Vue 的 **响应式系统** 加入了其 `data` 对象中能找到的所有属性

* 当这些属性的值发生改变时，视图会响应并进行重渲染
* 只有 `data` 中存在的属性才是响应式的

`Object.freeze()` 会阻止修改现有的属性，响应系统无法再追踪变化。

---

## Lifecycle Hooks

每个 Vue 实例在被创建后，会运行一些称为 *Lifecycle Hooks* 的函数，给了用户在不同阶段添加自己的代码的机会。比如 `created` hook：

```vue
<script>
new Vue({
  data: {
    a: 1
  },
  created: function () {
    console.log('a is: ' + this.a)
  }
})
</script>
```

* `this` 上下文指向调用它的 Vue 实例
* 不要使用箭头函数 - 箭头函数和父级上下文绑定在一起，`this` 不是预期的 Vue 实例

---

