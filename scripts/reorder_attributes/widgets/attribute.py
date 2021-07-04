from maya import cmds
from PySide2 import QtWidgets, QtCore

from reorder_attributes import utils


__all__ = [
    "AttributeItem",
    "AttributeModeWidget",
    "AttributeListWidget",
]

MODES = ["long", "short", "nice"]


class AttributeItem(QtWidgets.QListWidgetItem):
    def __init__(self, node, attr):
        super(AttributeItem, self).__init__()

        self.node = node
        self.attribute = attr
        self.modes = {
            mode: cmds.attributeQuery(attr, node=node, **{"{}Name".format(mode): True})
            for mode in MODES
        }

    # ------------------------------------------------------------------------

    @property
    def path(self):
        """
        :return: Path to attribute
        :rtype: str
        """
        return "{}.{}".format(self.node, self.attribute)

    # ------------------------------------------------------------------------

    def set_mode(self, mode):
        """
        Rename the attribute with the mode, the three possible modes and
        corresponding names have been stored during the initializing of this
        item.

        :param str mode:
        :raise ValueError: When mode is not valid.
        """
        if mode not in self.modes:
            raise ValueError("Provided mode '{}' is not valid, options "
                             "are {}.".format(mode, list(self.modes.keys())))

        text = self.modes[mode]
        self.setText(text)

    def delete(self):
        """
        Delete attribute, first set the lock stated of the attribute to false
        so the attribute can actually be deleted. These two functions are
        wrapped into one undo chunk for later undoing.
        """
        with utils.UndoChunkContext():
            cmds.setAttr(self.path, lock=False)
            cmds.deleteAttr(self.path)


class AttributeModeWidget(QtWidgets.QWidget):
    mode_changed = QtCore.Signal(str)

    def __init__(self, parent, default="long"):
        super(AttributeModeWidget, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create label
        label = QtWidgets.QLabel(self)
        label.setText("Channel Names:")
        layout.addWidget(label)

        # create group
        self.group = QtWidgets.QButtonGroup(self)
        self.group.buttonReleased.connect(self._emit_mode_changed)

        for i, mode in enumerate(MODES):
            button = QtWidgets.QRadioButton(self)
            button.setText(mode.capitalize())

            layout.addWidget(button)
            self.group.addButton(button)

            if mode == default:
                button.setChecked(True)

    # ------------------------------------------------------------------------

    @property
    def mode(self):
        """
        :return: Mode
        :rtype: str
        """
        button = self.group.checkedButton()
        return button.text().lower()

    def _emit_mode_changed(self):
        """
        When the radio button selection is changed this command gets called,
        it will read the name of the selected button. This name will get lower
        cased and parsed into the signal that gets emitted.
        """
        self.mode_changed.emit(self.mode)


class AttributeListWidget(QtWidgets.QListWidget):
    data_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(AttributeListWidget, self).__init__(parent)

        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # create context menu
        order = QtWidgets.QAction(self)
        order.setText("Order Alphabetically")
        order.triggered.connect(self.sortItems)
        self.addAction(order)

    # ------------------------------------------------------------------------

    @property
    def attributes(self):
        """
        :return: Attributs
        :rtype: list[AttributeItem]
        """
        return [self.item(i) for i in range(self.count())]

    # ------------------------------------------------------------------------

    def set_mode(self, mode):
        """
        Rename all attributes by setting the mode, this mode can be three
        different things as have been initialized in the attribute item.

        :param str mode:
        """
        for attribute in self.attributes:
            attribute.set_mode(mode)

    # ------------------------------------------------------------------------

    def dropEvent(self, event):
        super(AttributeListWidget, self).dropEvent(event)
        self.data_changed.emit()

    def sortItems(self):
        super(AttributeListWidget, self).sortItems()
        self.data_changed.emit()

    # ------------------------------------------------------------------------

    def refresh(self, node, mode):
        """
        Based on the input the widget gets updated with a list of the user
        defined attributes of the parsed nodes. The attributes display name
        depends on the mode.

        :param str node:
        :param str mode:
        """
        self.clear()

        if not node:
            return

        for attribute in cmds.listAttr(node, userDefined=True) or []:
            item = AttributeItem(node, attribute)
            item.set_mode(mode)

            self.addItem(item)
