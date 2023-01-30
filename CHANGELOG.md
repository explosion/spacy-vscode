# Changelog

All notable changes to this project will be documented in this file.

We try to follow semantic versioning (semver) if possible:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes 

> Given a version number 1.2.3, 1 is the major number, 2 the minor and 3 the patch number.

## [0.2.0] - 26/01/2022

### Added
- Python Environment Management
- Selecting Python Interpreter restarts the server on the new interpreter
- Python Interpreters are tested whether they contain all needed modules
- Added Output Channel for Client Server logging
- Added StatusBar
- Added more commands

### Changed
- Increased version of some node modules to get the newest updates (e.g. `vscode-languageclient`)

### Fixed


## [0.1.0] - 12/01/2022

### Added
- Resolving registry entries through hover display (e.g `@architecture`, `factory`, `@tokenizer`, etc.)

### Changed
- Moved from pygls v0.13.1 to v1.0.0

### Fixed
