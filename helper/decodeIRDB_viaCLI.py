#!/usr/bin/env python3
import os
import serial
import time

IRDBonSystem = '/home/lupus/git/Flipper-IRDB/'
IRDBonFlipper = '/ext/infrared/Flipper-IRDB/'

def CheckForTypeRAW(irfile):
    with open(irfile) as f:
        if 'type: raw' in f.read():
            #print("true")
            return True

def GenerateDecodedFiles(IRPath, IRFile):
	DecodedOnFlipper = '/ext/infrared/decoded/'
	msg = 'ir decode '+IRDBonFlipper+IRPath+IRFile+' '+DecodedOnFlipper+IRPath+IRFile

	print(msg)

	ser = serial.Serial('/dev/ttyACM0')
	#ser.write(msg.encode(encoding = 'ascii', errors = 'strict')+bytes([13, 10]))
	time.sleep(5)

for subdir, dirs, files in os.walk(IRDBonSystem):
    for IRFile in files:
        if IRFile.endswith(".ir"):
            if CheckForTypeRAW(os.path.join(subdir, IRFile)):
                #print(subdir + " and " + IRFile)
                GenerateDecodedFiles(subdir.replace(IRDBonSystem,""), IRFile)

