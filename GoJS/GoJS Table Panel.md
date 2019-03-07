# GoJS - Table Panel

Created by : Mr Dk.

2019 / 03 / 06 16:46

Nanjing, Jiangsu, China

---

### About

`Panel.Table` arranges objects in rows and columns

---

### Simple Table Panels

Each object in a Table Panel is put into the cell indexed by the value of __GraphObject.row__ and __GraphObject.column__

* The panel will look at the rows and columns for all of the objects in the panel to determine how many rows and columns the table should have
* Not every "cell" of the table needs to have a __GraphObject__ in it
* If there are multiple objects in a cell, they will probably overlap each other in the cell
* By default objects are center-aligned in each cell
* If a column or a row has no objects in it, that column or row is ignored

---

### Sizing of Rows or Columns

The height of each row

* Determined by the greatest height of all of the objects in that row

The width of each column 

* Determined by the greatest width of all of the objects in that column

Provide row height or column width information for any row or column independent of any individual object by setting properties of the desired `RowColumnDefinition`

Get - Call `Panel.getColumnDefinition` or `Panel.getRowDefinition`

Set - Call `RowColumnDefinition.width` or `RowColumnDefinition.height`

Limit to certain ranges - Call `RowColumnDefinition.minimum` or `RowColumnDefinition.maximum`

---

### Stretch and Alignment

`GraphObject.stretch` specifies whether the width and/or height should take up all of the space given to it by the Panel

`GraphObject.alignment` property controls where the object is placed if it is smaller than available space

Stretch - 

* Horizontal
* Vertical

Alignment - 

* Top
* Center
* Bottom

---

### Spinning Rows or Columns

Set the `GraphObject.rowSpan` or `GraphObject.columnSpan` properties to specify how many cell in a Table Panel it can cover

---

### Separators and Row/Column Padding

Support the optional drawing of lines between rows or columns

`RowColumnDefinition.separatorStrokeWidth` controls the extra space

`RowColumnDefinition.separatorStroke` controls if a line is drawn

`RowColumnDefinition.separatorDashArray` controls how a line is drawn

`RowColumnDefinition.separatorPadding` is used to add extra space to rows or columns

`RowColumnDefinition.background` includes the padding in its area

Any separator properties set on a particular `RowColumnDefinition` will take precedence over the default values provided on the Panel

---

### TableRows and TableColumns

To avoid having to specify the row for each object

 Put all of the objects for each row into a `TableRow` Panel

* Still need to specify the column for each object in each row

---

