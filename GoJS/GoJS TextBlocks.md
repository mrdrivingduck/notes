# GoJS - TextBlocks

Created by : Mr Dk.

2019 / 03 / 05 09:52

Nanjing, Jiangsu, China

---

### About

__TextBlocks__ inherits from __GraphObject__, is used to display text

---

### Text

`TextBlock.text` is the only way to show a text string

---

### Fonts and Colors

`TextBlock.font` specifies the size and stylistic appearance of the text

* The value may be any CSS font specifier string

`TextBlock.stroke` draws the text

* The value may be any CSS color or a __Brush__

`GraphObject.background` specifies the brush to use as the background

* Default - no background (transparent)
* The background is always rectangular

---

### Sizing and Clipping

The natural size of a TextBlock is just big enough to render the text string with the given font

* Larger dimensions result in areas with no text
* Smaller dimensions result in clipping

---

### Max Lines and Overflow

`GraphObject.desiredSize` constrains the TextBlock's available size

* `width` & `height`

`TextBlock.maxLines` limit the vertical height (the number of lines allowed)

`TextBlock.overflow` decides how to use the remaining space

---

### Wrapping

`TextBlock.wrap`

* There must be some constraint on the width to be narrower than it would naturally be

---

### Text Alignment

`TextBlock.textAlign` specifies where to draw the characters horizontally.

`TextBlock.verticalAlignment` controls the vertical alignment

* The value must be a CSS string
* Neither of them affect the sizing of the TextBlock

`GraphObject.alignment` controls where to place the object within the area allocated by the parent Panel

---

### Flipping

`TextBlock.flip` flips the text horizontally and vertically

---

### Editing

`TextBlock.editable` support the in-place editing of text by user

`TextBlock.textValidation` & `TextBlock.textEditor` validate the user's input

---

