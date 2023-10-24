#!/usr/bin/env python3
import os
import mod_sqlitehandler as sqlite

db_fzirdb = os.path.join(os.getcwd(), 'db', 'flipper_irdblite.db')


## Execute program
######################################

if __name__ == '__main__':
    
    sqlite.write2sqlite()
    print("Find your database at:", db_fzirdb)
    sqlite.translate_buttons()
    
