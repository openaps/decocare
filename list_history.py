#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse

# from datetime import datetime
# from scapy.all import *
import json
import sys
import textwrap
from binascii import hexlify
from pprint import pformat, pprint

from decocare import history, lib, models
from decocare.history import HistoryPage, parse_record


def get_opt_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile",
        nargs="+",
        default=sys.stdin,
        type=argparse.FileType("r"),
        help="Find dates in this file.",
    )

    parser.add_argument("--collate", dest="collate", default=False, action="store_true")

    parser.add_argument("--larger", dest="larger", action="store_true")

    parser.add_argument("--no-larger", dest="larger", action="store_false")

    parser.add_argument(
        "--model",
        # type=get_model,
        choices=list(models.known.keys()),
    )

    parser.add_argument(
        "--out",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="Write records here.",
    )
    parser.set_defaults(larger=False)
    return parser


##
# move to history.py
#


def eat_nulls(fd):
    nulls = bytearray()
    for B in iter(lambda: bytearray(fd.read(1)), bytearray("")):
        if B[0] == 0x00:
            nulls.extend(B)
        else:
            fd.seek(fd.tell() - 1)
            break
    print("found %s nulls" % len(nulls))
    return nulls


def find_records(stream, opts):
    records = []
    errors = []
    bolus = bytearray()
    extra = bytearray()
    opcode = ""

    for B in iter(lambda: bytearray(stream.read(2)), bytearray("")):

        if B == bytearray([0x00, 0x00]):
            print(("#### STOPPING DOUBLE NULLS @ %s," % stream.tell()), end=" ")
            nulls = eat_nulls(stream)
            print("reading more to debug %#04x" % B[0])
            print(lib.hexdump(B, indent=4))
            print(lib.int_dump(B, indent=11))

            extra = bytearray(stream.read(32))
            print("##### DEBUG HEX")
            print(lib.hexdump(extra, indent=4))
            print("##### DEBUG DECIMAL")
            print(lib.int_dump(extra, indent=11))
            # print("XXX:???:XXX", history.parse_date(bolus).isoformat( ))
            break
        record = parse_record(stream, B, larger=opts.larger)
        records.append(record)

    return records


def main():
    parser = get_opt_parser()
    opts = parser.parse_args()
    tw_opts = {
        "width": 50,
        "subsequent_indent": "          ",
        "initial_indent": "       ",
    }
    wrapper = textwrap.TextWrapper(**tw_opts)
    for stream in opts.infile:
        print("## START %s" % (stream.name))
        records = []
        if opts.collate:
            page = HistoryPage(bytearray(stream.read()), opts.model)
            records.extend(page.decode(larger=opts.larger))
        else:
            records = find_records(stream, opts)
        i = 0
        for record in records:

            prefix = "#### RECORD {} {}".format(i, str(record))
            if getattr(record, "pformat", None):
                print(record.pformat(prefix))
            else:
                json.dumps(record, indent=2)
            i += 1
        print("`end {}: {} records`".format(stream.name, len(records)))
        if opts.collate:
            opts.out.write(json.dumps(records, indent=2))
        stream.close()


if __name__ == "__main__":
    import doctest

    failures, tests = doctest.testmod()
    if failures > 0:
        print("REFUSING TO RUN DUE TO FAILED TESTS")
        sys.exit(1)
    main()
#####
# EOF
