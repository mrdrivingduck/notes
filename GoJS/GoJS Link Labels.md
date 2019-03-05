# GoJS - Link Labels

Created by : Mr Dk.

2019 / 03 / 05 22:44

Nanjing, Jiangsu, China

---

### About

It is common to add annotations or decorations on a link, particularly text

---

### Simple Link Labels

Add a __GraphObject__ to a __Link__

* It will be positioned at the middle of the link
* Clicking on the text label results in selection of the whole Link

---

### Link label segmentIndex and segmentFraction

`GraphObject.segmentIndex` specifies which segment of the link route the obj should be on

`GraphObject.segmentFraction` controls how far the obj should be `(0, 1)`

---

### Link label segmentOffset and alignmentFocus

`GraphObject.segmentOffset` controls where to position the obj relative to the point on a link segment

`GraphObject.alignmentFocus` changes the spot in the obj that is being positioned relative to the link segment point

---

### Link label segmentOrientation

`GraphObject.segmentOrientation` controls the angle of the label obj relative to the angle of the link segment

* default - `Link.None`
* `Link.OrientAlong` - have the object always rotated at the same angle as the link segment
* `Link.OrientUpright` is alike - but is often used when there is text in the label

---

### Link labels near the ends

Set the `GraphObject.segmentOffset` to Point `(NaN, NaN)`

* Cause the offset to be half the width and half the height of the label object

---

### Arrowheads

Arrowheads are just labels - __Shapes__ that are initialized in a convenient manner

---

