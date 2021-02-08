"""The script outlines the style sheet for tile colors"""


COLOR_DICT = {
    "black": {"bgcolor": "#D9D7D7", "color": "black", "bcolor": "#414141"},
    "purple": {"bgcolor": "#fbdbff", "color": "#d30bea", "bcolor": "#fb87ff"},
    "red": {"bgcolor": "#ffecee", "color": "#fe3a51", "bcolor": "#fec9d0"},
    "yellow": {"bgcolor": "#fef8e7", "color": "#ff9900", "bcolor": "#f2ce98"},
    "blue": {"bgcolor": "#eaf8fe", "color": "#29ade8", "bcolor": "#c6ebfb"},
    "green": {"bgcolor": "#bafce2", "color": "#00c678", "bcolor": "#2ce89e"},
    "teal": {"bgcolor": "#c2eaf0", "color": "#426A70", "bcolor": "#6b8485"},
}

WIDGET_FORMAT = """
QListWidget QWidget {{
  color: {color};
  background : {bgcolor};
  font-family: "Helvetica";
}}
QListView::item
{{
  background-color: {bgcolor};
  color: {color};
  font-size: 15px; font-weight: bold; padding: 6px;
  border: 1px solid {bcolor};
  border-radius: 4px;
  margin-top: 3px;
  margin-bottom: 3px;
}}
QListView::item:selected
{{
  color: {color};
  border : 2px solid {color};
}}
"""

# The following code is for widget background and currently that is not added
# BG_FORMAT = """background-image: url('{}') 100px 100px stretch stretch;
# background-repeat: no-repeat; background-position: center center;
# """

TILE_STYLE = {}

for color_name, setting in COLOR_DICT.items():
    TILE_STYLE[color_name] = WIDGET_FORMAT.format(**setting)
