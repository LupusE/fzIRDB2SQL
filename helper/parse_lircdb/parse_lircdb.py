##
## $ git clone https://git.code.sf.net/p/lirc-remotes/code lirc-remotes-code
##

import re

## find buttons and name the result
lircconf_pattern = re.compile(r"""
                ^\s+header\s+(?P<mark_header>.*?)\s+(?P<space_header>.*?)\n
                ^\s+one\s+(?P<mark_one>.*?)\s+(?P<space_one>.*?)\n
                ^\s+zero\s+(?P<mark_zero>.*?)\s+(?P<space_zero>.*?).*\n
                ^\s+pre_data\s+0x(?P<address>....).*\n
                ^\s+KEY_POWER\s+0x(?P<key_power>....).*\n
                ^\s+KEY_1\s+0x(?P<key_1>....).*\n
                ^\s+KEY_2\s+0x(?P<key_2>....).*\n
                ^\s+KEY_3\s+0x(?P<key_3>....).*\n
                ^\s+KEY_4\s+0x(?P<key_4>....).*\n
                ^\s+KEY_5\s+0x(?P<key_5>....).*\n
                ^\s+KEY_6\s+0x(?P<key_6>....).*\n
                ^\s+KEY_7\s+0x(?P<key_7>....).*\n
                ^\s+KEY_8\s+0x(?P<key_8>....).*\n
                ^\s+KEY_9\s+0x(?P<key_9>....).*\n
                ^\s+KEY_0\s+0x(?P<key_0>....).*\n
                ^\s+KEY_VOLUMEUP\s+0x(?P<key_volup>....).*\n
                ^\s+KEY_VOLUMEDOWN\s+0x(?P<key_voldn>....).*\n
                ^\s+KEY_MUTE\s+0x(?P<key_mute>....).*\n
                ^\s+KEY_CHANNELUP\s+0x(?P<key_chup>....).*\n
                ^\s+KEY_CHANNELDOWN\s+0x(?P<key_chdn>....).*\n
                ^\s+KEY_UP\s+0x(?P<key_up>....).*\n
                ^\s+KEY_DOWN\s+0x(?P<key_down>....).*\n
                ^\s+KEY_LEFT\s+0x(?P<key_left>....).*\n
                ^\s+KEY_RIGHT\s+0x(?P<key_right>....).*\n
                ^\s+KEY_OK\s+0x(?P<key_ok>....).*\n
                ^\s+KEY_ENTER\s+0x(?P<key_enter>....).*\n
                ^\s+KEY_MENU\s+0x(?P<key_menu>....).*\n
#                ^\s+KEY_EXIT\s+0x(?P<key_exit>....).*\n
#                ^\s+KEY_LIST\s+0x(?P<key_list>....).*\n
#                ^\s+KEY_RED\s+0x(?P<key_red>....).*\n
#                ^\s+KEY_GREEN\s+0x(?P<key_green>....).*\n
#                ^\s+KEY_YELLOW\s+0x(?P<key_yellow>....).*\n
#                ^\s+KEY_BLUE\s+0x(?P<key_blue>....).*\n
#                ^\s+KEY_STOP\s+0x(?P<key_stop>....).*\n
#                ^\s+KEY_PLAY\s+0x(?P<key_play>....).*\n
#                ^\s+KEY_PAUSE\s+0x(?P<key_pause>....).*\n
#                ^\s+KEY_RECORD\s+0x(?P<key_records>....).*\n
#                ^\s+KEY_REWIND\s+0x(?P<key_rewind>....).*\n
#                ^\s+KEY_FORWARD\s+0x(?P<key_forward>....).*\n
#                ^\s+KEY_TEXT\s+0x(?P<key_text>....).*\n
                """, re.VERBOSE | re.MULTILINE | re.DOTALL)

lircdb = '/home/lupus/git/lirc-remotes-code/remotes/lg/AKB69680403.lircd.conf'

readfile = open(lircdb,'r')
lircdata = readfile.read()
readfile.close()

## buttons to import (lirc names)
buttons =  ["KEY_POWER","KEY_MENU","KEY_UP","KEY_DOWN","KEY_LEFT","KEY_RIGHT","KEY_OK","KEY_ENTER",
            "KEY_VOLUMEUP","KEY_VOLUMEDOWN","KEY_MUTE","KEY_CHANNELUP","KEY_CHANNELDOWN",
            "KEY_1","KEY_2","KEY_3","KEY_4","KEY_5","KEY_6","KEY_7","KEY_8","KEY_9","KEY_0"
#            "KEY_LIST","KEY_RED","KEY_GREEN","KEY_YELLOW","KEY_BLUE",
#            "KEY_STOP","KEY_PLAY","KEY_PAUSE","KEY_RECORD","KEY_REWIND","KEY_FORWARD","KEY_TEXT"
            ]

#print(lircdata)

for match in lircconf_pattern.finditer(lircdata):
    print("1")
    button_code = []
    header = []
    protocol = ""

    ## get protocol
    ###############
    bin_adr = bin(int(match.group("address"), 16))[2:].zfill(16)
    inv_bin_addr = ''.join(['1' if i == '0' else '0' for i in bin_adr[:int(len(bin_adr)/2)]])
    if bin_adr[int(len(bin_adr)/2):] == inv_bin_addr:
        print("Adr logical reversed -> 2x 8bit = 16bit")
        protocol = "NECext"

        bin_pwr = bin(int(match.group("key_power"), 16))[2:].zfill(16)
        inv_bin_pwr = ''.join(['1' if i == '0' else '0' for i in bin_pwr[:int(len(bin_pwr)/2)]])
        if bin_pwr[int(len(bin_pwr)/2):] == inv_bin_pwr:
            print("pwr logical inversed -> 2x 8bit = 16bit / 32bit total")
            protocol = "NEC"

    else:
        print("Protocol unkonwn, break")
        break

## check for timings against protocol -> tolerance!
#    header = match.group("mark_header")
#    header += match.group("space_header")
#    header += match.group("mark_one")
#    header += match.group("space_one")
#    header += match.group("mark_zero")
#    header += match.group("space_zero")

    ## read button config
    #####################
#    for button in buttons:
#        print(button)
#        print(button,match.group(button)) 
#        try:
#            if match.group(button) != "":
#                button_code.append([button,match.group(button)])
#        except:
#            pass


#print(header)
#print(button_code)


## generate flipper infrared file
#################################

## see https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/file_formats/InfraredFileFormats.md
fzirfile = "Filetype: IR signals file" + '\n'
fzirfile += "Version: 1" + '\n'
fzirfile += "#" + '\n'
## Rename from https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/UniversalRemotes.md
for fzbutton in button_code:
    match str(fzbutton[0]):
        case "key_power":
            name_fzbutton = "Power"
        case "KEY_MUTE":
            name_fzbutton = "Mute"
        case "KEY_VOLUMEUP":
            name_fzbutton = "Vol_up"
        case "KEY_VOLUMEDOWN":
            name_fzbutton = "Vol_dn"
        case "KEY_CHANNELUP":
            name_fzbutton = "Ch_next"
        case "KEY_CHANNELDOWN":
            name_fzbutton = "Ch_prev"
        case _:
            name_fzbutton = str(fzbutton[0]).replace("KEY_","")

#buttons =  ["KEY_POWER","KEY_MENU","KEY_UP","KEY_DOWN","KEY_LEFT","KEY_RIGHT","KEY_OK","KEY_ENTER",
#            "KEY_VOLUMEUP","KEY_VOLUMEDOWN","KEY_MUTE","KEY_CHANNELUP","KEY_CHANNELDOWN",
#            "KEY_1","KEY_2","KEY_3","KEY_4","KEY_5","KEY_6","KEY_7","KEY_8","KEY_9","KEY_0",
#            "KEY_LIST","KEY_RED","KEY_GREEN","KEY_YELLOW","KEY_BLUE",
#            "KEY_STOP","KEY_PLAY","KEY_PAUSE","KEY_RECORD","KEY_REWIND","KEY_FORWARD","KEY_TEXT","pip"]




    fzirfile += "name: " + name_fzbutton + '\n'
    fzirfile += "type: parsed" + '\n'
    fzirfile += "protocol: " + protocol + '\n'
    fzaddress = format(int(format(int(match.group("address"), 16), "016b")[:8][::-1], 2), '0' + str(len(format(int(match.group("address"), 16), "016b")[:8][::-1]) // 4) + 'x') + " 00 00 00"
    fzirfile += "address: " + fzaddress + '\n'
    #print(address, fzbutton[1])
    bin_fzbutton = format(int(fzbutton[1], 16), "016b")
    fzcommand = format(int(bin_fzbutton[:8][::-1], 2), '0' + str(len(bin_fzbutton[:8][::-1]) // 4) + 'x') + " 00 00 00"
    fzirfile += "command: " + fzcommand  + '\n'
    fzirfile += "#" + '\n'

print(fzirfile)
