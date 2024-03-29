# xBan project [![Current Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/peterhs73/xBan/releases) [![](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

xBan offers a completely offline kanban work-flow. It allows edits, drag and drop tiles and boards, and saves as yaml format. All operations are done locally. xBan can also convert valid dictionary formatted yaml file into a kanban board.

![xBan GUI](https://media.giphy.com/media/4IAFWoA2C6HKPNb4xg/giphy.gif)

Some of the color schemes are inspired by Quip.

## Quickstart

To install xBan directly from github release (version 0.3.0):
    
    python -m pip install git+https://github.com/peterhs73/xBan.git@v0.3.0#egg=xban

To create/render xban (or valid yaml) file:

	xban FILEPATH

To turn on debug mode:
	
	xban -d FIELPATH 

### Development

Clone xBan to local:
	
	git clone https://github.com/peterhs73/xBan.git

Under the xBan directory, run installation in edit mode:

	pip install -e .

Run the tests:

	tox


## Features

A xBan project consists of a title section, a description section and an individual board. Each board has a title and its own tiles. Selected features:

- Drag and drop tiles and boards
- Add/delete tiles and boards
- Change tile color


## References

- [Change Log](https://github.com/peterhs73/xBan/blob/master/CHANGELOG.md)
- [Releases](https://github.com/peterhs73/xBan/releases)
