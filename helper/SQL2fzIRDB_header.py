import os
import sqlite3

db_fzirdb = os.path.join(os.getcwd(), 'db', 'flipper_irdblite.db')
con = sqlite3.connect(db_fzirdb)
cur = con.cursor()

files = cur.execute("""
SELECT irf.category
	,irf.brand
	,irf.file
	,irc.comment
	,irf.md5hash
FROM irfile irf
LEFT JOIN ircomment irc ON irf.md5hash = irc.md5hash
WHERE irf.source = 'IRDB'
    AND irf.category = 'TVs'
    AND irf.brand = 'Hitachi'
""")

irfiles = files.fetchall()
#print(len(irfiles))


for irfile in irfiles:

    irfile_arr = []
    irfile_arr.append("Filetype: IR signals file")
    irfile_arr.append("Version: 1")
    irfile_arr.append("#")
    if irfile[3]:
        irfile_arr.append(irfile[3])
    irfile_arr.append("# type: {}".format(irfile[0]))
    irfile_arr.append("# brand: {}".format(irfile[1]))
    irmodel = irfile[2].replace(".ir","").replace(irfile[1],"").replace("_","")
    irfile_arr.append("# model: {}".format(irmodel))
    irfile_arr.append("# protocol: {}".format(irfile[0]))
    irfile_arr.append("#")

    buttons = cur.execute(("""
    SELECT 
        irb.name
		,IFNULL((SELECT button
				 FROM btntrans btrn
				 WHERE TRIM(irb.name) = btrn.name
					AND btrn.name IS NOT ''
					),irb.name) name2
		,irb.type
		,irb.protocol
		,irb.address
		,irb.command
    FROM irbutton irb
    WHERE irb.md5hash = '{}'
    """).format(irfile[4]))

    irbuttons = buttons.fetchall()

    for irbutton in irbuttons:
        irfile_arr.append("#")
        irfile_arr.append("name: {}".format(irbutton[0]))
        if irbutton[2] == 'parsed':
            irfile_arr.append("type: {}".format(irbutton[2]))
            irfile_arr.append("protocol: {}".format(irbutton[3]))
            irfile_arr.append("address: {}".format(irbutton[4]))
            irfile_arr.append("command: {}".format(irbutton[5]))
        elif irbutton[2] == 'raw':
            irfile_arr.append("type: {}".format(irbutton[2]))
            irfile_arr.append("frequency: {}".format(irbutton[3]))
            irfile_arr.append("duty_cycle: {}".format(irbutton[4]))
            irfile_arr.append("data: {}".format(irbutton[5]))
        else:
           print("Error!)")

    #print('\n'.join(irfile_arr))
    print("Write {} buttons to filename {}".format(len(irbuttons),(os.path.join(os.getcwd(), irfile[0], irfile[1], irfile[2]))))

    new_irdb_path = os.path.join(os.getcwd(), irfile[0])
    if not os.path.exists(new_irdb_path):
        os.makedirs(os.path.join(new_irdb_path, irfile[1]))
    f = open(os.path.join(os.getcwd(), irfile[0], irfile[1], irfile[2]), "a")
    f.write('\n'.join(irfile_arr))
    f.close()


con.close()