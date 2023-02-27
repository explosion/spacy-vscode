# Changelog

All notable changes to this project will be documented in this file.

We try to follow semantic versioning (semver) if possible:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

> Given a version number 1.2.3, 1 is the major number, 2 the minor and 3 the patch number.

## [0.4.0] - 06/02/2023

### Added

- Hover feature for variables
- Links to code for registry functions
- Github testing

### Changed

### Fixed

- Improved formatting for hover displays

## [0.3.0] - 01/02/2023

### Added

- Hover feature for sections
- Documentation and argument/return types for the functions in the hover feature
- Improved Python Environment Management
  - Moved checks to extra python script
  - Added checks if python modules fulfill version range
  - Added checks if `Python Extension` is enabled/installed
- Added `client_constants`

### Changed

- Refactored code within the `detect_registry_names` hover feature function
- Changed logging to `LogOutputChannel`
- Removed automated python interpreter selection
- Added options to select specific interpreter or currently selected interpreter via dialog

### Fixed

- Statusbar color is using color theme instead of hardcoded color
- Added python prefix check for windows OS

## [0.2.0] - 26/01/2023

### Added

- Added Python Environment Management
  - Selecting Python Interpreter restarts the server on new interpreter
  - Added checks if Python Interpreters have all required modules
- Added `OutputChannel` for logging client server
- Added `StatusBar` icon
- Added more commands for debugging

### Changed

- Increased version node modules (e.g. `vscode-languageclient`)

## [0.1.0] - 12/01/2023

### Added

- Added `Hover` functionality
  - Resolving spaCy registry entries through hover display (e.g `@architecture`, `factory`, `@tokenizer`, etc.)

### Changed

- Moved from `pygls` v0.13.1 to v1.0.0
