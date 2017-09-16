from maya import OpenMaya, OpenMayaUI, cmds
from . import utils 

# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4"):
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken

# ----------------------------------------------------------------------------

TITLE = "Reorder Attr"
CHANNELBOX = "ChannelBoxForm"

# ----------------------------------------------------------------------------

def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QMainWindow)
    
    return window  
    
# ----------------------------------------------------------------------------
    
def mayaToQT(name):
    """
    Maya -> QWidget

    :param str name: Maya name of an ui object
    :return: QWidget of parsed Maya name
    :rtype: QWidget
    """
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None:         
        ptr = OpenMayaUI.MQtUtil.findLayout(name)    
    if ptr is None:         
        ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:     
        return shiboken.wrapInstance(long(ptr), QWidget)
    
def qtToMaya(widget):
    """
    QWidget -> Maya name

    :param QWidget widget: QWidget of a maya ui object
    :return: Maya name of parsed QWidget
    :rtype: str
    """
    return OpenMayaUI.MQtUtil.fullName(
        long(
            shiboken.getCppPointer(widget)[0]
        ) 
    )
    
# ----------------------------------------------------------------------------

def getChannelBox():
    """
    Get ChannelBox, convert the main channel box to QT.

    :return: Maya's main channel box
    :rtype: QWidget
    """
    channelBox = mayaToQT(CHANNELBOX)
    return channelBox

def getChannelBoxMenu():
    """
    Get ChannelBox Menu, convert the main channel box to QT and return the 
    Edit QMenu which is part of the channel box' children.

    :return: Maya's main channel box menu
    :rtype: QMenu
    """
    channelBox = getChannelBox()
        
    # find widget
    menus = channelBox.findChildren(QMenu)

    # find Edit menu
    for menu in menus:
        if menu.menuAction().text() == "Edit":
            return menu
             
# ----------------------------------------------------------------------------

class AttributeItem(QListWidgetItem):
    def __init__(self, node, attr):
        QListWidgetItem.__init__(self)
    
        # variables
        self._node = node
        self._attr = attr
        
        # save modes
        self.modes = {
            "short":cmds.attributeQuery(attr, node=node, shortName=True),
            "nice":cmds.attributeQuery(attr, node=node, niceName=True),
            "long":cmds.attributeQuery(attr, node=node, longName=True),
        }

    # ------------------------------------------------------------------------
    
    @property
    def node(self):
        return self._node
        
    @property
    def attr(self):
        return self._attr
        
    # ------------------------------------------------------------------------
    
    @property
    def name(self):
        return "{0}.{1}".format(self.node, self.attr)
        
    # ------------------------------------------------------------------------
    
    def rename(self, mode):
        """
        Rename the attribute with the mode, the three possible modes and 
        correspoding names have been stored during the initializing of this 
        item.
        """
        text = self.modes.get(mode)
        self.setText(text)
        
    # ------------------------------------------------------------------------
        
    def delete(self):
        """
        Delete attribute, first set the lock stated of the attribute to false
        so the attribute can actually be deleted. These two functions are
        wrapped into one undo chunk for later undoing.
        """
        with utils.UndoContext():
            cmds.setAttr(self.name, lock=False)
            cmds.deleteAttr(self.name)
        
# ----------------------------------------------------------------------------
      
class AttributeDisplayWidget(QWidget):
    signal = Signal(str) 
    def __init__(self, parent=None, defaultName="Long"):
        QWidget.__init__(self, parent)
        
        # create channel name options
        layout = QHBoxLayout(self)
        
        label = QLabel(self)
        label.setText("Channel Names:")
        layout.addWidget(label)
        
        self.group = QButtonGroup(self)
        self.group.buttonReleased.connect(self.buttonReleased)
        
        # create radio buttons
        buttonNames = ["Long", "Short", "Nice"]
        for i, name in enumerate(buttonNames):
            rb = QRadioButton(self)
            rb.setText(name)
            
            layout.addWidget(rb)
            self.group.addButton(rb)
            
            # check default button
            if defaultName == name:
                rb.setChecked(True)
 
    # ------------------------------------------------------------------------
                
    def buttonReleased(self):
        """
        When the radio button selection is changed this command gets called,
        it will read the name of the selected button. This name will get lower
        cased and parsed into the signal that gets emitted.
        """
        button = self.group.checkedButton()
        text = button.text().lower()
        self.signal.emit(text)
        
class DropListWidget(QListWidget):
    signal = Signal() 
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        
    # ------------------------------------------------------------------------
    
    @property
    def attributes(self):
        """
        Get all attributes in the widget, this list is reversed as its needed
        to start the deletion process of the attributes in reverse.
        
        :return: List of attributes ( AttributeItem )
        :rtype: list
        """
        attrs = [self.item(i) for i in range(self.count())]
        attrs.reverse()
        return attrs
        
    # ------------------------------------------------------------------------
    
    def rename(self, mode):
        """
        Rename all attributes by setting the mode, this mode can be three 
        different things as have been initialized in the attribute item.
        
        :param str mode: Attribute name mode: "long", "short" or "nice".
        """
        for attribute in self.attributes:
            attribute.rename(mode)
            
    # ------------------------------------------------------------------------
    
    def update(self, node, mode):
        """
        Based on the input the widget gets updated with a list of the user 
        defined attributes of the parsed nodes. The attributes display name
        depends on the mode.
        
        :param str node: Node of which to query user defined attributes
        :param str mode: Attribute name mode: "long", "short" or "nice".
        """
        # clear
        self.clear()
        
        if not node:
            return
            
        # get user defined attributes
        attrs = cmds.listAttr(node, ud=True) or []
        
        # add attributes to list widget
        for attr in attrs:
            item = AttributeItem(node, attr)
            item.rename(mode)
            
            self.addItem(item)

        QListWidget.update(self)
                
    def dropEvent(self, event):
        QListWidget.dropEvent(self, event)
        self.signal.emit()
        
# ----------------------------------------------------------------------------

class ReorderAttributesWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        # variables
        self._id = None
        self.node = None
        self.mode = "long"
 
        # set ui
        self.setParent(parent)        
        self.setWindowFlags(Qt.Window)  

        self.setWindowTitle(self.title)      
        self.setWindowIcon(QIcon(":/attributes.png"))           
        self.resize(300, 500)

        # create layout
        layout = QVBoxLayout(self)
        
        # create attribute display widget
        name = AttributeDisplayWidget(self)
        layout.addWidget(name)
        
        # create attribute widget
        self.widget = DropListWidget(self)
        self.widget.setDragDropMode(
            QAbstractItemView.InternalMove
        )
        layout.addWidget(self.widget)
        
        # connect signals
        name.signal.connect(self.widget.rename)
        self.widget.signal.connect(self.reorder)

        # update
        self.update()
        self.addCallback()
        
    # ------------------------------------------------------------------------
    
    @property
    def title(self):
        """
        The title of the window, this title differs based on the selection.
        If no node is active, the default title will be returned. If a node is
        active, the full path will be stripped into a base name and appened
        to the default title.
        
        :return: Window title
        :rtype: str
        """
        if not self.node:
            return TITLE
            
        name = self.node.split("|")[-1]
        return "{0} - {1}".format(TITLE, name) 

    # ------------------------------------------------------------------------
    
    def isReferenced(self):
        """
        Check if the node selected is referenced, reordering of attributes is
        not supported on referenced objects.
        
        :return: Referenced state of self.node
        :rtype: bool
        """
        if self.node and cmds.referenceQuery(self.node, inr=True):
            return True
        return False
         
    # ------------------------------------------------------------------------

    def update(self, *args):
        """
        Update function gets ran every time the selection is changed. The 
        latest selected node will be queried. The list widget updated with the
        attributes of that node. The UI is disabled of the node selected is
        referenced.
        """
        # get latest selected node
        self.node = utils.getLastSelectedNode()
        
        # update widget
        self.widget.update(self.node, self.mode)
        
        # update title
        self.setWindowTitle(self.title) 

        # disable ui if referenced
        referenced = self.isReferenced()
        self.widget.setEnabled(not referenced)
        
        QWidget.update(self)
       
    # ------------------------------------------------------------------------
            
    def reorder(self):
        """
        Reorder all of the attributes based on the new attribute list. All of
        the attributes in the list are deleted, they are deleted in such an 
        order that when all of the deletion are undone. The attribute order
        is changed to what the input of the user.
        """
        with utils.UndoState():
            for attr in self.widget.attributes:
                attr.delete()
                
            for _ in range(self.widget.count()):
                cmds.undo()
            
    # ------------------------------------------------------------------------
    
    def addCallback(self):
        """
        Register a callback to run the update function every time the
        selection list is modified.
        """
        self._id = OpenMaya.MModelMessage.addCallback(
            OpenMaya.MModelMessage.kActiveListModified, 
            self.update
        )
        
    def removeCallback(self):
        """
        Remove the callback that updates the ui every time the selection
        list is modified.
        """
        OpenMaya.MMessage.removeCallback(self._id)
    
    # ------------------------------------------------------------------------
            
    def closeEvent(self, event):
        """
        Subclass the closeEvent function to first remove the callback, 
        this callback shouldn't be floating around and should be deleted
        with the widget.
        """
        self.removeCallback()
        QWidget.closeEvent(self, event)

# ----------------------------------------------------------------------------
        
def show(*args):
    reorder = ReorderAttributesWidget(mayaWindow())
    reorder.show()
