# GoJS - Link Points

Created by : Mr Dk.

2019 / 03 / 05 23:13

Nanjing, Jiangsu, China

---

### About

There is flexibility in controlling exactly how and where a link connects to a node

* In the previous examples the link has always ended at the edge of the node
* But you can specify the __Spot__ on a node at which a link terminates

---

### Non-rectangular Nodes

When a __Node__ does not have a rectangular shape

* By default links will end where the line toward the center of the node intersects with the edge of the node

---

### ToSpot and FromSpot

Easily require links to end at a particular point within the bounds of the node

* Set `GraphObject.toSpot` to a Spot value to cause links coming into the node to end at that spot within the node
* Set `GraphObject.fromSpot` for the ends of links coming out of the node

`Spot.Right` / `Spot.Left` / `Spot.RightSide` / `Spot.leftSide`

`Spot.Top` / `Spot.Bottom`

---

### Undirected Spots

---

### Spots for Individual Links

Setting `Link.fromSpot` and `Link.toSpot` properties

---

### Some Layouts set Link Spots

Some of the predefined __Layouts__ automatically set `Link.fromSpot` and `Link.toSpot` when the nature of the layout implies a natural direction

---

