# GoJS - Panel Item Arrays

Created by : Mr Dk.

2019 / 03 / 05 15:22

Nanjing, Jiangsu, China

---

### About

How does one display a variable number of elements in a node by data binding to a JavaScript Array?

* Just bind (or set) `Panel.itemArray`
* The Panel will contain as many elements as there are values in the bound Array

---

### Item Templates

Customize the elements created for each array item by specifying the `Panel.itemTemplate`

As with node data, you can have as many properties on your item data as your app demands, using whatever property names you prefer. Use data binding to automatically use those property values to customize the appearance and behavior of your item Panels.

---

### Different Panel Types

* Panel.Vertical
* Panel.Horizontal
* Panel.Table
* Panel.Position

Sometimes one wants to get the row for a particular item, or one wants to have a property value depend on the row index

* You can always depend on the value of `Panel.itemIndex` to get that property

---

### Arrays in Models

---

