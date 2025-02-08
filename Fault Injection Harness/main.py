from utils import get_COM_info,wait_for_safe
import cwlite
import cshouter
import uart_ctrl
import time
import winsound
# you may want to change these parameters
limit=1000   #Fault injection attemps
offsets=range(132,133,1)   #time offset list
showdetail=1    #do you want to see every faults
#the correct output
excepted_res="64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 "

def judgestr(str_ret):
    array = str_ret.split("\n")
    if len(array)<64:
        print("crash\n")
        return False
    a1=array[1:33]
    a2=array[33:97]
    #print(array)
    #print(a2[:32])
    if a1[:2]==a2[:2]:
        return False
    return True


#get COM id of target board and chipshouter
CS_COM,TB_COM=get_COM_info(13,9)
if "fault" in [CS_COM,TB_COM]:
    print("get COM fault")
    exit()
#initialize chipwhisperer and chipshouter
cs=cshouter.init_cs(CS_COM=CS_COM)
scope=cwlite.init_scope()
cshouter.set_params(cs=cs)
print(cs.voltage)
cwlite.init_scope_settings(scope=scope)


#get devices armed
time.sleep(2)
cshouter.chk_n_arm(cs=cs)
time.sleep(2)
# scope.arm()

#zero init state of serial
right=0
wrong=0


cur=0
cur_upperbond=len(offsets)
fault_pattern=dict()
while(True):
    
    target_ser=0
    cshouter.chk_n_arm(cs=cs)
    time.sleep(0.5)
    cwlite.reset_target(scope=scope)
    time.sleep(0.5)

    while(True):
        wait_for_safe(cs)
        if (right+wrong)%limit==0 and right+wrong>0:
            print(str(offsets[cur])+"---\n"+str(wrong+right)+"\tfault rate:"+str(wrong/(right+wrong)))
            right=0
            wrong=0
            cur+=1
            print(fault_pattern)
            fault_pattern=dict()
        if cur>=cur_upperbond:
            winsound.Beep(1500, 1000)
            exit()
        scope.glitch.ext_offset = offsets[cur]
        scope.arm()
        if target_ser:
            target_ser.flushInput()
        target_ser=uart_ctrl.connect_lite(target_ser=target_ser,TB_COM=TB_COM)
        ret='wrong'
        ret=uart_ctrl.start_target_program(target_ser=target_ser)

        # you may wanna 
        str_ret = ret.decode('utf-8')
        #if judgestr(str_ret):
        #print(str_ret)
        #if str_ret=="1":
        #if ret==b"\x06<\x06<\x06<":
        if str_ret==excepted_res:
        #if str_ret=="@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~":
        #if str_ret=="64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127":
        #if "\n203\n211\n246\n238\n186\n103\n107\n33\n224\n242\n196\n117\n34\n41\n36\n130\n253\n131\n15\n51\n12\n29\n132\n167\n148\n187\n148\n114\n139\n45\n147\n254\n190\n76\n24\n234\n229\n167\n224\n23\n227\n95\n160\n144\n222\n36\n38\n46\n112\n149\n26\n209\n215\n223\n179\n168\n201\n109\n17\n52\n251\n24\n121\n242" in str_ret:
        #if str_ret=="e\n177\n36\n28\n150\n179\n94\n225\n133\n227\n154\n88\n229\n180\n129\n146\n91\n229\n59\n62\n195\n27\n93\n8\n35\n102\n2\n27\n93\n125\n245\n184\n50\n224\n149\n26\n35\n156\n208\n163\n55\n219\n186\n109\n226\n211\n160\n148\n129\n5\n195\n18\n10\n7\n74\n69\n7\n153\n170\n37\n71\n231\n0\n235\n28":
        #if str_ret=="e\n98\n128\n18\n185\n12\n18\n20\n84\n192\n44\n194\n147\n122\n71\n168\n124\n127\n150\n209\n185\n26\n164\n37\n137\n2\n41\n65\n114\n13\n111\n106\n139\n105\n5\n196\n137\n54\n66\n80\n210\n19\n8\n161\n61\n123\n0\n82\n157\n212\n243\n3\n233\n89\n24\n237\n202\n6\n130\n230\n79\n28\n56\n50\n165":
        #if str_ret=="e\n9\n203\n211\n246\n238\n186\n103\n107\n33\n224\n242\n196\n117\n34\n41\n36\n130\n253\n131\n15\n51\n12\n29\n132\n167\n148\n187\n148\n114\n139\n45\n147\n254\n190\n76\n24\n234\n229\n167\n224\n23\n227\n95\n160\n144\n222\n36\n38\n46\n112\n149\n26\n209\n215\n223\n179\n168\n201\n109\n17\n52\n251\n24\n121\n242":
        #if str_ret=="e\n0\n2\n4\n6\n8\n10\n12\n14\n16\n18\n20\n22\n203\n211\n246\n238\n186\n103\n107\n33\n224\n242\n196\n117\n34\n41\n36\n130\n253\n131\n15\n51\n12\n29\n132\n167\n148\n187\n148\n114\n139\n45\n147\n254\n190\n76\n24\n234\n229\n167\n224\n23\n227\n95\n160\n144\n222\n36\n38\n46\n112\n149\n26\n209\n215\n223\n179\n168\n201\n109\n17\n52\n251\n24\n121\n242":
        #if str_ret=="e\n41\n205\n158\n170\n163\n194\n207\n45\n245\n106\n123\n201\n48\n21\n65\n217\n236\n217\n65\n225\n15\n169\n137\n121\n22\n176\n67\n96\n33\n163\n123\n122\n208\n70\n186\n253\n128\n12\n164\n116\n59\n145\n74\n34\n146\n83\n27\n197\n185\n205\n249\n194\n66\n131\n52\n102\n77\n239\n208\n163\n141\n43\n150\n127":
            right+=1
        else:
            wrong+=1
            if showdetail:
                print(right+wrong)
                #print("wrong!")
                print(ret)
                winsound.Beep(1500, 200)
            if ret not in fault_pattern:
                fault_pattern[ret]=1
            else:
                fault_pattern[ret]+=1
            break
    cs.armed = False
    time.sleep(2)