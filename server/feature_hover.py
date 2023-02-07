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
from .util import get_current_word, SpanInfo
from dataclasses import dataclass
from catalogue import RegistryError

# TODO: glossary for now, to be replaced with glossary.CONFIG_DESCRIPTIONS from spacy
CONFIG_DESCRIPTIONS = {
    "nlp": "Definition of the `Language` object, its tokenizer and processing pipeline component names.",
    "components": "Definitions of the pipeline components and their models. Pipeline components can be found in [nlp].",
    "paths": "Paths to data and other assets. Re-used across the config as variables, e.g. `${paths.train}`, and can be overridden by the CLI.",
    "system": "Settings related to system and hardware. Re-used across the config as variables, e.g. `${system.seed}`, and can be overridden by the CLI.",
    "training": "Settings and controls for the training and evaluation process.",
    "pretraining": "Optional settings and controls for the language model pretraining.",
    "initialize": "Data resources and arguments passed to components when `nlp.initialize` is called before training (but not at inference-time).",
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

    # get the config as a dictinary
    config_dict = server.config

    line_n = params.position.line
    line_str = document.lines[line_n]
    current_span = get_current_word(line_str, params.position.character)

    hover_object = registry_resolver(
        line_str, current_span.span_string, current_span.start, current_span.end
    )
    if hover_object is None:
        hover_object = section_resolver(
            line_str, current_span.span_string, current_span.start, current_span.end
        )
        if hover_object is None:
            hover_object = variable_resolver(line_str, config_dict)

    if hover_object is not None:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown, value=hover_object.span_string
            ),
            range=Range(
                start=Position(line=line_n, character=hover_object.start),
                end=Position(line=line_n, character=hover_object.end + 1),
            ),
        )
    else:
        return None


def registry_resolver(
    line_str: str, current_word: str, w_start: int, w_end: int
) -> Optional[SpanInfo]:
    """
    Check if currently hovered text is registered in the spaCy registry and return its description.

    ARGUMENTS:
    line_str (str): the current line as a string.
    current_word (str): the current word being hovered.
    w_start (int): The start index of the current_word.
    w_end (int): The end index of the current_word.
    """

    registry_span = detect_registry_func(line_str, current_word, w_start, w_end)
    if registry_span:
        # the name of the function within the registry
        registry_func = registry_span.span_string
        r_start = registry_span.start
        r_end = registry_span.end
        # the name of the registry, e.x. "architectures" or "factory"
        registry_name = detect_registry_name(line_str, r_start)
    else:
        return None

    # hardcoded renaming for factories
    if registry_name == "factory":
        registry_name = "factories"

    try:
        # Retrieve data from registry
        registry_desc = registry.find(registry_name, registry_func)

    except RegistryError as e:
        return None

    # get link to the GitHub code for the registry
    registry_link = ""
    if registry_desc["file"]:
        registry_path = registry_desc["file"]
        line_no = registry_desc["line_no"]
        registry_link = f"[Go to code]({registry_path}#L{line_no})"

    # find registry description or return no description
    registry_docstring = (
        registry_desc.get("docstring") or "Currently no description available"
    )

    # Fix the formatting of docstrings for display in hover
    if registry_docstring.split("\n\n")[-1].count(":") > 1:
        # factories have different formatting than other registry functions
        if registry_name == "factories":
            registry_arguments = (
                registry_docstring.split("\n\n")[-1][:-2]
                .replace("\n       ", "")
                .replace("\n   ", "\n\n - ")
            )
            registry_info = (
                "\n\n".join(registry_docstring.split("\n\n")[:-2])
                .replace("\n   ", "")
                .replace("\n", "\n\n")
            )

            hover_display = f"### (*registry*) {registry_func}\n\n{registry_link}\n\n{registry_info}\n#### Arguments:\n\n - {registry_arguments}"
        else:
            registry_arguments = (
                registry_docstring.split("\n\n")[-1]
                .replace("\n   ", "")
                .replace("\n", "\n\n - ")
            )
            registry_info = "\n\n".join(registry_docstring.split("\n\n")[:-1])
            hover_display = f"### (*registry*) {registry_func}\n\n{registry_link}\n\n{registry_info}\n#### Arguments:\n\n - {registry_arguments}"
    else:
        hover_display = f"### (*registry*) {registry_func}\n\n{registry_link}\n\n{registry_docstring}"

    return SpanInfo(hover_display, r_start, r_end)


def detect_registry_func(
    line: str, current_word: str, w_start: int, w_end: int
) -> Optional[SpanInfo]:
    """
    Detect if a word indicates a registry name

    ARGUMENTS:
    line (str): the current line as a string.
    current_word (str): the current word as a string.
    w_start (int): The start index of the current_word.
    w_end (int): The end index of the current_word.

    EXAMPLES:
    spacy.registry_name_.v1
    spacy-legacy.registry_name.v2
    compounding.v1
    textcat
    """

    # Special Case for Factories
    # Because their registry_names can be "ner", "textcat"
    if "factory" in line:
        return SpanInfo(current_word, w_start, w_end)

    # match optional first segment (i.e. <letters and underscores>.), required second segment and version (i.e. "<letters and underscores>.v<any_numbers>")
    registry_regex = r"([\w]*\.)?[\w]*\.v[\d]*"
    registry_match = re.search(registry_regex, line)

    if registry_match is None:
        return None

    full_registry_func = registry_match.group(0)
    if current_word in full_registry_func:
        # if actually hovering over part of the registry name, return values
        registry_func_start = registry_match.span()[0]
        registry_func_end = registry_match.span()[1] - 1
        return SpanInfo(full_registry_func, registry_func_start, registry_func_end)
    else:
        return None


def detect_registry_name(line: str, registry_start: int) -> str:
    """
    Detect type and return type and name of registry

    ARGUMENTS:
    line (str): the current line as a string.
    registry_start (int): The start index of the current hover word.

    RETURN:
    full_registry_func (str): The full registry function as a string

    EXAMPLE:
    @architecture
    factory
    """

    if registry_start <= 0:
        return ""

    for i in range(registry_start - 1, 0, -1):
        if re.match("\W", line[i]):
            continue
        else:
            type_span = get_current_word(line, i)
            return type_span.span_string


def section_resolver(
    line_str: str, current_word: str, w_start: int, w_end: int
) -> Optional[SpanInfo]:
    """
    Check if current hovered text is a section title and then return it's description

    ARGUMENTS:
    line_str (str): the current line as a string.
    current_word (str): the current word being hovered.
    w_start (int): The start index of the current_word.
    w_end (int): The end index of the current_word.

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

    # match the section titles, always start with a bracket and more than 1 character
    if line_str[0] != "[" or len(current_word) <= 1:
        return None

    # break section into a list of components
    sections_list = line_str[1:-2].split(".")
    # if the current hover word is in the dictionary of descriptions
    if current_word in CONFIG_DESCRIPTIONS.keys():
        hover_display = (
            f"(*section*) **{current_word}**: {CONFIG_DESCRIPTIONS[current_word]}"
        )
        return SpanInfo(hover_display, w_start, w_end)
    elif current_word == sections_list[1] and sections_list[0] in config_schemas.keys():
        # get field title from the config schema
        field_title = (
            config_schemas[sections_list[0]]
            .__fields__[sections_list[1]]
            .field_info.title
        )
        hover_display = (
            f"(*section*) {sections_list[0]} -> **{sections_list[1]}**: {field_title}"
        )
        return SpanInfo(hover_display, w_start, w_end)
    else:
        return None


def variable_resolver(
    line_str: str,
    config_dict: dict,
) -> Optional[SpanInfo]:
    """
    Check if current hovered text is a section title and then return it's description

    ARGUMENTS:
    line_str (str): the current line as a string.
    config_dict (dict): the config file as a dictionary

    EXAMPLES:
    ${system.seed}
    ${components.tok2vec.model.encode.width}
    """

    # match the variables, always enclosed with ${<string>}
    variable_regex = r"(?<=\$\{)[^][]*(?=})"
    variable_match = re.search(variable_regex, line_str)

    if variable_match is None:
        return None

    variable_list = variable_match.group(0).split(".")
    v_start = variable_match.span()[0]
    v_end = variable_match.span()[1] - 1

    # get value for final item in the variable from nested config dict
    for key in variable_list[:-1]:
        config_dict = config_dict.setdefault(key, {})
    variable_value = config_dict[variable_list[-1]]

    hover_display = (
        f"(*variable*) **{'.'.join(variable_list)}**: `{str(variable_value)}`"
    )
    return SpanInfo(hover_display, v_start, v_end)
