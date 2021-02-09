# xBan project [![Current Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/IgorAntun/node-chat) [![](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

xBan offers completely offline kanban work-flow. It allows edits, drag and drop tiles and boards, and saves as yaml format. All operations are done locally. xBan can also convert valid dictionary formatted yaml file into a kanban board.

![xBan GUI](https://media.giphy.com/media/vm1CAIEJ6YIazJ221o/giphy.gif)

Some of the color schemes are inspired by Quip.

## Quickstart

To install xBan directly from github release (version 0.2.0):
    
    python -m pip install git+https://github.com/peterhs73/xBan.git@v0.2.0#egg=xban

To render xban file

	xban render file_path

To create a xban compatible file (and open the file)

	xban create new_file

To test xban package

	tox


## Features

A xBan project consists of a title section, a description section and individual board. Each board has a title and its own tiles. Selected features:

- Drag and drop tiles and boards
- Add/delete tiles and boards
- Change tile color


## References

- [Change Log](https://github.com/peterhs73/xBan/blob/master/CHANGELOG.md)
- [Releases](https://github.com/peterhs73/xBan/releases)