# spaCy VSCode Extension

Version 0.5.0

The spaCy VSCode Extension provides additional tooling and features for working with spaCy's config files. Version 1.0.0 includes hover descriptions for registry functions, variables, and section names within the config as an installable extension.

[![spaCy](https://img.shields.io/static/v1?label=made%20with%20%E2%9D%A4%20for&message=spaCy&color=09a3d5&style=flat-square)](https://spacy.io)

## 🚀 Quickstart

- **Step 1.** Install a supported version of Python on your system (`>=3.7`)
- **Step 2.** Install the [Python Extension for Visual Studio Code]()
- **Step 3.** Create a [virtual python environment]()
- **Step 4.** Install all python requirements

  - `spaCy >= 3.4.0`
  - `pygls >= 1.0.0`

- **Step 5.** Install spaCy Extension for Visual Studio Code
- **Step 6.** Select your python environment

<img src='./images/extension_python_env.gif' width=720>

- **Step 7.** You are ready to work with `.cfg` files in spaCy!

## 🔥 Features

The extension displays additional information on hover for some components and validates the config file on open.

<img src='./images/extension_features.gif' width=720>

### Hover

The hover feature provides three different types of information.

1. **The function registry**  
   Functions within the config file are registered within [spaCy's registry system](https://spacy.io/api/top-level#registry). When one of these functions is hovered over, the feature will provide information about the function and its arguments, along with a link to the code for the function, if available.

2. **Resolving references to variables**  
   Variables are denoted in the config file as `${<variable-name>}`. When a variable is hovered over, the feature will provide the value of that variable specified in the config file.

3. **Section titles**  
   The config system is separated by sections such as `[training.batcher]` or `[components]`. When a section, such as "training" or "components", or subsection, such as "batcher", is hovered over, the feature will provide a description of it, if available.

## ℹ️ Support

If you have questions about the extension, please ask on the spaCy discussion forum.
