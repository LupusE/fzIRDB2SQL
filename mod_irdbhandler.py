import re
import os
import hashlib

dir_fzirdb = os.path.join(os.getcwd(), '..', 'Flipper-IRDB')
category_fzirdb = next(os.walk(dir_fzirdb))[1]

## add _CONVERTED_ directory = 1
exclude_converted = 1

ext_irdb_include = (['.ir'])
dir_irdb_exclude = set([ os.path.join(dir_fzirdb, '.git*') ])
if exclude_converted == 0:
    dir_irdb_exclude.append(os.path.join(dir_fzirdb,'_Converted_'))

## IR file pattern for one button in regex
btn_pattern = re.compile(r"""
                name: (.*)\n
                type: (.*)\n
                (protocol|frequency): (.*)\n
                (address|duty_cycle): (.*)\n
                (command|data): (.*)\n
                """, re.VERBOSE | re.MULTILINE)


## Get filtered [folder/files, md5hash] as list
######################################

def get_irfiles(dir_fzirdb):
    irpath_list = []
    for root, dir, files in os.walk(dir_fzirdb, topdown=True):
        for irfile in files:
            if (not root.startswith(tuple(dir_irdb_exclude)) and (irfile.endswith(tuple(ext_irdb_include)))):
                    irfilepath = os.path.join(root, irfile)
		    ## Create MD5 hsh als PK for SQL
                    with open(str(irfilepath), 'rb') as md5file:
                        digest = hashlib.file_digest(md5file, 'md5')
                    irpath_list.append([irfilepath, digest.hexdigest()])
            else:
                pass
    print(("{} IR files from {} to process").format(len(irpath_list),dir_fzirdb))
    
    return(irpath_list)
    ## Format: '/path/to/file.ir', 'MD5Hash'

    
## Get file header (category, brand, filename, MD5)
######################################

def get_irdbattibutes(full_irpath):

    splitcategory = ''
    splitbrand = ''
    splitsource = ''

    if (full_irpath.find(os.path.join('_Converted_','CSV'))) >= 0:
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-3]
        splitcategory = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitsource = 'CSV'
    elif (full_irpath.find(os.path.join('_Converted_','Pronto'))) >= 0:
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitcategory = 'NULL'
        splitsource = 'Pronto'
    elif (full_irpath.find(os.path.join('_Converted_','IR_Plus'))) >= 0:
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitcategory = 'NULL'
        splitsource = 'IR_Plus'
    #elif (full_irpath.find(os.path.join('_Converted_'))) >= 0:
    #    return('')
 
    else:
        splitcategory = os.path.normpath(full_irpath).split(os.sep)[-3]
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitsource = 'IRDB'
        ## Hack: correct category for console/Nintendo/Gameboy/ and similar
        if splitcategory not in category_fzirdb:
            splitcategory = os.path.normpath(full_irpath).split(os.sep)[-4]
            splitbrand = os.path.normpath(full_irpath).split(os.sep)[-3]
        if splitcategory in ['git']:
            splitcategory = os.path.normpath(full_irpath).split(os.sep)[-2]
            splitbrand = 'NULL'
    
    splitfile = os.path.normpath(full_irpath).split(os.sep)[-1].replace("'","")

    return(splitcategory, splitbrand, splitfile, splitsource)


## Get file header (comments)
######################################

def get_irdbcomments(irfile):
    comments = []
    commentstr = ""

    with open(irfile, 'r') as filecomments:
        for line in filecomments:
            if line.startswith("#") and (len(line.strip())) > 1:
                comments.append(line)

    commentstr = "".join(comments)
    #print(commentstr)
    return(commentstr)


## Parse buttons (name, type, protcol/frequency, address/duty_cycle, command/data)
######################################

def get_irbuttons(full_irpath):
    # read file to buffer, to find multiline regex
    readfile = open(full_irpath,'r')
    irbuff = readfile.read()
    readfile.close()

    buttons = []
    for match in btn_pattern.finditer(irbuff):
        btnname = match.group(1).strip().replace("'","")
        btntype = match.group(2).strip()
        btnprot = match.group(4).strip()
        btnaddr = match.group(6).strip()
        btncomm = match.group(8).strip()

        buttons.append(btnname+","+btntype+","+btnprot+","+btnaddr+","+btncomm)

    # if 'type = raw' then 'proto = frequency', 'address = dutycycle', 'command = data'
    # Frequency is technically fixed at 38MHz for the Flipper Zero
    #   but due to tollerance 40/36 are possible
    # Dutycycle: % of time on (bursts) to be one signal.
    #   To be interpreted as on, the signal must be on 33% of 562,2 us
    # Data is a string of the captued values.
    #   Each value represents alternating length in ms of on/off

    return(buttons)
    ## Format type = parsed: 'Power', 'parsed', 'NECext', '1A 34 00 00', 'C2 00 00 00'
    ## Format type = raw: 'Power', 'raw', '38000', '0.330000', '9772 4497 626 551[...] 632 545 627 549 634'

