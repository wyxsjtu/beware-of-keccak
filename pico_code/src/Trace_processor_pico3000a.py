import numpy as np
import struct
import sys
import os.path

# import matplotlib.pyplot as plt


class TraceProcessor:

    def __init__(self, read_file_name, write_file_name=''):
        self.TotalNumBytes = 0
        self.CurveNum = 0
        self.SampleNum = 0
        self.BytesOfOneSample = 0
        self.BytesOfCipher = 0
        self.isFloat = 0
        self.Sample_Encoding_inspector = 0
        self.BytesOfTilePerTrace = 0
        self.GlobalTitle = ''
        self.Description = ''
        self.Xoffset = 0
        self.XLabel = ''
        self.YLabel = ''
        self.XScale = 1
        self.YScale = 1
        self.DisplayTrace = 0
        self.LogScal = 0
        self.head_read_allowed = 1
        self.head_write_allowed = 1

        self.isFloat_for_independent_write = None
        self.BytesOfOneSample_for_independent_write = None

        if read_file_name:
            self.read_fid = open(read_file_name, 'rb')
            print('read_fid created')
        if write_file_name:
            # if os.path.exists(write_file_name):
            #     try:
            #         sys.exit(1)
            #     except SystemExit:
            #         print('file' + write_file_name + ' exists!')
            #     finally:
            #         print('trace processor terminated while init write_fid')
            # else:
            self.write_fid = open(write_file_name, 'wb')
            print('write_fid created')

    def close_read_fid(self):
        if self.read_fid:
            self.read_fid.close()

    def close_write_fid(self):
        if self.write_fid:
            self.write_fid.close()

    def read_trace_head(self):
        if self.head_read_allowed:
            print('reading head')

            # --------------------------
            temp_result, = struct.unpack('B', self.read_fid.read(1))
            self.TotalNumBytes = self.TotalNumBytes + 1

            while temp_result != int('5f', 16):

                if temp_result == int('41', 16):  # Number of traces
                    _, = struct.unpack('B', self.read_fid.read(1))
                    print('one')
                    self.CurveNum, = struct.unpack('I', self.read_fid.read(4))
                    self.TotalNumBytes += 5

                elif temp_result == int('42', 16):  # Number of samples per trace
                    print('two')
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.SampleNum, = struct.unpack('I', self.read_fid.read(4))
                    self.TotalNumBytes += 5

                elif temp_result == int('43', 16):  # Sample Coding
                    print('three')
                    _, = struct.unpack('B', self.read_fid.read(1))
                    temp_result, = struct.unpack('B', self.read_fid.read(1))
                    # how many byte in a floating code
                    self.BytesOfOneSample = temp_result & 15
                    # check fourth bit , 1 for float 0 for int
                    self.isFloat = (temp_result & 16) > 0
                    self.Sample_Encoding_inspector = temp_result
                    self.TotalNumBytes += 2

                elif temp_result == int('44', 16):  # Length of cryptographic data included in trace
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.BytesOfCipher, = struct.unpack('H', self.read_fid.read(2))
                    self.TotalNumBytes += 3

                elif temp_result == int('45', 16):  # Title space reserved per trace
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.BytesOfTilePerTrace, = struct.unpack('B', self.read_fid.read(1))
                    self.TotalNumBytes += 2

                elif temp_result == int('46', 16):  # Global trace title
                    temp_result, = struct.unpack('B', self.read_fid.read(1))
                    self.TotalNumBytes += 1
                    for i in range(temp_result):
                        temp_char, = struct.unpack('c', self.read_fid.read(1))
                        self.GlobalTitle += temp_char.decode('ascii')
                    self.TotalNumBytes += temp_result

                elif temp_result == int('47', 16):  # Description
                    temp_result, = struct.unpack('B', self.read_fid.read(1))
                    self.TotalNumBytes += 1
                    self.Description = struct.unpack('c', self.read_fid.read(temp_result))
                    self.TotalNumBytes += temp_result

                elif temp_result == int('48', 16):  # Offset in X-axis for trace representation
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.Xoffset, = struct.unpack('I', self.read_fid.read(4))
                    self.TotalNumBytes += 5

                elif temp_result == int('49', 16):  # Label of X-axis
                    temp_result, = struct.unpack('B', self.read_fid.read(1))
                    self.TotalNumBytes += 1
                    for i in range(temp_result):
                        temp_char, = struct.unpack('c', self.read_fid.read(1))
                        self.XLabel += temp_char.decode('ascii')
                    self.TotalNumBytes += temp_result

                elif temp_result == int('4A', 16):  # Label of Y-axis
                    temp_result, = struct.unpack('B', self.read_fid.read(1))
                    self.TotalNumBytes += 1
                    for i in range(temp_result):
                        temp_char, = struct.unpack('c', self.read_fid.read(1))
                        self.YLabel += temp_char.decode('ascii')
                    self.TotalNumBytes += temp_result

                elif temp_result == int('4B', 16):  # Scale value for X-axis
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.XScale, = struct.unpack('f', self.read_fid.read(4))
                    self.TotalNumBytes += 5

                elif temp_result == int('4C', 16):  # Scale value for Y-axis
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.YScale, = struct.unpack('f', self.read_fid.read(4))
                    self.TotalNumBytes += 5

                elif temp_result == int('4D', 16):  # Trace offset for displaying trace numbers
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.DisplayTrace, = struct.unpack('I', self.read_fid.read(4))
                    self.TotalNumBytes += 5

                elif temp_result == int('4E', 16):  # Logarithmic scale
                    _, = struct.unpack('B', self.read_fid.read(1))
                    self.LogScal = struct.unpack('B', self.read_fid.read(1))
                    self.TotalNumBytes += 2

                else:
                    break

                # B for unsigned char
                temp_result, = struct.unpack("B", self.read_fid.read(1))
                # temp_result_dec = hex(temp_result)
                self.TotalNumBytes += 1

            # read '00' of '5f00'
            temp_result, = struct.unpack("B", self.read_fid.read(1))
            # temp_result_dec = hex(temp_result)
            self.TotalNumBytes += 1
            self.head_read_allowed = 0
            print('read head finished')
        else:
            print('head has been read')

    def read_one_trace(self):

        format_text = str(self.BytesOfCipher) + "B"
        temp_tuple = struct.unpack(format_text, self.read_fid.read(self.BytesOfCipher))
        text = np.asarray(temp_tuple)

        if self.isFloat:
            if self.BytesOfOneSample == 4:
                # f for float32
                format_sample = str(self.SampleNum) + "f"
                temp_tuple = struct.unpack(format_sample, self.read_fid.read(self.BytesOfOneSample * self.SampleNum))
                curve_samples = np.asarray(temp_tuple)
                # plt.plot(range(0, 30), data[i, :])
                # t = 1
            elif self.BytesOfOneSample == 2:
                # e for float16
                format_sample = str(self.SampleNum) + "e"
                temp_tuple = struct.unpack(format_sample, self.read_fid.read(self.BytesOfOneSample * self.SampleNum))
                curve_samples = np.asarray(temp_tuple)
            else:
                try:
                    sys.exit(1)
                except SystemExit:
                    print('illegal bytes num in float type!')
                finally:
                    print('process terminated in read_one_trace func')
        else:
            if self.BytesOfOneSample == 4:
                # i for integer (signed int32)
                format_sample = str(self.SampleNum) + "i"
                temp_tuple = struct.unpack(format_sample, self.read_fid.read(self.BytesOfOneSample * self.SampleNum))
                curve_samples = np.asarray(temp_tuple)

            elif self.BytesOfOneSample == 2:
                # h for short (signed int16)
                format_sample = str(self.SampleNum) + "h"
                temp_tuple = struct.unpack(format_sample, self.read_fid.read(self.BytesOfOneSample * self.SampleNum))
                curve_samples = np.asarray(temp_tuple)

            elif self.BytesOfOneSample == 1:
                # b for signed int8
                format_sample = str(self.SampleNum) + "b"
                temp_tuple = struct.unpack(format_sample, self.read_fid.read(self.BytesOfOneSample * self.SampleNum))
                curve_samples = np.asarray(temp_tuple)

            else:
                try:
                    sys.exit(1)
                except SystemExit:
                    print('illegal bytes num in integer type!')
                finally:
                    print('process terminated in read_one_trace func')

        return [text, curve_samples]

    def write_trace_head(self):
        if self.head_write_allowed:
            print('writing head')

            # --------------------------

            # # reset the BytesOfOneSample and isFloat from Encode format when write trace
            # if self.isFloat_for_independent_write is not None:
            #     if (self.isFloat_for_independent_write == 0 or self.isFloat_for_independent_write == 1) \
            #             and self.BytesOfOneSample_for_independent_write <= 8:
            #         self.isFloat = self.isFloat_for_independent_write
            #         self.BytesOfOneSample = self.BytesOfOneSample_for_independent_write
            #         self.Sample_Encoding_inspector = self.isFloat_for_independent_write * 16 \
            #                                          + self.BytesOfOneSample_for_independent_write

            #     else:
            #         try:
            #             sys.exit(1)
            #         except SystemExit:
            #             print('illegal setting! isFloat must be 0 or 1, BytesOfOneSample must less equals than 8')
            #         finally:
            #             print('process terminated in write_trace_head func')


            # else:
            #     # how many byte in a floating code
            #     self.BytesOfOneSample = self.Sample_Encoding_inspector & 15
            #     # check fourth bit , 1 for float 0 for int
            #     self.isFloat = (self.Sample_Encoding_inspector & 16) > 0

            # 0x41 CurveNum
            self.write_fid.write(struct.pack('B', 0x41))
            self.write_fid.write(struct.pack('B', 4))
            self.write_fid.write(struct.pack('i', self.CurveNum))

            #0x42 SampleNum
            self.write_fid.write(struct.pack('B', 0x42))
            self.write_fid.write(struct.pack('B', 4))
            self.write_fid.write(struct.pack('I', self.SampleNum))

            # 0x43 Sample Encoding format  # 0x14: float32  0x02 short  0x01: int8
            self.write_fid.write(struct.pack('B', 0x43))
            self.write_fid.write(struct.pack('B', 1))
            self.write_fid.write(struct.pack('B', self.Sample_Encoding_inspector))

            # 0x44 Length of text
            self.write_fid.write(struct.pack('B', 0x44))
            self.write_fid.write(struct.pack('B', 2))
            self.write_fid.write(struct.pack('H', self.BytesOfCipher))

            # 0x5f 0x00
            self.write_fid.write(struct.pack('B', 0x5F))
            self.write_fid.write(struct.pack('B', 0x00))

            self.head_write_allowed = 0
            print('write head finished')
        else:
            print('head has been writen')

    def write_one_trace(self, text, samples):

        try:
            # write text
            format_text = str(self.BytesOfCipher) + "B"
            self.write_fid.write(struct.pack(format_text, *text))

            # FIXME: for pico3000a only
            format_sample = str(self.SampleNum) + "h"

            # write samples
            if self.isFloat:
                if self.BytesOfOneSample == 4:
                    # f for float32
                    format_sample = str(self.SampleNum) + "f"

                elif self.BytesOfOneSample == 2:
                    # e for float16
                    format_sample = str(self.SampleNum) + "e"

                else:
                    try:
                        sys.exit(1)
                    except SystemExit:
                        print('illegal bytes num in float type!')
                    finally:
                        print('process terminated in write_one_trace func')
            else:
                if self.BytesOfOneSample == 4:
                    # i for integer (signed int32)
                    format_sample = str(self.SampleNum) + "i"

                elif self.BytesOfOneSample == 2:
                    # h for short (signed int16)
                    format_sample = str(self.SampleNum) + "h"

                elif self.BytesOfOneSample == 1:
                    # b for signed int8
                    format_sample = str(self.SampleNum) + "b"

                else:
                    print(f"wtf: {self.BytesOfOneSample}")
                    try:
                        sys.exit(1)
                    except SystemExit:
                        print('illegal bytes num in integer type!')
                    finally:
                        print('process terminated in write_one_trace func')
            self.write_fid.write(struct.pack(format_sample, *samples))

        except struct.error as err:
            print(str(err))

