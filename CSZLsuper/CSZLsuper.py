# -*- coding: utf-8 -*-

#import win32api
import tushare as ts
import threading
from tkinter import *
#import hashlib
import pandas as pd
from pandas import DataFrame

import random
import time

import CSZLsuperGET


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


    #初始化变量等
    CSZLsuperGET.CSZL_superinit()

    #初始化10日数据

    #初始化选项
    getinput=int(input("是否初始化列表数据:1表示初始化 2表示不初始化\n"))
    if(getinput==1):
        CSZLsuperGET.CSZL_DataCreate()

    getinput=int(input("是否初始化历史总数据:1表示初始化 2表示不初始化\n"))
    if(getinput==1):
        CSZLsuperGET.CSZL_HistoryDataSave()


    #读取10日数据
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
            CSZLsuperGET.EXIT()
            time.sleep(10)

            #再保存信息
            CSZLsuperGET.CSZL_DataOutput()

            break

        sleeptime=random.randint(50,99)
        time.sleep(sleeptime/10)
    

    a=1
    


