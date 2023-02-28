import pytest
from mock import Mock
from lsprotocol.types import (
    TextDocumentIdentifier,
    TextDocumentPositionParams,
    Position,
)
from pygls.workspace import Document, Workspace
from thinc.api import Config
from spacy import registry

from ..server import hover_feature
from ..feature_validation import validate_config
from ..util import format_docstrings


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

fake_document_content_non_valid = """
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
state_typtokens = false
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

[tra]
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

[training.batch
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
t = 0.0

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_

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
ents  1.0
ents_p = 0.0
ents_r = 0.0

[pretraining]

[initialize]
vectors = n
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.compo

[initialize.tokenizer]
"""

server = FakeServer()
server.publish_diagnostics = Mock()  # type:ignore[assignment]
server.show_message = Mock()  # type:ignore[assignment]
server.show_message_log = Mock()  # type:ignore[assignment]
server.workspace.get_document = Mock(return_value=fake_document)


def _reset_mocks():
    server.publish_diagnostics.reset_mock()
    server.show_message.reset_mock()
    server.show_message_log.reset_mock()


# Test Hover Resolve Registries
@pytest.mark.parametrize(
    "line, character, registry_func",
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
def test_resolve_registries(line, character, registry_func):
    _reset_mocks()
    params = TextDocumentPositionParams(
        text_document=TextDocumentIdentifier(uri=fake_document.uri),
        position=Position(line=line, character=character),
    )
    hover_obj = hover_feature(server, params)
    assert registry_func in hover_obj.contents.value


# Test Hover Resolve Sections
@pytest.mark.parametrize(
    "line, character, section_name",
    [
        (72, 1, "corpora"),
        (80, 1, "training"),
        (94, 10, "batcher"),
    ],
)
def test_resolve_sections(line, character, section_name):
    _reset_mocks()
    params = TextDocumentPositionParams(
        text_document=TextDocumentIdentifier(uri=fake_document.uri),
        position=Position(line=line, character=character),
    )
    hover_obj = hover_feature(server, params)
    assert section_name in hover_obj.contents.value


# Test formatting of docstrings
@pytest.mark.parametrize(
    "registry_func, registry_name, docstring, formatted_docstring",
    [
        (
            "spacy.Tokenizer.v1",
            "tokenizers",
            "Registered function to create a tokenizer. Returns a factory that takes\nthe nlp object and returns a Tokenizer instance using the language detaults.",
            "Registered function to create a tokenizer. Returns a factory that takes\nthe nlp object and returns a Tokenizer instance using the language detaults.",
        ),
        (
            "ner",
            "factories",
            "make_ner(nlp: Language, name: str, model: Model, moves: Optional[TransitionSystem], update_with_oracle_cut_size: int, incorrect_spans_key: Optional[str], scorer: Optional[Callable])\nCreate a transition-based EntityRecognizer component. The entity recognizer\n    identifies non-overlapping labelled spans of tokens.\n\n    The transition-based algorithm used encodes certain assumptions that are\n    effective for \"traditional\" named entity recognition tasks, but may not be\n    a good fit for every span identification problem. Specifically, the loss\n    function optimizes for whole entity accuracy, so if your inter-annotator\n    agreement on boundary tokens is low, the component will likely perform poorly\n    on your problem. The transition-based algorithm also assumes that the most\n    decisive information about your entities will be close to their initial tokens.\n    If your entities are long and characterised by tokens in their middle, the\n    component will likely do poorly on your task.\n\n    model (Model): The model for the transition-based parser. The model needs\n        to have a specific substructure of named components --- see the\n        spacy.ml.tb_framework.TransitionModel for details.\n    moves (Optional[TransitionSystem]): This defines how the parse-state is created,\n        updated and evaluated. If 'moves' is None, a new instance is\n        created with `self.TransitionSystem()`. Defaults to `None`.\n    update_with_oracle_cut_size (int): During training, cut long sequences into\n        shorter segments by creating intermediate states based on the gold-standard\n        history. The model is not very sensitive to this parameter, so you usually\n        won't need to change it. 100 is a good default.\n    incorrect_spans_key (Optional[str]): Identifies spans that are known\n        to be incorrect entity annotations. The incorrect entity annotations\n        can be stored in the span group, under this key.\n    scorer (Optional[Callable]): The scoring method.\n    ",
            "make_ner(nlp: Language, name: str, model: Model, moves: Optional[TransitionSystem], update_with_oracle_cut_size: int, incorrect_spans_key: Optional[str], scorer: Optional[Callable])\n\nCreate a transition-based EntityRecognizer component. The entity recognizer identifies non-overlapping labelled spans of tokens.\n#### Arguments:\n\n -     model (Model): The model for the transition-based parser. The model needs to have a specific substructure of named components --- see the spacy.ml.tb_framework.TransitionModel for details.\n\n -  moves (Optional[TransitionSystem]): This defines how the parse-state is created, updated and evaluated. If 'moves' is None, a new instance is created with `self.TransitionSystem()`. Defaults to `None`.\n\n -  update_with_oracle_cut_size (int): During training, cut long sequences into shorter segments by creating intermediate states based on the gold-standard history. The model is not very sensitive to this parameter, so you usually won't need to change it. 100 is a good default.\n\n -  incorrect_spans_key (Optional[str]): Identifies spans that are known to be incorrect entity annotations. The incorrect entity annotations can be stored in the span group, under this key.\n\n -  scorer (Optional[Callable]): The scoring method.\n  ",
        ),
        (
            "tok2vec",
            "factories",
            "Currently no description available",
            "Currently no description available",
        ),
        (
            "spacy.MultiHashEmbed.v2",
            "architectures",
            "Construct an embedding layer that separately embeds a number of lexical\nattributes using hash embedding, concatenates the results, and passes it\nthrough a feed-forward subnetwork to build a mixed representation.\n\nThe features used can be configured with the 'attrs' argument. The suggested\nattributes are NORM, PREFIX, SUFFIX and SHAPE. This lets the model take into\naccount some subword information, without constructing a fully character-based\nrepresentation. If pretrained vectors are available, they can be included in\nthe representation as well, with the vectors table kept static\n(i.e. it's not updated).\n\nThe `width` parameter specifies the output width of the layer and the widths\nof all embedding tables. If static vectors are included, a learned linear\nlayer is used to map the vectors to the specified width before concatenating\nit with the other embedding outputs. A single Maxout layer is then used to\nreduce the concatenated vectors to the final width.\n\nThe `rows` parameter controls the number of rows used by the `HashEmbed`\ntables. The HashEmbed layer needs surprisingly few rows, due to its use of\nthe hashing trick. Generally between 2000 and 10000 rows is sufficient,\neven for very large vocabularies. A number of rows must be specified for each\ntable, so the `rows` list must be of the same length as the `attrs` parameter.\n\nwidth (int): The output width. Also used as the width of the embedding tables.\n    Recommended values are between 64 and 300.\nattrs (list of attr IDs): The token attributes to embed. A separate\n    embedding table will be constructed for each attribute.\nrows (List[int]): The number of rows in the embedding tables. Must have the\n    same length as attrs.\ninclude_static_vectors (bool): Whether to also use static word vectors.\n    Requires a vectors table to be loaded in the Doc objects' vocab.",
            "Construct an embedding layer that separately embeds a number of lexical\nattributes using hash embedding, concatenates the results, and passes it\nthrough a feed-forward subnetwork to build a mixed representation.\n\nThe features used can be configured with the 'attrs' argument. The suggested\nattributes are NORM, PREFIX, SUFFIX and SHAPE. This lets the model take into\naccount some subword information, without constructing a fully character-based\nrepresentation. If pretrained vectors are available, they can be included in\nthe representation as well, with the vectors table kept static\n(i.e. it's not updated).\n\nThe `width` parameter specifies the output width of the layer and the widths\nof all embedding tables. If static vectors are included, a learned linear\nlayer is used to map the vectors to the specified width before concatenating\nit with the other embedding outputs. A single Maxout layer is then used to\nreduce the concatenated vectors to the final width.\n\nThe `rows` parameter controls the number of rows used by the `HashEmbed`\ntables. The HashEmbed layer needs surprisingly few rows, due to its use of\nthe hashing trick. Generally between 2000 and 10000 rows is sufficient,\neven for very large vocabularies. A number of rows must be specified for each\ntable, so the `rows` list must be of the same length as the `attrs` parameter.\n#### Arguments:\n\n - width (int): The output width. Also used as the width of the embedding tables. Recommended values are between 64 and 300.\n\n - attrs (list of attr IDs): The token attributes to embed. A separate embedding table will be constructed for each attribute.\n\n - rows (List[int]): The number of rows in the embedding tables. Must have the same length as attrs.\n\n - include_static_vectors (bool): Whether to also use static word vectors. Requires a vectors table to be loaded in the Doc objects' vocab.",
        ),
    ],
)
def test_hover_formatting(registry_func, registry_name, docstring, formatted_docstring):
    _reset_mocks()

    registry_desc = registry.find(registry_name, registry_func)

    registry_docstring = (
        registry_desc.get("docstring") or "Currently no description available"
    )
    assert registry_docstring == docstring

    registry_formatted_docstring = format_docstrings(registry_docstring)
    assert registry_formatted_docstring == formatted_docstring


# Test validation of configs
@pytest.mark.parametrize(
    "cfg, valid",
    [(fake_document_content, True), (fake_document_content_non_valid, False)],
)
def test_validation(cfg, valid):
    _reset_mocks()
    config = validate_config(server, cfg)
    if config:
        _valid = True
    else:
        _valid = False
    assert _valid == valid
