"""Script containing all logic for validation functionality"""
from lsprotocol.types import DidOpenTextDocumentParams

from thinc.api import Config
from typing import Optional


def validate_on_open(params: DidOpenTextDocumentParams) -> Optional[Config]:
    """Validate .cfg files and return their Config object"""
    try:
        return Config().from_str(params.text_document.text)
    except Exception as e:
        # TODO Exception handling
        return None
