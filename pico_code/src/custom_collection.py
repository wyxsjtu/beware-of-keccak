#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
# PS3000A BLOCK MODE EXAMPLE
# This example opens a 3000a driver device, sets up one channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import serial
from picosdk.ps3000a import ps3000a as ps
import numpy as np
from picosdk.functions import mV2adc, adc2mV, assert_pico_ok
from ps3000aExamples.Trace_processor import TraceProcessor

### serial port settings ###

# set up of serial
ser = serial.Serial()
ser.port = 'COM20'
ser.baudrate = 9600
ser.bytesize = 8
ser.parity='N'
ser.stopbits = 2
ser.timeout = 5

text_buffer_s = b'\x73'  # ASCII 's'
text_buffer_p = b'\x70'  # ASCII 'p'

input_bytes = 9
output_bytes = 9

### end serial port settings ###

### oscilloscope settings ###




# set up for oscilloscope
# Create chandle and status ready for use

status = {}
chandle = ctypes.c_int16()
# Opens the device/s
status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(chandle), None)

try:
    assert_pico_ok(status["openunit"])
except:

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


# collection parameters

# ----------------------------------------- Set Channels------------------------------------------

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

# Set up parameters of channel A
# handle = chandle
# channel = PS3000A_CHANNEL_A = 0
# enabled = 1
# coupling type = PS3000A_DC = 1
# range = PS3000A_10V
# analogue offset = 0 V
channel_A = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_A"]
enabled_A = 1
coupling_type_A = ps.PS3000A_COUPLING["PS3000A_DC"] # DC
chARange = ps.PS3000A_RANGE["PS3000A_50MV"] # amplitude
analogue_offset_A = 0.0


# Set up parameters of channel B 
# handle = chandle
# channel = PS3000A_CHANNEL_A = 0
# enabled = 1
# coupling type = PS3000A_DC = 1
# range = PS3000A_10V
# analogue offset = 0 V
channel_B = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_B"]
enabled_B = 1
coupling_type_B = ps.PS3000A_COUPLING["PS3000A_DC"] # DC
chBRange = ps.PS3000A_RANGE["PS3000A_50MV"] # amplitude
analogue_offset_B = 0.0


# find maximum ADC count value
# handle = chandle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps3000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])


# ----------------------------------------- Set Time Axis ------------------------------------------

# Setting the number of sample to be collected
total_sample_num = 10000 
shift = 0
if shift <= 0:  # left shift
    preTriggerSamples = 0
    postTriggerSamples = total_sample_num + np.abs(shift)
    left_shift = np.abs(shift)
else:           # right shift
    preTriggerSamples = shift
    postTriggerSamples = total_sample_num - np.abs(shift)
    left_shift = 0
maxsamples = total_sample_num
# ref. codes
# preTriggerSamples = 0  # right_shift
# postTriggerSamples = 170000
# left_shift = 1000      # used when getting datas
# maxsamples = preTriggerSamples + postTriggerSamples - left_shift


# ----------------------------------------- Set Trigger ------------------------------------------

# Sets up single trigger parameters
# Handle = Chandle
# Source = ps3000A_channel_B = 0
# Enable = 0
# Threshold = 1024 ADC counts
# Direction = ps3000A_Falling = 3
# Delay = 0
# autoTrigger_ms = 1000

# The PicoScope 3000 Series D models have an external trigger input (marked Ext). This external trigger input is scaled to a 16-bit value as follows:
# external max value, 5v  -- +32 767 / 0x7FFF
#                   , 0V  -- 0 / 0x00
# external min value, -5v -- –32 767 / 0x8001
trigger_source = ps.PS3000A_CHANNEL["PS3000A_EXTERNAL"]
trigger_enable = 1
# 1.5V trigger
threshold_mV = 1500
threshold = int(32767 * 1500 / 5000)
direction = ps.PS3000A_DIGITAL_DIRECTION["PS3000A_DIGITAL_DIRECTION_HIGH"]
delay = 0
autoTrigger_ms = 0

# ----------------------------------------- Set Sampling Rate------------------------------------------

# Gets timebase innfomation parameters

#sampling_rate_to_timebase = {
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
sampling_rate = "125M"


# ----------------------------------------- Set Trace Saving Parameters------------------------------------------

# Trace saving settings
collection_trace_num = 500000

read_path_chA = ''
write_path_chA = "G:My_Raw_trace.trs"

trace_handler_chA = TraceProcessor(read_path_chA, write_path_chA)
trace_handler_chA.CurveNum = collection_trace_num
trace_handler_chA.SampleNum = maxsamples
# trace_handler.Sample_Encoding_inspector = int('01', 16)
# use int16 to save
trace_handler_chA.isFloat_for_independent_write = 0
trace_handler_chA.BytesOfOneSample_for_independent_write = 2

trace_handler_chA.BytesOfCipher = input_bytes + output_bytes
trace_handler_chA.write_trace_head()


read_path_chB = ''
write_path_chB = "G:My_Raw_trace.trs"

trace_handler_chB = TraceProcessor(read_path_chB, write_path_chB)
trace_handler_chB.CurveNum = collection_trace_num
trace_handler_chB.SampleNum = maxsamples
# trace_handler.Sample_Encoding_inspector = int('01', 16)
# use int16 to save
trace_handler_chB.isFloat_for_independent_write = 0
trace_handler_chB.BytesOfOneSample_for_independent_write = 2

trace_handler_chB.BytesOfCipher = input_bytes + output_bytes
trace_handler_chB.write_trace_head()

# =================================================End of Settings here  =========================================




# set up channel A
status["setChA"] = ps.ps3000aSetChannel(chandle, channel_A, enabled_A, coupling_type_A, chARange, analogue_offset_A)
assert_pico_ok(status["setChA"])

# set up channel B
status["setChB"] = ps.ps3000aSetChannel(chandle, channel_B, enabled_B, coupling_type_B, chBRange, analogue_offset_B)
assert_pico_ok(status["setChB"])

# Sets up single trigger
status["trigger"] = ps.ps3000aSetSimpleTrigger(chandle, trigger_enable, trigger_source, threshold, direction, delay, autoTrigger_ms)
assert_pico_ok(status["trigger"])

# Gets timebase innfomation
# Handle = chandle
# Timebase
# Nosample = maxsamples
# TimeIntervalNanoseconds = ctypes.byref(timeIntervalns)
# MaxSamples = ctypes.byref(returnedMaxSamples)
# Segement index = 0
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
timebase = sampling_rate_to_timebase[sampling_rate]
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int16()
status["GetTimebase"] = ps.ps3000aGetTimebase2(chandle, timebase, maxsamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["GetTimebase"])
print('timeIntervalns', timeIntervalns.value)

# Creates a overlow location for data
overflow = ctypes.c_int16()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxsamples)

# Create buffers ready for assigning pointers for data collection
bufferAMax = (ctypes.c_int16 * maxsamples)()
bufferAMin = (ctypes.c_int16 * maxsamples)()  # used for downsampling which isn't in the scope of this example
bufferBMax = (ctypes.c_int16 * maxsamples)()
bufferBMin = (ctypes.c_int16 * maxsamples)()  # used for downsampling which isn't in the scope of this example

# open serial
ser.open()
T1 = ser.is_open
print('serial open status', T1)

# test serial and get welcome message
num = ser.write(text_buffer_s)
get_text = ser.read(50)
print(get_text)




for i in range(collection_trace_num):
# for i in range(2):

    if i%5000 == 0:
        print(i)
    rand_uint8 = np.random.randint(256, size=input_bytes, dtype=np.uint8)
    rand_uint8_buffer = bytes(rand_uint8)
    # print(rand_uint8)
    # print(rand_uint8_buffer.hex())

    # Starts the block capture
    # Handle = chandle
    # Number of prTriggerSamples
    # Number of postTriggerSamples
    # Timebase = 2 = 4ns (see Programmer's guide for more information on timebases)
    # time indisposed ms = None (This is not needed within the example)
    # Segment index = 0
    # LpRead = None
    # pParameter = None
    status["runblock"] = ps.ps3000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, 1, None, 0, None, None)
    assert_pico_ok(status["runblock"])

    # Setting the data buffer location for data collection from channel A
    # Handle = Chandle
    # source = ps3000A_channel_A = 0
    # Buffer max = ctypes.byref(bufferAMax)
    # Buffer min = ctypes.byref(bufferAMin)
    # Buffer length = maxsamples
    # Segment index = 0
    # Ratio mode = ps3000A_Ratio_Mode_None = 0  # downsampling mode
    source = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_A"]
    ratio_mode = ps.PS3000A_RATIO_MODE["PS3000A_RATIO_MODE_NONE"]
    status["SetDataBuffersA"] = ps.ps3000aSetDataBuffers(chandle, source, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, ratio_mode)
    assert_pico_ok(status["SetDataBuffersA"])

    source = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_B"]
    ratio_mode = ps.PS3000A_RATIO_MODE["PS3000A_RATIO_MODE_NONE"]
    status["SetDataBuffersB"] = ps.ps3000aSetDataBuffers(chandle, source, ctypes.byref(bufferBMax), ctypes.byref(bufferBMin), maxsamples, 0, ratio_mode)
    assert_pico_ok(status["SetDataBuffersB"])


    # send 'p' and input bytes into MCU by serial
    num = ser.write(text_buffer_p)
    num = ser.write(rand_uint8_buffer)
    # MCU while rise a pin after receive the rand_uint8_buffer which could be detected by scope

    get_text = ser.read(output_bytes)
    # print(get_text.hex())


    # Checks data collection to finish the capture
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps3000aIsReady(chandle, ctypes.byref(ready))

    # Handle = chandle
    # start index = 0
    # noOfSamples = ctypes.byref(cmaxSamples)
    # DownSampleRatio = 0
    # DownSampleRatioMode = 0
    # SegmentIndex = 0
    # Overflow = ctypes.byref(overflow)

    status["GetValues"] = ps.ps3000aGetValues(chandle, left_shift, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["GetValues"])
    # print('over_flow', [x for x in overflow])

    # # Finds the max ADC count
    # # Handle = chandle
    # # Value = ctype.byref(maxADC)
    # maxADC = ctypes.c_int16()
    # status["maximumValue"] = ps.ps3000aMaximumValue(chandle, ctypes.byref(maxADC))
    # assert_pico_ok(status["maximumValue"])

    # Converts ADC from channel A to mV
    # adc2mVChAMax = adc2mV(bufferAMax, chARange, maxADC)
    # adc2mVChBMax = adc2mV(bufferBMax, chBRange, maxADC)

    # # Creates the time data
    # time = np.linspace(0, (cmaxSamples.value) * timeIntervalns.value, cmaxSamples.value)

    # Plots the data from channel A onto a graph
    # plt.figure()
    # plt.plot(time, adc2mVChAMax[:])
    # plt.xlabel('Time (ns)')
    # plt.ylabel('Voltage (mV)')
    # plt.show()

    # plt.figure()
    # plt.plot(time, adc2mVChBMax[:])
    # plt.xlabel('Time (ns)')
    # plt.ylabel('Voltage (mV)')
    # plt.show()

    # plt.figure()
    # plt.plot(bufferAMax[:])
    # plt.show()
    #
    # plt.figure()
    # plt.plot(bufferBMax[:])
    # plt.show()

    # np.save('./Trace/trace_{:0>4}.npy'.format(i), np.asarray(adc2mVChAMax, dtype=np.int16))

    trace_handler_chA.write_one_trace(text=rand_uint8_buffer+get_text, samples=np.asarray(bufferAMax, dtype=np.int16))
    trace_handler_chB.write_one_trace(text=rand_uint8_buffer+get_text, samples=np.asarray(bufferBMax, dtype=np.int16))
    # TODO:
    # define a MCU pre-heat loop numbers to heat MCU prior (dont record the beginning XX traces of the collection)

    SS = 1

# closee the serial
ser.close()
T2 = ser.is_open
print('serial open status', T2)

# Stops the scope
# Handle = chandle
status["stop"] = ps.ps3000aStop(chandle)
assert_pico_ok(status["stop"])

# Closes the unit
# Handle = chandle
status["close"] = ps.ps3000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# Displays the staus returns
print(status)

xx = 1
