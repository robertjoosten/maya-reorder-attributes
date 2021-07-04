from maya import cmds
from maya.api import OpenMaya
from PySide2 import QtWidgets, QtGui, QtCore

from reorder_attributes import widgets
from reorder_attributes import utils


WINDOW_TITLE = "Reorder Attributes"


class ReorderAttributesWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ReorderAttributesWidget, self).__init__(parent)

        # variables
        self.callback = None
        self.node = None
        scale_factor = self.logicalDpiX() / 96.0

        self.setParent(parent)        
        self.setWindowFlags(QtCore.Qt.Window)

        self.setWindowTitle(self.title)      
        self.setWindowIcon(QtGui.QIcon(":/attributes.png"))
        self.resize(300 * scale_factor, 500 * scale_factor)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # create attribute display widget
        self.mode = widgets.AttributeModeWidget(self)
        layout.addWidget(self.mode)
        
        # create attribute widget
        self.container = widgets.AttributeListWidget(self)
        layout.addWidget(self.container)
        
        # connect signals
        self.mode.mode_changed.connect(self.container.set_mode)
        self.container.data_changed.connect(self.reorder)

        # update
        self.refresh()
        self.register_callback()
        
    # ------------------------------------------------------------------------
    
    @property
    def title(self):
        """
        The title of the window, this title differs based on the selection.
        If no node is active, the default title will be returned. If a node is
        active, the full path will be stripped into a base name and appended
        to the default title.
        
        :return: Window title
        :rtype: str
        """
        if not self.node:
            return WINDOW_TITLE
            
        node_name = self.node.split("|")[-1]
        return "{} - {}".format(WINDOW_TITLE, node_name)

    @property
    def is_referenced(self):
        """
        Check if the node selected is referenced, reordering of attributes is
        not supported on referenced objects.
        
        :return: Referenced state of self.node
        :rtype: bool
        """
        return self.node and cmds.referenceQuery(self.node, isNodeReferenced=True)

    # ------------------------------------------------------------------------

    def register_callback(self):
        """
        Register a callback to run the update function every time the
        selection list is modified.
        """
        self.callback = OpenMaya.MModelMessage.addCallback(
            OpenMaya.MModelMessage.kActiveListModified, 
            self.refresh
        )
        
    def remove_callback(self):
        """
        Remove the callback that updates the ui every time the selection
        list is modified.
        """
        if self.callback is not None:
            OpenMaya.MMessage.removeCallback(self.callback)
    
    # ------------------------------------------------------------------------
            
    def closeEvent(self, event):
        """
        Subclass the closeEvent function to first remove the callback, 
        this callback shouldn't be floating around and should be deleted
        with the widget.
        """
        self.remove_callback()
        super(ReorderAttributesWidget, self).closeEvent(event)

    # ------------------------------------------------------------------------

    def reorder(self):
        """
        Reorder all of the attributes based on the new attribute list. All of
        the attributes in the list are deleted, they are deleted in such an
        order that when all of the deletion are undone. The attribute order
        is changed to what the input of the user.
        """
        with utils.UndoStateContext():
            for attribute in reversed(self.container.attributes):
                attribute.delete()

            for _ in range(self.container.count()):
                cmds.undo()

    def refresh(self, *args):
        """
        Update function gets ran every time the selection is changed. The
        latest selected node will be queried. The list widget updated with the
        attributes of that node. The UI is disabled of the node selected is
        referenced.
        """
        self.node = utils.get_last_selected_path()
        self.container.setEnabled(not self.is_referenced)
        self.container.refresh(self.node, self.mode.mode)
        self.setWindowTitle(self.title)


def show():
    parent = utils.get_main_window()
    reorder = ReorderAttributesWidget(parent)
    reorder.show()
