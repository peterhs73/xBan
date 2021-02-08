#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Test the xban tile style are correctly formatted"""

from xban.style import TILE_STYLE


BLACK_SYTLE = """
QListWidget QWidget {
  color: black;
  background : #D9D7D7;
  font-family: "Helvetica";
}
QListView::item
{
  background-color: #D9D7D7;
  color: black;
  font-size: 15px; font-weight: bold; padding: 6px;
  border: 1px solid #414141;
  border-radius: 4px;
  margin-top: 3px;
  margin-bottom: 3px;
}
QListView::item:selected
{
  color: black;
  border : 2px solid black;
}
"""


def test_color_format():

    assert TILE_STYLE["black"] == BLACK_SYTLE
