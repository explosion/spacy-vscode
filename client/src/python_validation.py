import sys
from packaging import version
import argparse

parser = argparse.ArgumentParser(description="Script to validate python interpreter")
parser.add_argument("pygls_version", help="Required version of pygls")
parser.add_argument("spacy_version", help="Required version of spaCy")
args = parser.parse_args()

try:
    import pygls

    if version.parse(pygls.__version__) >= version.parse(args.pygls_version):
        try:
            import spacy

            if version.parse(spacy.__version__) >= version.parse(args.spacy_version):
                sys.stdout.write("I003")
            else:
                sys.stdout.write("E009")
        except ModuleNotFoundError as e:
            sys.stdout.write("E007")
    else:
        sys.stdout.write("E008")

except ModuleNotFoundError as e:
    sys.stdout.write("E006")
