# GoJS - Shape

Created by : Mr Dk.

2019 / 03 / 05 10:11

Nanjing, Jiangsu, China

---

### About

Use the __Shape__ class to paint a geometrical figure

Shapes, like __TextBlock__ and __Picture__, are "atomic" objects

* They cannot contain any other objects
* a __Shape__ will never draw some text or an image

---

### Figures

`Shape.figure` is set to commonly named kinds of shapes

`GraphObject.desiredSize` & `GraphObject.width` & `GraphObject.height` for sizing

---

### Filling and Strokes

`Shape.stroke` specifies the brush used to draw the shape's __outline__

`Shape.strokeWidth` specifies the width of drawing the outline

`Shape.fill` specifies the brush used to fill the shape's outline

---

### Geometry

Every __Shape__ gets its "shape" from the __Geometry__ that it uses

A Geometry is just a saved description of how to draw some lines given a set of points

Setting `Shape.figure` uses a named predefined geometry that can be parameterize

---

### Angle and Scale

`GraphObject.angle` & `GraphObject.scale`

`Shape.fill` & `GraphObject.background` rotate along with the shape

`GraphObject.areaBackground` is not affected by the object's scale or angle

---

### Custom Figures

---

