# Vue.js - Vuex

Created by : Mr Dk.

2019 / 03 / 31 21:39

Nanjing, Jiangsu, China

---

## About

>  **Vuex** 是一个专门为 Vue.js 应用程序开发的 **状态管理模式**。它采用集中式存储管理应用的所有组件的状态，并以相应的规则保证状态以一种可预测的方式发生变化。

在实际开发过程中，对于 Vue.js 组件之间的通信，父组件通过 `props` 向子组件传递参数，子组件不能修改 `props` 中的参数，只能通过 `$emit` 触发父组件的函数修改。在组件之间的层次或关系越来越复杂时，这种传统的实现方式会越来越麻烦 - 比如爷孙组件传值、兄弟组件传值等等。

> 当应用遇到 **多个组件共享状态** 时，单向数据流的简洁性很容易被破坏：
>
> * 多个视图依赖于同一状态
> * 来自不同视图的行为需要变更同一状态

Vuex 将组件中的共享状态抽取出来，以一个全局单例模式管理。

---

## Installation

```bash
$ npm install vuex --save
```

---

## Usage

在应用的入口引入：(通常是 `main.js`)

```javascript
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

var store = new vuex.Store({
  state: {
    // ...
  }
})

new Vue({
  el: '#app',
  router,
  store, // Use the store
  template: '<App/>',
  components: { App }
})
```

为了将 store 分离出去，可以新建一个 `store` 文件夹，在其中新建 `index.js`：

```javascript
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

export default new vuex.Store({
  state: {
    // ...
  }
})
```

在 `main.js` 中直接引入该 store 实例：

```javascript
import store from './store'

new Vue({
  el: '#app',
  router,
  store, // Use the store
  template: '<App/>',
  components: { App }
})
```

---

## Module

上述方法做到了将 store 从入口文件中分离了出去，但由于所有组件都要使用 Vuex 中的状态，将所有状态全部写在 `index.js` 里肯定不好。所以应当将不同的 state 从 `store/index.js` 中分离，通过 Module 来实现。

比如，新建一个叫做 `gojs` 的 Module，存放所有 GoJS 的状态。新建 `store/gojs.js`：

```javascript
export default {
  state:{
    show: false
  }
}
```

在 `store/index.js` 中引入这个 Module：

```javascript
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

import gojs from './gojs.js';

export default new vuex.Store({
  modules: {
    gojs: gojs
  }
})
```

在引用 state 变量时

* `this.$store.state.show` → `this.$store.state.gojs.show`
* 需要声明 Module Name

对于模块内部的 Mutation 和 Getter，接收的第一个参数是 **模块的局部状态对象**。默认情况下，模块内部的 Action、Mutation、Getter 注册在 **全局命名空间** 中。多个模块能对同一 Mutation 或 Action 作出响应。

可以通过设置 `namespaced: true` 使其成为带命名空间的模块。所有属性将会根据模块注册的路径调整命名。

---

## Mutations

更改 Vuex 的 store 中的状态的唯一方法：提交 Mutation。一个 Mutation 包含：

* 字符串形式的 type
* 回调函数 handler

通过以相应的 type 调用 `store.commit` 方法

```javascript
store.commit('increment')
```

可以向 `store.commit` 中传入额外的参数：Payload。Payload 是一个对象：

```javascript
mutations: {
  increment (state, payload) {
    state.count += payload.amount
  }
}
```

```javascript
store.commit('increment', {
  amount: 10
})
```

也可以使用另一种风格 commit mutation：

```javascript
store.commit({
  type: 'increment',
  amount: 10
})
```

在这种风格下，handler 保持不变。

### Principle

Mutation **必须是同步函数**。

### In Component

在组件中使用 `this.$store.commit('xx')` 提交 Mutation。**在根结点必须注入 `store` ！！！**

---

## Action

类似于 Mutation，不同在于：

* Action 提交的是 Mutation，而不是直接变更状态
* Action 可以包含任意异步操作

通过 `store.dispatch` 方法触发。

---

