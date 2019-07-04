# Vue.js - Core

Created by : Mr Dk.

2019 / 02 / 21 18:12

Nanjing, Jiangsu, China

---

## About

Vue (读音 /vjuː/，类似于 __view__) 是一套用于构建用户界面的 JavaScript __渐进式框架__

> 与其它大型框架不同的是，Vue 被设计为可以自底向上逐层应用。Vue 的核心库只关注视图层，不仅易于上手，还便于与第三方库或既有项目整合。另一方面，当与现代化的工具链以及各种支持类库结合使用时，Vue 也完全能够为复杂的单页应用提供驱动。

官方网站 - https://cn.vuejs.org/

---

## Installation

### Independent Version

从 Vue.js 的[官网](https://cn.vuejs.org/)直接下载 `vue.min.js`，并用 `<script>` 引入

### CDN

```html
<script src="https://unpkg.com/vue/dist/vue.js"></script>
```

### NPM

Vue.js 提供了官方的命令行工具，用于快速搭建大型单页应用

```bash
$ npm install -g @vue/cli
$ vue create my-project

# ...
# Enter for default
# ...

$ cd my-project

# ...
```

---

## Core

Vue.js 的核心是一个允许采用简洁的模板语法来声明式地将数据渲染进 DOM 的系统

>Vue.js 使用了基于 HTML 的模板语法，允许开发者声明式地将 DOM 绑定至底层 Vue 实例的数据。所有 Vue.js 的模板都是合法的 HTML ，所以能被遵循规范的浏览器和 HTML 解析器解析。
>
>在底层的实现上，Vue 将模板编译成虚拟 DOM 渲染函数。结合响应系统，Vue 能够智能地计算出最少需要重新渲染多少组件，并把 DOM 操作次数减到最少。

文件扩展名为 `.vue` 的文件称为 __single-file components（单文件组件）__：

![vue-template](../img/vue-template.png)

每个 `.vue` 文件包含三个顶级语言块：

* `<template></template>`
  * 包含 HTML 结构
* `<script></script>`
  * 包含 JavaScript 脚本
* `<style></style>`
  * 包含样式

> 一个重要的事情值得注意， __关注点分离不等于文件类型分离。__ 在现代 UI 开发中，我们已经发现相比于把代码库分离成三个大的层次并将其相互交织起来，把它们划分为松散耦合的组件再将其组合起来更合理一些。在一个组件里，其模板、逻辑和样式是内部耦合的，并且把他们搭配在一起实际上使得组件更加内聚且更可维护。
>
> 即便你不喜欢单文件组件，你仍然可以把 JavaScript、CSS 分离成独立的文件然后做到热重载和预编译。

---

## Summary

个人理解：

由于 `.vue` 文件不能直接被浏览器执行

需要使用 npm 安装 Vue.js 后

通过 Vue.js 运行在 Node.js 上的 dependencies 

将 `.vue` 文件中的声明式渲染

翻译为对应的 `.html`、`.css`、`.js` 文件以便在浏览器上运行

这个翻译的过程由 Vue.js 框架完成

所谓的 __渐进式__ 也由 Vue.js 框架实现

---

