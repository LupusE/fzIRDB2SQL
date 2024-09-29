import re

## find buttons and name the result
lircconf_pattern = re.compile(r"""
                ^\s+name\s+(?P<name>.*?)\n
                ^\s+bits\s+(?P<bits_hdr>.*?)\n
                ^\s+flags\s+(?P<flags>.*?)\n                                            
                ^\s+header\s+(?P<mark_header>.*?)\s+(?P<space_header>.*?)\n
                ^\s+one\s+(?P<mark_one>.*?)\s+(?P<space_one>.*?)\n
                ^\s+zero\s+(?P<mark_zero>.*?)\s+(?P<space_zero>.*?).*\n
                ^\s+ptrail\s+(?P<ptrail>.*?)\n
                ^\s+repeat\s+(?P<repeat>.*?)\n
                ^\s+pre_data_bits\s+0x(?P<bits_adr>....).*\n
                ^\s+pre_data\s+0x(?P<address>....).*\n
                ^\s+gap\s+0x(?P<dataframe_pause>....).*\n
                ^\s+KEY_POWER\s+0x(?P<key_power>....).*\n
                #^\s+begin codes(?P<codes>)end codes*\n
                """, re.VERBOSE | re.MULTILINE | re.DOTALL)

lircdb = '/home/lupus/git/lirc-remotes-code/remotes/lg/AKB69680403.lircd.conf'

readfile = open(lircdb,'r')
lircdata = readfile.read()
readfile.close()

for match in lircconf_pattern.finditer(lircdata):
    print("1")
    button_code = []
    header = []
    protocol = ""

    bits_data = match.group("bits_hdr") + match.group("bits_adr")