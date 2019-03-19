# Vue.js - Deep Watch

Created by : Mr Dk.

2019 / 03 / 19 10:59

Nanjing, Jiangsu, China

---

### About

对于 Vue.js 中的 `watch` 属性的一些高级用法

该属性用于响应某个数据的变化

在侦听到数据发生变化时，调用对应的函数

> 允许执行异步操作 (访问一个 API)，限制执行该操作的频率，并在得到最终结果前，设置中间状态

```javascript
watch: {
    someVal: function (newVal, oldVal) {
        // TO DO ...
    }
}
```

---

### Handler

`watch` 的 `handler` 属性，在默认情况下可以简写

因为上述的 `watch` 中只有 `handler` 一个属性

在上面的代码块中，编译后其实就是一个 handler

如果在 `watch` 中还需要使用下文叙述的其它属性

`handler` 就要作为 `watch` 的一个属性被显式声明了

---

### Immediate

`watch` 的特点是，在最初绑定时是不会执行的

只有在侦听的数据发生变化时才会被调用

如果希望在 `watch` 中声明后先调用一次 `handler`

需要使用 `immediate: true` 属性

```javascript
watch: {
    someVal: {
        handler: function (newVal, oldVal) {
            // TO DO ...
        },
        immediate: true
    }
}
```

---

### Deep

深度监听 - 如果监听的是一个对象

默认情况下 Vue.js 不会响应对象属性的变化

只会响应对象引用的变化

* 即只有给该对象重新赋值的时候才会被监听到
* 该对象的某属性发生变化时不会被监听到

使用 `deep: true` 属性进行 __深入观察__ 😍

* 监听器将会层层向下遍历，给所有属性加上监听器
* 性能开销较大

```javascript
watch: {
    someVal: {
        handler: function (newVal, oldVal) {
            // TO DO ...
        },
        deep: true
    }
}
```

优化：__使用字符串形式的监听__

* 监听器将层层向下解析，直到遇到相应的属性，并设置监听函数

> 咋网上没几个人用这种方法呢？
>
> 下次再验证吧
>
> 如果说对性能真的有优化
>
> 那确实不错

---

### Summary

随着开发的层次渐进

遇到的用法也越来越高级了

搓手手~~ 😀

---

