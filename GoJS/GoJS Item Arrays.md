# GoJS - Item Arrays

Created by : Mr Dk.

2019 / 03 / 10 21:10

Nanjing, Jiangsu, China

---

## About

在 model data 中，不仅可以挂载数值，还可以将一个数组绑定到 `Panel.itemArray` 上：

```javascript
nodeDataArray: [
  { key: 1, items: [ "Alpha", "Beta", "Gamma", "Delta" ] },
  { key: 2, items: [ "first", "second", "third" ] }
]
```

---

## Item Templates

为绑定到 `Panel.itemArray` 上的每一个元素设计样式模板 - `itemTemplate` 属性

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

在 `itemTemplate` 属性中，可以直接使用数组中对应的属性名：

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

获取数组中的某个元素 - 索引

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

如果要在 Model 动态修改 item array，需要调用 GoJS 的 API

增 / 删 - 提供 item array 和 index 即可：

```javascript
void Model.insertArrayItem(arr: Array<any>, idx: number, val: any);
void Model.removeArrayItem(arr: Array<any>, idx?: number);
```

修改某一项：

```javascript
void setDataProperty(data: ObjectData, propname: string, val: any);
```

可以通过 index 直接引用 item array 中的某项作为 ObjectData，更新某一 prop 的值

---

