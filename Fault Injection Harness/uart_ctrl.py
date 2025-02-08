import serial
import time
#target_ser=0
def reconnect(target_ser,TB_COM):
    try:
        if target_ser:
            target_ser.close()
    except Exception as e:
        print(e)
    finally:
        print("re-connectting...")
        new_target_ser = serial.Serial(TB_COM, 115200)
    return new_target_ser

def connect_lite(target_ser,TB_COM):
    if not target_ser:
        new_target_ser = serial.Serial(TB_COM, 115200)
    else:
        new_target_ser=target_ser
    return new_target_ser

def start_target_program(target_ser):
    target_ser.write(b'a')
    time.sleep(0.15)
    #print(target_ser.in_waiting)
    ret = target_ser.read(target_ser.in_waiting)[:]
    #ret=101010
    #print(ret)
    return ret

if __name__ == "__main__":
    ts=connect_lite(0,'COM15')
    start_target_program(ts)