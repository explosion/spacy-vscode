import argparse
import logging
from .server import spacy_server

logging.basicConfig(filename="pygls.log", level=logging.DEBUG, filemode="w")

def add_arguments(parser):
    parser.description = "spacy server"

    parser.add_argument(
        "--tcp", action="store_true",
        help="Use TCP server"
    )
    parser.add_argument(
        "--ws", action="store_true",
        help="Use WebSocket server"
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Bind to this address"
    )
    parser.add_argument(
        "--port", type=int, default=2087,
        help="Bind to this port"
    )


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.tcp:
        spacy_server.start_tcp(args.host, args.port)
    elif args.ws:
        spacy_server.start_ws(args.host, args.port)
    else:
        spacy_server.start_io()


if __name__ == '__main__':
    main()
