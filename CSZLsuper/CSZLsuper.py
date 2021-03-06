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



G_mode={'TestModeFlag':False,               #测试模式
        'InitListUpdateModeFlag':False,     #初始列表初始化
        'K_Data_UpdateModeFlag':True,      #近20日K线数据初始化
        'RoutineTestFlag':False             #直接运行测试
        }  

'''
def ModeChoice():
    global G_mode

    G_mode['TestModeFlag']=False
    G_mode['InitListUpdateModeFlag']=False
    G_mode['K_Data_UpdateModeFlag']=False

    getinput=int(input("是否为测试模式:1表示是 其他表示不是\n"))
    if(getinput==1):    
        G_mode['TestModeFlag']=True

    getinput=int(input("是否初始化列表数据:1表示初始化 2表示不初始化\n"))
    if(getinput==1):    
        G_mode['InitListUpdateModeFlag']=True

    getinput=int(input("是否初始化历史总数据:1表示初始化 2表示不初始化\n"))

    if(getinput==1):    
        G_mode['K_Data_UpdateModeFlag']=True
'''


if __name__ == '__main__':

    #重要数据分析
    #CSZLsuperGET.CSZL_SecretDataAnalyse()

    '''
    getinput=int(input("是否启用默认设置\n"))
    if(getinput!=1):
        ModeChoice()
    '''

    #总列表初始化
    g_all_listin=CSZLsuperGET.CSZL_superinit()

    if(G_mode['TestModeFlag']):
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
    

