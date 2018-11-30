#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.signal as signal
from scipy.fftpack import fft,ifft
from collections import defaultdict
from fastdtw import fastdtw 
from scipy.spatial.distance import euclidean
import struct



plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

'''
返回cwf或者crw文件的波形数组
'''

'''
局放波形数据（.pwf）
头文件说明
        PDWaveform_HeadFile
        {
            //total 28bytes
            double PD_Test_Voltage;//测试放电电压 8bytes 
            double WaveSpeed;//波速 8bytes 
            int PD_pCRange;//局放范围pC为单位 4bytes 
            int PD_Max_pC;//PD最大pC值 4bytes 
            int WaveformLength;//波形文件长度 4bytes 
        }
'''
def getDataFromWaveFile(datafile):
    with open(datafile, 'rb') as f:
        ss = f.read(28) 
        varss = struct.unpack('<ddIII',ss)
        PD_pCRange = varss[2]
        WaveformLength = varss[4]
        ss = f.read() 
        hexbytes = struct.unpack(str(WaveformLength)+"b",ss)  
        print('hexbytes:' , hexbytes[1:100]) 
        list1= np.array(hexbytes) / 128 * PD_pCRange 
        return (list1,varss)

def generateWaveByPwf(datafile, cc):
    wavedata,_ = getDataFromWaveFile(datafile)    
    list1 =  wavedata
    #list1 = butter_lowpass_filter(list1 ,5e6)
    list1 = list1.tolist()
    xx=range(len(list1) )    
    mIndex = list1.index(max(list1))
    plt.plot(xx,list1 , linewidth=0.5,c=cc , linestyle="-", label=datafile)# 折线 1 x 2 y 3 color

    plt.scatter([mIndex, ], [list1[mIndex], ], s=50, color='g') #在这点加个蓝色的原点 原点大小50
    return list1,mIndex

def getFastLine(segList, targetList):
    listret=[]
    len1 = len(segList) 
    len2 = len(targetList)
    xx1 = range(len2-len1)
    for ii in xx1:
        dist = euclidean(segList , targetList[ii:ii+len1]) 
        listret.append(dist)
    xindex = listret.index(min(listret))
    return listret ,xindex

def plot(list1 , cc='b'):
    xx1 = range(len(list1))
    plt.plot(xx1,list1 , linewidth=0.5,c=cc)# 折线 1 x 2 y 3 color

def plot1(list1 , cc='b'):
    xx1 = range(len(list1))
    plt.plot(xx1,list1 , linewidth=0.5,c=cc)# 折线 1 x 2 y 3 color
    xindex = list1.index(min(list1))
    plt.scatter([xindex,],[list1[xindex],], 50, color ='blue')


def main():  


    plt.figure(1)                # 第一张图
    list1,maxIndex1 = generateWaveByPwf("L1_12.3kV_1nC_401m_20181122160048.pwf"  , 'b')
    list2,maxIndex2 = generateWaveByPwf("L1_12.3kV_1nC_401m_20181122160208F.pwf" , 'r')
    plt.legend(loc='upper right')
    print(maxIndex1 , ':' , maxIndex2)
    lrnum = 50   # 第一个最值的-20，20个点
    offset = 500 #2×offset个单元进行fastdtw比较
    list_seg = list1[maxIndex1-offset :maxIndex1+offset ]
    list_target = list2[maxIndex2-offset-lrnum:maxIndex2+offset+lrnum]


    listret , iindex = getFastLine(list_seg , list_target) 
    print( '窗口偏移量:' , iindex)
    
    diffx = maxIndex2 - maxIndex1

    list2 = list2[(diffx + lrnum  - iindex):]
    print( '最终偏移量:' , diffx + lrnum  - iindex)
    plt.figure(2)                # 第二张图
    plt.subplot(211)
    plt.title(U'匹配图')
    plot(list1 , 'b') 
    plot(list2 , 'r')

    plt.subplot(212)
    plt.title(U"滑动窗欧式距离曲线")
    plot1(listret , cc='b')

    plt.grid(axis='y')
    plt.show()
    print('done.')

if __name__ == '__main__':
    main()

