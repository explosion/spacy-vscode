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
        return SpanInfo("", 0, 0)

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
    docstring_split = docstring.split("\n\n")

    has_func = False
    has_args = False
    has_format = False

    # test docstring for formatting features
    if docstring_split[0].count("make_") == 1:
        has_func = True
    if docstring_split[-1].count(":") > 1 and docstring_split[-1].count("make_") != 1:
        has_args = True
    if "\n       " in docstring:
        has_format = True

    # if no re-formatting features, return the docstring as is
    if not has_func and not has_args and not has_format:
        return docstring

    # if the string has a make function and not argument descriptions,
    # just return the arguments and other additional info if present
    if has_func:
        if not has_args:
            registry_arguments = docstring_split[0]
            registry_arguments = "\n\n - ".join(
                registry_arguments.split("(")[1][:-1].split(",")
            )
            # remove first paragraph from docstring
            registry_info = "\n\n".join(docstring_split[1:]) or ""
        # remove the make function
        docstring_split = docstring_split[1:]

    # if docstring has formatting issues and has an argument list
    if has_format and has_args:
        # create the arguments list from the last paragraph,
        # remove unnessesary \n and replace others with paragraph breaking \n\n and bullet points
        registry_arguments = (
            docstring_split[-1][:-2]
            .replace("\n       ", "")
            .replace("\n   ", "\n\n - ")
        )
        # reformat all other paragraphs
        # remove unnessesary \n and replace others with paragraph breaking \n\n
        registry_info = (
            "\n\n".join(docstring_split[:-1]).replace("\n   ", "").replace("\n", "\n\n")
        )
    elif has_args:
        # create the arguments list from the last paragraph,
        # remove unnessesary \n and replace others with paragraph breaking \n\n and bullet points
        registry_arguments = (
            docstring_split[-1].replace("\n   ", "").replace("\n", "\n\n - ")
        )
        # remove last paragraph from info
        registry_info = "\n\n".join(docstring_split[:-1])

    if registry_arguments:
        formatted_docstring = (
            f"{registry_info}\n#### Arguments:\n\n - {registry_arguments}"
        )
        return formatted_docstring
    elif has_func:
        # if make function name is present with no arguments, return no description
        return "Currently no description available"
    else:
        return docstring
