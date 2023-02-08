"""Script for utility functions that can be used across the other implementations"""

import re
from dataclasses import dataclass


@dataclass
class SpanInfo:
    span_string: str  # The span text, can have markdown elements
    start: int  # Start index of the string
    end: int  # End index of the string


def get_current_word(line: str, start_pos: int) -> SpanInfo:
    """
    Returns the a span string seperated by non-word characters

    EXAMPLE OUTPUT:
    ('architectures', 1, 13)
    ('spacy', 18, 22)
    """

    # Verify index lies within boundaries
    if start_pos < 0 or start_pos >= len(line):
        return "", 0, 0

    end_i = start_pos
    start_i = start_pos

    for i in range(start_pos, len(line), 1):
        if re.match("\W", line[i]):
            break
        else:
            end_i = i

    for i in range(start_pos, -1, -1):
        if re.match("\W", line[i]):
            break
        else:
            start_i = i

    return SpanInfo(line[start_i : end_i + 1], start_i, end_i)


def format_docstrings(docstring: str):
    """
    Formats the docstring into compatible Markdown for hover display
    """

    if docstring.split("\n\n")[-1].count(":") > 1:
        # some docstrings have different formatting than others
        if "\n       " in docstring:
            registry_arguments = (
                docstring.split("\n\n")[-1][:-2]
                .replace("\n       ", "")
                .replace("\n   ", "\n\n - ")
            )
            registry_info = (
                "\n\n".join(docstring.split("\n\n")[:-2])
                .replace("\n   ", "")
                .replace("\n", "\n\n")
            )

            formatted_docstring = (
                f"{registry_info}\n#### Arguments:\n\n - {registry_arguments}"
            )
        else:
            registry_arguments = (
                docstring.split("\n\n")[-1]
                .replace("\n   ", "")
                .replace("\n", "\n\n - ")
            )
            registry_info = "\n\n".join(docstring.split("\n\n")[:-1])
            formatted_docstring = (
                f"{registry_info}\n#### Arguments:\n\n - {registry_arguments}"
            )
    else:
        formatted_docstring = docstring

    return formatted_docstring
