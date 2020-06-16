# Vue.js - Event

Created by : Mr Dk.

2019 / 02 / 23 12:09

Nanjing, Jiangsu, China

---

## Trigger

调用内置的 `$emit` 方法，传入事件名称，触发一个事件

```vue
<button v-on:click="$emit('enlarge-text')">
  Enlarge text
</button>
```

通过 `v-on` 设置自定义事件监听器

```vue
<blog-post
  v-on:enlarge-text="postFontSize += 0.1"
></blog-post>
```

可以在父组件中设置监听器，在子组件中触发事件。用于子组件和父组件之间的沟通。

---

## Naming

与 `prop` 不同，触发的事件名必须和监听器的名称完全相同才行

* 事件名不会被用作 JavaScript 变量名或属性名了，因此不需要驼峰命名
* `v-on` 监听器在 DOM 模板中会被自动转换为小写 - 因为 HTML 是大小写不敏感的
  * `v-on:myEvent` 会被转换为 `v-on:myevent` 而导致不可能被监听到
* 对于事件的命名，**始终使用 kebab-case 命名**

---

