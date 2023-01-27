import pytest
from mock import Mock
from lsprotocol.types import (
    TextDocumentIdentifier,
    TextDocumentPositionParams,
    Position,
)
from pygls.workspace import Document, Workspace
from thinc.api import Config

from ..server import hover_feature


class FakeServer:
    """We don't need real server to unit test features."""

    publish_diagnostics = None
    show_message = None
    show_message_log = None

    def __init__(self):
        self.workspace = Workspace("", None)
        self.config: Config = None


fake_document_uri = "file://fake_config.cfg"
fake_document_content = """
[paths]
train = null
dev = null
vectors = null
init_tok2vec = null

[system]
gpu_allocator = null
seed = 0

[nlp]
lang = "id"
pipeline = ["tok2vec","ner"]
batch_size = 1000
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}

[components]

[components.ner]
factory = "ner"
moves = null
update_with_oracle_cut_size = 100

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true
nO = null

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode.width}
upstream = "*"

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = ${components.tok2vec.model.encode.width}
attrs = ["NORM","PREFIX","SUFFIX","SHAPE"]
rows = [5000,2500,2500,2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[corpora]

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}
max_length = 0
gold_preproc = false
limit = 0
augmenter = null

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
max_length = 2000
gold_preproc = false
limit = 0
augmenter = null

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
max_steps = 20000
eval_frequency = 200
frozen_components = []
before_to_disk = null

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2
get_length = null

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
t = 0.0

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = false
eps = 0.00000001
learn_rate = 0.001

[training.score_weights]
ents_per_type = null
ents_f = 1.0
ents_p = 0.0
ents_r = 0.0

[pretraining]

[initialize]
vectors = null
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.tokenizer]
"""
fake_document = Document(fake_document_uri, fake_document_content)


server = FakeServer()
server.publish_diagnostics = Mock()
server.show_message = Mock()
server.show_message_log = Mock()
server.workspace.get_document = Mock(return_value=fake_document)


def _reset_mocks():
    server.publish_diagnostics.reset_mock()
    server.show_message.reset_mock()
    server.show_message_log.reset_mock()


# Test Hover Resolve Registries
@pytest.mark.parametrize(
    "line, character, registry_name",
    [
        (19, 36, "spacy.Tokenizer.v1"),
        (24, 13, "ner"),
        (43, 14, "tok2vec"),
        (49, 32, "spacy.MultiHashEmbed.v2"),
        (56, 34, "spacy.MaxoutWindowEncoder.v2"),
        (73, 22, "spacy.Corpus.v1"),
        (95, 23, "spacy.batch_by_words.v1"),
        (101, 22, "compounding.v1"),
    ],
)
def test_resolve_registries(line, character, registry_name):
    _reset_mocks()
    params = TextDocumentPositionParams(
        text_document=TextDocumentIdentifier(uri=fake_document.uri),
        position=Position(line=line, character=character),
    )
    hover_obj = hover_feature(server, params)
    assert registry_name in hover_obj.contents.value
