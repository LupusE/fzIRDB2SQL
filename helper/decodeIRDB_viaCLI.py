#!/usr/bin/env python3

## This script is a helper to convert .ir files from the IRDB or
## an own collection with 'parsed: raw' buttons, if the protocol
## is known by the Flipper Zero.
##
## The analysis is done locally, so the local repo must contain
## exact the same files as the Flipper Zero on the SD Card.
##
## Todo:
## - Errorhandling, when no flipper attached

import os
import serial
import time

IRDBonSystem = '/home/lupus/git/Flipper-IRDB/'
IRDBonFlipper = '/ext/infrared/Flipper-IRDB/'
ParsedFilesOnFlipper = '/ext/infrared/parsed/'
FlipperZeroPort = '/dev/ttyACM0'
ProcessedCount = 0

## Filter files for only neccesary to convert
def CheckForTypeRAW(irfile):
    with open(irfile) as f:
        if 'type: raw' in f.read():
            #print("true")
            return True

## Send CLI command to Flipper Zero to parse files
def GenerateParsedFile(IRPath, IRFile):
	msg = 'ir decode '+IRDBonFlipper+IRPath+IRFile+' '+ParsedFilesOnFlipper+IRPath+IRFile

	print(msg)

	ser = serial.Serial(FlipperZeroPort)
	ser.write(msg.encode(encoding = 'ascii', errors = 'strict')+bytes([13, 10]))
	time.sleep(5)

## Processing, walkthrough local filesystem -> give result to FZ CLI
IRDBFileslist = []
for subdir, dirs, files in os.walk(IRDBonSystem):
    for IRFile in files:
        if IRFile.endswith(".ir") and CheckForTypeRAW(os.path.join(subdir, IRFile)):
            #print(subdir + " and " + IRFile)
            IRDBFileslist += [[subdir.replace(IRDBonSystem,""), IRFile]]

print(str(len(IRDBFileslist))+" files to process. Start.")
for IRDBFile in IRDBFileslist:
    GenerateParsedFile(IRDBFile[0], IRDBFile[1])
    ProcessedCount += 1

print("Finished. "+str(ProcessedCount)+" processed files.")
