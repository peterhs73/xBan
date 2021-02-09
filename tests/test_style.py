#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Test the xban tile style are correctly formatted"""

from xban.style import TILE_STYLE


BLACK_SYTLE = """
QListWidget {
  border-style: none;
  outline:none;
}
QListView::item {
  background-color: #D9D7D7;
  color: black;
  font-size: 15px; font-weight: bold;
  border: 1px solid #414141;
  border-radius: 4px;
  margin-top: 3px;
  margin-bottom: 3px;
  margin-right: 3px;
  padding: 6px 10px 6px 10px;
}
QListView QTextEdit {
  color: black;
  background : #D9D7D7;
  border-style: none;
}
QListView::item:selected {
  color: black;
  border: 2px solid black;
}
QListView QTextEdit QScrollBar:vertical {
  color: #D9D7D7;
  background: #D9D7D7;
}
QListView QTextEdit QScrollBar::handle:vertical {
  background:black;
}
"""


def test_color_format():

    assert TILE_STYLE["black"] == BLACK_SYTLE
