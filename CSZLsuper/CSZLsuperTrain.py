#coding=utf-8

import CSZLsuper
import CSZLsuperGET
import threading
import datetime
import time
import random

import tushare as ts
import pandas as pd

#import sys
import math
import os
import numpy as np
import functools
import math

#正则表达式
import re



HistoryLoaded=[]
DataRecord=[]  
#全局初始化数据
g_all_result=[]

#长期属性 一般一次训练只初始化一次
LongProp=[]
#实时短期属性 每个循环可能都需要改变
ShortProp=[]

def CSZL_TrainMainNEW(g_all_resultin):
    #global DataRecord
    global g_all_result
    global HistoryLoaded
    global LongProp

    #初始化g_all_result
    g_all_result=g_all_resultin

    #初始化训练周期
    TrainDate=CSZL_TrainInitNEW()

    #初始化长期属性
    CSZL_LongProp()

    #初始化短期属性
    CSZL_ShortProp()

    start_time = time.time()
    TrainInput_test(ShortProp)
    print('函数执行完毕,用时:%sms' % ((time.time()-start_time)*1000))

    zzzz=1

def CSZL_LongProp():
    global LongProp

    #todo改成可读取式的
    #code mkt codemean pe pb stflag stop reserve3
    LongProp=np.zeros((4000,8),dtype=float)

    x=len(g_all_result)
    y=HistoryLoaded.shape[1]    #7
    z=HistoryLoaded.shape[2]    #50
    
    #todo自动调整平衡位置
    counter2=[0,0,0,0]

    for i in range(x):    
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=HistoryLoaded[(i,0,0)]
        #保证相同项
        if(zzz==zzz2):
            
            #code(index)
            LongProp[i,0]=HistoryLoaded[i,0,0]

            #mkt
            #LongProp[(i,1)]=g_all_result[i]['s_mktcap']
            if g_all_result[i]['s_mktcap']>0 and g_all_result[i]['s_mktcap']<400000:
                counter2[0]+=1
                LongProp[(i,1)]=1
            elif g_all_result[i]['s_mktcap']>=400000 and g_all_result[i]['s_mktcap']<800000:
                counter2[1]+=1
                LongProp[(i,1)]=2
            elif g_all_result[i]['s_mktcap']>=800000 and g_all_result[i]['s_mktcap']<2500000:
                counter2[2]+=1
                LongProp[(i,1)]=3
            elif g_all_result[i]['s_mktcap']>=2500000:
                counter2[3]+=1
                LongProp[(i,1)]=4

            #codemean
            if HistoryLoaded[(i,0,0)]>0 and HistoryLoaded[(i,0,0)]<300000:
                LongProp[(i,2)]=1
            elif HistoryLoaded[(i,0,0)]>=300000 and HistoryLoaded[(i,0,0)]<600000:
                LongProp[(i,2)]=2
            elif HistoryLoaded[(i,0,0)]>=600000 and HistoryLoaded[(i,0,0)]<603000:
                LongProp[(i,2)]=3
            elif HistoryLoaded[(i,0,0)]>=603000 and HistoryLoaded[(i,0,0)]<999999:
                LongProp[(i,2)]=4
            #pe

            #LongProp[(i,5)]=g_all_result[i]['s_per']
            if g_all_result[i]['s_per']<0 or g_all_result[i]['s_per']>=100:
                #counter2[0]+=1
                LongProp[(i,3)]=1
            elif g_all_result[i]['s_per']>=0 and g_all_result[i]['s_per']<25:
                #counter2[1]+=1
                LongProp[(i,3)]=4
            elif g_all_result[i]['s_per']>=25 and g_all_result[i]['s_per']<45:
                #counter2[2]+=1
                LongProp[(i,3)]=3
            elif g_all_result[i]['s_per']>45 and g_all_result[i]['s_per']<100:
                #counter2[3]+=1
                LongProp[(i,3)]=2
            #pb
            #LongProp[(i,6)]=g_all_result[i]['s_pb']
            if g_all_result[i]['s_pb']<0 or g_all_result[i]['s_pb']>=6:
                #counter2[0]+=1
                LongProp[(i,4)]=1
            elif g_all_result[i]['s_pb']>=0 and g_all_result[i]['s_pb']<2:
                #counter2[1]+=1
                LongProp[(i,4)]=4
            elif g_all_result[i]['s_pb']>=2 and g_all_result[i]['s_pb']<3.5:
                #counter2[2]+=1
                LongProp[(i,4)]=3
            elif g_all_result[i]['s_pb']>3.5 and g_all_result[i]['s_pb']<6:
                #counter2[3]+=1
                LongProp[(i,4)]=2

            #st

            if g_all_result[i]['s_stflag']>0:
                #counter2[0]+=1
                LongProp[(i,5)]=1
            else:
                #counter2[3]+=1
                LongProp[(i,5)]=2    
   
            #stopperiod
            if HistoryLoaded[(i,1,(z-100))]==0:
                LongProp[(i,6)]=3
            elif HistoryLoaded[(i,1,(z-1))]==0:
                LongProp[(i,6)]=2
            else:
                LongProp[(i,6)]=1  

        else:
            wrongconter+=1
            continue

def CSZL_ShortProp():
    global LongProp
    global ShortProp
    #code availableflag tempresult strategy1 strategy2 strategy3 reserve1 reserve2

    ShortProp=np.zeros((4000,8),dtype=float)

    x=len(g_all_result)         #4000
    y=HistoryLoaded.shape[1]    #7
    z=HistoryLoaded.shape[2]    #50
    
    target_dateA=20170629
    target_dateB=20180118

    Available=0

    for i in range(x):    
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=HistoryLoaded[(i,0,0)]
        #保证相同项
        if(zzz==zzz2):
            #code(index)
            ShortProp[i,0]=HistoryLoaded[i,0,0]

 
            #得到最后的结果
            Close=0
            for ii in range(z):

                if HistoryLoaded[(i,6,ii)]==target_dateA:
                    
                    if(HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,1,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,2,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,4,ii)]):
                        zzz=HistoryLoaded[(i,0,0)]
                        ShortProp[(i,1)]=-1
                        break
                    
                    #ShortProp[(i,9)]=HistoryLoaded[(i,3,ii)]
                    ShortProp[(i,6)]=HistoryLoaded[(i,3,ii)]
                    Close=HistoryLoaded[(i,3,ii)]
                elif HistoryLoaded[(i,6,ii)]==target_dateB and Close!=0:

                    if(HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,1,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,2,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,4,ii)]):
                        zzz=HistoryLoaded[(i,0,0)]
                        ShortProp[(i,1)]=-2
                        break

                    ShortProp[(i,2)]=((HistoryLoaded[(i,3,ii)]-Close)/Close)*100
                    ShortProp[(i,7)]=HistoryLoaded[(i,3,ii)]        
                    ShortProp[(i,1)]=1
                    Available+=1
                    break

            dsfsf=2


        else:
            wrongconter+=1
            continue


def CSZL_TrainValueCalNEW(InputData):
    x=InputData.shape[0]
    y=InputData.shape[1]

    cur_strategy=0
    finalzzz=0
    datacal=0
    cur_strategycal=0

    #TrainInput_test(InputData)


    for i in range(x):
        if InputData[(i,3)]>0 :

            if InputData[(i,1)]==zmkt and InputData[(i,4)]==zbb:
                #print(InputData[(i,0)])
                cur_strategy+=InputData[(i,7)]
                cur_strategycal+=1
            #kkk=InputData[(i,9)]
            finalzzz+=InputData[(i,7)]
            datacal+=1
    #print("/n")
    if(cur_strategycal==0):
        return -99

    final_cur_strategy=cur_strategy/cur_strategycal
    finalzzzz=finalzzz/datacal

    test=final_cur_strategy-finalzzzz
    return (test)

def CSZL_TrainInitNEW():
    global HistoryLoaded
    global DataRecord

    TrainDate=[]

    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'History_data.npy'
    HistoryLoaded=np.load(txtFile1)


    startdate=20171226
    enddate=20180126

    z=HistoryLoaded.shape[2]    #50

    for ii in  range(z):
        #这里暂时拿特定一个数据来作为日期检测的种子,之后会寻找更加合适的方法1327
        if(HistoryLoaded[(1,6,ii)]>=startdate and HistoryLoaded[(1,6,ii)]<=enddate ):
            TrainDate.append(HistoryLoaded[(1,6,ii)])

    return TrainDate

def CSZL_TrainMain(g_all_resultin):
    global DataRecord
    global g_all_result

    g_all_result=g_all_resultin

    #z222=ts.get_k_data('600004')

    cwd = os.getcwd()
    '''
    zzzz=ts.get_report_data(2017,2)

    txtFileB = cwd + '\\data\\'+'Report_data.npy'
    np.save(txtFileB, zzzz)

    print(zzzz)
    '''

    #print(z222)
    #print(z222.close.data[0])

    TrainDate=CSZL_TrainInit()

    if True:

        first=TrainDate[0]
        xx=0
        for singledate in TrainDate:
            if(first==singledate):
                lastdate=first
                continue
        
            #print(singledate)
            data=CSZL_TrainInputInit(lastdate,singledate)
        
            for AA in range(1,5):
                for BB in range(1,5):
                    DataRecord[xx,AA-1,BB-1,0]=singledate
                    DataRecord[xx,AA-1,BB-1,1]=CSZL_TrainValueCal(data,AA,BB)


            #上次日期
            lastdate=singledate
            xx+=1

        
        now=datetime.datetime.now()
        now=now.strftime('%Y%m%d')

        txtFileA = cwd + '\\data\\'+'Train_data.npy'
        np.save(txtFileA, DataRecord)


    if False:
        test=1




    txtFile1 = cwd + '\\data\\'+'Train_data.npy'
    DataRecord=np.load(txtFile1)


    x=DataRecord.shape[0]    #50
    y=DataRecord.shape[1]    #4
    z=DataRecord.shape[2]    #4
    p=DataRecord.shape[3]    #2

    ztestarray=np.zeros((4,4),dtype=float)

    #ztestarray=ztestarray+100000

    for i in range(x):
        for ii in range(y):
            for iii in range(z):
                ztestarray[ii,iii]+=DataRecord[i,ii,iii,1]
                #ztestarray[ii,iii]=ztestarray[ii,iii]*(100+DataRecord[i,ii,iii,1])/100
                #print("%10d %2d %2d %8.2f " % (DataRecord[i,ii,iii,0], ii+1, iii+1, DataRecord[i,ii,iii,1]),end="")
            #print("\n")  

    for i in range(4):
        for ii in range(4):
            print("%8.2f " % (ztestarray[i,ii]),end="")
        print("\n") 

    print(ztestarray)
    zzzzzzz=1


def CSZL_TrainInit():
    global HistoryLoaded
    global DataRecord

    TrainDate=[]

    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'History_data.npy'
    HistoryLoaded=np.load(txtFile1)

    #HistoryLoaded=HistoryLoaded.tail(50)
    startdate=20171226
    enddate=20180126

    z=HistoryLoaded.shape[2]    #50

    for ii in  range(z):
        #这里暂时拿600004来作为日期检测的种子，因为该股三年内没有停牌过，之后会寻找更加合适的方法1327
        if(HistoryLoaded[(1,6,ii)]>=startdate and HistoryLoaded[(1,6,ii)]<=enddate ):
            TrainDate.append(HistoryLoaded[(1,6,ii)])

    #日期 数值1 数值2 结果
    DataRecord=np.zeros((z,4,4,2),dtype=float)
    return TrainDate


def CSZL_TrainInputInit(target_dateA,target_dateB):
    global g_all_result
    global HistoryLoaded

    # 
    #code mkt time availableflag codemean pe pb tempresult bid1 sell
    TrainInput=np.zeros((4000,10),dtype=float)
    

    #从历史数据中读取数据
    '''
    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'History_data.npy'
    HistoryLoaded=np.load(txtFile1)
    '''

    #x=HistoryLoaded.shape[0]    #4000

    x=len(g_all_result)
    y=HistoryLoaded.shape[1]    #7
    z=HistoryLoaded.shape[2]    #50


    Available=0     #有效数据
    wrongconter=0
    counter2=[0,0,0,0]


    for i in range(x):    
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=HistoryLoaded[(i,0,0)]
        #保证相同项
        if(zzz==zzz2):
            
            #code(index)
            TrainInput[(i,0)]=HistoryLoaded[(i,0,0)]

            #mkt
            #TrainInput[(i,1)]=g_all_result[i]['s_mktcap']
            if g_all_result[i]['s_mktcap']>0 and g_all_result[i]['s_mktcap']<300000:
                #counter2[0]+=1
                TrainInput[(i,1)]=1
            elif g_all_result[i]['s_mktcap']>=300000 and g_all_result[i]['s_mktcap']<1000000:
                #counter2[1]+=1
                TrainInput[(i,1)]=2
            elif g_all_result[i]['s_mktcap']>=1000000 and g_all_result[i]['s_mktcap']<3000000:
                #counter2[2]+=1
                TrainInput[(i,1)]=3
            elif g_all_result[i]['s_mktcap']>=3000000:
                #counter2[3]+=1
                TrainInput[(i,1)]=4

            #codemean
            if HistoryLoaded[(i,0,0)]>0 and HistoryLoaded[(i,0,0)]<300000:
                TrainInput[(i,4)]=1
            elif HistoryLoaded[(i,0,0)]>=300000 and HistoryLoaded[(i,0,0)]<600000:
                TrainInput[(i,4)]=2
            elif HistoryLoaded[(i,0,0)]>=600000 and HistoryLoaded[(i,0,0)]<603000:
                TrainInput[(i,4)]=3
            elif HistoryLoaded[(i,0,0)]>=603000 and HistoryLoaded[(i,0,0)]<999999:
                TrainInput[(i,4)]=4
            #pe

            #TrainInput[(i,5)]=g_all_result[i]['s_per']
            if g_all_result[i]['s_per']<0 or g_all_result[i]['s_per']>=100:
                counter2[0]+=1
                TrainInput[(i,5)]=1
            elif g_all_result[i]['s_per']>=0 and g_all_result[i]['s_per']<25:
                counter2[1]+=1
                TrainInput[(i,5)]=4
            elif g_all_result[i]['s_per']>=25 and g_all_result[i]['s_per']<45:
                counter2[2]+=1
                TrainInput[(i,5)]=3
            elif g_all_result[i]['s_per']>45 and g_all_result[i]['s_per']<100:
                counter2[3]+=1
                TrainInput[(i,5)]=2
            #pb
            #TrainInput[(i,6)]=g_all_result[i]['s_pb']
            if g_all_result[i]['s_pb']<0 or g_all_result[i]['s_pb']>=6:
                #counter2[0]+=1
                TrainInput[(i,6)]=1
            elif g_all_result[i]['s_pb']>=0 and g_all_result[i]['s_pb']<2:
                #counter2[1]+=1
                TrainInput[(i,6)]=4
            elif g_all_result[i]['s_pb']>=2 and g_all_result[i]['s_pb']<3.5:
                #counter2[2]+=1
                TrainInput[(i,6)]=3
            elif g_all_result[i]['s_pb']>3.5 and g_all_result[i]['s_pb']<6:
                #counter2[3]+=1
                TrainInput[(i,6)]=2


            #去除数据不全的
            if HistoryLoaded[(i,1,(z-1))]==0:
                TrainInput[(i,3)]=-1
                continue


            
            #得到最后的结果
            Close=0
            for ii in range(z):



                if HistoryLoaded[(i,6,ii)]==target_dateA:
                    
                    if(HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,1,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,2,ii)]):
                        zzz=HistoryLoaded[(i,0,0)]
                        TrainInput[(i,3)]=-2
                        break
                    
                    #TrainInput[(i,9)]=HistoryLoaded[(i,3,ii)]
                    TrainInput[(i,8)]=HistoryLoaded[(i,3,ii)]
                    Close=HistoryLoaded[(i,3,ii)]
                elif HistoryLoaded[(i,6,ii)]==target_dateB and Close!=0:

                    TrainInput[(i,7)]=((HistoryLoaded[(i,3,ii)]-Close)/Close)*100
                    TrainInput[(i,9)]=HistoryLoaded[(i,3,ii)]        
                    TrainInput[(i,3)]=1
                    Available+=1
                    break


        else:
            wrongconter+=1
            continue

            
        '''
        for ii in range(y):
            for iii in range(10):
                print("%12.2f " % HistoryLoaded[(i,ii,iii)],end="")

            print("\n")
        print("\n")
        '''
        #print(Available)        
        #print(i)



    #TrainInput_test(TrainInput)

    '''
    for i in range(x-1):
        for ii in range(y):
            for iii in range(10):
                print("%12.2f " % HistoryLoaded[(i,ii,iii)],end="")

            print("\n")
        print("\n")
    '''
    #暂时对不使用sec数据
    SecUse=False
    if SecUse:
        #从Secdata中读取文件
        #获取目录下所有文件
        cwd = os.getcwd()
        file_dir = cwd + '\\data\\secret'
    
        for root, dirs,files in os.walk(file_dir):
            L=[]
            for file in files:  
                if os.path.splitext(file)[1] == '.npy':  
                    L.append(os.path.join(root, file))

        #遍历所有文件
        for z_file in L:

            #试试我的正则功力
            nums = re.findall(r"secretA(\d+).",z_file)
            cur_date=float(nums[0])
            if cur_date==target_dateB:

                SecLoaded=np.load(z_file)

                '''
                cwd = os.getcwd()
                txtFile1 = cwd + '\\data\\secret\\'+'secretA20180119.npy'
                SecLoaded=np.load(txtFile1)
                '''

                x=SecLoaded.shape[0]    #4000
                y=SecLoaded.shape[1]    #270
                z=SecLoaded.shape[2]    #21

                for i in range(x):
                    #if SecLoaded[(i,0,0)]==600055:
                    #print("\n")
                    if TrainInput[(i,3)]==1:
                        for ii in range(y):
                            zzz=1
                            #for iii in range(z):
                    

                '''
                for i in range(x-1):
                    #if SecLoaded[(i,0,0)]==600055:
                    #print("\n")
                    for ii in range(y):
                        for iii in range(z):
                            zzz=1
                            #print("%8.2f " % SecLoaded[(i,ii,iii)],end="")

                        #print("\n")
                    #print("\n")
                '''


    #将数据集分为测试组和训练组
    test_data=int(Available/5)
    train_data=Available-test_data

    fail=0

    while(test_data>0):
        randomdata=random.randint(0,3999)
        if TrainInput[(randomdata,3)]==1:
            TrainInput[(randomdata,3)]=2

            test_data-=1
        else:
            fail+=1


    #TrainInput_test(TrainInput)
    '''
    for i in range(x):
        print(i)
        for ii in range(y):
            print(i)
    '''
    return TrainInput
    
def TrainInput_test(TrainInput):
    x=TrainInput.shape[0]
    y=TrainInput.shape[1]

    for i in range(x-1):
        for ii in range(y):
            print("%8.2f " % TrainInput[(i,ii)],end="")
        print("\n")    


def CSZL_TrainValueCal(InputData,zmkt=1,zbb=1):
    x=InputData.shape[0]
    y=InputData.shape[1]

    cur_strategy=0
    finalzzz=0
    datacal=0
    cur_strategycal=0

    #TrainInput_test(InputData)


    for i in range(x):
        if InputData[(i,3)]>0 :

            if InputData[(i,1)]==zmkt and InputData[(i,4)]==zbb:
                #print(InputData[(i,0)])
                cur_strategy+=InputData[(i,7)]
                cur_strategycal+=1
            #kkk=InputData[(i,9)]
            finalzzz+=InputData[(i,7)]
            datacal+=1
    #print("/n")
    if(cur_strategycal==0):
        return -99

    final_cur_strategy=cur_strategy/cur_strategycal
    finalzzzz=finalzzz/datacal

    test=final_cur_strategy-finalzzzz
    return (test)


def CSZL_TrainResult(InputData):
    x=InputData.shape[0]
    y=InputData.shape[1]

    for i in range(x):
        print(i)
        for ii in range(y):
            print(i)

    aa=1

def CSZL_TrainBack(self):
    x=InputData.shape[0]
    y=InputData.shape[1]

    for i in range(x):
        print(i)
        for ii in range(y):
            print(i)

    aa=1
