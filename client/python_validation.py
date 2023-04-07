import sys
from distutils.version import LooseVersion
import argparse

parser = argparse.ArgumentParser(description="Script to validate python interpreter")
parser.add_argument("pygls_version", help="Required version of pygls")
parser.add_argument("spacy_version", help="Required version of spaCy")
args = parser.parse_args()

try:
    import pygls

    if LooseVersion(pygls.__version__) >= LooseVersion(args.pygls_version):
        try:
            import spacy

            if LooseVersion(spacy.__version__) >= LooseVersion(args.spacy_version):
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
