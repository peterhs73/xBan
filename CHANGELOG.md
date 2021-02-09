# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
