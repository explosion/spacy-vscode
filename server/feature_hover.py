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
    "paths": "Paths to data and other assets. Re-used across the config as variables, e.g. ${paths.train}, and can be overridden by the CLI.",
    "system": "Settings related to system and hardware. Re-used across the config as variables, e.g. ${system.seed}, and can be overridden by the CLI.",
    "training": "Settings and controls for the training and evaluation process.",
    "pretraining": "Optional settings and controls for the language model pretraining.",
    "initialize": "Data resources and arguments passed to components when `nlp.initialize` is called before training (but not at inference-time).",
    "corpora": "Readers for corpora like dev and train.",
}


@dataclass
class HoverInfo:
    display_string: str  # Can have markdown elements
    start: int  # Start index of the source string
    end: int  # End index of the source string


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
    current_span = get_current_word(line_str, params.position.character)

    hover_object = registry_resolver(
        line_str, current_span.span_string, current_span.start, current_span.end
    )
    if hover_object is None:
        hover_object = section_resolver(
            line_str, current_span.span_string, current_span.start, current_span.end
        )

    if hover_object is not None:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown, value=hover_object.display_string
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
) -> Optional[HoverInfo]:
    """
    Check if currently hovered text is registered in the spaCy registry and return its description.

    ARGUMENTS:
    line_str (str): the current line as a string.
    current_word (str): the current word being hovered.
    w_start (int): The start index of the current_word.
    w_end (int): The end index of the current_word.
    """

    registry_span = detect_registry_func(line_str, current_word)
    if registry_span:
        registry_func = registry_span.span_string
        r_start = registry_span.start
        r_end = registry_span.end
        registry_name = detect_registry_name(line_str, r_start)

    # Special Case for Factories
    # Because their registry_names can be "ner", "textcat"
    elif line_str.find("factory") != -1:
        registry_func = current_word
        r_start = w_start
        r_end = w_end
        registry_name = "factories"
    else:
        return None

    try:
        # Retrieve data from registry
        registry_desc = registry.find(registry_name, registry_func)

    except RegistryError as e:
        return None

    registry_docstring = registry_desc.get("docstring", "Currently no description available")

    # TODO Create link to codebase (if possible)
    # if registry_desc["file"] is not None:
    # registry_path = f"➡️ [Go to code]({registry_desc['file']})"

    # TODO Fine-Tune display message
    hover_display = f"## ⚙️ {registry_func}\n{registry_docstring}"

    return HoverInfo(hover_display, r_start, r_end)


def detect_registry_func(line: str, current_word: str) -> Optional[SpanInfo]:
    """
    Detect if a word indicates a registry name

    ARGUMENTS:
    line (str): the current line as a string.
    current_word (str): the current word as a string.

    EXAMPLES:
    spacy.registry_name_.v1
    spacy-legacy.registry_name.v2
    compounding.v1
    """
    # match optional first segment (i.e. <letters and underscores>.), required second segment and version (i.e. "<letters and underscores>.v<any_numbers>")
    registry_regex = r"([\w]*\.)?[\w]*\.v[\d]*"
    registry_match = re.search(registry_regex, line)

    if registry_match is None:
        return None
    else:
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
) -> Optional[HoverInfo]:

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

    # match the section titles, always start with a bracket
    if line_str[0] == "[":
        # break section into a list of components
        sections_list = line_str[1:-2].split(".")
        # if the current hover word is in the dictionary of descriptions
        if current_word in CONFIG_DESCRIPTIONS.keys():
            # TODO Fine-Tune display message
            hover_display = f"## ⚙️ {current_word}\n{CONFIG_DESCRIPTIONS[current_word]}"
            return HoverInfo(hover_display, w_start, w_end)
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
                f"## ⚙️ {sections_list[0]} -> {sections_list[1]}\n{field_title}"
            )
            return HoverInfo(hover_display, w_start, w_end)
        else:
            return None
    else:
        return None
