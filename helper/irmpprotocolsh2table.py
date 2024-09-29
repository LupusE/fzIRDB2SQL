
import re

irmpprotocolfile = 'helper/irmp_db/irmpprotocols.h'

readfile = open(irmpprotocolfile,'r')
irmpdata = readfile.read()
readfile.close()

pattern = re.compile(r"""
#                ^\s+\#define\s+(?P<proto_header1>.*?)_START_BIT_PULSE_TIME\s+(?P<start_pulse>.*?)\s+*\n
#                ^\s+\#define\s+(?P<proto_header2>.*?)_START_BIT_PAUSE_TIME\s+(?P<start_pause>.*?)\s+*\n

                ^*define\ NEC_START_BIT_PULSE_TIME\s+(?P<start_pulse>.*?)\s+*\n
                #^\s+\#define\sNEC_START_BIT_PAUSE_TIME\s+(?P<start_pause>.*?)\s+*\n


#                ^\s+one\s+(?P<mark_one>.*?)\s+(?P<space_one>.*?)\n
#                ^\s+zero\s+(?P<mark_zero>.*?)\s+(?P<space_zero>.*?).*\n
#                ^\s+pre_data\s+0x(?P<address>....).*\n
#                ^\s+KEY_POWER\s+0x(?P<key_power>....).*\n
 
                """, re.VERBOSE | re.MULTILINE | re.DOTALL)

print(pattern)