import shiboken2
from six import integer_types
from maya import mel
from maya import cmds
from maya import OpenMayaUI
from maya.api import OpenMaya
from PySide2 import QtWidgets, QtCore


CHANNEL_BOX = "ChannelBoxForm"


def get_last_selected_path():
    """
    Query the current selection with the Maya API and return the last item on
    the selection list. The reason the API has to be used is that there is a
    delay with cmds, not returning the right node. This function gets called
    as a result of a OpenMaya.MModelMessage.kActiveListModified callback.

    :return: Full path of latest selected object.
    :rtype: str/None
    """
    selection = OpenMaya.MGlobal.getActiveSelectionList()

    if not selection.length():
        return

    node = selection.getDependNode(selection.length() - 1)
    if node.hasFn(OpenMaya.MFn.kDagNode):
        dag = OpenMaya.MDagPath.getAPathTo(node)
        return dag.fullPathName()
    else:
        dep = OpenMaya.MFnDependencyNode(node)
        return dep.name()


# ----------------------------------------------------------------------------


def maya_to_qt(name, type_=QtWidgets.QWidget):
    """
    :param str name: Maya path of an ui object
    :param cls type_:
    :return: QWidget of parsed Maya path
    :rtype: QWidget
    :raise RuntimeError: When no handle could be obtained
    """
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:
        ptr = integer_types[-1](ptr)
        return shiboken2.wrapInstance(ptr, type_)

    raise RuntimeError("Failed to obtain a handle to '{}'.".format(name))


def qt_to_maya(widget):
    """
    :param QWidget widget: QWidget of a maya ui object
    :return: Maya path of parsed QWidget
    :rtype: str
    """
    ptr = shiboken2.getCppPointer(widget)[0]
    ptr = integer_types[-1](ptr)
    return OpenMayaUI.MQtUtil.fullName(ptr)


# ----------------------------------------------------------------------------


def get_main_window():
    """
    :return: Maya main window
    :raise RuntimeError: When the main window cannot be obtained.
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    ptr = integer_types[-1](ptr)
    if ptr:
        return shiboken2.wrapInstance(ptr, QtWidgets.QMainWindow)

    raise RuntimeError("Failed to obtain a handle on the Maya main window.")


def get_channel_box():
    """
    :return: Maya's main channel box
    :rtype: QtWidget.QWidget
    """
    channel_box = maya_to_qt(CHANNEL_BOX)
    return channel_box


def get_channel_box_menu():
    """
    :return: Maya's main channel box menu
    :rtype: QtWidgets.QMenu
    :raise RuntimeError: When menu cannot be found.
    """
    channel_box = get_channel_box()
    channel_box_menus = channel_box.findChildren(QtWidgets.QMenu)

    for menu in channel_box_menus:
        if menu.menuAction().text() == "Edit":
            return menu

    raise RuntimeError("No edit menu found in channel box widget.")


# ----------------------------------------------------------------------------


class UndoStateContext(object):
    """
    The undo state is used to force undo commands to be registered when this
    tool is being used. Once the "with" statement is being exited, the default
    settings are restored.
    
    with UndoStateContext():
        # code
    """
    def __init__(self):
        self.state = cmds.undoInfo(query=True, state=True)
        self.infinity = cmds.undoInfo(query=True, infinity=True)
        self.length = cmds.undoInfo(query=True, length=True)

    def __enter__(self):
        cmds.undoInfo(state=True, infinity=True)
        
    def __exit__(self, *exc_info):
        cmds.undoInfo(
            state=self.state, 
            infinity=self.infinity, 
            length=self.length
        )


class UndoChunkContext(object):
    """
    The undo context is used to combine a chain of commands into one undo.
    Can be used in combination with the "with" statement.
    
    with UndoChunkContext():
        # code
    """
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        
    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)
