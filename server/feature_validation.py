"""Script containing all logic for validation functionality"""
from lsprotocol.types import DidOpenTextDocumentParams

from thinc.api import Config
from typing import Optional
from .spacy_server import SpacyLanguageServer


def validate_config(
    server: SpacyLanguageServer, cfg: Optional[str]
) -> Optional[Config]:
    """Validate .cfg files and return their Config object"""
    try:
        config = Config().from_str(cfg)  # type: ignore[arg-type]
        server.show_message_log("Validation Successful")
        return config
    except Exception as e:
        server.show_message_log("Validation Unsuccessful")
        server.show_message("Warning: Config not valid ")
        return None
