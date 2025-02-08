import ctypes
import serial
from picosdk.ps3000a import ps3000a as ps
from picosdk.functions import mV2adc, adc2mV, assert_pico_ok

# The ps3000a.dll dynamic link library (DLL) in the SDK allows you to program any supported
# oscilloscope using standard C function calls.
# A typical program for capturing data consists of the following steps:
# · Open the scope unit.
# · Set up the input channels with the required voltage ranges and coupling type.
# · Set up triggering.
# · Start capturing data. (See Sampling modes, where programming is discussed in more detail.)
# · Wait until the scope unit is ready.
# · Stop capturing data.
# · Copy data to a buffer.
# · Close the scope unit.

# set up for oscilloscope
# Create chan and status ready for use

status = {}
chandle = ctypes.c_int16()

# Opens the device/s
status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(chandle), None)

try:
    assert_pico_ok(status["openunit"])
except:
    
    print("pico not ok?")
    # powerstate becomes the status number of openunit
    powerstate = status["openunit"]

    # If powerstate is the same as 282 then it will run this if statement
    if powerstate == 282:
        # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
        status["ChangePowerSource"] = ps.ps3000aChangePowerSource(chandle, 282)
        # If the powerstate is the same as 286 then it will run this if statement
    elif powerstate == 286:
        # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
        status["ChangePowerSource"] = ps.ps3000aChangePowerSource(chandle, 286)
    else:
        raise

    assert_pico_ok(status["ChangePowerSource"])


print(status["openunit"])

