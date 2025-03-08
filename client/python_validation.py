import sys
from distutils.version import LooseVersion
import argparse

if sys.version_info < (3, 9):
    import importlib_metadata as metadata
else:
    import importlib.metadata as metadata

parser = argparse.ArgumentParser(description="Script to validate python interpreter")
parser.add_argument("pygls_version", help="Required version of pygls")
parser.add_argument("spacy_version", help="Required version of spaCy")
args = parser.parse_args()


try:
    pygls_version = metadata.version("pygls")
    if LooseVersion(pygls.__version__) >= LooseVersion(args.pygls_version):
        spacy_version = metadata.version("spacy")
        try:
            if LooseVersion(spacy_version) >= LooseVersion(args.spacy_version):
                sys.stdout.write("I003")
                sys.exit()
            else:
                sys.stdout.write("E009")
                sys.exit()
        except ModuleNotFoundError as e:
            sys.stdout.write("E007")
            sys.exit()
    else:
        sys.stdout.write("E008")
        sys.exit()

except ModuleNotFoundError as e:
    sys.stdout.write("E006")
    sys.exit()
