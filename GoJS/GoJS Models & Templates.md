# GoJS - Models & Templates

Created by : Mr Dk.

2019 / 03 / 05 11:45

Nanjing, Jiangsu, China

---

## About

You can build a diagram of nodes and links programmatically

>  This is similar to the earlier problem when building a node's visual tree in code of having to use temporary named variables and referring to them when needed

```javascript
var node1 =
  $(go.Node, "Auto",
    $(go.Shape,
      { figure: "RoundedRectangle",
        fill: "lightblue" }),
    $(go.TextBlock,
      { text: "Alpha",
        margin: 5 })
  )
diagram.add(node1);

var node2 =
  $(go.Node, "Auto",
    $(go.Shape,
      { figure: "RoundedRectangle",
        fill: "pink" }),
    $(go.TextBlock,
      { text: "Beta",
        margin: 5 })
  );
diagram.add(node2);

diagram.add(
  $(go.Link,
    { fromNode: node1, toNode: node2 },
    $(go.Shape)
  ));
```

But __GoJS__ offers a way to build diagrams in a more declarative manner

You only provide the __node and link data (i.e. the model)__ necessary for the diagram and __instances of parts (i.e. the templates)__ that are automatically copied into the diagram

Those templates may be parameterized by properties of the node and link data

```javascript
var nodeDataArray = [
  { key: "Alpha"},
  { key: "Beta" }
];
var linkDataArray = [
  { from: "Alpha", to: "Beta" }
];
diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
```

---

## Using a Model and Templates

### Concepts

* A model is basically just __a collection of data__ that holds the essential information for each node and each link
* A template is basically just __a Part that can be copied__; you would have different templates for Nodes and for Links

### Templates

* A Diagram already has very simple __default templates__ for Nodes and Links
* If you want to customize the appearance of the nodes in your diagram, you can replace the default node template by setting `Diagram.nodeTemplate`

### Models

* Models interpret and maintain references between the data
* Each node data is expected to have a unique key value so that references to node data can be resolved reliably
* Models also manage dynamically adding and removing data.

---

## Model Data

The node data and the link data in models can be any JavaScript object

* You can decide what properties those objects have - add as many as you need for your app
* Since this is JavaScript, you can even add properties dynamically
* Several properties that __GoJS__ models assume exist on the data, such as "key" (on node data) and "category" and "from" and "to" (the latter two on link data).

A node data object normally has its node's unique key value in the "key" property

* Currently node data keys must be strings or numbers
* Get the key for a Node either via the `Node.key` property or via `someNode.data.key`

---

## Data Binding

> A data binding is a declarative statement that the value of the property of one object
> should be used to set the value of a property of another object.

We can declare such data-bindings by creating __Binding__ objects and associating them with the target __GraphObject__

```javascript
diagram.nodeTemplate =
  $(go.Node, "Auto",
    $(go.Shape,
      { figure: "RoundedRectangle",
        fill: "white" },                 // default Shape.fill value
      new go.Binding("fill", "color")),  // binding
    $(go.TextBlock,
      { margin: 5 },
      new go.Binding("text", "key"))     // binding
  );

var nodeDataArray = [
  { key: "Alpha", color: "lightblue" },  // node data: color
  { key: "Beta", color: "pink" }
];
var linkDataArray = [
  { from: "Alpha", to: "Beta" }
];
diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
```

A template is a Part that may have some data Bindings and that is not itself in a diagram
but may be copied to create parts that are added to a diagram

---

## Kinds of Models

> A model is a way of interpreting a collection of data objects as an abstract graph
> with various kinds of relationships determined by data properties and the assumptions that the model makes.

The simplest kind of model, __Model__, can only hold "parts" without any relationships between them

* No links or groups
* Act as the base class for other kinds of models.

### GraphLinksModel

Supports link relationships using a separate link data object for each Link

* There is no inherent limitation on which Nodes a Link may connect
* Reflexive and duplicate links are allowed
* Links might also result in cycles in the graph

Supports identifying logically and physically different connection objects, known as "ports"

* An individual link may connect with a particular port rather than with the node as a whole

Supports the group-membership relationship

### TreeModel

Supports link relationships that form a tree-structured graph

* There is no separate link data, so there is no `linkDataArray`
* Extra property on the child node data `parent` which refers to the parent node by its key

---

## Modifying Models

Add or remove nodes programmatically

`Model.addNodeData` & `Model.removeNodeData` & `Model.copyNodeData`

`Model.findNodeDataForKey`

* It doesn't work to simply modify `Model.nodeDataArray`
  * __GoJS__ software will not be notified about any change to any JavaScript Array
* It doesn't work to simply modify a node data object
  * Any binding that depends on the property will not be notified
  * Call `Model.setDataProperty`

__When initializing a JavaScript Object as a new node data object, such calls are not necessary.__

---

## Saving and Loading Models

Write and read models as text in JSON format

* `Model.fromJson`
* `Model.toJson`

---

