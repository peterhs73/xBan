#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""This script host some customized utilities"""


from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QEvent
import logging
from PySide6.QtCore import Signal, QThread, QSize


class BanButton(QPushButton):
    """Custom pushbutton to adjust hover event"""

    sizeSig = Signal(QSize)

    def __init__(self, *args, **kwargs):
        """Assign hover color and event filter

        The default color is grey with white background

        :param color list of tuples: first tuple is the hover colors and
            second is the press colors.
            The behavior is after pressed the color return to before.
        """

        hover, press = kwargs.pop("color", []) or [
            ("white", "#bdbdbd"),
            ("white", "grey"),
        ]
        default_color = kwargs.pop("default_color", []) or ("grey", "white")
        style_format = "QPushButton {{color: {}; background-color: {};}}"
        self.default_c = style_format.format(*default_color)
        self.hover_c = style_format.format(*hover)
        self.press_c = style_format.format(*press)

        super().__init__(*args, **kwargs)
        self.installEventFilter(self)
        self.setStyleSheet(self.default_c)

    def eventFilter(self, object, event):
        """Workaround for hover event painting

        This is a workaround of the button hover behavior of css
        The issue is that when the menu button is pressed, there is no
        unhover event, which will keep the color of the hover when the
        menu is exited. Here I modify the press event and release event
        to fake the exit of the hover event. This again cannot be
        replicated by css either (this is probably a bug as well).
        """

        if event.type() == QEvent.HoverEnter:
            self.setStyleSheet(self.hover_c)

        elif event.type() == QEvent.HoverLeave:
            self.setStyleSheet(self.default_c)

        elif event.type() == QEvent.MouseButtonPress:
            self.setStyleSheet(self.press_c)

        elif event.type() == QEvent.MouseButtonRelease:
            self.setStyleSheet(self.default_c)

        return super().eventFilter(object, event)

    def resizeEvent(self, event):
        """add resize event to change the broadcast the size change

        THIs is used for resize the menu for color menu
        """
        super().resizeEvent(event)
        self.sizeSig.emit(self.size())


class QLogSignal(QThread):
    """Qt signal for logging
    To create a thread safe logging, need to use signal-slot to pass the
    logging and formatting message
    """

    log_msg = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


class QLogHandler(logging.Handler):
    """Custom handler to stream log to QTextEdit
    To have a thread safe to exit, need to define parent of the signal
    thread, here passed as the parent parameters.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.signal = QLogSignal(parent)

    def emit(self, record):
        """Emit colored log record"""
        msg = self.format(record)
        self.signal.log_msg.emit(msg)
