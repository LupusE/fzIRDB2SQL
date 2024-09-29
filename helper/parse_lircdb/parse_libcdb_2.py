##
## $ git clone https://git.code.sf.net/p/lirc-remotes/code lirc-remotes-code
##

import re

## find buttons and name the result
lircconf_pattern = re.compile(r"""
                ^\s+name\s+(?P<name>.*?)\n
                ^\s+bits\s+(?P<bits>.*?)\n                              
                ^\s+header\s+(?P<mark_header>.*?)\s+(?P<space_header>.*?)\n
                ^\s+one\s+(?P<mark_one>.*?)\s+(?P<space_one>.*?)\n
                ^\s+zero\s+(?P<mark_zero>.*?)\s+(?P<space_zero>.*?).*\n
                ^\s+pre_data\s+0x(?P<address>....).*\n
                ^\s+KEY_POWER\s+0x(?P<key_power>....).*\n
                #^\s+begin codes(?P<codes>)end codes*\n
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

print(lircdata)

for match in lircconf_pattern.finditer(lircdata):
    print("1")
    button_code = []
    header = []
    protocol = ""


#define NEC_START_BIT_PULSE_TIME                9000.0e-6                       // 9000 usec pulse
#define NEC_START_BIT_PAUSE_TIME                4500.0e-6                       // 4500 usec pause
#define NEC_REPEAT_START_BIT_PAUSE_TIME         2250.0e-6                       // 2250 usec pause
#define NEC_PULSE_TIME                           560.0e-6                       //  560 usec pulse
#define NEC_1_PAUSE_TIME                        1690.0e-6                       // 1690 usec pause
#define NEC_0_PAUSE_TIME                         560.0e-6                       //  560 usec pause
#define NEC_FRAME_REPEAT_PAUSE_TIME               40.0e-3                       // frame repeat after 40ms

#define NEC_ADDRESS_OFFSET                       0                              // skip 0 bits
#define NEC_ADDRESS_LEN                         16                              // read 16 address bits
#define NEC_COMMAND_OFFSET                      16                              // skip 16 bits (8 address + 8 /address)
#define NEC_COMMAND_LEN                         16                              // read 16 bits (8 command + 8 /command)
#define NEC_COMPLETE_DATA_LEN                   32                              // complete length
#define NEC_STOP_BIT                            1                               // has stop bit
#define NEC_LSB                                 1                               // LSB...MSB
#define NEC_FLAGS                               0                               // flags

#define NEC42_ADDRESS_OFFSET                    0                               // skip 0 bits
#define NEC42_ADDRESS_LEN                      13                               // read 13 address bits
#define NEC42_COMMAND_OFFSET                   26                               // skip 26 bits (2 x 13 address bits)
#define NEC42_COMMAND_LEN                       8                               // read 8 command bits
#define NEC42_COMPLETE_DATA_LEN                42                               // complete length (2 x 13 + 2 x 8)

#define NEC16_ADDRESS_OFFSET                    0                               // skip 0 bits
#define NEC16_ADDRESS_LEN                       8                               // read 8 address bits
#define NEC16_COMMAND_OFFSET                    8                               // skip 8 bits (8 address)
#define NEC16_COMMAND_LEN                       8                               // read 8 bits (8 command)
#define NEC16_COMPLETE_DATA_LEN                 16                              // complete length

    ## get protocol
    ###############
    bin_adr = bin(int(match.group("address"), 16))[2:].zfill(16)
    inv_bin_addr = ''.join(['1' if i == '0' else '0' for i in bin_adr[:int(len(bin_adr)/2)]])
    print("Address:", match.group("address"), "Bin1:", bin_adr[int(len(bin_adr)/2):], "Bin2Inv:",inv_bin_addr)
    
    match bin_adr[int(len(bin_adr)/2):]:
        case status if bin_adr[int(len(bin_adr)/2):] == inv_bin_addr:
            print("Adr logical reversed -> 2x 8bit = 16bit | NECext")
            protocol = "NECext"
        case _:
            print("Address does not match any proto")

    
#    match bin_adr[int(len(bin_adr)/2):]:
#        case inv_bin_addr:
#            print("Adr logical reversed -> 2x 8bit = 16bit")
#            protocol = "NECext"
#        case _:
#            print("Address does not match any proto")

#        bin_pwr = bin(int(match.group("key_power"), 16))[2:].zfill(16)
#        inv_bin_pwr = ''.join(['1' if i == '0' else '0' for i in bin_pwr[:int(len(bin_pwr)/2)]])
#        if bin_pwr[int(len(bin_pwr)/2):] == inv_bin_pwr:
#            print("pwr logical inversed -> 2x 8bit = 16bit / 32bit total")
#            protocol = "NEC"

 #       print()

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
