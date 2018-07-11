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



All_K_Data=[]
#DataRecord=[]  
#全局初始化数据
g_all_result=[]

#长期属性 一般一次训练只初始化一次
LongProp=[]
#实时短期属性 每个循环可能都需要改变
ShortProp=[]
#高低位置属性
PosProp=[]
#3天前的形状 2天前的形状 1天前的形状 0 1 2 counter total value
a=[]

def CSZL_TrainInitNEW():
    '''
    输入全部的历史数据

    输出交易日的日期序列TrainDate

    '''

    global All_K_Data
    #global DataRecord

    TrainDate=[]

    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'ALL_History_data.npy'
    All_K_Data=np.load(txtFile1)


    startdate=20100126
    enddate=20180126

    z=All_K_Data.shape[2]    #50

    for ii in  range(z):
        #这里暂时拿特定一个数据来作为日期检测的种子,之后会寻找更加合适的方法1328
        if(All_K_Data[(1328,6,ii)]>=startdate and All_K_Data[(1328,6,ii)]<=enddate ):
            TrainDate.append(All_K_Data[(1,6,ii)])

    return TrainDate

def CSZL_LongProp():
    '''
    基于HistoryLoaded和g_all_result更新长策略LongProp
    '''

    global All_K_Data
    global LongProp

    #todo改成可读取式的
    #code mkt codemean pe pb stflag stop reserve3
    LongProp=np.zeros((4000,8),dtype=float)

    x=len(g_all_result)
    y=All_K_Data.shape[1]    #7
    z=All_K_Data.shape[2]    #50
    
    #todo自动调整平衡位置
    counter2=[0,0,0,0]

    wrongconter=0
    rightcounter=0
    searchcounter=0
    updatecounter=0

    #读取历史数据的位置
    hisdata_index=1
    #取出历史数据名称列表用于后面找不到位置时进行的搜索
    CodeList=All_K_Data[:,0,0]
    
    for i in range(1,x):
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=All_K_Data[(hisdata_index,0,0)]

        #如果当前更新列表和历史数据版本不一致导致数据错位
        if(zzz!=zzz2 and zzz!=0): 
            #从历史数据列表中寻找是否有对应值
            buff=np.argwhere(CodeList==int(zzz))
            #如果有指则重新定义历史数据位置
            if(buff!=None):
                foundindex=int(buff)
                hisdata_index=foundindex
                zzz2=All_K_Data[(hisdata_index,0,0)]
                searchcounter+=1
            else:
                updatecounter+=1
                continue
       
        #code(index)
        LongProp[i,0]=zzz2

        #mkt
        #LongProp[(i,1)]=g_all_result[i]['s_mktcap']
        if g_all_result[i]['s_mktcap']<400000:
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
        else:
            wrongconter+=1

        #codemean
        if All_K_Data[hisdata_index,0,0]>0 and All_K_Data[hisdata_index,0,0]<300000:
            LongProp[(i,2)]=1
        elif All_K_Data[hisdata_index,0,0]>=300000 and All_K_Data[hisdata_index,0,0]<600000:
            LongProp[(i,2)]=2
        elif All_K_Data[hisdata_index,0,0]>=600000 and All_K_Data[hisdata_index,0,0]<603000:
            LongProp[(i,2)]=3
        elif All_K_Data[hisdata_index,0,0]>=603000 and All_K_Data[hisdata_index,0,0]<999999:
            LongProp[(i,2)]=4
        else:
            wrongconter+=1

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
        else:
            wrongconter+=1

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
        else:
            wrongconter+=1

        #st

        if g_all_result[i]['s_stflag']>0:
            #counter2[0]+=1
            LongProp[(i,5)]=1
        else:
            #counter2[3]+=1
            LongProp[(i,5)]=2    
   
        #stopperiod
        if All_K_Data[(hisdata_index,1,(z-100))]==0:
            LongProp[(i,6)]=3
        elif All_K_Data[(hisdata_index,1,(z-1))]==0:
            LongProp[(i,6)]=2
        else:
            LongProp[(i,6)]=1  
        rightcounter+=1
        hisdata_index+=1


    if(wrongconter!=0):
        print("发现错误")

def CSZL_ShortProp():
    global LongProp
    global ShortProp


    #print ('\033[5;31;2m%8.4f %d \033[0m' % (num,num2) )

    #code availableflag AtoBresult shape sectionrate high low reserve1 buy sell 
    ShortProp=np.zeros((4000,10),dtype=float)

    x=len(g_all_result)         #4000
    y=All_K_Data.shape[1]    #7
    z=All_K_Data.shape[2]    #50
    
    target_dateA=20140108
    target_dateB=20180125

    #有效数据
    Available=0

    countershape=[0,0,0,0,0,0,0,0,0,0,0,0,0]

    counter3=[0,0,0,0]


    #三天前 两天前 一天前 [0变动和 1变动计数 2reserve 3reserve 4商排名 5涨停次数 6涨停次数排名 7跌停次数 8跌停次数排名 9reserve]
    Ktype_counter=np.zeros((13,13,13,10),dtype=float)
    #第二位为0是涨幅排序，1是涨停排序，2是跌停排序
    Ktype_sorter=np.zeros((12*12*12,4),dtype=float)

    
    #cur_shape=0
    last_shape=0
    last_shape2=0
    last_shape3=0
    last_shape4=0

    last_close3=0
    last_close2=0
    last_close=0

    zzzcounter=0


    rightcounter=0
    searchcounter=0
    updatecounter=0


    #读取历史数据的位置
    hisdata_index=1
    #取出历史数据名称列表用于后面找不到位置时进行的搜索
    CodeList=All_K_Data[:,0,0]

    for i in range(x):
        if(i%30==0):
            print(i)
  
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=All_K_Data[(hisdata_index,0,0)]

        #如果当前更新列表和历史数据版本不一致导致数据错位
        if(zzz!=zzz2 and zzz!=0): 
            #从历史数据列表中寻找是否有对应值
            buff=np.argwhere(CodeList==int(zzz))
            #如果有指则重新定义历史数据位置
            if(buff!=None):
                foundindex=int(buff)
                hisdata_index=foundindex
                zzz2=All_K_Data[(hisdata_index,0,0)]
                searchcounter+=1
            else:
                updatecounter+=1
                continue
        elif(zzz==0):
            continue

        #countershape.clear()
        #countershape=[0,0,0,0,0,0,0,0,0,0,0,0,0]


        #code(index)
        ShortProp[i,0]=zzz

        short_startflag=False
        #得到最后的结果
        Close=0

        #波动率计数
        #sectionrate=0
        #sectionratecounter=0
        sectionratecounter2=Z_Counter()

        #初始化收盘价以及3日形态计数
        last_close3=0
        last_close2=0
        last_close=0

        last_shape4=0
        last_shape3=0
        last_shape2=0
        last_shape=0


        if(zzz==408):
            sdfe=1

        for ii in range(z):
            
            #DateA to DateB 's result
            if All_K_Data[(hisdata_index,6,ii)]>=target_dateA and short_startflag==False:
                
                #如果开始这天是无意义的（一字涨停或跌停）一天，记录ShortProp[(i,1)]=-1
                if(All_K_Data[(hisdata_index,3,ii)]==All_K_Data[(hisdata_index,1,ii)]and All_K_Data[(hisdata_index,3,ii)]==All_K_Data[(hisdata_index,2,ii)]and All_K_Data[(hisdata_index,3,ii)]==All_K_Data[(hisdata_index,4,ii)]):
                    continue

                short_startflag=True

                ShortProp[(i,8)]=All_K_Data[(hisdata_index,3,ii)]
                Close=All_K_Data[(hisdata_index,3,ii)]
            elif All_K_Data[(hisdata_index,6,ii)]>=target_dateB and Close!=0:
                #如果结束这天是无意义的（一字涨停或跌停）一天，记录ShortProp[(i,1)]=-2
                if(All_K_Data[(hisdata_index,3,ii)]==All_K_Data[(hisdata_index,1,ii)]and All_K_Data[(hisdata_index,3,ii)]==All_K_Data[(hisdata_index,2,ii)]and All_K_Data[(hisdata_index,3,ii)]==All_K_Data[(hisdata_index,4,ii)]):
                    zzz=All_K_Data[(hisdata_index,0,0)]
                    ShortProp[(i,1)]=-2
                    break

                ShortProp[(i,2)]=((All_K_Data[(hisdata_index,3,ii)]-Close)/Close)*100
                ShortProp[(i,9)]=All_K_Data[(hisdata_index,3,ii)]        
                ShortProp[(i,1)]=1
                Available+=1
                break

            if(short_startflag):
                #获取当日开盘价
                cur=All_K_Data[(hisdata_index,1,ii)]
                #如果当日开盘价为0退出循环
                if cur==0:
                    break

                #cur_shape=CSZLsuperGET.k_type_def2(All_K_Data[(hisdata_index,1,ii)],All_K_Data[(hisdata_index,2,ii)],All_K_Data[(hisdata_index,3,ii)],All_K_Data[(hisdata_index,4,ii)])
                cur_shape=CSZLsuperGET.k_type_def(All_K_Data,hisdata_index,ii,0.005)

                #当日成交
                vol=All_K_Data[(hisdata_index,5,ii)]
            
                #震荡区间(当日最高减去当日最低)
                section=All_K_Data[(hisdata_index,2,ii)]-All_K_Data[(hisdata_index,4,ii)]
                #区间波动率计数
                #sectionrate+=(section/cur)
                #sectionratecounter+=1
                sectionratecounter2.Add((section/cur))
                #kkds=sectionratecounter2.Sum()


                #单日
                '''
                这里假设的情况是知道 第一日形态 第二日形态 第三日形态(且次日非涨停跌停) 
                当前日为第四日，将当日收盘减去上一日收盘得到的结果（在第三日最后一分钟买入，第四日最后一分钟卖出）
                '''
                #前三日形态不为0(有值)
                if(last_shape3!=0):
                    #上个交易日非涨停或跌停(如果涨停或跌停则不记录)
                    if((last_close2-last_close)/last_close2<0.095 and (last_close2-last_close)/last_close2>-0.095):
                        #记录结果
                        plusbuff=((All_K_Data[(hisdata_index,3,ii)]-last_close)/last_close)

                        if(plusbuff>0.095):
                            Ktype_counter[last_shape3,last_shape2,last_shape,5]+=1
                        elif(plusbuff<-0.095):
                            Ktype_counter[last_shape3,last_shape2,last_shape,7]+=1

                        Ktype_counter[last_shape3,last_shape2,last_shape,1]+=plusbuff
                        Ktype_counter[last_shape3,last_shape2,last_shape,0]+=1
                        if(last_shape3==3 and last_shape2==7 and last_shape==6):
                            zzzcounter+=1
                

                #两日
                '''
                if(last_close3!=0 and last_shape4!=0):
                    if((last_close3-last_close2)/last_close3<0.095 and (last_close3-last_close2)/last_close3>-0.095):

                        plustest=((All_K_Data[(hisdata_index,3,ii)]-last_close2)/last_close2)

                        if(plustest>0.22):
                            zzzzzzz=0

                        Ktype_counter[last_shape4,last_shape3,last_shape2,1]+=plustest
                        Ktype_counter[last_shape4,last_shape3,last_shape2,0]+=1

                        #用于测试
                        if(last_shape3==9 and last_shape2==5 and last_shape==4):
                            zzzcounter+=1
                '''
                #更新前几日的收盘价
                last_close3=last_close2
                last_close2=last_close
                last_close=All_K_Data[(hisdata_index,3,ii)]
                #更新前几日的形态
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
        if(sectionratecounter2.Sum()>0):
            sectioncal=sectionratecounter2.Average()
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

        hisdata_index+=1


    for i in range(1,13):
        for ii in range(1,13):
            for iii in range(1,13):

    
                #分类
                if(Ktype_counter[i,ii,iii,1]!=0):

                    #准备排序，由于一共有12x12x12种组合，将前三日对应到排序数组中
                    #第四日平均涨幅
                    Ktype_sorter[((i-1)*12*12+(ii-1)*12+iii-1),0]=Ktype_counter[i,ii,iii,1]/Ktype_counter[i,ii,iii,0];
                    #第四日涨停概率
                    Ktype_sorter[((i-1)*12*12+(ii-1)*12+iii-1),1]=Ktype_counter[i,ii,iii,5]/Ktype_counter[i,ii,iii,0];
                    #第四日跌停概率
                    Ktype_sorter[((i-1)*12*12+(ii-1)*12+iii-1),2]=Ktype_counter[i,ii,iii,7]/Ktype_counter[i,ii,iii,0];

                    '''
                    if(Ktype_counter[i,ii,iii,2]>0.005 and Ktype_counter[i,ii,iii,0]>100):
                        Ktype_counter[i,ii,iii,3]=3
                        print("xxxx%6.4f %4d " % (Ktype_counter[i,ii,iii,2],Ktype_counter[i,ii,iii,0]),end="")
                    elif(Ktype_counter[i,ii,iii,2]<-0.01):
                        Ktype_counter[i,ii,iii,3]=0
                        print("oo%6.4f %4d " % (Ktype_counter[i,ii,iii,2],Ktype_counter[i,ii,iii,0]),end="")
                    else:
                        Ktype_counter[i,ii,iii,3]=-3
                        print("  %6.4f %4d " % (Ktype_counter[i,ii,iii,2],Ktype_counter[i,ii,iii,0]),end="")                        
                    '''
                else:
                    pass
                    #print("%8.4f %4d " % (0,0),end="")
                    #Ktype_counter[i,ii,iii,3]=-1
            #print("\n")
        #print("\n") 

    #从排序数组中取出
    a1=Ktype_sorter[:,0]
    b1=Ktype_sorter[:,1]
    c1=Ktype_sorter[:,2]

    #a2是排序后a1的标号
    a2=np.argsort(a1)
    a3=np.argsort(a1)
    b2=np.argsort(b1)
    b3=np.argsort(b1)
    c2=np.argsort(c1)
    c3=np.argsort(c1)


    #序号与数字重排(这边居然搞了20分钟才搞清楚关系，也不知道搞没搞最简，先这样了)
    #迷之操作
    for i in range(len(a2)):
        a3[a2[i]]=i
        b3[b2[i]]=i       
        c3[c2[i]]=i

    for i in range(1,13):
        for ii in range(1,13):
            for iii in range(1,13):
                #反向取出迷之操作过的数组就是当前i ii iii所对应的rank，这个rank越大，数值越大例如+0.05为1728 
                cur_rank=a3[((i-1)*12*12+(ii-1)*12+iii-1)]
                Ktype_counter[i,ii,iii,4]=cur_rank

                cur_rank2=b3[((i-1)*12*12+(ii-1)*12+iii-1)]
                Ktype_counter[i,ii,iii,6]=cur_rank2

                cur_rank3=c3[((i-1)*12*12+(ii-1)*12+iii-1)]
                Ktype_counter[i,ii,iii,8]=cur_rank3

                #print("%4.4f &4d %4d " % (Ktype_counter[i,ii,iii,5],cur_rank2),end="")
                #print("%4d %4d %4d " % (Ktype_counter[i,ii,iii,5],Ktype_counter[i,ii,iii,0],cur_rank2),end="")

            #print("\n")
        #print("\n") 

    #print(a1)

    cwd = os.getcwd()

    txtFileA = cwd + '\\output\\KtypeThree.npy'
    np.save(txtFileA, Ktype_counter)

    zzzzz=1

def CSZL_PosProp():
    '''
    计算位置

    '''
    global All_K_Data

    global PosProp

    # code 全最高 全最低 666最高 最低 166最高 166最低 5最高 5最低 全局位置 666位置 166位置
    PosProp=np.zeros((4000,15),dtype=float)
    
    x=len(g_all_result)         #4000
    y=All_K_Data.shape[1]    #7
    z=All_K_Data.shape[2]    #50


    #读取历史数据的位置
    hisdata_index=1
    #取出历史数据名称列表用于后面找不到位置时进行的搜索
    CodeList=All_K_Data[:,0,0]

    updatecounter=0
    searchcounter=0

    #新建5个计数器用来记录5个位置的值
    SectionCounter=[]
    for ii in range(5):
        temp=Z_Counter()
        SectionCounter.append(temp)
        del temp

    section3=20
    section2=5
    SectionCounter2=[]
    for ii in range(section3*section2*5):
        temp=Z_Counter()
        SectionCounter2.append(temp)
        del temp


    for i in range(x):
        if(i%30==0):
            print(i)
  
        temp=str(g_all_result[i]['s_code'],"utf-8")
        zzz=float(temp)
        zzz2=All_K_Data[(hisdata_index,0,0)]


        #如果当前更新列表和历史数据版本不一致导致数据错位
        if(zzz!=zzz2 and zzz!=0): 
            #从历史数据列表中寻找是否有对应值
            buff=np.argwhere(CodeList==int(zzz))
            #如果有指则重新定义历史数据位置
            if(buff!=None):
                foundindex=int(buff)
                hisdata_index=foundindex
                zzz2=All_K_Data[(hisdata_index,0,0)]
                searchcounter+=1
            else:
                updatecounter+=1
                continue
        elif(zzz==0):
            continue

        PosProp[i,0]=zzz

        if(zzz==600000):
            fsdfse=5

        #回测逻辑
        #新建一个区间测试
        #section5=SectionCal(5)

        section20=SectionCal(20)



        for ii in range(1,z-1):
            if All_K_Data[hisdata_index,3,ii+1]==0:
                break

            #以正的序列
            #section5.Add(All_K_Data[hisdata_index,:,ii])
            section20.Add(All_K_Data[hisdata_index,:,ii])
            bufpos=section20.GetPos()
            date=All_K_Data[hisdata_index,6,ii]
            

            if(bufpos!=0 and (20160600<date)):
                #将位置信息放入对应计数器
                for iii in range(5):
                    if(bufpos<=((iii+1)*0.2)):

                        bufpercent1=(All_K_Data[hisdata_index,3,ii]-All_K_Data[hisdata_index,3,ii-1])/All_K_Data[hisdata_index,3,ii-1]
                        bufpercent2=(All_K_Data[hisdata_index,3,ii+1]-All_K_Data[hisdata_index,3,ii])/All_K_Data[hisdata_index,3,ii]
                        bufpercent3=(All_K_Data[hisdata_index,4,ii+1]-All_K_Data[hisdata_index,3,ii])/All_K_Data[hisdata_index,3,ii]
                        dy=(int)(date/10000)                     
                        dm=(int)((date-(dy)*10000)/100)
                        dd=(int)(date%100)

                        date_from = datetime.datetime(dy,dm ,dd , 00, 00, 00)
                        dayofweek=date_from.weekday()
                        #剔除异常值(如果上个交易日涨停或跌停显然不能计入数据)
                        if(bufpercent1<0.095 and bufpercent1>(-0.095) and (bufpercent1<0.045 or bufpercent1>0.055) and (bufpercent1<-0.055 or bufpercent1>-0.045)):
                            if(bufpercent2<0.11 and bufpercent2>-0.11 ):
                                cur_shape=CSZLsuperGET.k_type_def(All_K_Data,hisdata_index,ii,0.005)

                                #bufintpos=(int)(((bufpercent2*100)+10)*2)
                                bufintpos2=(int)(((bufpercent1*100)+10))

                                if(bufintpos2<0):
                                    bufintpos2=0
                                if(bufintpos2>19):
                                    bufintpos2=19
                                #SectionCounter2[bufintpos+iii*20+dayofweek*5*20].Add(bufpercent2)
                                SectionCounter2[bufintpos2+iii*section3+dayofweek*section2*section3].Add(bufpercent2)
                                #if(bufpercent3>0.01):
                                        
                                    #else:
                                        #SectionCounter2[cur_shape+iii*13].Add(bufpercent2)
                                #if(bufpercent2>0.095):
                                    #SectionCounter2[iii].Add(bufpercent2)
                                #elif(bufpercent2<-0.095):
                                    #SectionCounter[iii].Add(bufpercent2)
                        break

            #test=section5.Max()

            safsef=4

        if(i>3000):
            for iiii in range(5):
                for ii in range(section2):
                    for iii in range(section3):
                        asdad3=SectionCounter2[ii*section3+iii+iiii*section2*section3].Average()
                        asdad2=SectionCounter2[ii*section3+iii+iiii*section2*section3].Count()
                        print("%2.4f %d " % (asdad3,asdad2),end="")

                        '''
                        asdad2=SectionCounter2[ii*20+iii+iiii*5*20].Average()
                        asdad3=SectionCounter2[ii*20+iii+iiii*5*20].Count()
                        if(asdad2>0.003):
                            print("%2.4f %4d " % (asdad2+4,asdad3),end="")
                        elif(asdad2<-0.001):
                            print("%2.4f %4d " % (asdad2+9,asdad3),end="")
                        else:
                            print("%2.4f %4d " % (asdad2+1,asdad3),end="")
                        '''

                    print("\n")
                print("\n")
        del section20

        if False:
            #快速计算当前处于的平均位置
            highall=0
            lowall=65534    
            high666=0
            low666=65533
            high166=0
            low166=65532
            high5=0
            low5=65531
            lastdata=0

            stop666=True
            stop166=True
            stop5=True
            stop1=True


            #有效数据
            avcounter=0
            for ii in range(z):
                #以逆的序列
                cur_high=All_K_Data[hisdata_index,2,(z-1-ii)]
                cur_low=All_K_Data[hisdata_index,4,(z-1-ii)]
                cur_price=All_K_Data[hisdata_index,3,(z-1-ii)]

                cur_date=All_K_Data[hisdata_index,6,(z-1-ii)]

                if(cur_high!=0 and cur_low!=0):                
                    avcounter+=1
                else:
                    continue     
        
                #TODO有时间用栈改
                if(cur_high>highall):
                    highall=cur_high
                if(cur_low<lowall):
                    lowall=cur_low

                if(avcounter>0 and stop1):
                    lastdata=cur_price
                    stop1=False

                if(avcounter>5 and stop5):
                    high5=highall
                    low5=lowall
                    stop5=False
     
                if(avcounter>166 and stop166):
                    high166=highall
                    low166=lowall
                    stop166=False
                if(avcounter>466 and stop666):
                    high666=highall
                    low666=lowall
                    stop666=False    
        
            PosProp[i,1]=highall
            PosProp[i,2]=lowall
            PosProp[i,3]=high666
            PosProp[i,4]=low666
            PosProp[i,5]=high166
            PosProp[i,6]=low166
            PosProp[i,7]=high5
            PosProp[i,8]=low5
        
            PosProp[i,9]=pos_cal(PosProp[i,1],PosProp[i,2],lastdata)
            PosProp[i,10]=pos_cal(PosProp[i,3],PosProp[i,4],lastdata)
            PosProp[i,11]=pos_cal(PosProp[i,5],PosProp[i,6],lastdata)



        hisdata_index+=1

def CSZL_CodelistToDatelist():
    global All_K_Data

   
    x=All_K_Data.shape[0]    #4000
    y=All_K_Data.shape[1]    #7
    z=All_K_Data.shape[2]    #2000

    # 日期 代码 信息
    DateBasedList=np.zeros((z,x,y),dtype=float)


    bufflist=ts.get_k_data('000001',start='2010-03-01', end='2018-06-13', index=True) 

    datelist=bufflist.date.tail(z)

    searchcounter=0
    updatecounter=0

    i=0
    for singledatezz in datelist:

        changedate=time.strptime(singledatezz,"%Y-%m-%d")
        changedate2=time.strftime("%Y%m%d",changedate)
        changedate3=int(changedate2)
        
        DateBasedList[(i,0,0)]=changedate3

        date_index=0
        for ii in range(x):
            cur_changedata=All_K_Data[ii,6,date_index]
            if(changedate3==cur_changedata):
                DateBasedList[i,ii,:]=All_K_Data[ii,:,date_index]
                DateBasedList[i,ii,6]=All_K_Data[ii,0,0]
                
            else:
                
                bufsearch=All_K_Data[ii,6,:]
                #从历史数据列表中寻找是否有对应值
                buff=np.argwhere(bufsearch==changedate3)
                #如果有指则重新定义历史数据位置
                if(buff!=None):
                    foundindex=int(buff)
                    date_index=foundindex
                    zzz2=All_K_Data[(ii,6,date_index)]

                    DateBasedList[i,ii,:]=All_K_Data[ii,:,date_index]
                    DateBasedList[i,ii,6]=All_K_Data[ii,0,0]
                    
                    searchcounter+=1
                else:
                    
                    updatecounter+=1
                    continue
        i+=1
        if(i>1999):
            break;

    '''
    for i in  range(z):
        print(DateBasedList[i,0,0])
        for ii in  range(x):
            asdad3=DateBasedList[i,ii,3]
            asdad2=DateBasedList[i,ii,6]
            print("%2.4f %d " % (asdad3,asdad2))
            
        print("\n")
    '''
    cwd = os.getcwd()

    txtFileA = cwd + '\\output\\ALL_History_data_Datebased.npy'
    np.save(txtFileA, DateBasedList)


    sdfsdf=5

def CSZL_DatebasedPosProp():

    cwd = os.getcwd()
    txtFileA = cwd + '\\output\\ALL_History_data_Datebased.npy'
    DateBasedList=np.load(txtFileA)

    x=DateBasedList.shape[0]    #2000
    y=DateBasedList.shape[1]    #4000
    z=DateBasedList.shape[2]    #7  

    
    #新建5个计数器用来记录5个位置的值
    SectionCounter=[]
    for ii in range(20):
        temp=Z_Counter()
        SectionCounter.append(temp)
        del temp


    section3=20
    section2=5

    SectionCounter2=[]

    for ii in range(section3*section2):
        temp=Z_Counter()
        SectionCounter2.append(temp)
        del temp

    avacounter=0

    for i in range(1,x-1):
        cur_date=DateBasedList[i,0,0]
        counter=DateBasedList[i,:,3]
        a=np.sum(counter!=0)
        if(a==0):
            continue

        todaylist=np.where(counter>0)
        todaylist2=todaylist[0]


        if(cur_date>20140101):
            for cur_index in todaylist2:
                code=DateBasedList[i,cur_index,6]
                last_close=DateBasedList[i-1,cur_index,3]
                cur_close=DateBasedList[i,cur_index,3]
                next_close=DateBasedList[i+1,cur_index,3]

                if(last_close==0 or cur_close==0 or next_close==0):
                    continue

                today_plus=(cur_close-last_close)/last_close
                tomorrow_plus=(next_close-cur_close)/cur_close

                dy=(int)(cur_date/10000)                     
                dm=(int)((cur_date-(dy)*10000)/100)
                dd=(int)(cur_date%100)

                date_form = datetime.datetime(dy,dm ,dd , 00, 00, 00)
                dayofweek=date_form.weekday()
                
                if(today_plus<0.095 and today_plus>(-0.095) and (today_plus<0.045 or today_plus>0.055) and (today_plus<-0.055 or today_plus>-0.045)):
                    if(tomorrow_plus<0.11 and tomorrow_plus>-0.11 ):

                        bufintpos2=(int)(((today_plus*100)+10))

                        if(bufintpos2<0):
                            bufintpos2=0
                        if(bufintpos2>19):
                            bufintpos2=19
            
                        SectionCounter[bufintpos2].Add(tomorrow_plus)

                       
                sfsefsef=4


            for i2 in range(20):
                bufper=SectionCounter[i2].Average()
                if bufper!=0:
                    SectionCounter2[dayofweek*section3+i2].Add(bufper)
                SectionCounter[i2].Clr()

            avacounter+=1

        if(avacounter>1000):

            for ii in range(section2):
                for iii in range(section3):
                    asdad3=SectionCounter2[ii*section3+iii].Average()
                    asdad2=SectionCounter2[ii*section3+iii].Count()
                    print("%2.4f %d " % (asdad3,asdad2),end="")

                    '''
                    asdad2=SectionCounter2[ii*20+iii+iiii*5*20].Average()
                    asdad3=SectionCounter2[ii*20+iii+iiii*5*20].Count()
                    if(asdad2>0.003):
                        print("%2.4f %4d " % (asdad2+4,asdad3),end="")
                    elif(asdad2<-0.001):
                        print("%2.4f %4d " % (asdad2+9,asdad3),end="")
                    else:
                        print("%2.4f %4d " % (asdad2+1,asdad3),end="")
                    '''

                print("\n")

        sadfsef=6

def CSZL_DatebasedDayRankProp():

    cwd = os.getcwd()
    txtFileA = cwd + '\\output\\ALL_History_data_Datebased.npy'
    DateBasedList=np.load(txtFileA)

    x=DateBasedList.shape[0]    #2000
    y=DateBasedList.shape[1]    #4000
    z=DateBasedList.shape[2]    #7  

    
    #新建5个计数器用来记录5个位置的值
    SectionCounter=[]
    for ii in range(20):
        temp=Z_Counter()
        SectionCounter.append(temp)
        del temp


    section3=20
    section2=5

    SectionCounter2=[]

    for ii in range(section3*section2):
        temp=Z_Counter()
        SectionCounter2.append(temp)
        del temp

    avacounter=0



    for i in range(1,x-1):
        cur_date=DateBasedList[i,0,0]
        counter=DateBasedList[i,:,3]
        a=np.sum(counter!=0)
        if(a==0):
            continue

        todaylist=np.where(counter>0)
        todaylist2=todaylist[0]



        if(cur_date>20140101):
            #新建所有数据的空数组用于放置百分比数据
            RankList_base=np.zeros((y),dtype=float)
            #先算出每个数据的百分比
            for cur_index in todaylist2:
                code=DateBasedList[i,cur_index,6]
                last_close=DateBasedList[i-1,cur_index,3]
                cur_close=DateBasedList[i,cur_index,3]

                if(last_close==0 or cur_close==0 ):
                    continue

                today_plus=(cur_close-last_close)/last_close
                RankList_base[cur_index]=today_plus

            #找出当天有意义的数据放入待排序列表
            plus_element_list=RankList_base[todaylist2]
            #新建一个空的列表用于放置所有排序后的数据
            RankList=np.zeros((y),dtype=int)
            #将有意义数据排序并得到index值
            buf_ranklist=plus_element_list.argsort()

            #zzztest=DateBasedList[i,todaylist2[buf_ranklist[1]],6];
            #zzztest2=DateBasedList[i,todaylist2[buf_ranklist[2880]],6];

            #循环所有有意义数据并将排名值放入原列表(包含无意义值)中的对应位置
            for cur_i in range(0,buf_ranklist.shape[0]):               
                #原列表中的 在buf_ranklist的第cur_i个值对应的在todaylist2(有意义对应原列表位置)里面的位置的值是cur_i
                RankList[todaylist2[buf_ranklist[cur_i]]]=cur_i


            
            #np.set_printoptions(precision=2,suppress=True,threshold=10000)
            #print(RankList_base)
 
            #print("\n")
            #print(RankList)  

          

            for cur_index in todaylist2:
                code=DateBasedList[i,cur_index,6]
                last_close=DateBasedList[i-1,cur_index,3]
                cur_close=DateBasedList[i,cur_index,3]
                next_close=DateBasedList[i+1,cur_index,3]
                cur_rank=RankList[cur_index]
                #当日的排名0~1，为了让最大值小于1往分母加1
                cur_rank_per=float(cur_rank)/(float)(todaylist2.shape[0]+1)
                fom_per=int(cur_rank_per*20)
                #if(fom_per==10):
                    #sdfasdfasf=9

                if(last_close==0 or cur_close==0 or next_close==0):
                    continue

                today_plus=(cur_close-last_close)/last_close
                tomorrow_plus=(next_close-cur_close)/cur_close

                dy=(int)(cur_date/10000)                     
                dm=(int)((cur_date-(dy)*10000)/100)
                dd=(int)(cur_date%100)

                date_form = datetime.datetime(dy,dm ,dd , 00, 00, 00)
                dayofweek=date_form.weekday()
                
                if(today_plus<0.095 and today_plus>(-0.095) and (today_plus<0.045 or today_plus>0.055) and (today_plus<-0.055 or today_plus>-0.045)):
                    if(tomorrow_plus<0.11 and tomorrow_plus>-0.11 ):

            
                        SectionCounter[fom_per].Add(tomorrow_plus)

                       
                sfsefsef=4

            for i2 in range(20):
                bufper=SectionCounter[i2].Average()
                if bufper!=0:
                    SectionCounter2[dayofweek*section3+i2].Add(bufper)
                SectionCounter[i2].Clr()

            avacounter+=1

        if(avacounter>1000):

            for ii in range(section2):
                for iii in range(section3):
                    asdad3=SectionCounter2[ii*section3+iii].Average()
                    asdad2=SectionCounter2[ii*section3+iii].Count()
                    print("%2.4f %d " % (asdad3,asdad2),end="")

                    '''
                    asdad2=SectionCounter2[ii*20+iii+iiii*5*20].Average()
                    asdad3=SectionCounter2[ii*20+iii+iiii*5*20].Count()
                    if(asdad2>0.003):
                        print("%2.4f %4d " % (asdad2+4,asdad3),end="")
                    elif(asdad2<-0.001):
                        print("%2.4f %4d " % (asdad2+9,asdad3),end="")
                    else:
                        print("%2.4f %4d " % (asdad2+1,asdad3),end="")
                    '''

                print("\n")

        sadfsef=6

def CSZL_DatebasedVolatilityClassifyProp():

    cwd = os.getcwd()
    txtFileA = cwd + '\\output\\ALL_History_data_Datebased.npy'
    DateBasedList=np.load(txtFileA)



    x=DateBasedList.shape[0]    #2000
    y=DateBasedList.shape[1]    #4000
    z=DateBasedList.shape[2]    #7  

    
    #新建5个计数器用来记录5个位置的值
    SectionCounter=[]
    SectionCounter2=[]
    for ii in range(y):
        temp=Z_Counter()
        temp2=RankCal(20)
        SectionCounter.append(temp)
        SectionCounter2.append(temp2)
        del temp
        del temp2


    SectionCounter3=[]
    sectionnewtest=40
    for ii in range(sectionnewtest):
        temp=Z_Counter()        
        SectionCounter3.append(temp)
        del temp



    avacounter=0


    for i in range(1,x-1):
        cur_date=DateBasedList[i,0,0]
        counter=DateBasedList[i,:,3]
        a=np.sum(counter!=0)
        if(a==0):
            continue

        todaylist=np.where(counter>0)
        todaylist2=todaylist[0]



        if(cur_date>20170101):
            #新建所有数据的空数组用于放置百分比数据
            RankList_base=np.zeros((y),dtype=float)

            AVG_RankList=np.zeros((y,3),dtype=float)

            #先算出每个数据的百分比
            for cur_index in todaylist2:
                code=DateBasedList[i,cur_index,6]
                last_close=DateBasedList[i-1,cur_index,3]
                cur_close=DateBasedList[i,cur_index,3]

                if(last_close==0 or cur_close==0 ):
                    continue

                today_plus=(cur_close-last_close)/last_close
                RankList_base[cur_index]=today_plus


            #找出当天有意义的数据放入待排序列表
            plus_element_list=RankList_base[todaylist2]
            #新建一个空的列表用于放置所有排序后的数据
            RankList=np.zeros((y),dtype=int)
            #将有意义数据排序并得到index值
            buf_ranklist=plus_element_list.argsort()


            #循环所有有意义数据并将排名值放入原列表(包含无意义值)中的对应位置
            for cur_i in range(0,buf_ranklist.shape[0]):               
                #原列表中的 在buf_ranklist的第cur_i个值对应的在todaylist2(有意义对应原列表位置)里面的位置的值是cur_i
                RankList[todaylist2[buf_ranklist[cur_i]]]=cur_i


            
            testrank=RankList[1533]
            testper=int(float(testrank)/(float)(todaylist2.shape[0]+1)*20)
            testcode=DateBasedList[i,1,6]

            cur_index_counter=0

            #规定日期之内超过则不算
            if False:
                for cur_i in range(0,RankList.shape[0]):
                    if(cur_i!=todaylist2[cur_index_counter]):
                        continue

                    code=DateBasedList[i,cur_index,6]
                    last_close=DateBasedList[i-1,cur_index,3]
                    cur_close=DateBasedList[i,cur_index,3]
                    next_close=DateBasedList[i+1,cur_index,3]
                    cur_rank=RankList[cur_index]
                    #当日的排名0~1，为了让最大值小于1往分母加1
                    cur_rank_per=float(cur_rank)/(float)(todaylist2.shape[0]+1)
                    fom_per=int(cur_rank_per*20)
                    #if(fom_per==10):
                        #sdfasdfasf=9

                    if(last_close==0 or cur_close==0 or next_close==0):
                        continue

                    #differper=abs(testper-fom_per)
                    differper=fom_per-testper

                    SectionCounter[cur_index].Add(differper)
                    SectionCounter2[cur_index].Add(fom_per,differper)

                    avg=SectionCounter2[cur_index].GetAvg()

                    if(avg!=0):
                        AVG_RankList[cur_index,0]=avg
                        tomorrow_plus=(next_close-cur_close)/cur_close
                        AVG_RankList[cur_index,1]=tomorrow_plus

                        #avg=SectionCounter2[cur_index].Add(fom_per)      
                    
                    if(cur_index_counter<todaylist2.shape[0]):
                        cur_index_counter+=1

                    sfsefsef=4
            #无论如何都是20个日期排名
            else:
                for cur_index in todaylist2:

                    code=DateBasedList[i,cur_index,6]
                    last_close=DateBasedList[i-1,cur_index,3]
                    cur_close=DateBasedList[i,cur_index,3]
                    next_close=DateBasedList[i+1,cur_index,3]
                    cur_rank=RankList[cur_index]
                    #当日的排名0~1，为了让最大值小于1往分母加1
                    cur_rank_per=float(cur_rank)/(float)(todaylist2.shape[0]+1)
                    fom_per=int(cur_rank_per*20)
                    #if(fom_per==10):
                        #sdfasdfasf=9

                    if(last_close==0 or cur_close==0 or next_close==0):
                        continue

                    #differper=abs(testper-fom_per)
                    differper=fom_per-testper

                    SectionCounter[cur_index].Add(differper)
                    SectionCounter2[cur_index].Add(fom_per,differper)

                    avg=SectionCounter2[cur_index].GetAvg()
                    AVG_RankList[cur_index,2]=code

                    if(avg!=0):
                        AVG_RankList[cur_index,0]=avg
                        tomorrow_plus=(next_close-cur_close)/cur_close
                        AVG_RankList[cur_index,1]=tomorrow_plus

                        #avg=SectionCounter2[cur_index].Add(fom_per)

                
                    cur_index_counter+=1
            #         

            #新建一个空的列表用于放置所有排序后的数据
            Rank20RankList=np.zeros((y),dtype=int)

            avg_rankbuff=AVG_RankList[:,0]
            avg_rankbuff2=np.where(avg_rankbuff>0)
            avg_rankbuff2=avg_rankbuff2[0]

            buffer2all=avg_rankbuff2.shape[0]

            if(buffer2all!=0):              
                
                avg_rankbuff3=avg_rankbuff[avg_rankbuff2]
                avg_rankbuff4=avg_rankbuff3.argsort()

                
                for cur_i in range(0,buffer2all):               
                    final_index=avg_rankbuff2[avg_rankbuff4[cur_i]]
                    Rank20RankList[final_index]=cur_i

                    bufferf1=float(cur_i)/float(buffer2all+1)
                    bufferf2=int(bufferf1*sectionnewtest)
                    code=AVG_RankList[final_index,2]
                    bufferf3=AVG_RankList[final_index,1]
                    SectionCounter3[bufferf2].Add(bufferf3)
                    sdjfisjiej=8

                for iii in range(0,sectionnewtest):
                    percent=SectionCounter3[iii].Average()

                    #print("%d %d" % (Rank20RankList[iii],code))
                    print("%2.4f" % (percent))
                    SectionCounter3[iii].Clr()

                print("\n")
                dfseft=9

            avacounter+=1

        if(avacounter>200):

            for ii in range(y):
                #DateBasedList[1999,ii,6]
                code=All_K_Data[ii,0,0]
                asdad3=SectionCounter[ii].Average()
                asdad4=SectionCounter[ii].Count()
                #asdad2=SectionCounter2[ii*section3+iii].Count()
                #print("%2.4f %d " % (asdad3,code),end="")
                print("%2.4f %d %d" % (asdad3,code,asdad4))

                '''
                asdad2=SectionCounter2[ii*20+iii+iiii*5*20].Average()
                asdad3=SectionCounter2[ii*20+iii+iiii*5*20].Count()
                if(asdad2>0.003):
                    print("%2.4f %4d " % (asdad2+4,asdad3),end="")
                elif(asdad2<-0.001):
                    print("%2.4f %4d " % (asdad2+9,asdad3),end="")
                else:
                    print("%2.4f %4d " % (asdad2+1,asdad3),end="")
                '''
            asdasdhh=9

        sadfsef=6

class SectionCal(object):
    Section_max=0
    Section_min=9999

    Section_index=0
    Section_long=0

    #最后一天的指
    Section_last=0   

    #初始化统计区间
    SectionData=[]
    #计数
    SectionCounter=0

    #初始化统计区间
    def __init__(self,long):
        #code day high low
        self.SectionData=np.zeros((long,7),dtype=float)
        self.Section_long=long

    def Add(self,data):


        max_del=self.SectionData[self.Section_index,2]
        min_del=self.SectionData[self.Section_index,4]


        if max_del==self.Section_max:
            self.SectionData[self.Section_index,2]=0
            buf_section=self.SectionData[:,2]
            self.Section_max=max(buf_section)
        if min_del==self.Section_min:
            self.SectionData[self.Section_index,4]=9999
            buf_section=self.SectionData[:,4]
            self.Section_min=min(buf_section)    


        i=0
        #将输入数据完整复制
        for singledata in data:           
            self.SectionData[self.Section_index,i]=singledata
            i+=1

        self.Section_last=self.SectionData[self.Section_index,3]
        #更新最大值
        if self.SectionData[self.Section_index,2]>self.Section_max:
            self.Section_max=self.SectionData[self.Section_index,2]
        #更新最小值
        if self.SectionData[self.Section_index,4]<self.Section_min:
            self.Section_min=self.SectionData[self.Section_index,4]


        if self.Section_index>=(self.Section_long-1):
            self.Section_index=0
        else:
            self.Section_index+=1

        self.SectionCounter+=1

    def GetPos(self):
        sectionall=self.Section_max-self.Section_min
        if self.Section_last!=0 and sectionall!=0 and self.SectionCounter>self.Section_long:
            return (self.Section_last-self.Section_min)/(sectionall)
        else:
            return 0

    def Max(self):
        return self.Section_max
    def Min(self):
        return self.Section_min
    def Count(self):
        return self.SectionCounter

class RankCal(object):


    Section_index=0
    Section_long=0


    #平均值
    Section_average=0     

    #初始化统计区间
    SectionData=[]
    #计数
    SectionCounter=0

    #初始化统计区间
    def __init__(self,long):
        #code rank
        self.SectionData=np.zeros((long,3),dtype=float)
        self.Section_long=long

    def Add(self,rank,rank2):

        self.SectionData[self.Section_index,1]=rank
        self.SectionData[self.Section_index,2]=rank2
        


        if self.Section_index>=(self.Section_long-1):
            self.Section_index=0
        else:
            self.Section_index+=1

        self.SectionCounter+=1

    def GetAvg(self):
        bufferavg=self.SectionData[:,1]
        self.Section_average=np.sum(bufferavg)/self.Section_long
        

        if self.SectionCounter>=self.Section_long:
            return self.Section_average
        else:
            return 0

    def GetAvg2(self):
        bufferavg=self.SectionData[:,2]
        self.Section_average=np.sum(bufferavg)/self.Section_long
        

        if self.SectionCounter>=self.Section_long:
            return self.Section_average
        else:
            return 0

    def Count(self):
        return self.SectionCounter

def pos_cal(high ,low ,now):
    try:
        if(low>60000 or high<0.1):
            per=-1
            return per
        per=(now-low)/(high-low)
    except Exception as ex:
        per=0

    return per
    

class Z_Counter(object):
    inner_counter=0
    inner_sum=0

    #def __init__(self):
        #pass

    def Add(self,num=0):
        self.inner_sum+=num
        self.inner_counter+=1
    def Sum(self):
        return self.inner_sum
    def Average(self):
        if(self.inner_counter!=0):
            return self.inner_sum/self.inner_counter
        return (0)

    def Count(self):
        return self.inner_counter

    def Clr(self):
        self.inner_counter=0
        self.inner_sum=0


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



def CSZL_TrainDataSave():

    global All_K_Data
    global PosProp

    #no code value1 value2 value3 Allavg 666avg 166avg 
    HisAna=np.zeros((4000,8),dtype=float)

    for z in range(4000):
        HisAna[z,0]=z
        HisAna[z,1]=All_K_Data[z,0,0]
        HisAna[z,5]=PosProp[z,9]     #当前位置相对于历史位置
        HisAna[z,6]=PosProp[z,10]     #当前位置相对于666日位置
        HisAna[z,7]=PosProp[z,11]     #当前位置相对于166日位置



    cwd = os.getcwd()
    #now=datetime.datetime.now()
    #now=now.strftime('%Y%m%d')

    txtFileA = cwd + '\\output\\HisAna.npy'
    np.save(txtFileA, HisAna)


def CSZL_SecAnalyseNew():
    '''
    使用secdata的逻辑


    '''    


    #开始更新sec逻辑
    SecUse=False
    SecUseB=True

    if SecUse:
        #从Secdata中读取文件
        #获取目录下所有文件
        cwd = os.getcwd()
        file_dir = cwd + '\\data\\secret\\A'
    
        for root, dirs,files in os.walk(file_dir):
            L=[]
            for file in files:  
                if os.path.splitext(file)[1] == '.npy':  
                    L.append(os.path.join(root, file))

        #遍历所有文件
        for z_file in L:

            #试试我的正则功力
            nums = re.findall(r"secretA(\d+).",z_file)
            if(nums!=[]):
                cur_date=float(nums[0])
            else:
                continue
            if cur_date==20180419:

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
                    if SecLoaded[(i,0,0)]==603937:

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

    if SecUseB:
        #从Secdata中读取文件
        #获取目录下所有文件
        cwd = os.getcwd()
        file_dir = cwd + '\\data\\secret\\B'
    
        for root, dirs,files in os.walk(file_dir):
            L=[]
            for file in files:  
                if os.path.splitext(file)[1] == '.npy':  
                    L.append(os.path.join(root, file))

        #遍历所有文件
        for z_file in L:

            #试试我的正则功力
            nums = re.findall(r"secretB(\d+).",z_file)
            if(nums!=[]):
                cur_date=float(nums[0])
            else:
                continue
            if cur_date==20180420:

                SecLoaded=np.load(z_file)


                x=SecLoaded.shape[0]    
                y=SecLoaded.shape[1]    #270

                for i in range(x):

                    if SecLoaded[(i,2)]==300537:

                        for ii in range(y):

                            print("%6.2f " % SecLoaded[(i,ii)],end="")
                        print("\n")


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


def CSZL_TrainMainNEW(g_all_resultin):
    #global DataRecord
    global g_all_result
    global All_K_Data
    global LongProp

    CSZL_Sorttest()

    #初始化g_all_result
    g_all_result=g_all_resultin

    #初始化训练周期
    TrainDate=CSZL_TrainInitNEW()

    CSZL_DatebasedVolatilityClassifyProp()

    #改为以date计算的list
    CSZL_CodelistToDatelist()

    #初始化位置属性
    CSZL_PosProp()

    CSZL_TrainDataSave()

    #初始化长期属性
    CSZL_LongProp()
    #start_time = time.time()
    #初始化短期属性
    CSZL_ShortProp()

    CSZL_SecAnalyseNew()
    #TrainInput_test(ShortProp)

    A,B=CSZL_TrainValueCalNEW(LongProp,ShortProp)




    CSZL_TrainDataSave()


    #print('函数执行完毕,用时:%sms' % ((time.time()-start_time)*1000))
    zzzz=1


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
