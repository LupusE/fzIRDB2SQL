#!/usr/bin/env python3

import os
import sqlite3
import csv
import sys ## Versioncontrol for raw analysis

import mod_irdbhandler as irdb
import mod_analysis as rawanalyis

db_fzirdb = os.path.join(os.getcwd(), 'db', 'flipper_irdblite.db')
dir_fzirdb = os.path.join(os.getcwd(), '..', 'Flipper-IRDB')

## Try to parse raw data to compareable format
rawanalysis = 1
if sys.version_info <= (3,9):
    print("No RAW Analysis possible. Function match() available from Python 3.10")
    print("Python version found:", sys.version)
    rawanalysis = 0

### simple db ###
 ## irfile    (category, brand,  file,       md5hash, source,  created,  updated)
 ## irbutton  (name,     type,   protocol,   address, command, md5hash)    
 ## ircomment (comment,  md5hash)
 ## rawbutton (name,     header, binarydata, tail,    bit,     divident, md5hash)

### new db (normalized) ###
 ## irfile    (categoryid, brandid,  file, md5hashid, source,  created,  updated)
 ## norm_cat   (categoryid, category)
 ## norm_brand (brandid, brand)
 ## norm_md5   (md5hashid, md5hash)
 ## norm_src   (sourceid, source)
 ## irbutton  (name, type, protocol, address, command, md5hash)
 ## norm_prot  (protocolid, protocol)
 ## ircomment (comment,  md5hash)
 ## rawbutton (name, header, binarydata, tail, bit, divident, md5hash)



## Write parsed items to database
######################################

def create_localirdb(fzirdb):
    try:
        con = sqlite3.connect(fzirdb)    
        cur = con.cursor()

    except OSError as e:
        print(e)

    if (db_renew) == 1:
        cur.execute("DROP TABLE IF EXISTS irfile;")
        cur.execute("DROP TABLE IF EXISTS irbutton;")
        cur.execute("DROP TABLE IF EXISTS ircomment;")
        cur.execute("DROP TABLE IF EXISTS rawbutton;")        

    cur.execute("CREATE TABLE IF NOT EXISTS irfile (category,brand,file,md5hash,source,created,updated);")
    cur.execute("CREATE TABLE IF NOT EXISTS irbutton (name,type,protocol,address,command,md5hash);")    
    cur.execute("CREATE TABLE IF NOT EXISTS ircomment (comment,md5hash);")
    if rawanalysis == 1:
        cur.execute("CREATE TABLE IF NOT EXISTS rawbutton (name,header,binarydata,tail,bit,divident,md5hash);")
        
    con.commit()
    con.close()


## Write items to database
######################################

def write_irdb2db():

    irheader = irdb.get_irdbattibutes(irfile[0])
    cur.execute(("INSERT INTO irfile VALUES ('{}', '{}','{}','{}','{}');").format(irheader[0],irheader[1],irheader[2],irfile[1],irheader[3]))

    ircomments = irdb.get_irdbcomments(irfile[0])
    if (len(ircomments)) != 0:
        ircomments = ircomments.replace("'","") # dirty hack, because sqlite using ' itself
        cur.execute(("INSERT INTO ircomment VALUES ('{}','{}');").format(ircomments,irfile[1]))

    for irbutton in irdb.get_irbuttons(irfile[0]):
        irbuttons = (irbutton.split(','))
        ### irheader[3] == irfile[1] ?? ###
        cur.execute(("INSERT INTO irbutton VALUES ('{}','{}','{}','{}','{}','{}');").format(irbuttons[0],irbuttons[1],irbuttons[2],irbuttons[3],irbuttons[4],irfile[1]))
        if irbuttons[1] == 'raw' and rawanalysis == 1:
            binary_button = rawanalyis.button_raw2binary(irbuttons[4])
            if len(binary_button) > 1:
                raw_header = ' '.join(binary_button[1])

                #print(irbuttons[0],binary_button[0],raw_header,binary_button[2],binary_button[3],binary_button[4],irheader[3])
                cur.execute(("INSERT INTO rawbutton VALUES ('{}','{}','{}','{}','{}','{}','{}');").format(irbuttons[0],binary_button[0],raw_header,binary_button[2],binary_button[3],binary_button[4],irfile[1]))

## Insert items to database
######################################
    
    ## irfile    (category,brand,file,md5hash,source,created,updated)
    ## irbutton  (name,type,protocol,address,command,md5hash)
    ## ircomment (comment,md5hash)
    ## rawbutton (name,header,binarydata,tail,bit,divident,md5hash)
            
    ## updatelist:    [0] ROWID, [1] file_old, [2] file_new, [3] md5sum, [4] categ,   [5] brand,     [6] NULL, [7] timestamp
    ## insertlist:    [0] file,  [1] md5sum,   [2] categ,    [3] brand,  [4] source , [5] timestamp, [6] NULL
    ## insertbtnlist: [0] name,  [1] type,     [2] proto,    [3] address [4] command, [5] md5sum,    [6] ROWID

def insert_irfile(insertlist):
    ## "INSERT INTO "
    con = sqlite3.connect(fzirdb)
    cur = con.cursor()

    cur.executemany("INSERT INTO irfile VALUES (?, ?, ?);", insertlist)
    
    con.commit()
    con.close()



## Update items in database
######################################

def update_irfile(updatelist):
                  ## sql_rowid,irf_file,irf_md5,ira_cat,ira_brand,sql_md5

    con = sqlite3.connect(fzirdb)
    cur = con.cursor()

    # sql_updatelist: ROWID, file, irfile , md5sum ,irattr[0],irattr[1]
    cur.executemany("INSERT INTO btntrans VALUES (?, ?, ?);", sql_updatelist)

    con.commit()
    con.close()

    
    ## update datetime for irfile.update, change irfile.md5hash to irf_md5
    ## add new irbuttons/ircomments
    ## mark deleted irbuttons where md5hash = sql_md5 WHEN count 1


def insert_irbtn()
    

## Read fileinfo from local IRDB
######################################

def select_irfile(fzirdb):
    try:
        con = sqlite3.connect(fzirdb)    
        cur = con.cursor()
        cur.execute("SELECT ROWID,irfid,file,md5hash,category,brand FROM irfile")
        
        localirdb = cur.fetchall()
#        print(localirdb)
	return(localirdb)

    except OSError as e:
        print(e)
        
    con.close()


## Add extra tables (button translation)
######################################

def translate_buttons(fzirdb):
    con = sqlite3.connect(fzirdb)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS btntrans;")
    cur.execute("CREATE TABLE IF NOT EXISTS btntrans ('id', 'name','button');")

    with open('db/csv/Flipper-IRDB2SQLite_btn-transl.csv','r') as translate:
        translate_dr = csv.DictReader(translate, delimiter=';')
        toSQLitedb = [(i['ID'], i['Button'], i['Translate']) for i in translate_dr]

    cur.executemany("INSERT INTO btntrans VALUES (?, ?, ?);", toSQLitedb)
    con.commit()
    con.close()

    print("Buttons translation table (btntrans) created in",fzirdb)


## Execute program
######################################

if __name__ == '__main__':
    
    read_from_sqlite(db_fzirdb)
#    print("Find your database at:", db_fzirdb)
#    translate_buttons(db_fzirdb)
