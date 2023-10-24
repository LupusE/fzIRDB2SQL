# fzIRDB2SQL
Flipper Zero InfraRed DataBase to SQL

## irfiles-import.py - Flipper-IRDB to sqlite.db

This is a tool to convert a local git repository of a [Flipper-IRDB](https://github.com/logickworkshop/Flipper-IRDB) to a SQLite3 Database.


### Todo:
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
  

