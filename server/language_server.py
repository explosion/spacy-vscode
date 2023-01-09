from pygls.server import LanguageServer


class SpaCyLanguageServer(LanguageServer):
    """
    The language server is responsible for receiving and sending messages over the Language Server Protocol
    which is based on the Json RPC protocol.
    DOCS: https://pygls.readthedocs.io/en/latest/pages/advanced_usage.html#language-server
    """

    SPACY_TEST = "spacy_test"

    def __init__(self, *args):
        super().__init__(*args)
