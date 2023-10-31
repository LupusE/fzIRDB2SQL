#!/usr/bin/env python3

import os
import mod_irdbhandler as irdb
import mod_sqlitehandler as sqlite
import time
import mod_analysis as analyis
import sys ## Versioncontrol for raw analysis


db_fzirdb = os.path.join(os.getcwd(), 'db', 'flipper_irdblite.db')
timestamp = time.time()

rawanalysis = 1  ## Try to parse raw data to compareable format
if sys.version_info <= (3,9):
    print("No RAW Analysis possible. Function match() available from Python 3.10")
    print("Python version found:", sys.version)
    rawanalysis = 0

## Execute program
######################################

if __name__ == '__main__':
    
    if (!os.path.exists(db_fzirdb)):
    	sqlite.create_localirdb(db_fzirdb)
    irsql = sqlite.select_irfile(db_fzirdb)
    
    sql_updatelist = []
    sql_insertlist = []
    sql_insertbtnlist = []

    ## Collect information and put in lists ## 

    ## Unique: GROUP BY file,md5hash,category,brand
    ## irsql:  [0] ROWID, [1] file,   [2] md5sum, [3] category, [4] brand
    ## irfile: [0] path,  [1] md5sum, [2] irfile
    ## irattr: [0] categ, [1] brand,  [2] file,   [3] source
    ## irbtn:  [0] name,  [1] type,   [2] proto,  [3] address,  [4] command

    for irfile in irdb.get_irfiles(dir_fzirdb):
    	irattr = irdb.get_irdbattibutes(irfile[0])
    	
        if (irsql[1]+irsql[2]+irsql[3]+irsql[4] == irfile[2]+irfile[1]+irattr[0]+irattr[1]):
            #print ("skip")

        elif ((irsql[1]+irsql[3]+irsql[4] == irfile[2]+irattr[0]+irattr[1]) AND (irsql[2] != irfile[1])):
            #print ("update")
            sql_updatelist.append(irsql[0],irsql[1],irfile[2],irfile[1],irattr[0],irattr[1],NULL,timestamp)
                               ## [0] ROWID, [1] file_old, [2] file_new, [3] md5sum, [4] categ, [5] brand, [6] NULL, [7] timestamp
            for irbutton in irdb.get_irbuttons(irfile[0]):
                irbtn = (irbutton.split(','))
                sql_insertbtnlist.append(irbtn[0],irbtn[1],irbtn[2],irbtn[3],irbtn[4],irsql[2],irsql[0])
                if irbuttons[1] == 'raw' and rawanalysis == 1:
                    binary_button = rawanalyis.button_raw2binary(irbuttons[4])
                    if len(binary_button) > 1:
                        raw_header = ' '.join(binary_button[1])

        else:
            #print ("insert")

            sql_insertlist.append(irfile[2],irfile[1],irattr[0],irattr[1],irattr[3],timestamp,NULL)
                               ## [0] file, [1] md5sum, [2] categ, [3] brand, [4] source , [5] timestamp, [6] NULL
            for irbutton in irdb.get_irbuttons(irfile[0]):
                irbtn = (irbutton.split(','))
                sql_insertbtnlist.append(irbtn[0],irbtn[1],irbtn[2],irbtn[3],irbtn[4],irsql[2],irsql[0])

                if irbuttons[1] == 'raw' and rawanalysis == 1:
                    binary_button = analyis.button_raw2binary(irbtn[4])
                    if len(binary_button) > 1:
                        raw_header = ' '.join(binary_button[1])

    ## Write lists in database ##

    print("Write {} updates to database".format(len(sql_updatelist))
    sqlite.update_irfile(sql_updatelist)
        
    print("Insert {} new irfiles to database".format(len(sql_insertlist))
    sqlite.insert_irfile(sql_insertlist)
    
    print("Insert {} new buttonsets to database".format(len(sql_insertbtnlist))
    sqlite.insert_irbtn(sql_insertbtnlist)
    
    #sqlite.write2sqlite(db_fzirdb)
    print("Find your database at:", db_fzirdb)
    sqlite.translate_buttons(db_fzirdb)
    
    
