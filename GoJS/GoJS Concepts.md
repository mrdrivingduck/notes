# GoJS - Concepts

Created by : Mr Dk.

2019 / 03 / 04 19:49

Nanjing, Jiangsu, China

---

### About

> __GoJS__ is a JavaScript library that lets you easily create interactive diagrams in modern web browsers. __GoJS__ supports __graphical templates__ and __data-binding__ of graphical object properties to model data. You only need to save and restore the model, consisting of simple JavaScript objects holding whatever properties your app needs. Many predefined tools and commands implement the standard behaviors that most diagrams need. Customization of appearance and behavior is mostly a matter of setting properties.

---

### Concepts

__Diagrams__ consist of __Parts__:

* __Nodes__ connected by __Links__ and grouped together into __Groups__
* Gathered together in __Layers__ and arranged by __Layouts__

Each __Diagrams__ has a __Model__:

* Holds and interprets your app data to determine:
  * node-to-node link relationships
  * group-member relationships
* The __Diagram__ automatically creates __Node/Group/Link__ in __Model__
* Can add whatever properties to each data object

__Node/Link__ is normally defined by a __template__ declaring its appearance and behavior

Each __template__ consists of __Panels__ of __GraphObjects__ - such as __TextBlocks__ or __Shapes__

* There default templates for all parts, but almost all apps will specify custom templates
  * Data binding of __GraphObject properties__ to __model data properties__ make each __Node__ and __Link__ unique for the data

__Nodes__ can be positioned manually - 

* Interactively
* Programmatically

Or can be arranged automatically - 

* Layout

__Tools__ handle mouse and keyboard events

__CommandHandler__ interprets keyboard events

---

### Visual Tree

The __Diagram__ contains all of the __Layers__

A __Layer__ contains all of the __Parts (Nodes & Links)__

A __Parts__ contains nested panels of __text, shapes and images__

---

### Usage

> __GoJS__ does not depend on any JavaScript library or framework, so you should be able to use it in any environment. However it does require that the environment support __modern HTML (HTML5) and JavaScript__.

---

### Summary

今天学习了一下这个 JS 库

简直是前端图形化编程的利器啊

试了一下官网上的 Sample

动态到完全不像是在浏览器上的效果

把这个用会就太牛b了

---

