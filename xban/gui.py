#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtCore import Qt, Signal, QMimeData
from PySide2.QtGui import QIcon, QTextCursor, QDrag, QKeySequence
from PySide2.QtWidgets import (
    QStyleFactory,
    QPushButton,
    QApplication,
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
    QShortcut,
    QGraphicsDropShadowEffect
)

import sys
import os
from xban.style import TILE_STYLE
from functools import partial
from xban.io import save_yaml
import logging

gui_logger = logging.getLogger("xban-gui")


class BanBoard(QWidget):
    """The main board of xBan"""

    def __init__(self, filepath, file_config, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QWidget {background: white;}")

        self.filepath = filepath
        self.file_config = file_config

        self.draw_board(file_config)
        self.setAcceptDrops(True)
        self.show()
        gui_logger.info("Main board created")

    def draw_board(self, file_config):
        """Initiate UI

        The UI consists of 2 parts, top is the board title and info
        and button is the subbords with tiles in each ones
        the subboard is drawn based on file_configuration
        """
        config, content = file_config

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(30, 30, 30, 30)

        title_edit = QLineEdit(config["xban_config"]["title"], self)
        title_edit.setPlaceholderText("Enter title here...")
        title_edit.setStyleSheet(
            'font-family: "Courier New"; font-size: 24px; font-weight: bold;'
        )

        info_edit = NoteTile(config["xban_config"]["description"], self)
        info_edit.setPlaceholderText("Enter description here...")
        info_edit.setStyleSheet("font-size: 14px;")

        mainlayout.addWidget(title_edit)
        mainlayout.addWidget(info_edit)

        sublayout = QHBoxLayout()
        color = config["xban_config"]["board_color"]
        sublayout.setMargin(10)
        sublayout.setSpacing(20)

        for i, tile_contents in enumerate(content.items()):
            subboard = SubBoard(tile_contents, color[i], self)
            sublayout.addWidget(subboard)
            subboard.delboardSig.connect(
                partial(self.delete_board, board=subboard)
            )

        add_btn = QPushButton("+")

        add_btn.setFixedWidth(30)
        add_btn.setStyleSheet("border-style: none")
        add_btn.clicked.connect(self.insert_board)
        sublayout.addWidget(add_btn)

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_board)

        mainlayout.addLayout(sublayout)
        self.setLayout(mainlayout)

    def insert_board(self):
        """Insert a board into the layout"""
        sublayout = self.layout().itemAt(2)
        new_board = SubBoard(("", ()), "black", self)
        new_board.delboardSig.connect(partial(self.delete_board, new_board))
        # insert second to last
        sublayout.insertWidget(sublayout.count() - 1, new_board)

    def delete_board(self, board):
        """Delete the board"""

        sublayout = self.layout().itemAt(2)
        sublayout.removeWidget(board)
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

    def closeEvent(self, event):
        """Auto save when close"""

        self.save_board()
        super().closeEvent(event)


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

        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setWordWrap(True)
        self.setAcceptDrops(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)

    def dropEvent(self, event):
        """Drop and drag event

        This is the main function on drop and drop
        if the source is not self, meaning the item is moved from
        another widget, need to delete the original item. This can
        only be done by finding the item row and delete the whole row
        """

        if event.source() != self:
            board = event.source()
            board.takeItem(board.currentRow())
            event.setDropAction(Qt.MoveAction)
        event.setDropAction(Qt.MoveAction)
        super().dropEvent(event)

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
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.addItem(item)


class SubBoard(QWidget):
    """The subboard of xBan

    The board contains the individual "blocks" of the board
    """

    delboardSig = Signal()

    def __init__(self, tile_contents, color, parent=None):
        super().__init__(parent)
        title_name, tile_items = tile_contents
        self.color = color

        # shadow.setEnabled(True)
        board = QVBoxLayout()
        tile_title = NoteTile(title_name, self)
        tile_title.setPlaceholderText("Title here...")
        tile_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        board.addWidget(tile_title)

        listwidget = BanListWidget(self)
        listwidget.setStyleSheet(TILE_STYLE.get(color, "black"))
        for tile in tile_items:
            listwidget.add_item(tile)

        board.addWidget(listwidget)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+", clicked=self.add_listitem)
        del_btn = QPushButton("-", clicked=self.del_listitem)
        context_btn = QPushButton("≡")
        context_btn.setMenu(self.context_menu())

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(context_btn)
        board.addLayout(btn_layout)

        self.setLayout(board)

    def parse(self):
        """Parse the subboard content into a content list

        In the board layout, the first item is the title widget
        and the second is the list widget
        """
        board = self.layout()
        title = board.itemAt(0).widget().toPlainText()
        listwidget = board.itemAt(1).widget()
        tile_items = [
            listwidget.item(i).text() for i in range(listwidget.count())
        ]
        return title, tile_items

    def add_listitem(self):
        """Add entry for listwidget"""
        listwidget = self.layout().itemAt(1).widget()
        listwidget.add_item("")
        # set the current row the new item
        listwidget.clearSelection()
        listwidget.setCurrentRow(listwidget.count() - 1)

    def del_listitem(self):
        """Delete entry for listwidget"""
        listwidget = self.layout().itemAt(1).widget()
        for item in listwidget.selectedItems():
            listwidget.del_item(item)

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
        menu.setWindowFlags(menu.windowFlags() | Qt.NoDropShadowWindowHint)
        color_menu = menu.addMenu("Tile Color")
        color_menu.setWindowFlags(
            color_menu.windowFlags() | Qt.NoDropShadowWindowHint
        )

        for color in TILE_STYLE:
            color_action = color_menu.addAction(color)
            color_action.triggered.connect(
                partial(self.color_change, color=color)
            )

        del_action = menu.addAction("Delete")
        del_action.triggered.connect(self.delete_board)

        return menu

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
            self.delboardSig.emit()


class NoteTile(QTextEdit):
    """Create individual note tiles"""

    tile_resizeSig = Signal()

    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.setPlainText(text)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setTabChangesFocus(True)
        self.moveCursor(QTextCursor.End)
        self.setAcceptRichText(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.textChanged.connect(self._resize)

    def _resize(self):
        """Resize the height based on the text document size

        The height is automatically adjusted to 1.1 times of the text
        height so no scrolling will be displayed
        """
        self.setFixedHeight(self.document().size().height() * 1.1)

    def resizeEvent(self, event):
        """Overwrite the resize event"""

        super().resizeEvent(event)
        self._resize()


def main_app(base_path, file, file_config):
    """Run the GUI of xBan"""
    app = QApplication(sys.argv)

    if hasattr(QStyleFactory, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    with open(os.path.join(base_path, "xBanStyle.css"), "r") as style_sheet:
        style = style_sheet.read()

    app.setWindowIcon(QIcon(os.path.join(base_path, "xBanUI.png")))
    xbanwindow = BanBoard(file, file_config)
    xbanwindow.setStyleSheet(style)
    app.setStyle("Fusion")
    sys.exit(app.exec_())
