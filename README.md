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

Use `F5` or the Debug menu to run both the client and server. Don't forget to quit both servers when restarting the extension.

> The launch settings can be adjusted in `.vscode/launch.json`

Most of the code and logic will go into in the [`server.py` file](.server/server.py).

### Project structure

For every feature, there will be a dedicated script (e.g. `feature_hover.py`) which will implement all the required functionality. They will then be used in the `server.py` script to link the functions to their respective trigger event (e.g. `@spacy_server.feature(HOVER)`). If a function/methiod might be useful for different features, you can move it to the `util.py` script.

### Building the extension
TODO
(Building the extension will probably be the most biggest challenge because we need to handle multiple things regarding python (e.g. python environment handling per device, etc.))

### Debugging
TODO
(There are some logs that are being written to during debug runtime but I need to further explore this)

### Writing unit tests
TODO
(There are some unit tests from the JSON Language server but I need to futher look into this)
