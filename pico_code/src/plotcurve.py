import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.signal import butter, filtfilt

def low_pass_filter(data, cutoff_freq, sample_rate, order=4):
    """
    使用Butterworth低通滤波器对数据进行滤波
    
    参数:
    data (numpy.ndarray): 需要滤波的数据数组
    cutoff_freq (float): 滤波器的截止频率(Hz)
    sample_rate (float): 数据的采样频率(Hz)
    order (int): 滤波器的阶数,默认为4
    
    返回:
    numpy.ndarray: 滤波后的数据
    """
    nyquist_freq = 0.5 * sample_rate
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


time=[]
voltage=[]
with open('E:/waveforms/20240625-0001/20240625-0001_12.csv', 'r') as file:
    reader = csv.reader(file)
    cntr=0
    for row in reader:
        #print(row)
        cntr+=1
        if cntr<4:
            continue
        if float(row[0])>2:
            break
        time.append(float(row[0]))  # 第一列是时间
        voltage.append(float(row[1]))  # 第二列是电压

nptime=np.array(time)
npvol=np.array(voltage)

# 滤波参数
cutoff_freq = 1_000_000  # Hz
sample_rate = 50_000_000  # Hz

# 对数据进行滤波
filtered_data = low_pass_filter(npvol, cutoff_freq, sample_rate)



# 创建图表
plt.figure(figsize=(12, 6))
plt.plot(time, filtered_data,markersize=0.1,linewidth=0.1,color=(18/255,77/255,159/255))
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Voltage over Time')
plt.grid(True)
plt.show()