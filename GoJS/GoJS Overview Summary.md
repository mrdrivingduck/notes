# GoJS - Overview Summary

Created by : Mr Dk.

2019 / 03 / 17 0:11

Nanjing, Jiangsu, China

---

## About

对最近正在使用的 GoJS 库进行一定的总结

---

## Concept

GoJS 的边界由 Diagram（图表）指定

在 HTML 的 `<div></div>` 中嵌入图表

在图表中主要需要指定两个部分：

1. 模板 - template
2. 模型 - model

对于每一个部分，又细分为两类：

1. 结点 - node
2. 连线 - link

---

## Template

模板主要用于图表显示的行为，分为：

1. 结点模板
2. 连线模板

### Node Template

主要描绘每个 Node 的显示行为

* 每个 Node 可以由更小的基本元素组成
  * Panel、TextBlock、Shape 等
  * 对组成元素进行布局
* 对于各元素的每个属性（property）都可以进行相应的定制
* 可以将元素的 property 与一些数据进行单向或双向绑定 - `go.Binding()`

### Link Template

主要描绘每条 Link 的显示行为

* 包括与 Node 连接处的一些特性
* 以及线条的粗细、颜色
* 是否有箭头、箭头的指向和样式等

---

## Model

模型主要用于图表内部数据的存储，也分为：

1. 结点模型
2. 连线模型

### Node Model

* 位于 `nodeDataArray` 中

### Link Model

* 位于 `linkDataArray` 中
* 存储了连线的各项属性，包括源结点的源端口以及目标结点的目标端口

### Save/Load Model

可以使用 `Model.toJson()` 将模型数据转化为 JSON 格式进行持久化

反之，使用 `Model.fromJson()` 可以将持久化的模型数据在 GoJS 图表中恢复

### Model Modification

如果需要对模型数据进行改动

__不可直接对 `nodeDataArray` 和 `linkDataArray` 进行改动！__

* 因为 GoJS 将不会对这种数据改动进行响应
* GoJS 内部的 Undo Manager 也不会记录改动，从而无法撤销

应当使用 GoJS 提供的 API 进行模型数据改动

* `addNodeData()` / `removeNodeData()`
* `addLinkData()` / `removeLinkData()`
* ......

---

## Event

可以设定一些事件进行监听，触发一些回调函数

* 可以对 diagram 本身设定一些监听事件
* 也可以对 Model 的数据改动设定一些监听事件
* 在 Template 的 property 中也可以设定一些回调函数，相当于触发 event

---

## Summary

一路都是看 GoJS 的官方文档和示例走过来的

可以说这个组件功能非常强大

想实现的样式基本都能实现

而且官方给的 Sample 非常齐全

基本涵盖了所有可能应用到的场景

并给出了源码可供参考

所以上手还是比较快的

---

