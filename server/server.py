from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_HOVER,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    Hover,
    TextDocumentPositionParams,
)

from typing import Optional
import spacy
from .feature_hover import hover
from .feature_validation import validate_on_open
from .spacy_server import SpacyLanguageServer


spacy_server = SpacyLanguageServer("pygls-spacy-server", "v0.1")


@spacy_server.feature(TEXT_DOCUMENT_HOVER)
def hover_feature(
    server: SpacyLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """Implement Hover functionality"""
    return hover(server, params)


@spacy_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: SpacyLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message("Config File Did Close")


@spacy_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(server: SpacyLanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    config = validate_on_open(params=params)
    if config:
        server.show_message("Config File Validation Successful")
        spacy_server.config = config
    else:
        server.show_message("Config File Validation Unsuccessful")
        spacy_server.config = None


# Temporary for testing
@spacy_server.command(spacy_server.SPACY_TEST)
def spaCy_test(ls, *args):
    nlp = spacy.blank("en")
    doc = nlp("This is great!")
    ls.show_message(f"spaCy loaded! {doc.text}")
