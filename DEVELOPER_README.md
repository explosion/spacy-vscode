# spaCy VSCode Extension

Version 0.1.0

## Introduction 

This VSCode extension is designed to help users with spaCy's configuration files (`.cfg`) by enabling hover features that give more context to users about the different architectures, variables and sections. It also provides autocompletion, validation and other "quality of life features" for working with spaCy's config system.

> Note: Because this project is based on the [JSON Server template](https://github.com/thomashacker/pygls/tree/master/examples/json-extension), some artifacts might still be hiding in some files. (e.g. unit tests are still for the JSON Server)

## Language Server Protocol

For the extension  we need some spaCy functionality (registry lookups, autocompletion, etc.), but VSCode runs on `Node.js` so we can't use Python natively. For these specific cases we can use [LSP (Language Server Protocol)](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/) which allows us to create a Language Server written in any language and communicate with the VSCode extension client. For our Python Language Server we use [pygls (pronounced py-glass)](https://github.com/openlawlibrary/pygls) which has all functionality already implemented. Thus we have two main folders [`client`](./extension/client/) (TypeScript, client-side code) and [`server`](./extension/server/) (Python, server-side code).

> More ressources about `LSP` and `pygls` here:
[LSP Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)
[pygls Docs](https://pygls.readthedocs.io/en/latest/)

### Setup for development
Make sure you have `Node >= 18.6.0` installed and use `npm install` to install all node modules. Then create a virtual python environment and install the following python requirements:

- `pygls >= 1.0.0`
- `spaCy >= 3.4.0`

> They are also included in the `requirements.txt` file. You can use `pip install -r requirement.txt` to install everything.

Create the file `setting.json` in the `.vscode/` folder and add the following line `"python.defaultInterpreterPath": "Path to your python environment"`. This makes sure that your VScode uses your specified python environment when developing and testing the extension.


## How to run the extension (Development)

Use `F5` or the Debug menu to run `DEBUG MODE`, after that a debug symbol will appear on the bottom left. To start both the client and server, click on the debug symbol and on `Server+Client`. Don't forget to quit both servers when restarting the extension.

> All possible launch settings are here `.vscode/launch.json`

Most of the code logic will go into in the [`server.py` file](.server/server.py).

### Project structure

For every feature, there will be a dedicated script (e.g. `feature_hover.py`) which will implement all the required functionality. They will then be used in the `server.py` script to link the functions to their respective trigger event (e.g. `@spacy_server.feature(HOVER)`). If a function/methiod might be useful for different features, you can move it to the `util.py` script.

### Extension Features

#### Configurations/Settings
- `defaultPythonInterpreter = ""` - You can use this setting to specify which Python Interpreter should be used by the spaCy-Extension server. If empty (by default), the spaCy-Extension will use the Python Interpreter currently selected in the workspace. The Python Interpreter can then by changed by using the Python command `Select Interpreter`.

#### Commands
- `spaCy Extension: Return Python Interpreter` - Returns the Python Interpreter on which the spaCy Extension server is running.
- `spaCy Extension: Restart Server` - Restarts the Language Server and uses the current selected Python Interpreter (or specified in `defaultPythonInterpreter`)

#### Python Environment Management
The spaCy Extension is capable to detect the current selected Python Interpreter in the current workspace and uses it to start the Language Server on. It is also capable to detect an Interpreter change and can restart the server accordingly. Before the Language Server is started, the extension first verifies whether the current selected Interpreter has all modules installed (`pygls`,`spacy`) and is compatible. If the user starts the server on an compatible environment and changes to an incompatible environment, the extension won't restart the server and stays on the previous environment.

If a `defaultPythonInterpreter` was set, the extension will only use this environment and is not affected by the current selected Python Interpeter or changes.

### Building the extension

To build and publish the extension we can use [Visual Studio Code Extension](https://code.visualstudio.com/api/working-with-extensions/publishing-extension#vsce) which can be installed like this `npm install -g @vscode/vsce`.

To package the extension use `vsce package`
It will create an installable `.vsix` file which can be used to install the extension locally.

To publish the extension use `vsce publish` (WIP)

### Logging / Debugging

#### Client Server (TypeScript)
To provide more information of the current state of the Client Server we use `console.info` and `console.warn` to notify the user. It should start with `spaCy Extension:` to make clear that it's related to the spaCy Extension.

#### Language Server (Python)

To provide more information of the current state of the Language Server we use `logging.debug` which writes logs to `pygls.log`.


### Writing unit tests
TODO
(There are some unit tests from the JSON Language server but I need to futher look into this)
