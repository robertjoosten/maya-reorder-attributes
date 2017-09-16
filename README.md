# rjReorderAttr
Reorder attributes in Maya.

<p align="center"><img src="https://github.com/robertjoosten/rjReorderAttr/blob/master/README.png"></p>
<a href="https://vimeo.com/210495749" target="_blank"><p align="center">Click for video</p></a>

## Installation
Copy the **rjReorderAttr** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Add functionality to the Channel Box -> Edit menu in Maya:
```python
import maya.cmds as cmds
cmds.evalDeferred("import rjReorderAttr; rjReorderAttr.install()")
```

Display UI:
```python
import rjReorderAttr.ui
rjReorderAttr.ui.show()
```

## Note
If the install command is used a button called Reorder Attributes will be added to the Channel Box -> Edit menu. If this is not the case the ui can be opened with the show command. Drag and drop the attributes to reorder. Attributes are deleted in the new order and the undo commands is then ran to redo the attributes in the order prefered.

A thank you too Nick Hughes for showing me the power of the undo command and how it can be used to sort attributes.
