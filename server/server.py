from pygls.lsp.methods import (
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    HOVER,
)
from pygls.lsp.types import (
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    Hover,
    TextDocumentPositionParams,
)

from typing import Optional
import spacy
from .feature_hover import hover
from .language_server import SpaCyLanguageServer


spacy_server = SpaCyLanguageServer("pygls-spacy-server", "v0.1")


@spacy_server.feature(HOVER)
def hover_feature(
    server: SpaCyLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """Implement all Hover functionality"""
    return hover(server, params)


# Temporary for testing
@spacy_server.command(spacy_server.SPACY_TEST)
def spaCy_test(ls, *args):
    nlp = spacy.blank("en")
    doc = nlp("This is great!")
    ls.show_message(f"spaCy loaded! {doc.text}")


# Temporary for testing
@spacy_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: SpaCyLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message("Config File Did Close")


# Temporary for testing
@spacy_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message("Config File Did Open")
