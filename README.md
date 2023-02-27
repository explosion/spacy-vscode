# spaCy VSCode Extension

The spaCy VSCode Extension provides additional tooling and features for working with spaCy's config files. Version 1.0.0 includes hover descriptions for registry functions, variables, and section names within the config as an installable extension. 

[![spaCy](https://img.shields.io/static/v1?label=made%20with%20%E2%9D%A4%20for&message=spaCy&color=09a3d5&style=flat-square)](https://spacy.io)

## 🚀 Quickstart
TODO

## 🔥 Features
The extension currently displays additional information on hover for some components and validates the config file on open.

### Hover
The hover feature provides three different types of information. 

1) **The function registry**  
Functions within the config file are registered within spaCy's registry system. When one of these functions is hovered over, the feature will provide information about the function and its arguments, along with a link to the code for the function, if available. 

2) **Resolving references to variables**  
Variables are denoted in the config file as `${<variable-name>}`. When a variable is hovered over, the feature will provide the value of that variable specified in the config file. 

3) **Section titles**  
The config system is separated by sections such as `[training.batcher]` or `[components]`. When a section, such as "training" or "components", or subsection, such as "batcher", is hovered over, the feature will provide a description of it, if available.
