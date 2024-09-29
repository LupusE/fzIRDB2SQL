
address = "56"
codes = [ "Power: 0x88" # DEC 136
         ,"Mute: 0x84" # DEC 138
         ,"SRC1: 0x96" # DEC 150
         ]

bin_adr = bin(int(address.split), 16)[2:].zfill(16)

print(bin_adr)

