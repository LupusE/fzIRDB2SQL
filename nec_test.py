#!/usr/bin/env python3

import math
## value a, value b, tolerance
math.isclose(10008,9000, rel_tol=0.09) ## 5% -> rel_tol=0.05

raw_tol = 0.05

#proto_nec = [
nec_startbit_mark = 9000
nec_startbit_space = 4500
#    ,nec_startbit_pause == 2250
#    ,nec_pulse == 560
#    ,nec_one_pause == 1690
#    ,nec_zero_pause == 560
nec_repeat_frame = 40000 # 40267
#    ,nec_length_addr == 16
#    ,nec_length_comm == 16
#    ,nec_length_data == 32
#    ,nec_stopbit == true
#    ,nec_lsb == true
#    ]

btn_data = [
    '9105 4479 619 575 565 576 543 572 567 574 566 575 544 570 569 572 567 573 546 1685 594 1639 682 1629 568 1690 600 1634 677 1634 573 1685 595 1639 672 495 593 574 545 1686 593 575 544 1688 591 576 543 1689 601 1632 679 1632 575 1683 597 572 547 1684 595 573 546 1686 593 574 545 570 569 40267 9103 2248 601 97067 9081 2244 595' # NEC
   #,'9232 4516 620 530 595 557 595 558 595 532 594 559 593 559 594 532 593 559 594 1684 594 1687 617 1685 593 1685 592 1688 616 1685 593 1685 593 1687 618 533 618 1664 616 533 592 1712 593 534 591 560 593 559 592 535 592 1711 594 532 594 1712 592 533 593 1712 592 1686 592 1686 592 1689 616 40557 9226 2239 594 97768 9223 2238 594' # NEC
   #,'1282 412 1272 421 431 1262 1275 418 1277 417 1278 441 411 1255 439 1253 431 1261 1276 418 1277 443 409 8634 1278 416 1279 414 438 1255 1272 422 1273 447 1248 419 433 1259 436 1257 438 1256 1281 413 1271 448 404 8640 1272 422 1273 420 432 1261 1276 417 1278 416 1279 440 412 1254 430 1262 432 1260 1277 417 1278 442 410 8631 1281 412 1272 448 404 1263 1274 420 1275 419 1275 418 434 1259 436 1258 436 1257 1280 414 1281 440 412 8636 1276 418 1276 417 435 1259 1278 416 1279 416 1279 441 411 1256 438 1254 440 1254 1273 422 1273 447 405 8643 1280 414 1281 440 412 1255 1272 422 1273 447 1248 420 432 1260 435 1259 436 1258 1279 415 1280 440 412 8634 1278 416 1279 415 437 1256 1281 413 1271 422 1272 421 431 1261 434 1259 436 1257 1280 414 1281 439 403' # Unknown
   ,'9250 4475 613 559 581 534 606 536 604 538 602 540 610 531 609 533 607 535 605 1639 609 1636 612 1633 605 1640 608 561 579 1638 610 1635 602 1640 608 559 581 1634 604 1638 610 1631 607 559 581 532 608 530 610 529 600 1640 608 532 608 532 608 532 608 1635 603 1642 606 1638 610 1633 605 40942 9180 2212 606 96142 9223 2219 610 95891 9188 2219 610 95827 9179 2217 601' # NECext
    ]

def button_raw2binary(btn_data):

    try:
        data_raw = [int(numeric_string) for numeric_string in btn_data.split(" ")]
    except:
        #print("Nonnumeric value. No import for {}".format(btn_data))
        return()

    print("### data_raw")
    print(data_raw)

    print("Raw1:", data_raw[0])

    if math.isclose(data_raw[0],nec_startbit_mark, rel_tol=raw_tol) and math.isclose(data_raw[1],nec_startbit_space, rel_tol=raw_tol):
        print("Maybe NEC")
    
    divisor = 500 #562.2 #min(data_raw) # old
    divisor = min(data_raw) # old
    if divisor == 0:
        #print("Prevent dividing by zero. No import for {}".format(btn_data))
        return()

    data_normalized = []
    for data_value in data_raw:
        data_normalized.append(int(data_value/divisor))

    print("### data_normalized")
    print(data_normalized)


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

for i in btn_data:
    print(button_raw2binary(i))
    #button_raw2binary(i)
    

