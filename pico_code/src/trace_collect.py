import ctypes
import serial
from picosdk.ps3000a import ps3000a as ps
from picosdk.functions import mV2adc, adc2mV, assert_pico_ok
import numpy as np
import matplotlib.pyplot as plt

from pwn import *
from tqdm import tqdm
import random
import time

import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300

from Trace_processor_pico3000a import TraceProcessor


#simple parameters
#ch A
parameter_enableA=1
parameter_coupling_type_A="PS3000A_DC"        #coupling
parameter_chARange="PS3000A_50MV"          #scale

#ch B
parameter_enableB=1
parameter_coupling_type_B="PS3000A_DC"        #coupling
parameter_chBRange="PS3000A_50MV"          #scale

#time
parameter_shift=0

#trigger
parameter_trig_delay=0
parameter_threshold_mV=1500

#curve
SAMPLING_RATE = '500M' # ?
TOTAL_SAMPLE_NUM = 1200 # 50_000 # 32_000_000 
TRACE_NUM = 5 # how many traces do we need?

#connectivity
parameter_target_serial="COM9"

#other
IS_SAVE = False
IS_DEBUG = True

#filename
board = 'stm32f407zgt6'
algo = 'sha3_512'
optlevel = 'O0'

#ps3000a.PS3000A_RANGE = make_enum([
#     "PS3000A_10MV",
#     "PS3000A_20MV",
#     "PS3000A_50MV",
#     "PS3000A_100MV",
#     "PS3000A_200MV",
#     "PS3000A_500MV",
#     "PS3000A_1V",
#     "PS3000A_2V",
#     "PS3000A_5V",
#     "PS3000A_10V",
#     "PS3000A_20V",
#     "PS3000A_50V",
#     "PS3000A_MAX_RANGES",
# ])

# sampling_rate_to_timebase = {
#     "1G"    : 0,
#     "500M"  : 1,
#     "250M"  : 2,
#     "125M"  : 3,
#     "62.5M" : 4,
#     "31.25M": 6,
#     "25M"   : 7,
#     "12.5M" : 12,
#     "6.25M" : 22,
#     "5M"    : 27,
#     "2.5M"  : 52,
#     "1.25M" : 102,
#     "1M"    : 127,
#     "0.5M"  : 252,
#     "0.1M"  : 1252
# }



# The ps3000a.dll dynamic link library (DLL) in the SDK allows you to program any supported oscilloscope using standard C function calls.  

# A typical program for capturing data consists of the following steps:  
# - Open the scope unit.  
# - Set up the input channels with the required voltage ranges and coupling type.  
# - Set up triggering.  
# - Start capturing data. (See Sampling modes, where programming is discussed in more detail.)  
# - Wait until the scope unit is ready.  
# - Stop capturing data.  
# - Copy data to a buffer.  
# - Close the scope unit.  




# Step 1: Open the scope unit
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



# Step 2.a: Input channel parameters

## Set up parameters of channel A
channel_A = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_A"]
enabled_A = parameter_enableA
coupling_type_A = ps.PS3000A_COUPLING[parameter_coupling_type_A] # DC
chARange = ps.PS3000A_RANGE[parameter_chARange] # amplitude
analogue_offset_A = 0.0

# Set up parameters of channel B 
channel_B = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_B"]
enabled_B = parameter_enableB
coupling_type_B = ps.PS3000A_COUPLING[parameter_coupling_type_B] # DC
chBRange = ps.PS3000A_RANGE[parameter_chBRange] # amplitude
analogue_offset_B = 0.0

# set up channel A
status["setChA"] = ps.ps3000aSetChannel(chandle, channel_A, enabled_A, coupling_type_A, chARange, analogue_offset_A)
assert_pico_ok(status["setChA"])

# set up channel B
status["setChB"] = ps.ps3000aSetChannel(chandle, channel_B, enabled_B, coupling_type_B, chBRange, analogue_offset_B)
assert_pico_ok(status["setChB"])

# find maximum ADC count value
# handle = chandle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps3000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])



# Step 2.b: Time axis parameters

# Setting the number of sample to be collected

shift = parameter_shift
if shift <= 0:  # left shift
    preTriggerSamples = 0
    postTriggerSamples = TOTAL_SAMPLE_NUM + np.abs(shift)
    left_shift = np.abs(shift)
else:           # right shift
    preTriggerSamples = shift
    postTriggerSamples = TOTAL_SAMPLE_NUM - np.abs(shift)
    left_shift = 0
maxsamples = TOTAL_SAMPLE_NUM 

# Step 2.c: Sampling Rate Parameters

# Gets timebase innfomation parameters

# sampling_rate = "1G" # ?

sampling_rate_to_timebase = {
    "1G"    : 0,
    "500M"  : 1,
    "250M"  : 2,
    "125M"  : 3,
    "62.5M" : 4,
    "31.25M": 6,
    "25M"   : 7,
    "12.5M" : 12,
    "6.25M" : 22,
    "5M"    : 27,
    "2.5M"  : 52,
    "1.25M" : 102,
    "1M"    : 127,
    "0.5M"  : 252,
    "0.1M"  : 1252
}


timebase = sampling_rate_to_timebase[SAMPLING_RATE]
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int16()
status["GetTimebase"] = ps.ps3000aGetTimebase2(chandle, timebase, maxsamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["GetTimebase"])
print('timeIntervalns', timeIntervalns.value)



# Step 3: Trigger parameters
TRIG_DELAY = parameter_trig_delay # how many samples to SKIP


# The PicoScope 3000 Series D models have an external trigger input (marked Ext). This external trigger input is scaled to a 16-bit value as follows:
# external max value, 5v  -- +32 767 / 0x7FFF
#                   , 0V  -- 0 / 0x00
# external min value, -5v -- –32 767 / 0x8001
trigger_source = ps.PS3000A_CHANNEL["PS3000A_EXTERNAL"]
trigger_enable = 1
# 1.5V trigger
threshold_mV = parameter_threshold_mV
threshold = int(32767 * threshold_mV / 5000)
direction = ps.PS3000A_DIGITAL_DIRECTION["PS3000A_DIGITAL_DIRECTION_HIGH"] # Rising edge
autoTrigger_ms = 0 

# Sets up single trigger
status["trigger"] = ps.ps3000aSetSimpleTrigger(chandle, trigger_enable, trigger_source, threshold, direction, TRIG_DELAY, autoTrigger_ms)
assert_pico_ok(status["trigger"])





# Step 4: Trace Saving Parameters


TRACESET_NAME = f"{board}.{algo}.{optlevel}.{TOTAL_SAMPLE_NUM}.{TRACE_NUM}" # trace set name


# For aes, input/output lenght is 16
INPUT_BYTES = 16
OUTPUT_BYTES = 16

read_path_chA = ''
write_path_chA = "./traces/" + TRACESET_NAME + ".chA" + ".trs"

trace_handler_chA = TraceProcessor(read_path_chA, write_path_chA)
trace_handler_chA.CurveNum = TRACE_NUM
trace_handler_chA.SampleNum = maxsamples
# The following is picoscope 3000 specific
trace_handler_chA.Sample_Encoding_inspector = int('02', 16) # use int16 to save
trace_handler_chA.BytesOfOneSample = 2
# trace_handler_chA.isFloat_for_independent_write = 0
# trace_handler_chA.BytesOfOneSample_for_independent_write = 2

trace_handler_chA.BytesOfCipher = INPUT_BYTES + OUTPUT_BYTES
trace_handler_chA.write_trace_head()


read_path_chB = ''
write_path_chB = "./traces/" + TRACESET_NAME + ".chB" + ".trs"

trace_handler_chB = TraceProcessor(read_path_chB, write_path_chB)
trace_handler_chB.CurveNum = TRACE_NUM
trace_handler_chB.SampleNum = maxsamples
# The following is picoscope 3000 specific
trace_handler_chB.Sample_Encoding_inspector = int('02', 16) # use int16 to save
trace_handler_chB.BytesOfOneSample = 2
# trace_handler_chB.isFloat_for_independent_write = 0
# trace_handler_chB.BytesOfOneSample_for_independent_write = 2

trace_handler_chB.BytesOfCipher = INPUT_BYTES + OUTPUT_BYTES
trace_handler_chB.write_trace_head()


# traces_file = "../traces/t/" + TRACESET_NAME # file path to save the raw traces 
# pts_file = "../traces/p/" + TRACESET_NAME # file path to save the plaintexts

# traces_array = np.zeros(TRACE_NUM, maxsamples)
# pts_array = np.zeros(TRACE_NUM, )

# Creates a overlow location for data
overflow = ctypes.c_int16()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxsamples)

# Create buffers ready for assigning pointers for data collection
bufferAMax = (ctypes.c_int16 * maxsamples)()
bufferAMin = (ctypes.c_int16 * maxsamples)()  # used for downsampling which isn't in the scope of this example
bufferBMax = (ctypes.c_int16 * maxsamples)()
bufferBMin = (ctypes.c_int16 * maxsamples)()  # used for downsampling which isn't in the scope of this example


# Step 5: Communication with the Target
target_ser=0
if target_ser:
    target_ser.flushInput()
if not target_ser:
    target_ser = serial.Serial(parameter_target_serial, 115200)
if target_ser:
    print("target connected")







# Step 6: Capturing the data

if IS_DEBUG:
    TRACE_NUM = 300

# collect
for i in tqdm(range(TRACE_NUM)):
    # Setting block capture mode
    status["runblock"] = ps.ps3000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, 1, None, 0, None, None)
    assert_pico_ok(status["runblock"])

    # Setting the data buffer location for data collection from channel A
    source = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_A"]
    ratio_mode = ps.PS3000A_RATIO_MODE["PS3000A_RATIO_MODE_NONE"]
    status["SetDataBuffersA"] = ps.ps3000aSetDataBuffers(chandle, source, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, ratio_mode)
    assert_pico_ok(status["SetDataBuffersA"])

    # Setting the data buffer location for data collection from channel B
    source = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_B"]
    ratio_mode = ps.PS3000A_RATIO_MODE["PS3000A_RATIO_MODE_NONE"]
    status["SetDataBuffersB"] = ps.ps3000aSetDataBuffers(chandle, source, ctypes.byref(bufferBMax), ctypes.byref(bufferBMin), maxsamples, 0, ratio_mode)
    assert_pico_ok(status["SetDataBuffersB"])

    # Send trigger bytes to the targer MCU, which will pull up a pin after receiving the plaintext
    target_ser.write(b'e')

    # Checks data collection to finish the capture
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0) # ?
    while ready.value == check.value:
        status["isReady"] = ps.ps3000aIsReady(chandle, ctypes.byref(ready))

    status["GetValues"] = ps.ps3000aGetValues(chandle, left_shift, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["GetValues"]) # ?

    if IS_SAVE:
        get_text = b"\x00" * 16
        trace_handler_chA.write_one_trace(text=get_text, samples=np.asarray(bufferAMax, dtype=np.int16))
        trace_handler_chB.write_one_trace(text=get_text, samples=np.asarray(bufferBMax, dtype=np.int16))


    ########################## debug lines
    if IS_DEBUG:
        # Creates the time data
        times = np.linspace(0, (cmaxSamples.value) * timeIntervalns.value, cmaxSamples.value)

        # Converts ADC from channel A to mV
        adc2mVChAMax = adc2mV(bufferAMax, chARange, maxADC)
        adc2mVChBMax = adc2mV(bufferBMax, chBRange, maxADC)

        # Plots the data from channel A
        plt.figure()
        plt.plot(times, adc2mVChAMax[:], linewidth=0.1)
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()

        # Plots the data from channel B
        # plt.figure()
        # plt.plot(times, adc2mVChBMax[:], linewidth=0.1)
        # plt.xlabel('Time (ns)')
        # plt.ylabel('Voltage (mV)')
        # plt.show()

        # plt.figure()
        # plt.plot(times, bufferBMax[:], linewidth=0.1)
        # plt.xlabel('Time (ns)')
        # plt.ylabel('ADC Buffer')
        # plt.show()

        # print(np.asarray(bufferAMax, dtype=np.int16))
        # print(np.asarray(bufferBMax, dtype=np.int16))
    