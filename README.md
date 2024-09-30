# fzIRDB2SQL
Flipper Zero InfraRed DataBase to SQL

## irfiles-import.py - Flipper-IRDB to sqlite.db

This is a tool to convert a local git repository of a [Flipper-IRDB](https://github.com/logickworkshop/Flipper-IRDB) to a SQLite3 Database.

**Note** - There are three main repo:
https://github.com/UberGuidoZ/Flipper-IRDB is a fork of
https://github.com/logickworkshop/Flipper-IRDB is a fork of
https://github.com/Lucaslhm/Flipper-IRDB
All three repo are maintained and the only difference from uploading to one of the repo is, which gets the file first. The other two will follow shortly.



## Folder [helper](helper/)

In the folder /helper/ contains some little tools, build to simpilfy the work with the IRDB SQLite database.

### File [decodeIRDB_viaCLI.py](helper/decodeIRDB_viaCLI.py)

A lot of .ir files in the Flipper-IRDB are `type: raw`. Except from the obious, the Flipper does not know this protocol, there are various reasons why the files can be raw. The person wo captured the file hold the button too long or started the capture in the middle of the stream. Or someone converted it from another source. Or it is just captures raw.

But the Flipper Zero provides a CLI. in the CLI is the command `ir decode <input file> <output file>` available. The input and output is locally on the Flipper, but better than nothing.

1. Put the wanted .ir files on your local filesystem
2. Copy (NOT MOVE!) the directory to the flippers SD Card, to the folder `/infrared`
3. Configure the variable `IRDBonSystem` to whereever you have your local files.
4. The parsed files will be written on the Flippers SD card to `/ext/infrared/decoded/`

If there is no changes, the new file will be stored 1:1... You'd just need to performe some checks, maybe based on the MD5sum.

There is no feedback from the Flipper. If you parse the whole IRDB (today 8594 files), it is a lot. I took two precautions:
- The Script is reading the local repo, searches only for files ending with .ir and contains `type: raw`
- All found files will be send as command one by one with 5 seconds pause to process.

### File [SQL2fzIRDB_header.py](helper/SQL2fzIRDB_header.py)

This is the first try to frite an exporter, based on all findings in the SQL.
- It will extend the comment to a few attributes. Work in Progress.
- It will replace the `name:` field of each button. Based on the Translation csv.


## Todo:
- ~~write a file exporter~~
  - write an android tool to generate files
  - or a webfrontend?
- write a documentation - [Ongoing](https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md)
- normalize the data
  - ~~write a button translation table~~
  - ~~analyze the file hierachy more~~
- write a check (~~based on md5~~) to update the db
  - write output to MySQL/MariaDB/MS SQL/Postgress/...
- ~~cleanup the code~~ (will never be finished)




# Documentation

## Functions

* `get_irfiles(dir_fzirdb)`
  * Input: `~/git/Flipper-IRDB/`
  * Output: `return(irpath_list)`  
    Example: `'/path/to/file.ir', 'MD5Hash'`
    
* `get_irdbattibutes(full_irpath)`
  * Input: `irpath_list` - list
  * Output: `return(splitcategory, splitbrand, splitfile, digest.hexdigest(), splitsource)`

* `get_irdbcomments(irfile)`
  * Input: `/path/to/irfile.ir`
  * Output: `return(commentstr)` - string
  
* `get_irbuttons(full_irpath)`
  * Input: `/path/to/irfile.ir`
  * Output: `return(buttons) - name, type, protcol/frequency, address/duty_cycle, command/data - list`  
    Format type = parsed: `'Power', 'parsed', 'NECext', '1A 34 00 00', 'C2 00 00 00'`  
    Format type = raw: `'Power', 'raw', '38000', '0.330000', '9772 4497 626 551[...] 632 545 627 549 634'`
  
* `write2sqlite()` - 1. main()
  * Input: N/A
  * Output: SQL Inserts
  
* `translate_buttons()` - 2. main()
  * Input: `db/csv/Flipper-IRDB2SQLite_btn-transl.csv`
  * Output: `cur.executemany("INSERT INTO btntrans VALUES (?, ?, ?);", toSQLitedb)`

## Database

* table: `irfile` - PK: md5hash
  * rows: category, brand, file, **md5hash**, source
* table: `irbutton` - PK: md5hash
  * rows: name, type, protocol, address, command, **md5hash**
* table: `ircomment` - PK: md5hash
  * rows: comment, **md5hash**

optional:
* table: `rawbutton` - PK: md5hash 
  * rows: name, header, binarydata, tail, bit, divident, **md5hash**

addon:
* table: `btntrans` - FK: irbutton.button
  * rows: 'id', 'name', 'button'
  

