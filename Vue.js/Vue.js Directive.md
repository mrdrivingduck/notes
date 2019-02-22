# Vue.js - Directive

Created by : Mr Dk.

2019 / 02 / 22 16:27

Nanjing, Jiangsu, China

---

### About

> Directives are prefixed with `v-` to indicate that they are special attributes provided by Vue, and as you may have guessed, they apply special reactive behavior to the rendered DOM.

---

### Conditionals

`v-if` - Determine the presence of an element

- Similar: `v-show`
- for more logic: `v-else-if`、`v-else`

Format: `<tagname v-if="flag">...</tagname>`

示例：根据 `seen` 作为条件判断 `<p>` 段落是否显示

```vue
<template>
  <div id="app">
    <p v-if="seen">{{ site }}</p>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      site: 'Here is a message.',
      seen: true
    }
  },
  name: 'App'
}
</script>
```

>This example demonstrates that we can bind data to not only __text__ and __attributes__, but also the __structure__ of the DOM. Moreover, Vue also provides a powerful transition effect system that can automatically apply transition effects when elements are inserted/updated/removed by Vue.

---

### Loops

`v-for` - Can be used for displaying a list of items using the data from an Array

Format: `<tagname v-for="obj in arr" :key="obj.xxx">...</tagname>`

示例：将数组 `arr` 中的信息显示到无序列表 `<ul>` 中

```vue
<template>
  <div id="app">
    <ul>
      <li v-for="num in arr" :key="num.text">
        {{ num.text }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      arr: [
        {text: '222'},
        {text: '333'},
        {text: '444'}
      ]
    }
  },
  name: 'App'
}
</script>
```

* 官网文档中的示例不加 `:key` 会报错 - 新版本的语法变动

---

### Event Listener

`v-on` - Attach event listeners that invoke methods on our Vue instances

Format: `<tagname v-on:xxx="xxxxxx">...</tagname>`

* `v-on:click`
* `v-on:submit`
* `v-on:keyup`
* ...

示例：给按钮 `<button>` 设置监听事件，反转字符串

```vue
<template>
  <div id="app">
    <p>{{ message }}</p>
    <button v-on:click="reverse">Reverse</button>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      message: 'Here is a message.'
    }
  },
  methods: {
    reverse: function () {
      this.message = this.message.split('').reverse().join('')
    }
  },
  name: 'App'
}
</script>
```

在 `reverse()` 中，更新了应用状态，但不需要触碰 DOM

* 所有的 DOM 操作都有 Vue 来处理，代码只需要关注逻辑层面即可

#### Descriptor

e.g. - `v-on:click.stop`

* `.stop`
* `.prevent`
* `.capture`
* `.self`
* `.once`

Also - `v.on:click.stop.prevent` is okay

`v-on` 可缩写为 `@`

示例：在输入框中设置监听器，输入 `Alt + C` 后反转字符串

```vue
<template>
  <div id="app">
    <p>{{ message }}</p>
    <input v-on:keyup.alt.67="reverse">
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      message: 'Here is a message.'
    }
  },
  methods: {
    reverse: function () {
      this.message = this.message.split('').reverse().join('')
    }
  },
  name: 'App'
}
</script>
```

---

### Two-way Binding

`v-model` - Make two-way binding between form input and app state a breeze

示例：

* 段落 `<p>` 中的内容根据输入框 `<input>` 中的输入而变化
* 输入框 `<input>` 中的内容和段落 `<p>` 中的内容一致（比如初始状态）

```vue
<template>
  <div id="app">
    <img src="./assets/logo.png">
    <p>{{ message }}</p>
    <input v-model="message">
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      message: 'Here is a message.'
    }
  },
  name: 'App'
}
</script>
```

> 可以用 `v-model` 指令在表单控件元素上创建双向数据绑定。根据控件类型它自动选取正确的方法更新元素。尽管有点神奇，`v-model` 不过是语法糖，在用户输入事件中更新数据，以及特别处理一些极端例子。

![vue-v-model](../img/vue-v-model.png)

与 `v-bind` 的区别：

* `v-bind` 用来绑定数据和属性以及表达式
  * `v-bind` 直接使用相当于 `{{  }}`
  * `v-once` 执行一次性插值，数据改变时，插值处内容不更新
    * 可能影响到结点上其它数据的绑定
  * 绑定属性：`<a v-bind:href="xxx">...</a>`
  * 绑定表达式或 HTML
* `v-model` 使用在表单中，实现双向数据绑定，在表单元素外使用不起作用
  * text / radio / checkBox / select / ...

---

### Summary

学习了一些 Vue.js 中的指令

对于前端好像有了那么一些感觉了

---

