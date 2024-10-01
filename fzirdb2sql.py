#!/usr/bin/env python3
import os
import mod_sqlitehandler as sqlite
import sys ## Versioncontrol for raw analysis

db_fzirdb = os.path.join(os.getcwd(), 'db', 'flipper_irdblite.db')
dir_fzirdb = os.path.join(os.getcwd(), '..', 'Flipper-IRDB')

## Try to parse raw data to compareable format
rawanalysis = 1
if sys.version_info <= (3,9):
    print("No RAW Analysis possible. Function match() available from Python 3.10")
    print("Python version found:", sys.version)
    rawanalysis = 0

## Execute program
######################################

if __name__ == '__main__':
    
    sqlite.write2sqlite(db_fzirdb, dir_fzirdb, rawanalysis)
    print("Find your database at:", db_fzirdb)
    sqlite.translate_buttons(db_fzirdb)
    
