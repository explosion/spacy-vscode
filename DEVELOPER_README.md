# spaCy VSCode Extension

Version 0.3.0

## Introduction

This VSCode extension is designed to help users with spaCy's configuration files (`.cfg`) by enabling hover features that give more context to users about the different architectures, variables and sections. It also provides features like autocompletion, validation and other "quality of life features" for working with the spaCy config system.

## Language Server Protocol

For the extension we need spaCy functionality (registry lookups, autocompletion, etc.), but since VScode runs on `Node.js` we can't use Python natively. For these specific cases we can use [LSP (Language Server Protocol)](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/) which allows us to create a Language Server written in any language to communicate with the VScode extension client. For our Python Language Server we use [pygls (pronounced py-glass)](https://github.com/openlawlibrary/pygls) which has all the LSP functionality implemented. We have two main folders [`client`](./extension/client/) (TypeScript, client-side code) and [`server`](./extension/server/) (Python, server-side code).

> More ressources about `LSP` and `pygls` here:
> [LSP Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) > [pygls Docs](https://pygls.readthedocs.io/en/latest/)

### Setup for development

Make sure you have `Node >= 18.6.0` installed and use `npm install` to install all node modules. Then create a virtual python environment and install the following python requirements:

- `pygls >= 1.0.0`
- `spaCy >= 3.4.0`

> You can also use `pip install -r requirement.txt`.

Create the file `setting.json` in the `.vscode/` folder and add the following line `"python.defaultInterpreterPath": "<Path to your python environment>"`. This makes sure that VScode uses your specified python environment when developing and testing the extension.

## How to run the extension (Development)

Use `F5` or the Debug menu to run `DEBUG MODE`, after that a debug symbol will appear on the bottom left.

> All possible launch settings are here `.vscode/launch.json`

Most of the feature logic will go into in the [`server.py` file](.server/server.py).

### Project structure

For every feature, there will be a dedicated script (e.g. `feature_hover.py`) which will implement all the required functionality. They will be used in the `server.py` script to link the functions to their respective event (e.g. `@spacy_server.feature(HOVER)`). If a function/method can be reused for other features, you can move it to the `util.py` script.

### Extension Features

#### Hover Functionality

#### Configurations/Settings

- `pythonInterpreter = ""` - Use this setting to specify which python interpreter should be used by the extension. The environment needs to have all required modules installe.

#### Commands

#### Python Environment Management

The spaCy Extension allows the user to either select a path to their desired python interpreter or use the current used interpreter. The selection can be done by clicking on the `spaCy` status bar which shows a dialog window with the two options.

### Building the extension

To build and publish the extension we use [Visual Studio Code Extension](https://code.visualstudio.com/api/working-with-extensions/publishing-extension#vsce)

> `npm install -g @vscode/vsce`.

To package the extension use `vsce package`
It will create an installable `.vsix` file which can be used to install the extension locally.

To publish the extension use `vsce publish` (#TODO)

### Logging / Debugging

#### Client Server (TypeScript)

The Client Server creates an Output Channel called `spaCy Extension Client` which outputs information about the current state of the Client Server. You can add logs to it by using `logging.info()`,`logging.warn()`, or `logging.error()`.

#### Language Server (Python)

To provide more information of the current state of the Language Server we use `logging.debug` which writes logs to `pygls.log`.

You can use `server.show_message()` to show vscode message boxes.

#### Statusbar

The extension adds a status bar which can be used to see whether the server is active and to select a python interpreter.

### Writing unit tests

#### Python

All python tests are contained in the [tests folder](./server/tests/)
Please make sure to have a modules installed, they can be found in the `tests/requirements.txt` file and installed via `pip install -e requirements.txt`.

- To run all tests use `pytest ./tests` or if you're in the tests folder you can also simply use `pytest`
- To run a specific test file use `pytest tests/test_file.py`
- To run a specific test function in a file use `pytest test/test_file.py::test_function`

> You can read more about [pytest](https://docs.pytest.org/en/7.2.x/) in their [docs](https://docs.pytest.org/en/7.2.x/how-to/index.html)
