import subprocess
import re
import time

def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_COM_info(CS_port=None,TB_port=None):
    pattern = r'\((.*?)\)'  # 匹配括号内的内容，非贪婪模式
    command="wmic path Win32_PnPEntity WHERE \"Caption LIKE \'%(COM%\'\" get Caption"
    COM_info=execute_command(command)
    lines = COM_info.split('\n')
    res=['fault','fault']
    for line in lines:
        if "CH340" in line:
            match = re.search(pattern, line)
            res[1]=match.group(1)
        elif TB_port and str(TB_port) in line:
            match = re.search(pattern, line)
            res[1]=match.group(1)
        elif CS_port and str(CS_port) in line:
            match = re.search(pattern, line)
            res[0]=match.group(1)
        elif "USB Serial Port" in line:
            match = re.search(pattern, line)
            res[0]=match.group(1)
    #print (res)
    return res

def wait_for_safe(cs):
    cnt=0
    while cs.trigger_safe == False:
        time.sleep(0.05)
        cnt+=1
        if cnt>20:
            if not cs.armed:
                cs.clr_armed=1