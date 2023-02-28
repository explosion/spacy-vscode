from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_HOVER,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    Hover,
    TextDocumentPositionParams,
)

from typing import Optional
import spacy
from .feature_hover import hover
from .feature_validation import validate_config
from .spacy_server import SpacyLanguageServer


spacy_server = SpacyLanguageServer("pygls-spacy-server", "v0.1")


@spacy_server.feature(TEXT_DOCUMENT_HOVER)
def hover_feature(
    server: SpacyLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """Implement Hover functionality"""
    return hover(server, params)


@spacy_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(server: SpacyLanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    spacy_server.config = validate_config(server=server, cfg=params.text_document.text)


@spacy_server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(server: SpacyLanguageServer, params: DidSaveTextDocumentParams):
    """Text document did save notification."""
    spacy_server.config = validate_config(server=server, cfg=params.text)
