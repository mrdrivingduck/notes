# GoJS - Item Arrays

Created by : Mr Dk.

2019 / 03 / 10 21:10

Nanjing, Jiangsu, China

---

## About

Display a variable number of elements in a node by data binding to a JavaScript Array

Bind `Panel.itemArray` and JavaScript Array `items`:

```javascript
nodeDataArray: [
  { key: 1, items: [ "Alpha", "Beta", "Gamma", "Delta" ] },
  { key: 2, items: [ "first", "second", "third" ] }
]
```

---

## Item Templates

```javascript
diagram.nodeTemplate =
  $(go.Node, "Auto",
    $(go.Shape, "RoundedRectangle"),
    $(go.Panel, "Vertical",
      new go.Binding("itemArray", "items"),
      {
        itemTemplate:
          $(go.Panel, "Auto",
            $(go.TextBlock,
              new go.Binding("text", "t")
            )
          )  // end of itemTemplate
      }
    )
  );
```

```javascript
nodeDataArray: [
  {
    key: 1,
    items: [
      { t: "Alpha", c: "orange" },
      { t: "Beta" },
      { t: "Gamma", c: "green" },
      { t: "Delta", c: "yellow" }
    ]
  },
  {
    key: 2,
    items: [
      { t: "first", c: "red" },
      { t: "second", c: "cyan" },
      { t: "third" }
    ]
  }
]
```

---

## Different Panel Types

If the panel type is `Panel.Spot`, `Panel.Auto`, or `Panel.Link`, the __first child__ element of the __Panel__ is assumed to be the "main" object and is kept as the first child in addition to all of the nested panels created for the values in the `Panel.itemArray`

When using a Panel of type `Panel.Table` as the container, it is commonplace to use an item template that is of type `Panel.TableRow` or `Panel.TableColumn`. This is the only way to specify the individual column or row indexes for the elements inside the template.

---

## Index

Sometimes one wants to get the row for a particular item

or one wants to have a property value depend on the row index

* `Panel.itemIndex`

If the item Panel is of type `Panel.TableRow`

* `GraphObject.row` property will also be set to the zero-based row number
* The same is true for `GraphObject.column` if the `itemTemplate` is a `Panel.TableColumn` Panel

The property is set when the item panels are created for Array item data

Create `Bindings` where the source is that "row" property: 

```javascript
new go.Binding("targetProperty", "row", function (i) {
    return ...;
}).ofObject()
```

---

## Modification

```javascript
void Model.insertArrayItem(arr: Array<any>, idx: number, val: any);
void Model.removeArrayItem(arr: Array<any>, idx?: number);
```

---

