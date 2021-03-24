# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2021-03-22
### Added
- Add the qmainwindow for the board widget
- Add save button
- Add statusbar that displays log message (currently saving event)
- Add brown color

### Fixed
- Fix the menu button hovering issue: when the button is pressed, the unhover event is not triggered,
  the hovered color persists after button button clicks. This is resolved by modifying the button
  press event to change the background color in the button behavior. I think this is a bug in the qt end.
  The hover behavior is still defined in css style file since it is easier to identify different buttons.
- Set a minimum width of the button.
- Fix issue where multiple tiles is selected across the boards
- Fix issue where after drop item no longer editable

### Changed
- Use class object name for better child style sheet settings
- Separate GUI to the mainwindow session and the board session for better readability
- Simply color pull down menu
- Add background color when press btn and consistent across the application
- Change color menu to match the context button size
- Change color menu to reflect the proper color of the option

## [0.2.0] - 2021-02-08
### Changed
- Change command line message when files already exist
- Change QListWidget editor to QTextEditor using delegates
- Change default background color
- Change the board buttons, delete button is now separate

### Fixed
- Fix the issue that the tile item is cropped
- Fix the scrollbar color and padding
- Fix the setup files to include non python file in installation
- Fix the wrong package name on `setup.py` (smh)
- Fix package namespace issue in `setup.py`

### Added
- Add more information on readme
- Add save logging
- Add shadow to tile board
- Add button tool tip
- Add `MANIFEST.in` for packaging

## [0.1.0] - 2021-02-07
### Added
- Add "black" and "teal" color
- Add logging

### Changed
- Rewrite the internal, now individual tiles are part of `QListWidget`
- Change xban files format to `yaml`
- Change interface from `QMainWindow` to command-line + `QWidget`

### Fixed
- Fix code formating
