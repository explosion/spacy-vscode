"""Script containing all logic for hover functionality"""

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
from .spacy_server import SpacyLanguageServer
from .util import get_current_word


def hover(
    server: SpacyLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """
    Implements the Hover functionality
    Check if currently hovered text is registered in the spaCy registry and return its description.
    """
    document = server.workspace.get_document(params.text_document.uri)

    if not document:
        return None

    line_n = params.position.line
    line_str = document.lines[line_n]

    current_word, w_start, w_end = get_current_word(line_str, params.position.character)
    registry_name, r_start, r_end = detect_registry_names(line_str, w_start, w_end)
    if registry_name:
        registry_type, t_start, t_end = detect_registry_type(line_str, r_start)

    # Special Case for Factories
    # Because their registry_names can be "ner", "textcat"
    else:
        registry_type, t_start, t_end = detect_registry_type(line_str, w_start)
        registry_name = current_word
        r_start = w_start
        r_end = w_end

    try:
        # Hardcoded renaming
        if registry_type == "factory":
            registry_type = "factories"

        # Retrieve data from registry
        registry_desc = registry.find(registry_type, registry_name)

        if not registry_desc["docstring"]:
            registry_docstring = "Currently no description available"
        else:
            registry_docstring = registry_desc["docstring"]

        # TODO Create link to codebase (if possible)
        # if registry_desc["file"] is not None:
        # registry_path = f"➡️ [Go to code]({registry_desc['file']})"

        # TODO Fine-Tune display message
        hover_display = f"## ⚙️ {registry_name} \n {registry_docstring}"

        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_display),
            range=Range(
                start=Position(line=line_n, character=r_start),
                end=Position(line=line_n, character=r_end + 1),
            ),
        )

    except Exception as e:
        return None


def detect_registry_names(line: str, word_start: int, word_end: int):
    """
    Detect if a word indicates a registry name

    Examples:
    spacy.registry_name_.v1
    spacy-legacy.registry_name.v2
    compounding.v1

    1. Case: "spacy." - A dot on the end indicates a beginning of a registry name (OPTIONAL)
    2. Case: ".<any word>." - A word enclosed with dots indicate the registry name
    3. Case: ".v<any number>" - A at the beginning indicates the end of a registry name
    4. Case: "compounding.v1" Example
    """
    registry_name_start = 0
    registry_name_end = 0

    # There won't exist a registry name beginning a new line
    # Registry names are always enclosed with a quote
    if word_start != 0 and word_end < len(line) - 1:
        # Case 1
        if line[word_start - 1] != "." and line[word_end + 1] == ".":
            prefix = line[word_start : word_end + 1]
            registry_name, r_start, r_end = get_current_word(line, word_end + 2)
            if line[r_end + 1] == ".":
                version, v_start, v_end = get_current_word(line, r_end + 2)
                registry_name_start = word_start
                registry_name_end = v_end
            # Case 4
            else:
                registry_name_start = word_start
                registry_name_end = r_end

        # Case 2
        elif line[word_start - 1] == "." and line[word_end + 1] == ".":
            registry_name = line[word_start : word_end + 1]
            prefix, p_start, p_end = get_current_word(line, word_start - 2)
            version, v_start, v_end = get_current_word(line, word_end + 2)
            registry_name_start = p_start
            registry_name_end = v_end

        # Case 3
        elif line[word_start - 1] == "." and line[word_end + 1] != ".":
            version = line[word_start : word_end + 1]
            registry_name, r_start, r_end = get_current_word(line, word_start - 2)
            if line[r_start - 1] == ".":
                prefix, p_start, p_end = get_current_word(line, r_start - 2)
                registry_name_start = p_start
                registry_name_end = word_end

        full_registry_name = line[registry_name_start : registry_name_end + 1]
        registry_regex = r"[\w\d]*\.[\w\d]*\.[\w\d]*"
        registry_regex_alt = r"[\w\d]*\.[\w\d]*"

        if re.match(registry_regex, full_registry_name):
            return full_registry_name, registry_name_start, registry_name_end
        elif re.match(registry_regex_alt, full_registry_name):
            return full_registry_name, registry_name_start, registry_name_end
        else:
            return None, None, None
    else:
        return None, None, None


def detect_registry_type(line: str, registry_start: int):
    """
    Detect type and return type and name of registry

    EXAMPLES:
    @architecture
    factory
    """

    t_start = 0
    t_end = 0

    if registry_start <= 0:
        return "", t_start, t_end

    for i in range(registry_start - 1, 0, -1):
        if re.match("\W", line[i]):
            continue
        else:
            registry_type, t_start, t_end = get_current_word(line, i)
            break

    return line[t_start : t_end + 1], t_start, t_end
