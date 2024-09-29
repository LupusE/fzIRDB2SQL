#!/usr/bin/env python3

import math
## value a, value b, tolerance
math.isclose(10008,9000, rel_tol=0.09) ## 5% -> rel_tol=0.05



btn_data = [
	'10008 4489 647 573 614 575 612 578 620 570 617 572 615 575 612 576 611 578 620 1642 650 1645 647 1646 645 1648 644 1649 643 1649 643 1651 651 1642 650 1643 649 542 645 542 645 540 637 549 638 548 639 546 641 545 642 543 644 1644 648 1643 638 1653 639 1652 640 1651 641 1650 642 1650 642 39750 9883 2223 642' # candle light1 1
	,'9694 4487 639 546 631 542 624 547 630 541 625 545 621 547 630 539 628 541 625 1646 625 1649 632 1642 629 1642 629 1643 628 1644 627 1643 628 1642 629 1641 619 546 620 543 623 1644 627 539 617 546 621 542 624 540 616 547 620 1648 623 1643 628 537 619 1651 620 1648 623 1645 626 1642 629 39758 9542 2215 629' # candle light1 2

	,'9751 4494 630 546 627 549 634 542 631 545 628 548 635 541 632 544 629 547 636 1645 629 1653 631 1650 634 1647 627 1654 630 1651 633 1648 636 1645 628 547 626 550 633 542 631 544 629 547 626 550 633 542 631 544 629 1653 631 1650 634 1647 627 1654 630 1651 633 1647 627 1654 630 1651 633 39795 9729 2233 627 95978 9727 2227 633'
	,'9762 4498 636 541 632 545 627 549 634 543 629 547 625 551 632 544 629 548 635 1646 627 1655 629 1653 631 1651 633 1648 636 1646 627 1654 630 1651 633 544 628 1652 632 544 628 547 625 551 632 543 629 546 626 549 634 1646 627 549 634 1647 626 1654 630 1652 632 1649 635 1646 627 1654 630 39800 9771 2229 631 95988 9740 2231 629'
	,'9791 4500 634 545 627 551 632 545 627 551 632 545 627 551 632 547 636 544 639 1647 637 1656 638 1654 630 1652 632 1649 635 1647 626 1654 630 1652 632 545 638 541 632 1648 625 1655 629 547 625 549 634 542 631 545 627 1653 631 1651 633 544 628 548 635 1646 627 1655 629 1654 630 1655 628 39718 9739 2226 634 95772 9739 2235 625'
	,'9772 4497 626 551 632 545 627 549 634 543 629 548 635 542 630 546 626 551 632 1648 635 1647 637 1646 627 1655 629 1653 631 1650 634 1647 626 1655 628 547 625 1654 630 1652 632 1649 635 542 630 545 627 548 624 550 633 1647 626 549 634 541 631 544 628 1651 633 1648 625 1656 627 1653 631 39771 9756 2229 631 95990 9710 2231 629 96005 9705 2227 633 96002 9697 2230 630'
	,'9669 4496 626 543 629 542 630 540 622 548 624 546 626 544 628 541 631 539 623 1653 630 1645 628 1648 625 1651 622 1654 629 1646 627 1649 624 1651 622 548 624 545 627 1648 625 545 627 542 630 540 622 547 625 545 627 1649 624 1651 622 548 624 1651 622 1654 619 1656 627 1648 625 1651 622 39806 9645 2234 625 95989 9640 2228 621'
	,'9666 4490 622 548 624 546 626 544 628 541 621 549 623 546 626 544 628 541 621 1654 629 1646 627 1649 624 1651 622 1654 629 1646 627 1649 624 1651 622 548 624 1650 623 1652 621 549 623 546 626 543 629 539 623 547 625 1649 624 546 626 543 629 1646 627 1649 624 1651 622 1653 630 1645 628 39805 9643 2225 624'
	,'9658 4500 622 549 623 548 624 548 624 548 624 547 625 547 625 547 625 546 626 1652 621 1657 626 1651 622 1656 627 1650 623 1655 628 1649 624 1654 629 542 630 541 621 550 622 1656 627 544 628 544 628 543 629 542 630 1648 625 1653 630 1647 626 546 626 1652 631 1647 626 1652 621 1657 626 39808 9690 2230 629 96005 9668 2232 627'
	,'9692 4496 626 546 626 545 627 545 627 544 628 543 629 543 629 542 630 542 630 1646 627 1651 632 1646 627 1651 632 1646 627 1651 632 1645 628 1649 624 548 624 1653 630 541 631 1646 627 544 628 544 628 543 629 542 630 1646 627 545 627 1650 623 549 623 1654 629 1648 625 1653 630 1647 626 39811 9688 2229 630 96004 9679 2229 630 96005 9676 2228 631'
	,'9838 4494 650 546 637 552 641 542 630 550 633 546 637 543 629 548 635 543 629 1652 632 1653 631 1655 639 1649 635 1653 641 1647 637 1651 633 1655 639 545 638 1649 635 551 642 543 640 1651 643 547 636 550 643 546 637 1653 641 548 645 1644 639 1653 641 548 645 1649 645 1649 634 1654 640 39739 9840 2230 640 95316 9973 2232 648 95927 9794 2225 635'
	,'9861 4497 636 546 637 546 637 544 639 543 629 551 632 548 635 546 637 543 629 1655 639 1647 636 1651 632 1654 640 1648 635 1652 642 1650 644 1650 644 547 646 549 644 555 648 553 650 1651 653 544 649 549 644 555 648 1655 649 1656 648 1656 648 1658 646 553 650 1648 646 1650 644 1651 643 39801 9765 2232 627 95965 9781 2235 635'

	#,'71 3785 87 3745 135 3729 135 3770 72 3790 77 3784 82 3747 134 3784 81 675 84 3019 138 3726 137 658 82 3055 86 3785 73 3748 138 3803 73 3748 137 657 84 3077 82 3786 75 3748 137 3768 75 3784 83 3744 136 661 78 3058 83 3745 136 3781 86 3780 81 3749 131 3732 132 3777 62 3793 75 7681 83 11497 130 7633 128 3768 78 3751 130 3800 80 19263 91'
	#,'80 3782 80 3750 129 7629 81 3752 126 3737 91 7686 78 647 127 3046 74 7652 91 15428 73 7674 90 7666 80 3786 75 11546 81 3807 70 3791 75 3789 71 3797 65 3789 81 3782 81 3748 130 661 80 3027 130 3786 80 3784 78 3783 81 677 81 3062 74 3789 75 3749 135 3764 81 684 67 3066 76 3838 82 3743 138 3767 75 3793 66 3750 139 3767 72 687 70 3069 68 3783 139 4501 139 3043 72 7611 139 3774 64 3791 74 688 67 3826 73 3064 77 3817 78 3787 73 15380 72 7653 77 3764 138 3758 139 3771 66 644 139 6908 69 3748 138 619 139 3000 138 3724 138 664 70 3088 72 3793 68 3796 66 7661 65 3794 69 3829 68 3794 69 3816 66 7612 140 3722 141 11450 138 7686 70 15419 66 3750 138 4480 140 2999 139 7688 67 7659 67 3797 66 4551 70 3827 68 3070 69 3814 67 643 140 2999 140 3770 68 7612 139 7618 141 666 67'
	#,'141 3723 140 3723 140 3774 64 3796 68 7654 78 3790 68 3813 70 687 72 3064 79 4544 75 6929 71 3791 73 689 66 7688 79 3082 75 3789 73 7612 138 3767 76 3786 77 682 75 3060 82 3786 72 3812 70 7654 76 7653 72 3748 139 4529 67 3068 75 3810 70 3748 140 7666 70 3798 65 3793 72 4550 70 3067 72 688 68 3091 68 3795 68 7613 139 7631 72 688 68 3825 75 3066 70 4570 71 6932 70 3795 68 3748 140 4526 71 3825 73 3064 78 7684 71 3749 138 3725 138 3770 68 7613 139 3767 74 3766 137 621 137 6908 70 644 138 3041 78 3788 72 3748 137 659 81 3062 74 3792 67 689 70 3087 74 3790 73 3749 136 3768 71 3791 75 3783 83 642 132 3042 78 3748 134 3786 79 3749 131 3769 75 3750 133 3731 131 3765 81 3785 73 649 129 3044 78 3769 132 3764 83 3789 65 3825 79 3787 70 3757 129 3769 74 684 75 3059 81 677 81 3078 81 3750 130 3770 72 3791 74 3793 67 3754 132 626 133 3040 81 679 78 3062 77 3770 130 627 132 3047 69 3792 74 3788 77 3750 133 3766 78 684 69 3064 79 641 136 3044 73'
	] 



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

    print("### data_raw")
    print(data_raw)

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
    

