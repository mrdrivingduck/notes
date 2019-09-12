# Node.js - Event Loop

Created by : Mr Dk.

2019 / 09 / 12 14:49

Nanjing, Jiangsu, China

---

## About

事件循环，解决 JavaScript 单线程非阻塞运行的一种机制

__异步__ 的基本原理

---

## Task

在 JavaScript 中，分为两类任务：

* Macro-Task (宏任务)
  * script 全部代码
  * `setTimeOut`
  * `setInterval`
  * `setImmediate`
  * I/O
  * UI 渲染
* Micro-Task (微任务)
  * `Process.nextTick()`
  * Promise
  * ...

---

## Event Loop in Browser

### Browser Threads

* GUI 渲染线程
* JavaScript 引擎线程
* 定时触发器线程
* 事件触发线程
* HTTP 请求线程

其中，JavaScript 引擎线程应当是主线程 - 负责执行代码

另外，GUI 渲染线程和 JavaScript 引擎线程互斥

### Call Stack

所有的 Task 在执行时会被放到调用栈中，等待被主线程执行

__同步任务__ 会在 Call Stack 中等待主线程依次执行

__异步任务__ 会在异步任务产生结果后，将注册的 __回调函数__ 放入任务队列中

* __宏任务队列__ 和 __微任务队列__

### Task Queue Scheduling

首先执行同步代码

执行完毕后，查看 Call Stack 是否为空

如果为空，则检查 Micro-Task Queue

* 一次性执行完所有的 Micro-Task

执行 Macro-Task Queue

单个 Macro-Task 执行完毕后，检查 Micro-Task Queue

* 如果不为空，则再次执行所有的 Micro-Task
* 依次类推

https://juejin.im/post/5c3d8956e51d4511dc72c200#heading-35 中有一个动画很形象

### async/await

实际上是 Promise 的语法糖

* 对于 `await`，解释器会创建一个 Promise 对象
* 将 `async` 函数中的操作放到 `then()` 回调函数中

而 Promise 就是一个微任务

---

## Event Loop in Node.js

Node 中的 Event Loop 是基于 `libuv` 实现的

该事件循环被分为 6 个阶段

* 按照顺序反复运行
* 每进入一个阶段，会从该阶段对应的回调队列中取出函数执行，直到队列为空或达到阈值

每个阶段都有一个队列哦

6 个阶段分别为：

* Timers - 执行 `setTimeout` 、`setInterval` 的回调
* I/O callbacks - 执行某些系统操作的回调 (如 TCP 错误类型)
* Idle, prepare
* Poll - 轮询阻塞 (?)
  * 处理 Timers 中的定时器
  * 执行 I/O 回调
  * 处理轮询队列中的事件，同步执行，直到队列为空或达到系统限制
* Check - 执行 `setImmediate()` 回调
* Close callbacks

网上的讲解也太乱了，我也没看源代码不敢乱说

只注意到一个 Node.js 和 Browser 的区别：

* 在浏览器中，micro-task 的任务队列在每个 macro-task 执行完后执行
* 在 Node.js 中，micro-task 会在 Event Loop 的各个阶段之间执行

也即，micro-task 任务队列的执行时机不同

而 `Process.nextTick()` 不是 Event Loop 中的一部分，而是有一个单独的任务队列

* 当每个阶段完成后，如果存在 `nextTick` 队列，就会清空所有队列中的回调函数
* 优先于 micro-task 执行

---

## Refefence

https://juejin.im/post/5c3d8956e51d4511dc72c200#heading-35

---

## Summary

虽然我很菜 但我还是要吐槽

怎么大部分中国程序员的表达能力如此之差哦

看个博客，句子狗屁不通，逻辑前后矛盾

唉 太南了 不禁有些怀念本科同学 Triple-Z

不仅能讲，还讲得明白讲得清楚

---

