# GoJS - Links

Created by : Mr Dk.

2019 / 03 / 05 16:35

Nanjing, Jiangsu, China

---

### About

Use the __Link__ to implement a visual relationship between nodes

---

### Creating Links

Links are created by the presence of link data objects

* in the `GraphLinksModel.linkDataArray`
* by a parent key reference as the value of the `TreeModel.nodeParentKeyProperty`

Create new links programmatically by modifying the model

* Calling `GraphLinksModel.addLinkData`
* Calling `TreeModel.setParentKeyForNodeData`
* `LinkingTool.insertLink`

---

### Non-directional Links

Those without arrowheads to indicate a visual direction

---

### Arrowheads

Many links do want to indicate directionality by using arrowheads

Just add a Shape and set its `Shape.toArrow` property

* Many predefined arrowhead types

---

### Routing

Customize the path that each __Link__ takes, you need to set properties on the link

* The property that has the most general effect on the points that the link's route follows is `Link.routing`
  * `Link.Normal`
  * `Link.Orthogonal`
  * `Link.AvoidsNodes`

---

### End Segment Lengths

Determine the length of the very first segment or the very last segment

* Only for orthogonally routed links
* `GraphObject.fromEndSegmentLength`
* `GraphObject.toEndSegmentLength`

---

### Curve, Curviness, Corner

Once the `Link.routing` determines the route (i.e., the sequence of points) that the link takes, other properties control the details of how the link shape gets its path geometry - 

* `Link.curve` - controls whether the link shape has basically straight segments
  or is a big curve
  * `Link.None` - default - straight
  * `Link.Bezier` - naturally curved path for the link shape
  * `Link.JumpOver` - causes little "hops" in the path of an orthogonal link that crosses another orthogonal link that also has a `JumpOver` curve
  * `Link.JumpGap` - causes little "gaps" in the path of an orthogonal link that crosses another orthogonal link that also has a `JumpGap` curve
* `Link.curviness` - control how curved it is
  * If there are multiple links, it will automatically compute reasonable values for the curviness of each link, unless you assign `Link.curviness` explicitly
* Another kind of curviness comes from rounded corners when the `Link.routing` is `Orthogonal` or `AvoidsNodes`

---

### Easier Clicking on Links

Set the `Shape.strokeWidth` to a larger value, such as 8, but  may not want that appearance

The solution - add a thick path Shape but not have it draw anything

* If you want to keep the original path Shape, *both* Shapes need to be declared as the "main" element for the Link by setting `GraphObject.isPanelMain` to true

The transparent shape can also be used for highlighting purposes

* e.g. to implement the effect of highlighting the link when the mouse passes over it

---

### Short Lengths

---

### Disconnected Links

__GoJS__ does support the creation and manipulation of links that have either or both of
the `Link.fromNode` and `Link.toNode` properties with null values

* Provide a route by setting or binding `Link.points· to a list of two or more Points
* creation or reconnection of links that connect with "nothing" is permitted if set `LinkingBaseTool.isUnconnectedLinkValid` to true
* Links can be dragged if set `DraggingTool.dragsLink` to true

---

