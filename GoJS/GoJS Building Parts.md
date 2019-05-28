# GoJS - Building Parts

Created by : Mr Dk.

2019 / 03 / 04 23:59

Nanjing, Jiangsu, China

---

## About

__Node__ 或者 __Link__ 可以由多个 __GraphObjects__ 组成

包括嵌套的 __Panel__

GoJS 提供了两种构造零件的方式

---

## Building with Code

通过传统的 JavaScript 代码构造零件

完全可行

* 但当零件内部结构变得复杂时，代码也会变得非常复杂

---

## Building with `GraphObject.make`

静态函数，不需要在构造零件时使用一大堆局部变量

支持对象嵌套，且能够从代码中看出 Visual Tree 的深度

使用 models、templates、data-binding 自动创建 Nodes 和 Links

`GraphObject.make` 的第一个参数为类型，一般为 `GraphObject` 的子类

额外参数：

* 带有 `property - value` 的 JavaScript 原生对象
* GraphObject，作为构造的元素
* A __GoJS__ enumerated value constant - value of the unique property
* A string to set property
  * `TextBlock.text`
  * `Shape.figure`
  * `Picture.source`
  * `Panel.type`
* `RowColumnDefinition` for describing rows and columns in Table Panels
* A JavaScript Array - useful when returning more than one argument from a function
* Other specialized objects - used in the appropriate manner for the object being constructed

---

## The Use of `$ `

The use of __$__ as an abbreviation for __go.GraphObject.make__ is so handy that we will assume its use from now on. Having the call to __go.GraphObject.make__ be minimized into a single character helps remove clutter from the code and lets the indentation match the nesting of GraphObject in the visual tree that is being constructed. 

Some other JavaScript libraries automatically define "$" to be a handy-to-type function name, assuming that they are the only library that matters. But you cannot have the same symbol have two different meanings at the same time in the same scope, of course. So you may want to choose to use a different short name, such as "$$" or "GO" when using __GoJS__. The __GoJS__ documentation and samples make use of "$" because it makes the resulting code most clear. 

> Another advantage of using `GraphObject.make` is that it will make sure that any properties that you set are defined properties on the class. If you have a typo in the name of the property, it will throw an error, for which you can see a message in the console log.

---

## Summary

好 J8 复杂

---

