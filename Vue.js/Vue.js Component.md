# Vue.js - Component Registration

Created by : Mr Dk.

2019 / 02 / 22 23:45

Nanjing, Jiangsu, China

---

### About

__组件__ 是可复用的 Vue 实例

并带有一个名字，可以在根实例中将组件当做自定义元素使用

组件可以进行任意次数的复用

* 每用一次组件，一个新的 Vue 实例就会被创建

通常一个应用会以一棵嵌套的组件树的形式来组织：

![vue-component](../img/vue-components.png)

---

### Registration

#### Global Registration

Vue 实例的 `component()` 方法

全局注册的组件可以用于在其 __被注册之后__ 的任何新创建的 Vue 根实例及其所有子组件模板中

* 全局注册三个组件，三个组件中也可以互相使用另两个组件

```javascript
Vue.component('my-component', {
  data: function() {
    return {
      count: 0
    }
  },
  template: template: '<button v-on:click="count++">You clicked me {{ count }} times.</button>'
})

new Vue({
  el: '#app',
  components: { App },
  template: '<App/>'
})
```

__ATTENTION - 组件中的 `data` 必须是一个函数__

也可以将组件的内容实现在 `.vue` 文件中，以实现复用：

```vue
<template>
    <button v-on:click="add">You clicked me {{ count }} times.</button>
</template>

<script>
export default {
  data: function () {
    return {
      count: 0
    }
  },
  methods: {
    add: function () {
      this.count++
    }
  },
  name: 'Button'
}
</script>
```

```javascript
import Button from './components/Button.vue'
Vue.component('Button', Button)

new Vue({
  el: '#pp',
  components: { App },
  template: '<App/>'
})
```

#### Local Registration

Vue 实例中的 `components` 属性

使用普通的 JavaScript 对象定义组件：

```javascript
var ComponentA = { /*    */ }
var ComponentB = { /*    */ }

new Vue({
  el: '#app',
  components: {
    'component-a': ComponentA,
    'component-b': ComponentB
  }
})
```

局部注册的组件在其子组件中不可用

* `A` 组件中不能使用 `B` 组件

除非：

```javascript
var ComponentA = { /*    */ }

var ComponentB = {
  components: {
    'component-a': ComponentA
  },
  // ...
}
```

也可以直接将组件实现在 `.vue` 文件中

```vue
<template>
  <div id="app">
    <HelloWorld></HelloWorld>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
  components: {
    HelloWorld    // Helloworld: Helloworld
  },
  name: 'App'
}
</script>
```

---

### Automatic Global Registration of Base Components

下次用到了再研究

---

### Summary

明白了 Vue.js 为何要这样设计

将每一部分都拆分为组件

这样整个网页可以像搭积木一样一点一点被拼出来

---

