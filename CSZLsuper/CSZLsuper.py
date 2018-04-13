# -*- coding: utf-8 -*-

#import win32api
import tushare as ts
import threading
#from tkinter import *
#import hashlib
import pandas as pd
from pandas import DataFrame

import random
import time
import numpy as np

import CSZLsuperGET
import CSZLsuperTrain

#====定义线程引用====
def Z_CSZL_superGETAllroutine():
    CSZLsuperGET.CSZL_superGETAllroutine()

def Z_CSZL_superINFOupdate():
    CSZLsuperGET.CSZL_superINFOupdate()

def Z_CSZL_superAnalysePARTroutine():
    CSZLsuperGET.CSZL_superAnalysePARTroutine()

#====================

#====初始化线程池====
CSZL_threads = []
t_GETAllroutine = threading.Thread(target=Z_CSZL_superGETAllroutine, args=())
CSZL_threads.append(t_GETAllroutine)
t_INFOroutine = threading.Thread(target=Z_CSZL_superINFOupdate, args=())
CSZL_threads.append(t_INFOroutine)
t_AnalysePARTroutine = threading.Thread(target=Z_CSZL_superAnalysePARTroutine, args=())
CSZL_threads.append(t_AnalysePARTroutine)
#====================



if __name__ == '__main__':

    #重要数据分析
    #CSZLsuperGET.CSZL_SecretDataAnalyse()

    testSecretData_B=np.zeros((5000*20+1,30),dtype=float)

    buff_dr_result = ts.get_realtime_quotes(["600000","300328"])
    for xxx in buff_dr_result:
        print(xxx)

    timeArray = time.strptime(buff_dr_result['date'][1], "%Y-%m-%d")
    h,m,s = buff_dr_result['time'][0].strip().split(":")

    testSecretData_B[345,2]=int(timeArray[0])*10000+int(timeArray[1])*100+int(timeArray[2])


    testSecretData_B[345,3]=int(h)*10000+int(m)*100+int(s)
    testSecretData_B[345,4]=int(buff_dr_result['code'][1])
    testSecretData_B[345,5]=buff_dr_result['pre_close'][1]


    #总列表初始化
    g_all_listin=CSZLsuperGET.CSZL_superinit()

    getinput=int(input("是否为测试模式:1表示是 其他表示不是\n"))
    if(getinput==1):
        CSZLsuperTrain.CSZL_TrainMainNEW(g_all_listin)

    #历史数据分析(初始化)
    CSZLsuperGET.CSZL_HistoryDataAnalysis()



    #初始化线程定义
    for t in CSZL_threads:
        t.setDaemon(True)
        t.start()


    
    while True:
        print ("Main Run at : %s \n" % ( time.ctime(time.time())))
        getinput=int(input("是否退出:1表示退出 2表示读取信息\n"))
        if(getinput==1):
            #先让别的线程都退出
            CSZLsuperGET.Z_EXIT()
            time.sleep(10)

            #再保存信息
            CSZLsuperGET.CSZL_CurDataOutput()

            break

        sleeptime=random.randint(50,99)
        time.sleep(sleeptime/10)
    

    a=1
    


