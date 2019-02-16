# Node.js - Module

Created by : Mr Dk.

2019 / 02 / 16 23:27

Ningbo, Zhejiang, China

---

### About

随着代码来越来越多

为了编写可维护、可组织的代码

将函数分组放到不同的文件里

在 __Node.js__ 环境中，一个 `.js` 文件就称之为一个 `module`

优势：

* 提高代码可维护性，便于代码 __复用__
  * Node.js 内置模块 和 第三方模块
* 避免函数名和变量名冲突
  * 相同名称的函数和变量可以出现在不同模块中

---

### Usage

在模块中将函数暴露出去：

```javascript
module.exports = func;
```

在其它地方使用模块：

```javascript
var func = require('./module.js');    // relative path
func();
```

---

### Theory of Module

__Closure__ - 将模块中的函数包装

* 模块中的全局变量就变成了闭包中的局部变量

```javascript
(function() {
    // TO DO ...
})();
```

---

### Inner Object

#### `global`

JavaScript 的全局对象：

* 在浏览器中，叫 `window`
* 在 Node.js 中，叫 `global`

#### `process`

当前 Node.js 进程

---

### Inner Module

#### `fs`

文件系统模块，同时提供 __同步__ 和 __异步__ 方法

由于 Node.js 用于执行服务器端代码，__必须使用异步代码__

#### `stream`

Node.js 中的 __流__ 是一个对象

在创建流之后，只需要响应流的事件即可（类似于 _Vert.x_ 中的 _handler_）

* Read
  * 每次响应 `data` 事件，获取一个 chunk
  * 响应 `end` 时间，结束
* Write
  * 调用 `write()` 函数
  * 以 `end()` 函数结束

`pipe()` 可用于将两个流连接

#### `http`

简直和 _Vert.x_ 的 API 一毛一样。。。。。。

#### `crypto`

加密算法和哈希算法

---

### Summary

所以 总体上感觉 Node.js 就是 Python + Vert.x 的杂糅版

感觉没费什么脑子就能够理解了

JavaScript 服务器的事儿也就是这么多

主要还是看一看 JS 前端怎么玩

---

