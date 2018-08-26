"""		
Reorder attributes in Maya.

.. figure:: /_images/reorderAttributesExample.png
   :align: center
   
`Link to Video <https://vimeo.com/210495749>`_

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the reorderAttributes.mel file in Maya to permanently install the script.

Note
====
A button called Reorder Attributes will be added to the Channel Box ->
Edit menu. Clicking this button will open up an ui that will allow the user to
drag and drop the attributes to reorder. Attributes are deleted in the new
order and the undo commands is then ran to redo the attributes in the order
preferred.

A thank you too Nick Hughes for showing me the power of the undo command 
and how it can be used to sort attributes.
"""
from .ui import install

__author__    = "Robert Joosten"
__version__   = "0.9.4"
__email__     = "rwm.joosten@gmail.com"
