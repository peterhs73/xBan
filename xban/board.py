#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtCore import Qt, Signal, QMimeData, QSize
from PySide2.QtGui import QTextCursor, QDrag, QKeySequence, QColor
from PySide2.QtWidgets import (
    QWidget,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QLineEdit,
    QMenu,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QFrame,
    QStyledItemDelegate,
    QScrollBar,
    QWidgetAction,
    QLabel,
)

from xban.utils import BanButton
from xban.style import TILE_STYLE, MENU_STYLE
from functools import partial
from xban.io import save_yaml
import logging

gui_logger = logging.getLogger("xban-board")


class BanBoard(QWidget):
    """The main board of xBan"""

    def __init__(self, filepath, file_config, parent=None):
        super().__init__(parent)

        self.filepath = filepath
        self.file_config = file_config

        self.draw_board(file_config)
        self.setAcceptDrops(True)

        gui_logger.info("Main xban board created")

    def draw_board(self, file_config):
        """Initiate UI

        The UI consists of 2 parts, top is the board title and info
        and button is the subbords with tiles in each ones
        the subboard is drawn based on file_configuration
        """
        config, content = file_config

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(20, 20, 20, 20)

        title_edit = QLineEdit(
            config["xban_config"]["title"],
            objectName="windowEdit_title",
            parent=self,
        )
        title_edit.setPlaceholderText("Enter title here ...")

        info_edit = NoteTile(
            config["xban_config"]["description"], "windowEdit_text", self
        )
        info_edit.setPlaceholderText("Enter description here ...")

        mainlayout.addWidget(title_edit)
        mainlayout.addWidget(info_edit)

        self.sublayout = QHBoxLayout()
        color = config["xban_config"]["board_color"]
        self.sublayout.setMargin(10)
        self.sublayout.setSpacing(20)

        add_btn = BanButton(
            "+",
            clicked=self.insert_board,
            toolTip="add board",
            objectName="windowBtn_add",
        )
        shadow = QGraphicsDropShadowEffect(
            self, blurRadius=10, offset=5, color=QColor("lightgrey")
        )
        add_btn.setGraphicsEffect(shadow)
        self.sublayout.addWidget(add_btn)

        mainlayout.addLayout(self.sublayout)
        self.setLayout(mainlayout)

        for i, tile_contents in enumerate(content.items()):
            # insert the boards
            self.insert_board(tile_contents, color[i])

    def insert_board(self, content=("", ()), color="black"):
        """Insert a board into the layout"""
        new_board = SubBoard(content, color, self)
        new_board.delBoardSig.connect(partial(self.delete_board, new_board))
        new_board.listwidget.itemSelectionChanged.connect(
            partial(self.single_selection, new_board.listwidget)
        )
        # insert second to last
        self.sublayout.insertWidget(self.sublayout.count() - 1, new_board)

    def delete_board(self, board):
        """Delete the board"""

        self.sublayout.removeWidget(board)
        board.deleteLater()

    def parse_board(self):
        """Parse the board to the correct yaml files

        Note this function will rewrite the file
        """
        color = []
        content = {}
        title = self.layout().itemAt(0).widget().text()
        description = self.layout().itemAt(1).widget().toPlainText()
        sublayout = self.layout().itemAt(2)
        # exclude the plus button
        for i in range(sublayout.count() - 1):
            subboard = sublayout.itemAt(i).widget()
            color.append(subboard.color)
            sub_content = subboard.parse()
            content.update({sub_content[0]: sub_content[1]})
        config = {
            "xban_config": {
                "title": title,
                "description": description,
                "board_color": color,
            }
        }
        return [config, content]

    def get_index(self, pos):
        """Get index of the subboard layout based on the mouse position"""

        sublayout = self.layout().itemAt(2)
        for i in range(sublayout.count()):
            if sublayout.itemAt(i).geometry().contains(pos):
                return i
        return -1

    def dragEnterEvent(self, event):
        """Drag enter event

        Only accept the drag event when the moving widget is SubBoard instance
        The accepted drap event will proceed to dropEvent

        mouseMoveEvent needs to be defined for the child class
        """

        if isinstance(event.source(), SubBoard):
            event.accept()

    def dropEvent(self, event):
        """Drop Event

        When the widget is dropped, determine the current layout index
        of the cursor and insert widget in the layout

        Note the last widget of the layout is the plus button, hence
        never insert at the end
        """

        position = event.pos()
        widget = event.source()

        sublayout = self.layout().itemAt(2)
        index_new = self.get_index(position)
        if index_new >= 0:
            index = min(index_new, sublayout.count() - 1)
            sublayout.insertWidget(index, widget)
        event.setDropAction(Qt.MoveAction)
        event.accept()

    def save_board(self):
        """Save the board to yaml file"""

        xban_content = self.parse_board()
        save_yaml(self.filepath, xban_content)
        gui_logger.info(f"Saved to {self.filepath}")

    def single_selection(self, selected_board):
        """ensure that only single tile from a board is selected

        This is achieved by emit and received every time there
        is a selection made. The has selection check makes sure
        that it does not go into a recursion, since clear
        selection also triggers the signal
        """

        if selected_board.selectionModel().hasSelection():
            for i in range(self.sublayout.count() - 1):
                subboard = self.sublayout.itemAt(i).widget().listwidget

                if subboard is not selected_board:
                    subboard.clearSelection()


class SubBoard(QFrame):
    """The subboard of xBan

    The board contains the individual "blocks" of the board
    delBoardSig is trigger when the board is deleted
    """

    delBoardSig = Signal()

    def __init__(self, tile_contents, color, parent=None):
        super().__init__(parent)
        title_name, tile_items = tile_contents
        self.color = color
        self.setObjectName("subBoardFrame")

        shadow = QGraphicsDropShadowEffect(
            self, blurRadius=10, offset=5, color=QColor("lightgrey")
        )
        self.setGraphicsEffect(shadow)

        board = QVBoxLayout()
        board.setMargin(20)
        tile_title = NoteTile(title_name, "boardEdit", self)
        tile_title.setPlaceholderText("Title here ...")

        board.addWidget(tile_title)

        self.listwidget = BanListWidget(self)
        self.listwidget.setStyleSheet(TILE_STYLE.get(color, "black"))
        for tile in tile_items:
            self.listwidget.add_item(tile)

        board.addWidget(self.listwidget)

        btn_layout = QHBoxLayout()
        add_btn = BanButton(
            "+",
            clicked=self.add_listitem,
            toolTip="add tile",
            objectName="boardBtn",
        )
        del_btn = BanButton(
            "-",
            clicked=self.del_listitem,
            toolTip="delete tile",
            objectName="boardBtn",
            shortcut=QKeySequence(Qt.Key_Backspace),
        )
        color_btn = BanButton(
            "\u2261",
            toolTip="change color",
            objectName="boardBtn_color",
            color=[("white", "#bdbdbd"), ("grey", "white")],
        )

        self.color_menu = self.context_menu()
        color_btn.setMenu(self.color_menu)
        color_btn.sizeSig.connect(self.menu_resize)

        destory_btn = BanButton(
            "\u00D7",
            clicked=self.delete_board,
            toolTip="delete board",
            objectName="boardBtn_des",
            color=[("white", "tomato"), ("white", "red")],
        )

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)

        btn_layout.addWidget(color_btn)
        btn_layout.addWidget(destory_btn)
        board.addLayout(btn_layout)

        self.setLayout(board)

    def parse(self):
        """Parse the subboard content into a content list

        In the board layout, the first item is the title widget
        and the second is the list widget
        """
        board = self.layout()
        title = board.itemAt(0).widget().toPlainText()

        tile_items = [
            self.listwidget.item(i).text()
            for i in range(self.listwidget.count())
        ]
        return title, tile_items

    def add_listitem(self):
        """Add entry for listwidget"""

        self.listwidget.add_item("")
        # set the current row the new item
        self.listwidget.clearSelection()
        self.listwidget.setCurrentRow(self.listwidget.count() - 1)

    def del_listitem(self):
        """Delete entry for listwidget"""

        for item in self.listwidget.selectedItems():
            self.listwidget.del_item(item)

    def mouseMoveEvent(self, event):
        """event call when mouse movement (press and move) detected

        This is the core of the drag and drop for the element.
        The QDrag object will create a the pixel image of the widget
        HopSpot is set so that it remains where the grab point is
        """

        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            widget_image = self.grab()
            mimedata = QMimeData()
            drag.setMimeData(mimedata)
            drag.setPixmap(widget_image)
            drag.setHotSpot(event.pos() - self.rect().topLeft())
            drag.exec_()

        super().mouseMoveEvent(event)

    def context_menu(self):
        """Add context menu triggered by right click

        The two purpose is to delete the column
        and change tile color
        """

        menu = QMenu(self)

        for color_name in TILE_STYLE:
            label = QLabel(color_name, self)

            label.setStyleSheet(MENU_STYLE[color_name])
            action = QWidgetAction(self)
            action.setDefaultWidget(label)
            action.triggered.connect(
                partial(self.color_change, color=color_name)
            )
            menu.addAction(action)

        return menu

    def menu_resize(self, size):
        """Resize the menu to the same width of the button if possible

        A signal is emitted when the button is pressed, and the resize
        function is triggered.
        """
        self.color_menu.setMinimumWidth(size.width())

    def color_change(self, color):
        """Change the color of the tiles"""
        self.color = color
        self.layout().itemAt(1).widget().setStyleSheet(TILE_STYLE[color])

    def delete_board(self):
        """Send a confirm message to delete the board"""
        reply = QMessageBox.question(
            self,
            "Delete Board",
            "Confirm to delete the sub-board (cannot be reversed)",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )

        if reply == QMessageBox.Yes:
            self.delBoardSig.emit()


class BanListWidget(QListWidget):
    """Initiate individual note blocks (one layer up from note tiles)

    In order to display full individual note tiles without cropping,
    the list view needs to update its size when the individual note
    change; and the individual note needs to resize while the listview
    widget changes size. This results in two signal-slot: when the
    listview changes size, it emits widthChangeSig, which connects to
    NoteTile.adjust that adjust the width of the note. While notetile
    changes width (or height due to added text) resizeSig is emitted and
    connects to the BanBlock widget, which change the listwidgetitem's
    sizeHint().
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(TileDelegate(self))
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setWordWrap(True)
        self.setAcceptDrops(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setTextElideMode(Qt.ElideNone)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    def dropEvent(self, event):
        """Drop and drag event

        This is the main function on drop and drop
        if the source is not self, meaning the item is moved from
        another widget, need to delete the original item. This can
        only be done by finding the item row and delete the whole row

        The issue of listwidget is that after the drop event, the
        new list item is newly created and no longer shares the proper
        flags. I have found no setting to make item editable global
        in the listwidget, the current workaround is to reset the flag
        of each items. (it is much easier to reset all items, then to
        find out which item is being dropped - this is certainly doable
        but requires to custom define a item model)
        """
        if event.source() != self:
            board = event.source()
            board.takeItem(board.currentRow())

        event.setDropAction(Qt.MoveAction)
        super().dropEvent(event)

        for i in range(self.count()):
            item = self.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    def del_item(self, item):
        """Delete and item based on the item ID

        There no way to directly delete the item, and there's isn't
        a good way to search the row number by item. Here we iterate
        through all the entries and find the correct row value

        :param item QListWidgetItem: listwidget item
        """

        for i in range(self.count()):
            if self.item(i) is item:
                self.takeItem(i)

    def add_item(self, text):
        """add editable text item

        need to use item widget to make it editable
        :param text str: content of the item
        """
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsSelectable)
        self.addItem(item)


class TileDelegate(QStyledItemDelegate):
    """Delegate the list widget tile editor to NoteTile
    And adjust the size properly. This is used in listwidgetview
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """Change the default editor to NoteTile"""

        editor = TileEdit(parent=parent)
        editor.tile_finishSig.connect(self.finish_edit)

        return editor

    def setEditorData(self, editor, index):
        """Sets the editor data to the correct value"""

        editor.setText(index.data())
        editor.moveCursor(QTextCursor.End)

    def setModelData(self, editor, model, index):
        """Get data from the editor"""

        model.setData(index, editor.toPlainText())

    def sizeHint(self, option, index):
        """Change the sizehint this is to prevent horizontal crop

        Adjust the width slightly less than the default value
        """
        size = super().sizeHint(option, index)
        return QSize(size.width() - 20, size.height() + 10)

    def finish_edit(self):
        """Emit signal when editing is finished

        The signal tile_finishSig is triggered by QTextEdit
        out of focus event
        """
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)


class TileEdit(QTextEdit):
    """Editor for each tile"""
    tile_finishSig = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBar(QScrollBar())

    def focusOutEvent(self, event):
        self.tile_finishSig.emit()
        super().focusOutEvent(event)


class NoteTile(QTextEdit):
    """Create individual note tiles"""

    tile_resizeSig = Signal()
    tile_finishSig = Signal()

    def __init__(self, text="", objectName="", parent=None):
        super().__init__(parent)

        self.setObjectName(objectName)
        self.setPlainText(text)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setTabChangesFocus(True)
        self.moveCursor(QTextCursor.End)
        self.setAcceptRichText(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.textChanged.connect(self._resize)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _resize(self):
        """Resize the height based on the text document size

        The height is automatically adjusted to 1.1 times of the text
        height so no scrolling will be displayed
        """
        self.setFixedHeight(self.document().size().height() * 1.1)

    def focusOutEvent(self, event):
        self.tile_finishSig.emit()
        super().focusOutEvent(event)

    def resizeEvent(self, event):
        """Overwrite the resize event"""

        super().resizeEvent(event)
        self._resize()
