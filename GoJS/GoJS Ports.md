# GoJS - Ports

Created by : Mr Dk.

2019 / 03 / 05 23:37

Nanjing, Jiangsu, China

---

### About

Different logical and graphical places at which links should connect

*  The elements at which a link may connect are called __ports__
*  There may be any number of ports in a node
* By default there is just one port - the whole node

---

### Single Ports

You want to consider links logically related to the node as a whole but you don't want links
connecting to the whole node

Set `GraphObject.portId` to the empty string

* The name of the default port

---

### General Ports

In order for a link data object to distinguish which port the link should connect to

* `GraphLinksModel` supports two additional data properties
* Identify the names of the ports in the nodes at both ends of the link
* `GraphLinksModel.getToKeyForLinkData` identifies the node to connect to
* `GraphLinksModel.getToPortIdForLinkData` identifies the port within the node
* `GraphLinkModel.getFromKeyForLinkData`
* `GraphLinkModel.getFromPortIdForLinkData`

Normally a __GraphLinksModel__ assumes that there is no need to recognize port information on link data

* Set `GraphLinksModel.linkToPortIdProperty` and `GraphLinksModel.linkFromPortIdProperty` to support port identifiers on link data

---

### Drawing new Links

Set either or both `GraphObject.fromLinkable` and `GraphObject.toLinkable` properties to true allows users to __interactively__ draw new links between ports

* By default - 
  * The user may not draw more than one link in the same direction between any pair of ports
  * The user may not draw a link connecting a node with itself

Set `GraphObject.toMaxLinks` to `1`, the user may draw at most one link going into that port

Implement __Linking Validation__ to support more rules

---

