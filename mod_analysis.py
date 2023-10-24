

## convert type = 'raw' for analysis
######################################

# -- Old ----------
# Get min value from array. Devide all values though and convert to INT
# Assume 15000 is the absolute maximum of transmitted mark or space
# Split array by gaps greater than maximum
# -- Old ----------
#
# The goal is to convert from ...912 840 2829... to ...1 1 3... to
# compare with other signals in the database, regardless of repeats.

def button_raw2binary(btn_data):

    # The recorded pulse is alternate on/off
    ### Header 
    # Significant longer than data.
    # At least one long on to calibrate the AGC, followed by a an even or shorter off
    ### Data
    ## Manchester encoding, signal 1ms: (Bi-phase coding)
    # - 0 -> Off 0,5ms/On  0,5ms (signal 1ms) - 1:1
    # - 1 -> On  0,5ms/Off 0,5ms (signal 1ms) - 1:1
    # 2 on or 2 off can be appended -> 1:2/2:1 is possible
    ## Pulse distance control:
    # - 0 -> On 0,1ms/Off 0,9ms (signal 1ms) - 1:9
    # - 1 -> On 0,1ms/Off 1,9ms (signal 2ms) - 1:19
    ## Pulse length control:
    # - 0 -> On 0,5ms/Off 0,5ms (signal 1ms) - 1:1
    # - 1 -> On 0,5ms/Off 1,5ms (signal 2ms) - 1:3
    
    # The data are often address forward, address logic inverted, command, command logical inverted.
    # Some protocols using longer addresses, therefore only the command is logical inverted.

    try:
        data_raw = [int(numeric_string) for numeric_string in btn_data.split(" ")]
    except:
        #print("Nonnumeric value. No import for {}".format(btn_data))
        return()

    divisor = 562.2 #min(data_raw) # old
    if divisor == 0:
        #print("Prevent dividing by zero. No import for {}".format(btn_data))
        return()

    data_normalized = []
    for data_value in data_raw:
        data_normalized.append(int(data_value/divisor))

    data_headdatatail = []
    chunk_size = 2
    loopcnt = 0
    bitcnt = 0
    for chunk in [data_normalized[i:i + chunk_size] for i in range(0, len(data_normalized), chunk_size)]:
        if loopcnt == 0: # handle header data
            data_headdatatail.append(chunk)
        else:
            if len(chunk) == 2: # errorhandling, if last chunk is cut
                                # could be valid! Regarding some protcol
                match chunk[0]*chunk[1]:
                    case 1:
                        data_headdatatail.append(1)
                        bitcnt += 1
                    case 2: # 3 is correct, but there is a tolerance
                        data_headdatatail.append(0)
                        bitcnt += 1
                    case 3:
                        data_headdatatail.append(0)
                        bitcnt += 1
                    case _:
                        data_headdatatail.append(chunk) # just add tail
            else:
                continue # skip smaller chunks
        loopcnt += 1
    #print(data_headdatatail, bitcnt, "bit")

    data_binary = []
    irdata = 1
    step = 8
    for x in range(irdata, bitcnt, step):
        data_binary.append(''.join(map(str,data_headdatatail[x:x+step])))
 
    data_head = data_headdatatail[0]
    data_tail = data_headdatatail[bitcnt+1:]

    return(data_head, data_binary, data_tail, bitcnt, divisor)

