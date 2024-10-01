import os
import sqlite3
import csv

import mod_irdbhandler as irdb
import mod_analysis as rawanalyis


## Write parsed items to database
######################################

def write2sqlite(db_fzirdb, dir_fzirdb, rawanalysis):
    try:
        con = sqlite3.connect(db_fzirdb)    
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS irfile;")
        cur.execute("DROP TABLE IF EXISTS irbutton;")
        cur.execute("DROP TABLE IF EXISTS ircomment;")
        cur.execute("DROP TABLE IF EXISTS rawbutton;")        
        
        cur.execute("CREATE TABLE IF NOT EXISTS irfile (category,brand,file,md5hash,source);")
        cur.execute("CREATE TABLE IF NOT EXISTS irbutton (name,type,protocol,address,command,md5hash);")    
        cur.execute("CREATE TABLE IF NOT EXISTS ircomment (comment,md5hash);")
        if rawanalysis == 1:
            cur.execute("CREATE TABLE IF NOT EXISTS rawbutton (name,header,binarydata,tail,bit,divident,md5hash);")

    except OSError as e:
        print(e)

    print("Getting header and buttons for database",db_fzirdb)
    for irfile in irdb.get_irfiles(dir_fzirdb):
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
                    
    con.commit()
    con.close()
    print("Header and buttons written in database",db_fzirdb)

## Add extra tables (button translation)
######################################

def translate_buttons(db_fzirdb):
    con = sqlite3.connect(db_fzirdb)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS btntrans;")
    cur.execute("CREATE TABLE IF NOT EXISTS btntrans ('id', 'name','button');")

    with open('db/csv/Flipper-IRDB2SQLite_btn-transl.csv','r') as translate:
        translate_dict = csv.DictReader(translate, delimiter=',')
        toSQLitedb = []
        for i in translate_dict:
            if i['Translate'] == '':
                toSQLitedb.append([i['ID'],i['Button'],None])
            else:
                toSQLitedb.append([i['ID'],i['Button'],i['Translate']])

    cur.executemany("INSERT INTO btntrans VALUES (?, ?, ?);", toSQLitedb)
    con.commit()
    con.close()

    print("Buttons translation table (btntrans) created in",db_fzirdb)

