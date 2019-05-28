# GoJS - Data Binding

Created by : Mr Dk.

2019 / 03 / 05 14:21

Nanjing, Jiangsu, China

---

## About

Data binding is a way to extract a value from a source object and set a property on a target object

* The target objects are normally __GraphObjects__
* The source objects are usually JavaScript data objects held in a model

---

## Binding string and number properties

All you need to do is add to the target __GraphObject__ a new Binding that names the __target property__ on the visual object and the __source property__ on the data object

* The target property must be a settable property
* some GraphObject properties are not settable
* If specify a target property name that does not exist &rarr; warning messages in the console
* If the source property value is undefined &rarr; the binding is not evaluated

---

## Binding object properties such as `Part.location`

Data bind properties that have values that are objects

---

## Conversion functions

Provide a conversion function that converts the actual data property value to the needed value type or format

* For data properties on model objects, you will often want to use strings as the representation of Points, Sizes, Rects, Margins, and Spots, rather than references to objects of those classes
* Strings are easily read and written in JSON and XML
* Trying to read/write classes of objects would take extra space and would require additional cooperation on the part of both the writer and the reader

---

## Changing data values

Call `Model.setDataProperty` to modify data property

__Modifying a data property directly without calling the appropriate model method
may cause inconsistencies or undefined behavior.__

---

## Changing graph structure

For node data - 

* `Model.setCategoryForNodeData`
* `Model.setKeyForNodeData`
* `GraphLinksModel.setGroupKeyForNodeData`
* `TreeModel.setParentKeyForNodeData`
* `TreeModel.setParentLinkCategoryForNodeData`

For link data - 

* `GraphLinksModel.setCategoryForLinkData`
* `GraphLinksModel.setFromKeyForLinkData`
* `GraphLinksModel.setFromPortIdForLinkData`
* `GraphLinksModel.setToKeyForLinkData`
* `GraphLinksModel.setToPortIdForLinkData`
* `GraphLinksModel.setLabelKeysForLinkData`

---

## Binding to __GraphObject__ sources

The binding source object need not be a plain JavaScript data object held in the diagram's model. The source object may instead be a named __GraphObject__ in the same __Part__.

* The source property must be a settable property of the class.
* The binding is evaluated when the property is set to a new value.

```javascript
diagram.nodeTemplate =
  $(go.Node, "Auto",
    { selectionAdorned: false },
    $(go.Shape, "RoundedRectangle",
      // bind Shape.fill to Node.isSelected converted to a color
      new go.Binding("fill", "isSelected", function(sel) {
            return sel ? "dodgerblue" : "lightgray";
          }).ofObject()),  // no name means bind to the whole Part
    $(go.TextBlock,
      { margin: 5 },
      new go.Binding("text", "descr"))
  );

diagram.model.nodeDataArray = [
  { descr: "Select me!" },
  { descr: "I turn blue when selected." }
];
```

---

## Binding to the shared __Model.modelData__ source

---

## Two-way data binding

Transfer values from __GraphObject__ back to the model data, to keep the model data up-to-date with the diagram

Two-way Binding - `Binding.makeTwoWay`

* Pass values not only from source to target
* But also from the target object back to the source data

---

## Reason for Two-Way Bindings

Make sure that any changes to that property will be copied to the corresponding model data

* By making sure that the Model is up-to-date, you can easily "save the diagram" just by saving the model and "loading a diagram" is just a matter of loading a model into memory and setting `Diagram.model`

__Most bindings do not need to be TwoWay__

* For performance reasons you should not make a Binding be Two-Way unless you actually need to propagate changes back to the data
* Most settable properties are only set on initialization and then never change.

---

