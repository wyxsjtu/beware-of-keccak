import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import signal
from Trace_processor_pico3000a import TraceProcessor
from TrsHandler_pico3000a import *

def get_trigger_edges(trigger_trace, threshold = 0.3):
    max_scale = np.max(trigger_trace)
    rising_edges = []
    falling_edges = []
    INT_RAISE_CYCLES = 16
    INT_FALL_CYCLES = 12
    MAX_IDX = len(trigger_trace)
    mode = 0 # 0 for rising, 1 for falling
    for i,v in enumerate(trigger_trace):
        if mode == 0 and v > threshold * max_scale:
            mode = 1
            rising_edges.append(max(0, i-INT_RAISE_CYCLES))
            continue
        elif mode == 1 and v < threshold * max_scale:
            mode = 0
            falling_edges.append(min(MAX_IDX, i + INT_FALL_CYCLES))
            continue
    return np.array([rising_edges, falling_edges])


def remove_trigger_segs(data, trigger_edges):
    trace_output = []
    x = 0
    y = 0
    for i,d in enumerate(data):
        if x>= trigger_edges.shape[1]:
            # no edges remain
            trace_output.append(d)
        elif y == 0:
            if i<trigger_edges[y][x]:
                trace_output.append(d)
            else:
                y = 1
        else:
            if i>trigger_edges[y][x]:
                x += 1
                y = 0

    return np.array(trace_output)

def get_pico3203D_Trs(trs_path: str):
    trace_set = TrsHandler(trs_path)
    trace_set.parseFileHeader()
    print(trace_set)

    traces_data = trace_set.get_trace_npy()
    crypto_data_mat = trace_set.get_crypto_data_npy()

    return traces_data, crypto_data_mat

def plot_spectrom(channel_data, fs, low_pass_freq = None):
    # times = data[0, :]
    # channel_data = data[2, :]
    # Set up the parameters for the spectrogram
    # FIXME: 1e6 for us
    # fs = int(1/(times[1]-times[0])) * (1e6)  # Sampling frequency (Hz)
    nperseg = 512  # Number of points in each segment
    noverlap = nperseg // 2  # Overlap between segments
    window = signal.windows.hann(nperseg)  # Window function

    
    if low_pass_freq is not None:
        # low pass filter
        nyquist_freq = fs / 2  # Nyquist frequency
        cutoff_freq = low_pass_freq  # Cutoff frequency (Hz)
        b, a = signal.butter(4, cutoff_freq/nyquist_freq, 'low')  # Generate filter coefficients
        filtered_channel_data = signal.lfilter(b, a, channel_data)

        # Calculate the spectrogram using Scipy
        f, t, Sxx = signal.spectrogram(filtered_channel_data, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)
    else:
        # Calculate the spectrogram using Scipy
        f, t, Sxx = signal.spectrogram(channel_data, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)

    # Plot the spectrogram
    plt.pcolormesh(t, f, 10*np.log10(Sxx))

    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.title('Channel Spectrogram')
    plt.show()

# some helper functions

def get_pico3203D_data_csv(trace_file: str, num = -1):
    '''
    csv 格式：
    时间,通道 A,通道 B
    (us),(V),(mV)

    -50.00399688,0.04167692,-0.83661410
    -50.00199688,0.00000000,0.00000000
    -49.99999688,0.00000000,-2.09307300
    '''
    '''
    Channel A: Triggers
    Channel B: EM trace
    '''
    data = []
    # Open the file for reading
    with open(trace_file, newline='') as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile, delimiter=',')

        # Skip the first two rows (header and units)
        print(next(reader))
        print(next(reader))
        # Skip the 3rd rows (empty row)
        next(reader)

        # Iterate over each row and print the data
        for idx,row in enumerate(reader):
            time = float(row[0])
            channel_a = float(row[1])
            channel_b = float(row[2])
            # print(f"time: {time}, channel A: {channel_a}, channel B: {channel_b}")
            data.append([time, channel_a, channel_b])
            if num!=-1 and idx >= num:
                break

    return np.array(data, dtype=np.float64).T

def get_pico3203D_data_np(trace_file: str, pt_file: str,num = -1):
    traces = np.load(trace_file)
    pts = np.load(pt_file)
    return traces, pts
    # # open the same text file for reading
    # with open('my_file.txt', 'r') as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         line = line.strip()
    #         pts.append(bytes.fromhex(line))
    # return traces, pts



def plot_channel_a(data):
    plt.plot(data[0, :], data[1, :], linewidth=0.5)
    plt.xlabel('Time (us)')
    plt.ylabel('Channel A (V)')
    plt.title('Channel A Data')
    plt.show()

def plot_channel_b(data):
    plt.plot(data[0, :], data[2, :], linewidth=0.5)
    plt.xlabel('Time (us)')
    plt.ylabel('Channel B (mV)')
    plt.title('Channel B Data')
    plt.show()

