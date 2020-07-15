# Vue.js - Router

Created by : Mr Dk.

2019 / 02 / 26 23:15

Nanjing, Jiangsu, China

---

## About

*Vue Router* 能够将组件映射到路由，然后告诉 *Vue Router* 在哪里渲染它们。

## Installation

### CDN/Download

在 `<script></script>` 标签中直接加载

### NPM

```console
$ npm install vue-router
```

如果在一个模块化工程中使用，需要使用 `Vue.use()` 明确安装路由功能

```javascript
import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
```

## Relationship

<img src="../img/vue-router-src.png" alt="vue-router-src" style="zoom:50%;" />

1. 在 `/components` 中实现组件
2. 在 `/router/index.js` 中实例化 Router，并配置组件和路由的关系

   ```javascript
   import Vue from 'vue'
   import Router from 'vue-router'
   
   import HelloWorld from '@/components/HelloWorld'
   import Button from '@/components/Button'
   
   Vue.use(Router)
   
   export default new Router({
     routes: [
       {
         path: '/',
         name: 'HelloWorld',
         component: HelloWorld
       },
       {
         path: '/button',
         name: 'Button',
         component: Button
       }
     ]
   })
   ```

3. 在 `main.js` 中实例化 Vue，并配置 Router

   ```javascript
   import Vue from 'vue'
   import App from './App'
   import router from './router'
   
   Vue.config.productionTip = false
   
   /* eslint-disable no-new */
   new Vue({
     el: '#pp',
     components: { App },
     template: '<App/>',
     router: router
   })
   ```

4. 在 `App.vue` 中指定组件渲染的位置和组件跳转的链接

## Template

* `<router-view></router-view>` 标识组件渲染的位置
* `<router-link></router-link>` 设置导航链接
* `to` 属性指定链接，默认会被渲染成 `<a></a>` 标签

```vue
<template>
  <div id="app">
    <p>
      <router-link to="/component1">Component1</router-link>
      <router-link to="/component2">Component2</router-link>
    </p>
    <router-view></router-view>
  </div>
</template>
```

### Attributes of router-link

* `to` - 目标路由的链接，可带参数，点击后会将值传递到 `router.push()`
* `replace` - 调用 `router.replace()`，**导航后不会留下 history 记录**
* `append` - 在当前相对路径之后追加路径
* `tag` - 指定 `<router-link></router-link>` 的渲染标签
* ...

## Programmatic Navigation

除了按下 `router-link` 标签渲染出的链接，也可以在程序中直接调用 router 的 API，模拟点击的动作。

### `router.push(location, onComplete?, onAbort?)`

```javascript
const userId = '123'
router.push({ name: 'user', params: { userId } }) // -> /user/123
router.push({ path: `/user/${userId}` }) // -> /user/123
```

```javascript
// literal string path
router.push('home')

// object
router.push({ path: 'home' })

// named route
router.push({ name: 'user', params: { userId: '123' } })

// with query, resulting in /register?plan=private
router.push({ path: 'register', query: { plan: 'private' } })
```

### `router.replace(location, onComplete?, onAbort?)`

与 `router.push()` 作用类似，区别是不会产生历史条目。

### `router.go(n)`

在历史栈中向前进或向后退的次数。

```javascript
// go forward by one record, the same as history.forward()
router.go(1)

// go back by one record, the same as history.back()
router.go(-1)

// go forward by 3 records
router.go(3)

// fails silently if there aren't that many records.
router.go(-100)
router.go(100)
```

## Data Fetching

在路由跳转后，如何获得路由中的数据：

```javascript
this.$route.params.id // 坑：不是 router 而是 route ！！！
```

并可以在 `watch` 中监听路由的变化：

```javascript
watch: {
  // call again the method if the route changes
  '$route': 'fetchData'
}
```

## About the Re-clicking the Route Error

当重复点击同一个路由时，浏览器控制台报错。*Vue Router* 开发人员推荐的解决方式：

```javascript
this.$router.push({
  path: "/markdown",
  query: {
    repo: note.repo,
    path: note.path
  }
}).catch(err => { err }); // the solution
```

---

