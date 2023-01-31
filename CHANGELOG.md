# Changelog

All notable changes to this project will be documented in this file.

We try to follow semantic versioning (semver) if possible:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

> Given a version number 1.2.3, 1 is the major number, 2 the minor and 3 the patch number.

## [1.0.0] - 30/01/2022

### Added

- Python Environment Management
  - Added checks if python modules fulfill version range
  - Added checks if `Python Extension` is enabled/installed
- Added `compare-versions` module

### Changed

- Changed logging to `LogOutputChannel`

## [0.2.0] - 26/01/2022

### Added

- Added Python Environment Management
  - Selecting Python Interpreter restarts the server on new interpreter
  - Added checks if Python Interpreters have all required modules
- Added `OutputChannel` for logging client server
- Added `StatusBar` icon
- Added more commands for debugging

### Changed

- Increased version node modules (e.g. `vscode-languageclient`)

## [0.1.0] - 12/01/2022

### Added

- Added `Hover` functionality
  - Resolving spaCy registry entries through hover display (e.g `@architecture`, `factory`, `@tokenizer`, etc.)

### Changed

- Moved from `pygls` v0.13.1 to v1.0.0
