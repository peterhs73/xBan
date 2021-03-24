#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The mainwindow GUI of xban"""

import sys
import os
from functools import partial
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import (
    QMainWindow,
    QScrollArea,
    QStatusBar,
    QApplication,
    QStyleFactory,
    QGraphicsDropShadowEffect,
)
import logging
from xban.board import BanBoard
from xban.utils import BanButton, QLogHandler


class xBanWindow(QMainWindow):
    """The main window of xban

    The main window serves three major purposes:
    - statusbar (sand the save button)
    - scrollable area
    """

    def __init__(self, base_path, file, file_config, parent=None):
        super().__init__(parent)

        board = BanBoard(file, file_config)
        board_area = QScrollArea()
        board_area.setWidget(board)
        board_area.setWidgetResizable(True)
        self.setCentralWidget(board_area)

        self.stbar = QStatusBar()

        # add a save button at the right bottom corner
        save_btn = BanButton(
            "save",
            objectName="appBtn_save",
            toolTip="save xban file",
            shortcut="Ctrl+S",
        )

        shadow = QGraphicsDropShadowEffect(
            self, blurRadius=10, offset=5, color=QColor("lightgrey")
        )
        save_btn.setGraphicsEffect(shadow)
        save_btn.pressed.connect(board.save_board)

        self.stbar.addPermanentWidget(save_btn)
        self.setStatusBar(self.stbar)
        log_handler = QLogHandler(self)
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)
        log_handler.signal.log_msg.connect(
            partial(self.stbar.showMessage, timeout=1500)
        )
        self.stbar.showMessage(f"Initiate {file}", 1500)
        self.show()

    def closeEvent(self, event):
        """Auto save when close"""

        self.centralWidget().widget().save_board()
        super().closeEvent(event)


def main_app(base_path, file, file_config):
    """Run the GUI of xBan

    The function initiates and resize the application
    """
    app = QApplication(sys.argv)

    if hasattr(QStyleFactory, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    with open(os.path.join(base_path, "xBanStyle.css"), "r") as style_sheet:
        style = style_sheet.read()

    app.setWindowIcon(QIcon(os.path.join(base_path, "xBanUI.png")))
    xBanApp = xBanWindow(base_path, file, file_config)

    xBanApp.setStyleSheet(style)

    # resize and move screen to center
    screen = app.desktop().screenGeometry()
    size = app.desktop().availableGeometry()
    xBanApp.resize(size.width() / 3, size.height() / 1.5)
    xBanApp.move(
        (screen.width() - xBanApp.width()) / 2,
        (screen.height() - xBanApp.height()) / 2,
    )

    app.setStyle("Fusion")
    sys.exit(app.exec_())
