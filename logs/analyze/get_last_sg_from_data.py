##############################################################################
# Edward Robinson
#
# This file is made to convert raw data from the ReadGlucoseHistory command
# into readable data
#
# inputs :
# argv[1] = file input name
# 	if no file name is given then the file with the greatest date in
# 	the logs directory is used
#
##############################################################################
import getopt
import sys

# lineSize = 10
# fileInName = sys.argv[1]
# outType = sys.argv[2]
# if sys.argv[3] == "true":
#    withNewLine = True
# else:
#    withNewLine = False
# outType = "hex"
fileInName = "20140421_030133-ReadGlucoseHistory-page-16.data"
fileInName = "20140421_042530-ReadGlucoseHistory-page-0.data"
fileOutName = "latest-sg.xml"
# fileOutName = fileInName + ".values"
# withNewLine = False
# if outType == "bin":
#    fileOutName = fileInName + ".bin"
# else:
#    fileOutName = fileInName + ".hex"

myBytes = bytearray()
with open(fileInName, "rb") as file:
    while True:
        byte = file.read(1)
        if not byte:
            break
        myBytes.append(byte)

# j = len(myBytes)
# print(j)
# j = j - 1
# print(myBytes[j])
# print('{0:08b}'.format(myBytes[j]))
# print(hex(myBytes[j]))


# myBytes=myBytes.replace("\n","")
# myBytes=myBytes.replace("\t","")
j = 0
fileOut = open(fileOutName, "w")
numZerosCounter = 0
latest_sg = 0
# for each byte: convert it to a decimal, double it
# 	check that it is a valid sg and then mark it as the latest
for i in range(0, len(myBytes)):
    bin = "{:08b}".format(myBytes[i])
    hex = "{:02x}".format(myBytes[i])
    dec = int(hex, 16)
    sg = dec * 2
    if sg == 0:
        numZerosCounter = numZerosCounter + 1
    else:
        numZerosCounter = 0
    if numZerosCounter > 20:
        break
    if sg > 40 and sg < 400:
        latest_sg = sg

fileOut.write("<latest_sg>" + str(latest_sg) + "</latest_sg>")

####### old code ######
# only do line by line if there will be multiple lines
# if len(myBytes) > lineSize:
#    for i in range(0, len(myBytes) - lineSize, lineSize):
#        for j in range(0, lineSize):
#            # convert byte to appropriate format
#            if outType == "bin":
#                out = '{0:08b}'.format(myBytes[j + i])
#            else:
#                out = '{0:02x}'.format(myBytes[j + i])
#            fileOut.write(out)
#        if withNewLine:
#            fileOut.write("\n")
#        j = i + lineSize
#
# if the last few bytes don't fill a line from the loop above print them here
# if j < len(myBytes):
#    for i in range(0, len(myBytes) - j):
#        # convert to hex or binary and print
#        if outType == "bin":
#            out = '{0:08b}'.format(myBytes[i])
#        else:
#            out = '{0:02x}'.format(myBytes[i])
#        fileOut.write(out)
#        if withNewLine:
#            fileOut.write("\n")
# info stuff
# print("bytes raw : " + myBytes)
# print("bytes bin : " + '{0:08b}'.format(myBytes))
# print("bytes hex : " + hex(myBytes))
