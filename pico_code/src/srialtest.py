import serial
target_ser=0
if target_ser:
    target_ser.flushInput()
if not target_ser:
    target_ser = serial.Serial("COM9", 115200)
if target_ser:
    print("target connected")

target_ser.write(b'e')