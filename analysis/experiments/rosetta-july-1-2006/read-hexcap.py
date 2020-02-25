#!/usr/bin/python
import logging
import sys

import scapy
import scapy.all

logging.basicConfig(level=logging.INFO)
import argparse
from pprint import pformat, pprint


def get_argparse():

    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=argparse.FileType("r"))
    return parser


def do_input(stream):
    # pprint(stream)
    print(stream.name)
    text = stream.read()
    # scapy.all.import_hexcap( )


def main(*args):
    parser = get_argparse()
    args = parser.parse_args()
    pprint(args)
    for stream in args.inputs:
        do_input(stream)


if __name__ == "__main__":
    main(*sys.argv)
    logging.info("hello world")
