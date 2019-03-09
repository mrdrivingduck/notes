# GoJS - Template Maps

Created by : Mr Dk.

2019 / 03 / 09 21:55

Nanjing, Jiangsu, China

---

### About

Want to have nodes with drastically __different__ appearances or behaviors in a
__single__ diagram at the __same__ time.

__GoJS__ supports as many templates as you want.

Each `Diagram` actually holds a __Map__ of templates for each type of Part: `Node`, `Group`, and `Link`. Each Map associates a __category__ name with a template.

* The diagram uses the node data's category to look up the node template in the `Diagram.nodeTemplateMap`
* The default category for any data object is the empty string `''`

The value of `Diagram.nodeTemplate` is just the value of `thatDiagram.nodeTemplateMap.get("")`. Setting `Diagram.nodeTemplate` just replaces the template in `Diagram.nodeTemplateMap` named with the empty string.

---

### E.g.

```javascript
var templmap = new go.Map();
templmap.add("simple", simpletemplate);
templmap.add("detailed", detailtemplate);
templmap.add("", diagram.nodeTemplate);

diagram.nodeTemplateMap = templmap;

diagram.model.nodeDataArray = [
  { key: "Alpha" }, // uses default category: ""
  { key: "Beta", category: "simple" },
  { key: "Gamma", category: "detailed" },
  { key: "Delta", category: "detailed" }
];
```

---

### Item Templates

For Panels with a value for `Panel.itemArray`, there is also the `Panel.itemTemplateMap`.

`Panel.itemCategoryProperty` names the property on the item data that identifies the
template to use from the `itemTemplateMap`

---

