# spaCy VSCode Extension

## Introduction 

This VSCode extension is designed to help users with spaCy's configuration files (`.cfg`) by enabling hover features that give more context to users about the different architectures, variables and section. It also provides autocompletion, validation and other "quality of life features" for working with spaCy's config system.

> Note: This project is based on the [JSON Server template](https://github.com/thomashacker/pygls/tree/master/examples/json-extension), so some artifacts might still be hiding in some files. (e.g. unit tests are still for the JSON Server)

## Language Server Protocol

For the extension  we need some spaCy functionality (registry lookups, autocompletion, etc.), but VSCode runs on `Node.js` so we can't use Python natively. For these specific cases we can use [LSP (Language Server Protocol)](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/) which allows us to create a Language Server written in any language and communicate with the VSCode extension client. For our Python Language Server we use [pygls (pronounced py-glass)](https://github.com/openlawlibrary/pygls) which has all functionality already implemented. Thus we have two main folders [`client`](./extension/client/) (TypeScript, client-side code) and [`server`](./extension/server/) (Python, server-side code).

> More ressources about `LSP` and `pygls` here:
[LSP Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)
[pygls Docs](https://pygls.readthedocs.io/en/latest/)

### Setup for development
Make sure you have `Node >= 18.6.0` installed and use `npm install` inside the [extension](./extension/) folder to install all node modules. Then create a virtual python environment and install the following python requirements:

- `pygls == 0.13.1` (newer versions have breaking changes)
- `spaCy >= 3.4.0`

Create the file `setting.json` in the `extension/.vscode/` folder and add the following line `"python.defaultInterpreterPath": "Path to your python environment"`


## How to run the extension (Development)

Use `F5` or the Debug menu inside the `./extension` folder to run both the client and server. Don't forget to quit both servers when restarting the extension.

> The launch settings can be adjusted in `./extension/.vscode/launch.json`

Most of the code and logic will go into in the [`server.py` file](./extension/server/server.py).

### Building the extension
TODO

### Debugging
TODO

### Writing unit tests
TODO
