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
#3天前的形状 2天前的形状 1天前的形状 0 1 2 counter total value
a=[]


def CSZL_TrainMainNEW(g_all_resultin):
    #global DataRecord
    global g_all_result
    global HistoryLoaded
    global LongProp

    CSZL_Sorttest()

    #初始化g_all_result
    g_all_result=g_all_resultin

    #初始化训练周期
    TrainDate=CSZL_TrainInitNEW()

    CSZL_SecAnalyseNew()

    #初始化长期属性
    CSZL_LongProp()
    #start_time = time.time()
    #初始化短期属性
    CSZL_ShortProp()


    #TrainInput_test(ShortProp)

    A,B=CSZL_TrainValueCalNEW(LongProp,ShortProp)




    CSZL_TrainDataSave()


    #print('函数执行完毕,用时:%sms' % ((time.time()-start_time)*1000))
    zzzz=1

def CSZL_LongProp():
    '''
    基于HistoryLoaded和g_all_result更新长策略LongProp
    '''

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


    #print ('\033[5;31;2m%8.4f %d \033[0m' % (num,num2) )

    #code availableflag AtoBresult shape sectionrate high low reserve1 buy sell 
    ShortProp=np.zeros((4000,10),dtype=float)

    x=len(g_all_result)         #4000
    y=HistoryLoaded.shape[1]    #7
    z=HistoryLoaded.shape[2]    #50
    
    target_dateA=20170125
    target_dateB=20180125

    Available=0

    countershape=[0,0,0,0,0,0,0,0,0,0,0,0,0]

    counter3=[0,0,0,0]


    #三天前 两天前 一天前 [0变动和 1变动计数 2前两项商 3排名]
    Ktype_counter=np.zeros((13,13,13,8),dtype=float)
    Ktype_sorter=np.zeros((12*12*12,2),dtype=float)

    cur_shape=0
    last_shape=0
    last_shape2=0
    last_shape3=0
    last_shape4=0

    last_close3=0
    last_close2=0
    last_close=0

    zzzcounter=0


    for i in range(x):    
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=HistoryLoaded[(i,0,0)]
        #保证相同项

        #countershape.clear()
        #countershape=[0,0,0,0,0,0,0,0,0,0,0,0,0]

        if(zzz==zzz2):
            #code(index)
            ShortProp[i,0]=HistoryLoaded[i,0,0]

            short_startflag=False
            #得到最后的结果
            Close=0

            #波动率计数
            sectionrate=0
            sectionratecounter=0

            #初始化收盘价以及3日形态计数
            last_close3=0
            last_close2=0
            last_close=0

            last_shape4=0
            last_shape3=0
            last_shape2=0
            last_shape=0

            for ii in range(z):

                #DateA to DateB 's result
                if HistoryLoaded[(i,6,ii)]==target_dateA:
                    short_startflag=True
                    if(HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,1,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,2,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,4,ii)]):
                        #zzz=HistoryLoaded[(i,0,0)]
                        ShortProp[(i,1)]=-1
                        break
                    
                    #ShortProp[(i,9)]=HistoryLoaded[(i,3,ii)]
                    ShortProp[(i,8)]=HistoryLoaded[(i,3,ii)]
                    Close=HistoryLoaded[(i,3,ii)]
                elif HistoryLoaded[(i,6,ii)]==target_dateB and Close!=0:

                    if(HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,1,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,2,ii)]and HistoryLoaded[(i,3,ii)]==HistoryLoaded[(i,4,ii)]):
                        zzz=HistoryLoaded[(i,0,0)]
                        ShortProp[(i,1)]=-2
                        break

                    ShortProp[(i,2)]=((HistoryLoaded[(i,3,ii)]-Close)/Close)*100
                    ShortProp[(i,9)]=HistoryLoaded[(i,3,ii)]        
                    ShortProp[(i,1)]=1
                    Available+=1
                    break

                if(short_startflag):
                    cur=HistoryLoaded[(i,1,ii)]
                    if cur==0:
                        break



                    #high=HistoryLoaded[(i,2,ii)]-HistoryLoaded[(i,1,ii)]
                    whole=HistoryLoaded[(i,3,ii)]-HistoryLoaded[(i,1,ii)]
                    #low=HistoryLoaded[(i,4,ii)]-HistoryLoaded[(i,1,ii)]
                    

                    redline=HistoryLoaded[(i,2,ii)]-HistoryLoaded[(i,3,ii)]
                    redline2=HistoryLoaded[(i,2,ii)]-HistoryLoaded[(i,1,ii)]

                    greenline=HistoryLoaded[(i,4,ii)]-HistoryLoaded[(i,3,ii)]
                    greenline2=HistoryLoaded[(i,4,ii)]-HistoryLoaded[(i,1,ii)]

                    section=HistoryLoaded[(i,2,ii)]-HistoryLoaded[(i,4,ii)]

                    vol=HistoryLoaded[(i,5,ii)]
                    #区间波动率计数
                    sectionrate+=(section/cur)
                    sectionratecounter+=1

                   
                    #找形态
                    response_rate=0.005
                    cur_shape=0

                    if((whole/cur)>response_rate):
                        if((redline/cur)>response_rate):
                            if((greenline2/cur)<(-response_rate)):
                                cur_shape=4
                            else:
                                cur_shape=5
                        elif((greenline2/cur)<-response_rate):
                            cur_shape=2
                        else:
                            cur_shape=1

                    elif ((whole/cur)<(-response_rate)):
                        if((redline2/cur)>response_rate):
                            if((greenline/cur)<(-response_rate)):
                                cur_shape=9
                            else:
                                cur_shape=11
                        elif((greenline/cur)<(-response_rate)):
                            cur_shape=8
                        else:
                            cur_shape=12
                    else:
                        if((redline2/cur)>response_rate):
                            if((greenline2/cur)<(-response_rate)):
                                cur_shape=6
                            else:
                                cur_shape=10
                        elif((greenline2/cur)<(-response_rate)):
                            cur_shape=3
                        else:
                            cur_shape=7                     

                    #单日
                    '''
                    if(last_close!=0 and last_shape2!=0):
                        if((last_close2-last_close)/last_close2<0.095 and (last_close2-last_close)/last_close2>-0.095):

                            plustest=((HistoryLoaded[(i,3,ii)]-last_close)/last_close)

                            if(plustest>0.1):
                                zzzzzzz=0

                            Ktype_counter[last_shape3,last_shape2,last_shape,1]+=plustest
                            Ktype_counter[last_shape3,last_shape2,last_shape,0]+=1
                            if(last_shape3==9 and last_shape2==5 and last_shape==4):
                                zzzcounter+=1
                    '''

                    #两日
                    if(last_close3!=0 and last_shape4!=0):
                        if((last_close3-last_close2)/last_close3<0.095 and (last_close3-last_close2)/last_close3>-0.095):

                            plustest=((HistoryLoaded[(i,3,ii)]-last_close2)/last_close2)

                            if(plustest>0.22):
                                zzzzzzz=0

                            Ktype_counter[last_shape4,last_shape3,last_shape2,1]+=plustest
                            Ktype_counter[last_shape4,last_shape3,last_shape2,0]+=1

                            #用于测试
                            if(last_shape3==9 and last_shape2==5 and last_shape==4):
                                zzzcounter+=1


                    last_close3=last_close2
                    last_close2=last_close
                    last_close=HistoryLoaded[(i,3,ii)]

                    last_shape4=last_shape3
                    last_shape3=last_shape2
                    last_shape2=last_shape
                    last_shape=cur_shape

                    '''

                    countershape[int(ShortProp[(i,3)])]+=1
                    countershape[0]+=1

                    if whole>=0:
                        ShortProp[(i,3)]=1
                        if (high-whole)/cur>0.02:
                            ShortProp[(i,3)]=2
                    else:
                        ShortProp[(i,3)]=3
                        if (low-whole)/cur<-0.02:
                            ShortProp[(i,3)]=4
                    '''
            #波动率
            if(sectionratecounter>0):
                sectioncal=sectionrate/sectionratecounter
                if(sectioncal>0.045):
                    ShortProp[(i,4)]=1
                    #counter3[0]+=1
                elif(sectioncal>0.03):
                    ShortProp[(i,4)]=2
                    #counter3[1]+=1
                elif(sectioncal>0.02):
                    ShortProp[(i,4)]=3
                    #counter3[2]+=1
                else:
                    ShortProp[(i,4)]=4
                    #counter3[3]+=1


            dsfsf=2

        else:
            continue

    for i in range(1,13):
        for ii in range(1,13):
            for iii in range(1,13):

    
                #分类
                if(Ktype_counter[i,ii,iii,1]!=0):    
                    Ktype_counter[i,ii,iii,2]= Ktype_counter[i,ii,iii,1]/Ktype_counter[i,ii,iii,0]

                    #准备排序
                    Ktype_sorter[((i-1)*12*12+(ii-1)*12+iii-1),0]=Ktype_counter[i,ii,iii,2];

                    if(Ktype_counter[i,ii,iii,2]>0.005 and Ktype_counter[i,ii,iii,0]>100):
                        Ktype_counter[i,ii,iii,3]=3
                        #print("xxxx%6.4f %4d " % (Ktype_counter[i,ii,iii,2],Ktype_counter[i,ii,iii,0]),end="")
                    elif(Ktype_counter[i,ii,iii,2]<-0.01):
                        Ktype_counter[i,ii,iii,3]=0
                        #print("oo%6.4f %4d " % (Ktype_counter[i,ii,iii,2],Ktype_counter[i,ii,iii,0]),end="")
                    else:
                        Ktype_counter[i,ii,iii,3]=-3
                        #print("  %6.4f %4d " % (Ktype_counter[i,ii,iii,2],Ktype_counter[i,ii,iii,0]),end="")                        

                else:
                    #print("%8.4f %4d " % (0,0),end="")
                    Ktype_counter[i,ii,iii,3]=-1
            #print("\n")
        #print("\n") 
    a1=Ktype_sorter[:,0]
    a2=np.argsort(a1)
    a3=np.argsort(a1)

    #序号与数字重排(这边居然搞了20分钟才搞清楚关系，也不知道搞没搞最简，先这样了)
    for i in range(len(a2)):
        a3[a2[i]]=i


    for i in range(1,13):
        for ii in range(1,13):
            for iii in range(1,13):
                cur_rank=a3[((i-1)*12*12+(ii-1)*12+iii-1)]
                Ktype_counter[i,ii,iii,4]=cur_rank
                #zz2=(int)((sdfsdf)/(12*12))
                #zz3=(int)((sdfsdf-zz2*12*12)/12)
                #zz4=(int)(sdfsdf-zz2*12*12-zz3*12)
                #print("%4.4f %4d " % (Ktype_counter[i,ii,iii,2],cur_rank),end="")

            print("\n")
        print("\n") 

    #print(a1)

    cwd = os.getcwd()

    txtFileA = cwd + '\\output\\KtypeThree.npy'
    np.save(txtFileA, Ktype_counter)

    zzzzz=1

def CSZL_TrainValueCalNEW(InputDataLong,InputDataShort):

    #输出

    x=InputDataLong.shape[0]
    Ly=InputDataLong.shape[1]

    Sy=InputDataShort.shape[1]


    finalzzz=0
    datacal=0
    cur_strategycal=0

    #TrainInput_test(InputData)

    Counter=np.zeros((5,5,5,4),dtype=float)

    #初始化看的长策略和短策略，并加入最后计算
    for i in range(x):
        if InputDataShort[(i,1)]>0 :
     
            Counter[(int(InputDataLong[(i,1)]),int(InputDataLong[(i,6)]),int(InputDataShort[(i,4)]),1)]+=InputDataShort[(i,2)]
            Counter[(int(InputDataLong[(i,1)]),int(InputDataLong[(i,6)]),int(InputDataShort[(i,4)]),2)]+=1


            #kkk=InputData[(i,9)]
            finalzzz+=InputDataShort[(i,2)]
            datacal+=1

    #将最后结果计入Counter[i,ii,iii,3]
    for i in range(1,5):
        for ii in range(1,5):
            for iii in range(1,5):
                if(Counter[i,ii,iii,2]!=0):          
                    Counter[i,ii,iii,3]= Counter[i,ii,iii,1]/Counter[i,ii,iii,2]
                    print("%8.2f %d " % (Counter[i,ii,iii,3],Counter[i,ii,iii,2]),end="")


            print("\n")
        print("\n") 

    finalzzzz=finalzzz/datacal
    print('all:%f' % (finalzzzz))
    

    return (Counter,finalzzzz)

def CSZL_TrainInitNEW():
    global HistoryLoaded
    global DataRecord

    TrainDate=[]

    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'History_data.npy'
    HistoryLoaded=np.load(txtFile1)


    startdate=20060126
    enddate=20180126

    z=HistoryLoaded.shape[2]    #50

    for ii in  range(z):
        #这里暂时拿特定一个数据来作为日期检测的种子,之后会寻找更加合适的方法1328
        if(HistoryLoaded[(1328,6,ii)]>=startdate and HistoryLoaded[(1328,6,ii)]<=enddate ):
            TrainDate.append(HistoryLoaded[(1,6,ii)])

    return TrainDate

def CSZL_TrainDataSave():

    global HistoryLoaded

    #no code value1 value2 value3
    HisAna=np.zeros((4000,5),dtype=float)

    for z in range(4000):
        HisAna[z,0]=z
        HisAna[z,1]=HistoryLoaded[z,0,0]
        HisAna[z,2]=0.5

    cwd = os.getcwd()
    #now=datetime.datetime.now()
    #now=now.strftime('%Y%m%d')

    txtFileA = cwd + '\\output\\HisAna.npy'
    np.save(txtFileA, HisAna)


def CSZL_SecAnalyseNew():
    #开始更新sec逻辑
    SecUse=True
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
            if cur_date==20180413:

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
                    if SecLoaded[(i,0,0)]==600461:

                        for ii in range(y):
                            for iii in range(z):
                                print("%8.2f " % SecLoaded[(i,ii,iii)],end="")
                            print("\n")
                        print("\n")
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
    zzz=1

def CSZL_Sorttest():

    '''
    a = np.random.randint(0,1000.,size=(5,5,5,2))
    a1=np.argsort(a,axis = 0)
    a2=a[:,:,2]

    print(a)
    print('\n\n')
    print(a1)
    print('\n\n')
    print(a2)
    '''
    xxxx=1

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
