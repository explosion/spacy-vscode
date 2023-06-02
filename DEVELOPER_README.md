# spaCy VSCode Extension

Version 1.0.1

## Introduction

This VSCode extension is designed to help users with spaCy's configuration files (`.cfg`) by enabling hover features that give more context to users about architectures, variables and sections and provides features like autocompletion, validation and other "quality of life features" for working with the config system.

## Language Server Protocol

For the extension we need spaCy functionality (registry lookups, autocompletion, etc.), but since VScode runs on `Node.js` we can't use Python natively. For these specific cases we can use [LSP (Language Server Protocol)](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/) which allows us to create a Language Server written in any language to communicate with the VScode extension client. For our Python Language Server we use [pygls (pronounced py-glass)](https://github.com/openlawlibrary/pygls) which has all the LSP functionality implemented. We have two main folders [`client`](./extension/client/) (TypeScript, client-side code) and [`server`](./extension/server/) (Python, server-side code).

> More ressources about `LSP` and `pygls` here:
> [LSP Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)

> [pygls Docs](https://pygls.readthedocs.io/en/latest/)

### Setup for development

Make sure you have `Node >= 18.6.0` installed and use `npm install` to install all node modules. Then create a virtual python environment and install the following python requirements:

- `pygls >= 1.0.0`
- `spaCy >= 3.4.0`

> You can also use `pip install -r requirement.txt`.

Create the file `setting.json` in the `.vscode/` folder and add the following line `"python.defaultInterpreterPath": "<Path to your python environment folder>"`. This makes sure that VScode uses your specified python environment when developing and testing the extension.

## How to run the extension (Development)

Use `F5` or the Debug menu to run `DEBUG MODE`, after that a debug symbol will appear on the bottom left.

> All possible launch settings are here `.vscode/launch.json`

Most of the feature logic will go into in the [`server.py` file](.server/server.py).

### Project structure

For every feature, there will be a dedicated script (e.g. `feature_hover.py`) which will implement all the required functionality. They will be used in the `server.py` script to link the functions to their respective event (e.g. `@spacy_server.feature(HOVER)`). If a function/method can be reused for other features, you can move it to the `util.py` script.

### Extension Features

#### Hover Functionality

The hover feature provides three different types of information.

1. **The function registry**  
   Functions within the config file are registered within [spaCy's registry system](https://spacy.io/api/top-level#registry). When one of these functions is hovered over, the feature will provide information about the function and its arguments, along with a link to the code for the function, if available.

2. **Resolving references to variables**  
   Variables are denoted in the config file as `${<variable-name>}`. When a variable is hovered over, the feature will provide the value of that variable specified in the config file.

3. **Section titles**  
   The config system is separated by sections such as `[training.batcher]` or `[components]`. When a section, such as "training" or "components", or subsection, such as "batcher", is hovered over, the feature will provide a description of it, if available.

#### Configurations/Settings

- `pythonInterpreter = ""` - Use this setting to specify which python interpreter should be used by the extension. The environment needs to have all required modules installed.

#### Python Environment Management

The spaCy Extension allows the user to either select a path to their desired python interpreter or use the current used interpreter. The selection can be done by clicking on the `spaCy` status bar which shows a dialog window with the two options.

### Building the extension

To build and publish the extension we use [Visual Studio Code Extension](https://code.visualstudio.com/api/working-with-extensions/publishing-extension#vsce)

> `npm install -g @vscode/vsce`.

To package the extension use `vsce package`
It will create an installable `.vsix` file which can be used to install the extension locally.
You can right-click on the `.vsix` file to install it to VScode.

### Logging / Debugging

#### Client Server (TypeScript)

The Client Server creates an Output Channel called `spaCy Extension Log` which outputs information about the current state of the Client Server. You can add logs to it by using `logging.info()`,`logging.warn()`, or `logging.error()`.

#### Language Server (Python)

To provide more information of the current state of the Language Server we use `logging.debug` which writes logs to `pygls.log`.

You can use `server.show_message()` to show vscode message boxes or `server.show_message_log()` to log directly to the `spaCy Extension Log` output channel.

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

#### TypeScript

(TODO)

### Testing the codebase

To validate and test the code, please install all requirements listed [here](server/tests/requirements.txt):

- `pytest`
- `mock`
- `types-mock`
- `mypy`
- `black`

- Use `mypy server` to check any type errors
- Use `black server --check` to check black formatting
- Use `pytest server` to run all tests
- Use `npm run lint` to lint all typescript code

We have dedicated test workflows for this on github.
