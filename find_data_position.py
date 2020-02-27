#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

##############################################################################
# Edward Robinson
#
# This file is made to easily find some data in the file to help decode data files
#
# inputs :
# argv[1] = file input name
# argv[2] = op_code
# argv[3] = package length
##############################################################################

import getopt
import sys

file_in_name = sys.argv[1]
data_to_find = sys.argv[2]
pack_len = sys.argv[3]

# uncomment lines below to run as a test
file_in_name = "logs/analyze/20140421_030133-ReadGlucoseHistory-page-16.data"
data_to_find = ""
print_data_before = False  # if true will print data before , if false will print after


myBytes = bytearray()
with open(file_in_name, "rb") as file:
    while True:
        byte = file.read(1)
        if not byte:
            break
        myBytes.append(byte)


myHexBytes = []
myBinBytes = []
for i in range(0, len(myBytes)):
    myHexBytes.append("{:02x}".format(myBytes[i]))
    myBinBytes.append("{:08b}".format(myBytes[i]))

for i in range(0, len(myBytes)):
    if myHexBytes[i] == data_to_find:
        pack_start = i + 1
        hex_str = "-".join(myHexBytes[pack_start : pack_start + pack_len])
        bin_str = "-".join(myBinBytes[pack_start : pack_start + pack_len])
        print(
            "At "
            + str(i)
            + " found : ["
            + myHexBytes[i]
            + "] ["
            + hex_str
            + "] ["
            + bin_str
            + "]"
        )
