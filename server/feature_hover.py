from pygls.lsp.types import (
    Position,
    Range,
    Hover,
    TextDocumentPositionParams,
    MarkupContent,
    MarkupKind,
)
from pygls.lsp.types.basic_structures import (
    Range,
)

import re
from typing import Optional
from spacy import registry
from .language_server import SpaCyLanguageServer


def hover(
    server: SpaCyLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """Implement all Hover functionality"""
    document = server.workspace.get_document(params.text_document.uri)
    if document:
        line_n = params.position.line
        line_str = document.lines[line_n]

        ### TODO ###
        # Rewrite the regex to find specific cases with inline and dictionary registries
        # Check for e.g " @architecture", "@loggers"
        registry_types = re.findall(r"^@[a-zA-Z]*", line_str)
        # Check for "factory"
        if not registry_types and "factory" in line_str:
            registry_types = ["factories"]
        if registry_types:
            registry_type = registry_types[0].replace("@", "").strip()
            registry_names = re.findall(r"\"[a-zA-Z.\d]*\"", line_str)
            if registry_names:
                registry_name = registry_names[0].replace('"', "").strip()
                try:
                    registry_desc = registry.find(registry_type, registry_name)
                    registry_docstring = registry_desc["docstring"]
                    if registry_docstring is None:
                        return None
                    registry_path = ""
                    if registry_desc["file"] is not None:
                        registry_path = f"➡️ [Go to code]({registry_desc['file']})"

                    hover_display = f"## ⚙️ {registry_name} \n {registry_docstring} \n {registry_path}"

                    return Hover(
                        contents=MarkupContent(
                            kind=MarkupKind.Markdown, value=hover_display
                        ),
                        range=Range(
                            start=Position(line=line_n, character=0),
                            end=Position(line=line_n, character=len(line_str)),
                        ),
                    )
                except Exception as e:
                    print(e)
                    return None
    return None
