"""Script containing all logic for hover functionality"""

from lsprotocol.types import (
    Position,
    Range,
    Hover,
    TextDocumentPositionParams,
    MarkupContent,
    MarkupKind,
    Range,
)

import re
from typing import Optional
from spacy import registry, schemas, glossary
from .spacy_server import SpacyLanguageServer
from .util import get_current_word
import typer

# glossary for now, to be replaced with glossary.CONFIG_DESCRIPTIONS from spacy
section_glossary = {
    "nlp": "Definition of the nlp object, its tokenizer and processing pipeline component names",
    "components": "Definitions of the pipeline components and their models.",
    "paths": "Paths to data and other assets. Re-used across the config as variables, e.g. ${paths.train}, and can be overwritten on the CLI.",
    "system": "Settings related to system and hardware. Re-used across the config as variables, e.g. ${system.seed}, and can be overwritten on the CLI.",
    "training": "Settings and controls for the training and evaluation process.",
    "pretraining": "Optional settings and controls for the language model pretraining.",
    "initialize": "Data resources and arguments passed to components when nlp.initialize is called before training (but not at runtime).",
    "corpora": "Readers for corpora like dev and train.",
}


def hover(
    server: SpacyLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """
    Implements the Hover functionality
    """
    document = server.workspace.get_document(params.text_document.uri)

    if not document:
        return None

    line_n = params.position.line
    line_str = document.lines[line_n]
    current_word, w_start, w_end = get_current_word(line_str, params.position.character)

    hover_display, h_start, h_end = registry_resolver(
        line_str, current_word, w_start, w_end
    )
    if hover_display == None:
        hover_display, h_start, h_end = section_resolver(
            line_str, current_word, w_start, w_end
        )

    if hover_display != None:
        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_display),
            range=Range(
                start=Position(line=line_n, character=h_start),
                end=Position(line=line_n, character=h_end + 1),
            ),
        )
    else:
        return None


def registry_resolver(
    line_str: str, current_word: str, w_start: int, w_end: int
) -> tuple[str, int, int]:
    """
    Check if currently hovered text is registered in the spaCy registry and return its description.

    ARGUMENTS:
    line_str (str): the current line as a string.
    current_word (str): the current word being hovered.
    w_start (int): The start index of the current_word.
    w_end (int): The end index of the current_word.

    RETURN:
    hover_display (str): The string to display in the hover box.
    w_start (int): The start index of the hover word (current_word)
    w_end (int): The end index of the hover word (current_word)
    """

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

    # Hardcoded renaming
    if registry_type == "factory":
        registry_type = "factories"

    try:
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

        return hover_display, r_start, r_end

    except Exception as e:
        return None, None, None


def detect_registry_names(
    line: str, word_start: int, word_end: int
) -> tuple[str, int, int]:
    """
    Detect if a word indicates a registry name

    ARGUMENTS:
    line (str): the current line as a string.
    word_start (int): The start index of the current hover word.
    word_end (int): The end index of the current hover word.

    RETURN:
    full_registry_name (str): The full registry name as a string
    registry_name_start (int): The start index of the full registry name
    registry_name_end (int): The end index of the full registry name

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
        registry_regex = r"[\w\d]*\.[\w\d]*(\.[\w\d]*)?"

        if re.match(registry_regex, full_registry_name):
            return full_registry_name, registry_name_start, registry_name_end
        else:
            # returns empty registry name, start index, and end index
            return None, None, None
    else:
        return None, None, None


def detect_registry_type(line: str, registry_start: int) -> tuple[str, int, int]:
    """
    Detect type and return type and name of registry

    ARGUMENTS:
    line (str): the current line as a string.
    registry_start (int): The start index of the current hover word.

    RETURN:
    full_registry_name (str): The full registry type as a string
    registry_name_start (int): The start index of the registry type
    registry_name_end (int): The end index of the registry type


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


def section_resolver(
    line_str: str, current_word: str, w_start: int, w_end: int
) -> tuple[str, int, int]:

    """
    Check if current hovered text is a section title and then return it's description

    ARGUMENTS:
    line_str (str): the current line as a string.
    current_word (str): the current word being hovered.
    w_start (int): The start index of the current_word.
    w_end (int): The end index of the current_word.

    RETURN:
    hover_display (str): The string to display in the hover box.
    w_start (int): The start index of the hover word (current_word)
    w_end (int): The end index of the hover word (current_word)

    EXAMPLES:
    [training]
    [training.batcher.size]
    """

    config_schemas = {
        "nlp": schemas.ConfigSchemaNlp,
        "training": schemas.ConfigSchemaTraining,
        "pretraining": schemas.ConfigSchemaPretrain,
        "initialize": schemas.ConfigSchemaInit,
    }

    try:
        # match the section titles, always start with a bracket
        if line_str[0] == "[":
            # break section into a list of components
            sections_list = line_str[1:-2].split(".")
            # if the current hover word is in the dictionary of descriptions
            if current_word in section_glossary.keys():
                # TODO Fine-Tune display message
                hover_display = (
                    f"## ⚙️ {current_word} \n {section_glossary[current_word]}"
                )
                return hover_display, w_start, w_end
            elif (
                current_word == sections_list[1]
                and sections_list[0] in config_schemas.keys()
            ):
                # get field title from the config schema
                field_title = (
                    config_schemas[sections_list[0]]
                    .__fields__[sections_list[1]]
                    .field_info.title
                )
                # TODO Fine-Tune display message
                hover_display = (
                    f"## ⚙️ {sections_list[0]} -> {sections_list[1]} \n {field_title}"
                )
                return hover_display, w_start, w_end
            else:
                return None, None, None
        else:
            return None, None, None

    except Exception as e:
        return None, None, None
