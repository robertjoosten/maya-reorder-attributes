import logging
from maya import mel
from PySide2 import QtWidgets, QtGui

from reorder_attributes import ui
from reorder_attributes import utils


log = logging.getLogger(__name__)
BUTTON_TEXT = "Reorder Attributes"


def execute():
    """
    Add the reorder attributes button to the channel box menu, this button
    will launch the reorder tool.

    :raises RuntimeError: When the reorder attributes is already installed.
    """
    # get menu
    menu = utils.get_channel_box_menu()
    menu_path = utils.qt_to_maya(menu)
    mel.eval("generateCBEditMenu {0} 0;".format(menu_path))

    # validate install
    menu = utils.maya_to_qt(menu_path, QtWidgets.QMenu)  # preserve internal pointer
    for action in menu.actions():
        if not action.isSeparator():
            if action.text() == BUTTON_TEXT:
                raise RuntimeError("reorder-attributes has already been installed.")

    # add actions
    menu.addSeparator()
    icon = QtGui.QIcon(":/attributes.png")
    action = menu.addAction(icon, BUTTON_TEXT)
    action.triggered.connect(ui.show)

    log.info("reorder-attributes installed successfully.")
