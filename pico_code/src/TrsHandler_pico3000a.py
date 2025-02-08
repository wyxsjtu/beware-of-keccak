# 定义trs曲线格式操作类


import logging
import numpy as np
from struct import pack, unpack

def progress(count, total, job_name=''):
    """Print the colored progress bar"""

    if count != (total - 1):
        if count % (int(total / 10)) != 0:
            return
    width = 50
    percents = int(round(100.0 * count / float(total), 1))
    end = ''
    status = "Running..."
    if percents == 100:
        end = '\n'
        status = 'Finished.'
    # high contras blue is 96 in 8 basic color system
    bar = '\x1b[{};1m{}\x1b[0m'.format(96, (int(percents/2)) * '#')
    white = (width - int(percents/2)) * ' '
    out_str = '\r[{}{}] \x1b[94;1m{}% \x1b[93;1m{} {}\x1b[0m'.format(bar, white, percents, job_name, status)
    print(out_str, end=end)


class CommonFile(object):
    __filePath = ''
    __byteNum = 0
    __fileHandler = None

    def __init__(self, filePath):
        self.__filePath = filePath

    @property
    def byteNum(self):
        return self.__byteNum

    def openFile(self, mode):
        self.__fileHandler = open(self.__filePath, mode)

    def readbyte(self, num):
        byte_re = self.__fileHandler.read(num)
        self.__byteNum += num
        return byte_re

    def readint(self, num=4):
        byte_re = self.__fileHandler.read(num)
        self.__byteNum += num
        return int.from_bytes(byte_re, 'little')

    def readstr(self, num):
        byte_re = self.__fileHandler.read(num)
        self.__byteNum += num
        return byte_re.decode()

    def readfloat(self, num=4):
        byte_re = self.__fileHandler.read(num)
        self.__byteNum += num
        return float.fromhex(byte_re.hex())

    def seekfile(self, num=0):
        self.__fileHandler.seek(num, 0)
        return True

    def writeByte(self, value):
        self.__fileHandler.write(value)

    def closeFile(self):
        self.__fileHandler.close()


class TrsHandler(object):
    """.trs file handler class"""

    __path = ''
    __traceFile = None
    __traceHeaderFun = None

    __TraceHeader = {}
    __headerLength = 0
    __traceNumber = -1
    __pointCount = -1
    __sampleCoding = -1
    __sampleLength = 0
    __cryptoDataLength = 0
    __titleSpace = 0
    __globalTraceTitle = 'SCAStudio'
    __description = None
    __xAxisOffset = 0
    __xLabel = ''
    __yLabel = ''
    __xAxisScale = 0
    __yAxisScale = 0
    __traceOffsetForDisp = 0
    __logScale = 0

    def __init__(self, path):
        self.__path = path
        self.__traceFile = CommonFile(path)
        self.__traceHeaderFun = {b'\x41': self.__NT, b'\x42': self.__NS, b'\x43': self.__SC, b'\x44': self.__DS,
                                 b'\x45': self.__TS,
                                 b'\x46': self.__GT, b'\x47': self.__DC, b'\x48': self.__XO, b'\x49': self.__XL,
                                 b'\x4A': self.__YL,
                                 b'\x4B': self.__XS, b'\x4C': self.__YS, b'\x4D': self.__TO, b'\x4E': self.__LS,
                                 b'\x5F': self.__TB,
                                 b'\x55': self.__UN, b'\x04': self.__UN, b'\x9A': self.__UN}

    @property
    def filePath(self):
        return self.__path

    @filePath.setter
    def filePath(self, value):
        self.__path = value

    @property
    def traceNumber(self):
        return self.__traceNumber

    @traceNumber.setter
    def traceNumber(self, value):
        self.__traceNumber = value

    @property
    def pointNumber(self):
        return self.__pointCount

    @pointNumber.setter
    def pointNumber(self, value):
        self.__pointCount = value

    @property
    def sampleCoding(self):
        return self.__sampleCoding

    @sampleCoding.setter
    def sampleCoding(self, value):
        self.__sampleCoding = value

    @property
    def sampleLength(self):
        return self.__sampleLength

    @sampleLength.setter
    def sampleLength(self, value):
        self.__sampleLength = value

    @property
    def cryptoDataCount(self):
        return self.__cryptoDataLength

    @cryptoDataCount.setter
    def cryptoDataCount(self, value):
        self.__cryptoDataLength = value

    @property
    def title_space(self):
        return self.__titleSpace

    @title_space.setter
    def title_space(self, value):
        self.__titleSpace = value

    @property
    def header_length(self):
        return self.__headerLength

    def parseFileHeader(self):
        logging.debug('Start Parsing Trace Header')
        self.__traceFile.openFile('rb')
        while True:
            ch = self.__traceFile.readbyte(1)
            logging.debug('Parsing Trace Header : ' + ch.hex())
            try:
                self.__traceHeaderFun[ch]()
            except KeyError:
                print("Key Error: Invalid Trs File Format.")
                break
            except ValueError:
                print("Value Error: Invalid Trs File Format.")
                break
            if ch == b'\x5F':
                logging.debug('Parsing Trace Header Finished')
                break
        self.__traceFile.closeFile()

    def generateTraceHeader(self):
        traceHeader = b'\x41\x04'
        traceHeader += self.__traceNumber.to_bytes(4, 'little')
        traceHeader += b'\x42\x04'
        traceHeader += self.__pointCount.to_bytes(4, 'little')
        traceHeader += b'\x43\x01'
        if self.__sampleCoding == 0:
            traceHeader += self.__sampleLength.to_bytes(1, 'little')
        else:
            traceHeader += (self.__sampleLength | 0x10).to_bytes(1, 'little')

        traceHeader += b'\x44\x02'
        traceHeader += self.__cryptoDataLength.to_bytes(2, 'little')
        traceHeader += b'\x5F\x00'

        self.__traceFile.openFile('wb')
        self.__traceFile.writeByte(traceHeader)
        self.__traceFile.closeFile()

    def generateTrace(self, point, cryptoData=None, title=None):
        traceStr = b''
        self.__traceFile.openFile('ab+')
        if title is not None:
            traceStr += title.encode('utf8')
            # self.__traceFile.writeByte(title.encode('utf8'))
        if cryptoData is not None:
            traceStr += bytes(cryptoData)
            # self.__traceFile.writeByte(bytes(cryptoData))
        if self.__sampleCoding == 0:
            if self.__sampleLength == 1:
                traceStr += bytes(point)
            elif self.__sampleLength == 2:
                for i in point:
                    traceStr += pack('<H', i)
            elif self.__sampleLength == 4:
                for i in point:
                    traceStr += pack('<I', i)
        else:
            # self.__traceFile.writeFile(point)
            traceStr += pack('<' + str(self.__pointCount) + 'f', *point)
            # for i in point:
            #     # traceStr += pack('<f', i)
            #     self.traceFile.writeByte(pack('<f', i))

        self.__traceFile.writeByte(traceStr)
        self.__traceFile.closeFile()

    def __NT(self):
        """0x41, NT, Number of traces"""
        data_length = self.__readHeaderDataLength()
        if data_length != 4:
            logging.error('Wrong trace header : NT')
            raise ValueError('Wrong Trace Header')
        self.__traceNumber = self.__traceFile.readint(data_length)
        logging.debug('Trace Number : ' + str(self.__traceNumber))

    def __NS(self):
        """0x42, NS, Number of samples per trace"""
        data_length = self.__readHeaderDataLength()
        if data_length != 4:
            logging.error('Wrong trace header : NS')
            raise ValueError('Wrong Trace Header')
        self.__pointCount = self.__traceFile.readint(data_length)
        logging.debug('Point Count : ' + str(self.__pointCount))

    def __SC(self):
        """0x43, SC, Sample Coding"""
        data_length = self.__readHeaderDataLength()
        if data_length != 1:
            logging.error('Wrong Trace Header : SC')
            raise ValueError('Wrong Trace Header')
        value_tmp = self.__traceFile.readint(1)
        self.__sampleCoding = (value_tmp & 0x10)
        self.__sampleLength = value_tmp & 0x0F
        logging.debug('Sample Coding : ' + str(self.__sampleCoding))
        logging.debug('Sample Length : ' + str(self.__sampleLength))

    def __DS(self):
        """0x44, DS, Length of cryptographic data included in trace"""
        data_length = self.__readHeaderDataLength()
        if data_length != 2:
            logging.error('Wrong Trace Header : TS')
            raise ValueError('Wrong Trace Header')
        self.__cryptoDataLength = self.__traceFile.readint(data_length)
        logging.debug('Crypto Data Length : ' + str(self.__cryptoDataLength))

    def __TS(self):
        """0x45, TS, Title space reserved per trace"""
        data_length = self.__readHeaderDataLength()
        if data_length != 1:
            logging.error('Wrong Trace Header : TS')
            raise ValueError('Wrong Trace Header')
        self.__titleSpace = self.__traceFile.readint(data_length)
        logging.debug('Title Space : ' + str(self.__titleSpace))

    def __GT(self):
        """0x46, GT, Global trace title"""
        data_length = self.__readHeaderDataLength()
        self.__globalTraceTitle = self.__traceFile.readstr(data_length)
        logging.debug('Global Trace Title : ' + self.__globalTraceTitle)

    def __DC(self):
        """0x47, DC, Description"""
        data_length = self.__readHeaderDataLength()
        self.__description = self.traceFile.__readstr(data_length)
        logging.debug('Description : ' + self.__description)

    def __XO(self):
        """0x48, XO, Offset in X-axis for trace representation"""
        data_length = self.__readHeaderDataLength()
        if data_length != 4:
            logging.error('Wrong Trace Header : XO')
            raise ValueError('Wrong Trace Header : XO')
        self.__xAxisOffset = self.__traceFile.readint()
        logging.debug('X-axis Offset : ' + str(self.__xAxisOffset))

    def __XL(self):
        """0x49, XL, Label of X-axis"""
        data_length = self.__readHeaderDataLength()
        self.__xLabel = self.__traceFile.readstr(data_length)
        logging.debug('X Label : ' + self.__xLabel)

    def __YL(self):
        """0x4A, YL, Label of Y-axis"""
        data_length = self.__readHeaderDataLength()
        self.__yLabel = self.__traceFile.readstr(data_length)
        logging.debug('Y Label : ' + self.__yLabel)

    def __XS(self):
        """0x4B, XS, Scale value for X-axis"""
        data_length = self.__readHeaderDataLength()
        if data_length != 4:
            logging.error('Wrong Trace Header : XS')
            raise ValueError
        self.__xAxisScale = self.__traceFile.readfloat(data_length)
        logging.debug('X-axis Scale : ' + str(self.__xAxisScale))

    def __YS(self):
        """0x4C, YS, Scale value for Y-axis"""
        data_length = self.__readHeaderDataLength()
        if data_length != 4:
            logging.error('Wrong Trace Header : YS')
            raise ValueError
        self.__yAxisScale = self.__traceFile.readfloat(data_length)
        logging.debug('Y-axis Scale : ' + str(self.__xAxisScale))

    def __TO(self):
        """0x4D, TO, Trace offset for displaying trace numbers"""
        data_length = self.__readHeaderDataLength()
        if data_length != 4:
            logging.error('Wrong Trace Header : TO')
            raise ValueError
        self.__traceOffsetForDisp = self.__traceFile.readint(data_length)
        logging.debug('Trace Offet For Displying : ' + str(self.__traceOffsetForDisp))

    def __LS(self):
        """0x4E, LS, Logarithmic scale"""
        data_length = self.__readHeaderDataLength()
        if data_length != 1:
            logging.error('Wrong Trace header : LS')
            raise ValueError
        self.__logScale = self.__traceFile.readint(1)
        logging.debug('Log Scale : ' + str(self.__logScale))

    def __TB(self):
        """0x5F, TB, Trace block marker: an empty TLV that marks the end of the header"""
        self.__readHeaderDataLength()
        self.__headerLength = self.__traceFile.byteNum
        logging.debug('Trace Header Length : ' + str(self.__headerLength))

    def __UN(self):
        """Unknown header"""
        pass

    def __readHeaderDataLength(self):
        data_length = self.__traceFile.readint(1)
        if data_length & 0x80:
            data_length &= 0x7F
            data_length = self.__traceFile.readint(data_length)
        return data_length

    def getTrace(self, index):
        if index < 0 or index > self.__traceNumber - 1:
            logging.error('Wrong Trace Index')
            raise ValueError('Wrong Trace Index')

        samplePoint = ()
        traceTitle = ''
        cryptoData = None
        self.__traceFile.openFile('rb')
        self.__traceFile.seekfile(self.__headerLength + index * (
                    self.__titleSpace + self.__cryptoDataLength + self.__pointCount * self.__sampleLength))
        if self.__titleSpace != 0:
            traceTitle = self.__traceFile.readstr(self.titleSpace).decode('utf-8')
            logging.debug('Trace %d title : %s' % (index, traceTitle))
        if self.__cryptoDataLength != 0:
            cryptoData = list(self.__traceFile.readbyte(self.__cryptoDataLength))
            logging.debug('CryptoData:' + str(cryptoData))
        if self.__pointCount != 0:
            if self.__sampleCoding == 0:
                bstr = self.__traceFile.readbyte(self.__sampleLength * self.__pointCount)
                # print(index)
                if self.__sampleLength == 1:
                    samplePoint = unpack(str(self.__pointCount) + 'b', bstr)
                elif self.sampleLength == 2:
                    samplePoint = unpack('<' + str(self.__pointCount) + 'h', bstr)
                elif self.sampleLength == 4:
                    samplePoint = unpack('<' + str(self.__pointCount) + 'i', bstr)
            else:
                bstr = self.__traceFile.readbyte(self.__sampleLength * self.__pointCount)
                samplePoint = unpack('<' + str(self.__pointCount) + 'f', bstr)

        self.__traceFile.closeFile()

        return [samplePoint, cryptoData, traceTitle]

    def get_trace_npy(self, index_range=None):
        if index_range is None:
            index_range = np.arange(0, self.traceNumber)
        trace_count = index_range.shape[0]
        sample_mat = np.zeros((trace_count, self.pointNumber))

        for index in range(trace_count):
            sample_mat[index, :], _, _ = self.getTrace(index_range[index])
            progress(index, trace_count, 'Extract Sample')

        return sample_mat

    def get_crypto_data_npy(self, index_range=None):
        if index_range is None:
            index_range = np.arange(0, self.traceNumber)
        trace_count = index_range.shape[0]
        crypto_data_mat = np.zeros((trace_count, self.cryptoDataCount), dtype=np.uint8)
        for index in range(trace_count):
            _, crypto_data_mat[index, :], _ = self.getTrace(index_range[index])
            progress(index, trace_count, 'Extract Crypto Data')
        return crypto_data_mat

    def __str__(self):
        return "cryptoDataCount = {0}\nsampleLength = {1}\nsampleCoding = {2}\n" \
               "pointNumber = {3}\ntraceNumber = {4}\ntraceFile = {5}".format(self.__cryptoDataLength,
                                                                              self.__sampleLength, self.__sampleCoding,
                                                                              self.__pointCount, self.__traceNumber,
                                                                              self.__path)
