"""					
I N S T A L L A T I O N:
    Copy the "rjReorderAttr" folder to your Maya scripts directory:
        C:\Users\<USER>\Documents\maya\scripts

U S A G E:
    Add functionality to the Channel Box -> Edit menu in Maya:
        import maya.cmds as cmds
        cmds.evalDeferred("import rjReorderAttr; rjReorderAttr.install()")
    
    Display UI:  
        import rjReorderAttr.ui 
        rjReorderAttr.ui.show()

N O T E:
    If the install command is used a button called Reorder Attributes will be
    added to the Channel Box -> Edit menu. If this is not the case the ui can
    be opened with the show command. Drag and drop the attributes to reorder.
    Attributes are deleted in the new order and the undo commands is then ran
    to redo the attributes in the order prefered.

    A thank you too Nick Hughes for showing me the power of the undo command 
    and how it can be used to sort attributes.
"""

from maya import cmds, mel
from . import ui

__author__    = "Robert Joosten"
__version__   = "0.9.2"
__email__     = "rwm.joosten@gmail.com"

# ----------------------------------------------------------------------------

DIVIDER_NAME = "reorderAttrDivider"
BUTTON_NAME = "reorderAttrButton"

# ----------------------------------------------------------------------------

def install():
    """
    Add two additional buttons to the Channel Box -> Edit menu, a divider and 
    a button to open up the attribute reordering ui. The edit menu is 
    retrieved from the channel box form and a mel command is ran to populate
    this menu in case it hasn't been opened before. If rjReorderAttr is 
    already installed the original buttons will be removed and new ones 
    created.
    """
    # get edit menu of channel box
    menu = ui.getChannelBoxMenu()
    menu = ui.qtToMaya(menu)
    
    # generate channel box edit menu
    mel.eval("generateCBEditMenu {0} 0;".format(menu))
    
    # get all members
    children = cmds.menu(menu, query=True, itemArray=True)
    
    # remove existing members
    for name in [DIVIDER_NAME, BUTTON_NAME]:
        if not name in children:
            continue
            
        cmds.deleteUI(name)
 
    # add divider
    cmds.menuItem(
        DIVIDER_NAME,
        divider=True, 
        p=menu
    )

    # add button
    cmds.menuItem(
        BUTTON_NAME,
        label="Reorder Attributes", 
        p=menu, 
        command=ui.show
    )
    
    print "Reorder Attributes: installation succeeded"

