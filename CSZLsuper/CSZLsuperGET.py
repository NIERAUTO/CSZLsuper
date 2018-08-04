#coding=utf-8

import CSZLsuper
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

import ctypes
import CSZLsuperTrain

#序列化和反序列化
import pickle,pprint


z_init_nplist=[]
g_all_result=[] #实时全局数据表
g_part_result=[]
g_all_info=[]   #全局信息表

#常时数据采集结构
SecretData_A=[]
#特殊数据采集结构
SecretData_B=[]

KtypeThreeLoaded=[]


g_list_update_index=0   #全局更新数据位置
g_exit_flag=True
update_start=False
csharp_display_mode=True

#错误信息打印，暂时没用
log_save_flag=True

#初始化全局时间
CurHour=int(time.strftime("%H", time.localtime()))
CurMinute=int(time.strftime("%M", time.localtime()))


#所有的用于cmd信息输出的变量

INFO_all_routine=0  #1代表线程正常 -1代表线程异常 0代表线程等待
INFO_part_routine=0 #1代表线程正常 -1代表线程异常 0代表线程等待


#装饰器用于计算函数执行时间
def CSZL_log(arg):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if arg != func:
                start_time = time.time()
                print('%s %s():' % (arg, func.__name__))
                result=func(*args, **kw)
                print('函数执行完毕,用时:%sms' % ((time.time()-start_time)*1000))
                return result
            else:
                start_time = time.time()
                print('Execute %s():' % ( func.__name__))
                result=func(*args, **kw)
                print('函数执行完毕,用时:%sms' % ((time.time()-start_time)*1000))
                return result
        return wrapper
    if isinstance(arg, str): 
        return decorator
    else:
        return decorator(arg)


def Z_EXIT():
    """
    todo之后可能会用class来实现退出
    """
    global g_exit_flag
    g_exit_flag=False

    CSZL_SecretDataSave()



def Z_LOG_SAVE(savefname,wrongmessage):
    """
    保存错误信息
    """
    global log_save_flag

    if True:
        log_save_flag=False

        cwd = os.getcwd()

        txtFile1 = cwd + '\\log\\'+savefname
        '''
        if os.path.exists(savefname):
            print ("Error:'%s' already exists" %savefname)
        '''
        #下面两句才是最重点。。。。也即open函数在打开目录中进行检查，如果有则打开，否则新建
        fobj=open(txtFile1,'a')
        fobj.write('\n'+wrongmessage)
        fobj.close()

        log_save_flag=True

def Z_AvailableJudge(zzz):
    """
    数据可靠性检测
    """

    if(zzz==""):
        return (-1)

    return zzz

def CSZL_superINFOupdate():
    """
    CMD界面显示/保存数据为txt文件给显示用c#程序读取
    """

    global g_exit_flag

    global INFO_all_routine
    global g_list_update_index

    global INFO_part_routine

    global g_part_result

    

    print("INFO DISPLAY START")
    time.sleep(2)   

    wrong_counter=0;
    while g_exit_flag:
        os.system('cls')
        try:
            print ("CSZLsuper running at %s \n" % ( time.ctime(time.time())))

            if INFO_all_routine==1:
                print ("ALLroutine : Runing")
            elif INFO_all_routine==(-1):
                print ("ALLroutine : Wrong")
            else:
                print ("ALLroutine : Waiting")
            print("更新队列：%d个\n"%(g_list_update_index))

            if INFO_part_routine==1:

                cur_long=np.alen(g_part_result)

                print ("PARTroutine : Runing")

                if csharp_display_mode:
                    try:
                        cwd = os.getcwd()
                        txtFile1 = cwd + '\\log\\display.txt'
                        '''
                        if os.path.exists(savefname):
                            print ("Error:'%s' already exists" %savefname)
                        '''
                        #下面两句才是最重点。。。。也即open函数在打开目录中进行检查，如果有则打开，否则新建
                        fobj=open(txtFile1,'w')
                        for i in range(cur_long-1):
                            buff_all_index=g_part_result[cur_long-1-i]['s_key']
                            
                            testt=("%d,%s,%s,%f,%d,%f,%d,%d,%d,%d,%f,%f\n"%(i+1,
                            str(g_part_result[cur_long-1-i]['s_Cname'],"utf-8"),
                            str(g_part_result[cur_long-1-i]['s_code'],"utf-8"),
                            g_part_result[cur_long-1-i]['s_zValue'],
                            (g_all_info[buff_all_index]['s_HisOutput1']*10000),
                            #g_all_info[buff_all_index]['K_three_amount'],
                            g_part_result[cur_long-1-i]['s_now'],                            
                            g_all_info[buff_all_index]['K_three_super'],
                            g_all_info[buff_all_index]['K_three_superwrong'],
                            g_part_result[cur_long-1-i]['s_curztype'],
                            g_all_info[buff_all_index]['s_RP'],
                            g_all_info[buff_all_index]['s_Posof666'],
                            g_all_info[buff_all_index]['s_Posof166']
                            ))
                            fobj.write(testt)

                        fobj.close()
                    except:
                        wrong_counter+=1

                else:
                    if(cur_long>1):
                        for i in range(cur_long-1):
                            buff_all_index=g_part_result[cur_long-1-i]['s_key']

                            print("NO%d:%s %s with score %f,战力：%d 准确率：%d 超神次数：%d 超鬼次数：%d 今日形态：%d RP值：%d 466日位置：%f 166日位置：%f\n"%(i+1,
                            str(g_part_result[cur_long-1-i]['s_Cname'],"utf-8"),
                            str(g_part_result[cur_long-1-i]['s_code'],"utf-8"),
                            g_part_result[cur_long-1-i]['s_zValue'],
                            (g_all_info[buff_all_index]['s_HisOutput1']*10000),
                            g_all_info[buff_all_index]['K_three_amount'],
                            g_all_info[buff_all_index]['K_three_super'],
                            g_all_info[buff_all_index]['K_three_superwrong'],
                            g_part_result[cur_long-1-i]['s_curztype'],
                            g_all_info[buff_all_index]['s_RP'],
                            g_all_info[buff_all_index]['s_Posof666'],
                            g_all_info[buff_all_index]['s_Posof166']
                            ))
                            #print("NO%d:%s %s with score %f \n"%(i+1,str(g_part_result[cur_long-1-i]['s_Cname'],"utf-8"),str(g_part_result[cur_long-1-i]['s_code'],"utf-8"),g_part_result[cur_long-1-i]['s_zValue']))





            elif INFO_part_routine==(-1):
                print ("PARTroutine : Wrong")
            else:
                print ("PARTroutine : Waiting")


        except Exception as ex:
            print (Exception,":",ex)
        
        time.sleep(0.5)
    return 0

    '''
    global g_all_analyse_result

    cur_counter=0
    for cur_stock_info in g_all_analyse_result['name']:
        buff_a=float(g_all_analyse_result['bid'][cur_counter])
        buff_b=float(g_all_analyse_result['pre_close'][cur_counter])
        buff_c= (buff_a-buff_b)/buff_b
        if buff_c>0.05:
            buff_d=0
        cur_counter+=1
    '''
def get_cszl_index(result_list):
    return result_list["s_key"]



def CSZL_superinit():
    '''
    全局初始化
    可以从网络重新初始化
    初始化的表包括:
    
    g_all_result
    g_all_info
    g_part_result

    '''

    global g_all_result
    global g_part_result
    global g_exit_flag
    global g_list_update_index
    global g_all_info
    global z_init_nplist


    #初始化选项
    
    if(CSZLsuper.G_mode['InitListUpdateModeFlag']):
        CurDatalistCreate()


    #======初始化总得到的数据 g_all_result======#
    #初始化typedef s_high
    z_useful_stock_type=np.dtype(([('s_key', int), ('s_code', 'S6'), ('s_plus', float),('s_now', float),
    ('s_last', float),('s_high', float),('s_low', float),
    ('s_stflag', float),('K_three_amount', float),('K_three_super', float),('K_three_superwrong', float),('s_open', float),
    ('s_2dayagetype', float),('s_1dayagetype', float),('s_curztype', float),('s_RP', float),('s_b5', float),
    ('s_vol', float),('s_wholecap', float),('s_mktcap', float),('s_HisOutput1', float),
    ('s_InFastUpdataList', int),('s_counter', int),('s_useful', int),('s_zValue', float),
    ('s_UpdateHour', int),('s_UpdateMinute', int),('s_ReachedHour', int),('s_ReachedMinute', int),
    ('s_ReachedFlag', int),('s_ReachedPrice', float),('s_Buy', int),('s_Cname', 'S40'),
    ('s_per', float),('s_pb', float),('s_turnoverratio', float),('s_Posofall', float),
    ('s_Posof666', float),('s_Posof166', float),('s_Posof5', float)
    ]))
    #新建空结构体元素
    z_stock_empty_value = [(0, '000000',0,3,
    4,5,6,
    7,8,9,10,11,
    12,13,14,15,16,
    17,18,-19,20,
    21,22,23,-24,
    25,26,27,28,
    29,30,31,'----',
    33,34,35,36,
    37,38,39)]

    #新建使用空结构体新建np节点
    z_init_nplist = np.array(z_stock_empty_value, dtype=z_useful_stock_type)
    #使用空元素初始化g_all_list(np型的)
    g_all_result = z_init_nplist.copy() 

    #print (z_init_nplist)

    '''
    #UNDEFINE1226
    #从文档中初始化g_all_list
    #初始化文档路径
    cwd = os.getcwd()
    All_list_sourcepath=cwd+'\\data\\'+'listtest.txt'

    zf=open(All_list_sourcepath)
    #对于文档每行读取
    for lines in zf.readlines():
        #先复制个空的np节点
        z_temp_nplist = z_init_nplist.copy()
        #填充此np节点
        z_temp_nplist['s_key']=int(lines.split()[0])
        z_temp_nplist['s_code']=str(lines.split()[1])
        z_temp_nplist['s_mktcap']=str(lines.split()[2])

        #将次节点更新到 g_all_result
        g_all_result=np.concatenate((g_all_result,z_temp_nplist),axis=0)
        
    zf.close()
    '''
    #直接从tushare保存的csv中初始化数据

    cwd = os.getcwd()
    txtFile = cwd + '\\data\\'+'today_all_data.csv'

    buff_dr_result=pd.read_csv(txtFile,encoding= 'gbk')

    #print(buff_dr_result)

    for i in range(len(buff_dr_result['code'])):
        z_temp_nplist = z_init_nplist.copy()

        z_temp_nplist['s_key']=str(i+1)
        z_temp_nplist['s_code']=str(buff_dr_result['code'][i]).zfill(6)
        z_temp_nplist['s_mktcap']=buff_dr_result['mktcap'][i]
        z_temp_nplist['s_per']=buff_dr_result['per'][i]
        z_temp_nplist['s_pb']=buff_dr_result['pb'][i]
        z_temp_nplist['s_turnoverratio']=buff_dr_result['turnoverratio'][i]
        z_temp_nplist['s_Cname']=buff_dr_result['name'][i].encode("utf-8")

        #判断是否是st
        zzz=str(z_temp_nplist['s_Cname'][0],"utf-8")    
        if(zzz[1]=='T'):
            z_temp_nplist['s_stflag']=1
        elif(zzz[1]=='S'or zzz[1]=='*'or zzz[0]=='S'):
            z_temp_nplist['s_stflag']=2
        else:
            z_temp_nplist['s_stflag']=0                 

        g_all_result=np.concatenate((g_all_result,z_temp_nplist),axis=0)


    #全局信息数组就放在这个数组里面，allroutine不负责更新后面的信息模块，之所以并在一起是想省力
    g_all_info=g_all_result.copy()

    #print(g_all_result) 用于测试

    #======初始化重点观察的数据 g_part_list======#

    #使用空元素初始化g_part_list(np型的)
    g_part_result = z_init_nplist.copy()      

    #======初始化线程计数======#
    g_list_update_index=1

    #======初始化线程退出flag g_exit_flag======#
    g_exit_flag=True

    #======初始化重要数据======#
    CSZL_SecretDataInit()

    BotInit()

    return g_all_result

def CurDatalistCreate():
    """
    初始化当前更新列表
    
    
    """

    #todo 加个错误处理
    buff_dr_result=ts.get_today_all()

    cwd = os.getcwd()
    txtFile = cwd + '\\data\\'+'today_all_data.csv'
    buff_dr_result.to_csv(txtFile)


    '''
    #UNDEFINE1226
    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'initlist.txt'

    with open(txtFile1,'w') as fobj:
    
        i=0

        for singleinfo in buff_dr_result['code']:
        
            temp1=str(i+1)
            temp2=str(buff_dr_result['code'][i]).zfill(6)
            temp3=buff_dr_result['mktcap'][i]
            temp4=buff_dr_result['per'][i]
            temp5=buff_dr_result['pb'][i]
            temp6=buff_dr_result['turnoverratio'][i]      

            tempall=str(temp1)+'\t'+str(temp2)+'\t'+str(temp3)+'\t'+str(temp4)+'\t'+str(temp5)+'\t'+str(temp6)
        
            if(i==0):
                fobj.write(tempall)
            else:
                fobj.write('\n'+tempall)
        
            i=i+1
    '''


def CSZL_superGETAllroutine():
 
    global g_list_update_index
    global g_all_result
    global g_exit_flag
    global update_start
    #真正多线程时候这里可能会出问题
    global g_all_info

    global INFO_all_routine

    #一次更新的数量初始化为30(为了配合tushare)，当发生剩余更新量较少的情况时，减少本次更新量
    update_rate=30
    update_cur=update_rate
    
    #初始化复制缓存数组
    buff_result=[]
    #初始化更新计数器
    update_counter=1

    #如果不收到退出flag就无限循环
    while g_exit_flag:
        
        if(CSZL_ExitCheck()):
            #保存普通数据
            CSZL_CurDataOutput()
            #保存重要数据
            CSZL_SecretDataSave()
            g_exit_flag=False
        if (CSZL_TimeCheck()):

            try:
                #接收global数据(先不带防碰撞了)
                buff_result=g_all_result.copy()

                #生产list总数
                list_max=np.alen(buff_result)

                #初始化缓存传入数组
                update_buff_arr=[]

                #根据g_list_update_index更新传入数组
                for i in range(update_cur):
                    #temp=str(buff_result[g_list_update_index+i]['s_code']).zfill(6)    #用于转化扩展字符，但是现在使用obj类型不需要了
                    
                    temp=str(buff_result[g_list_update_index+i]['s_code'],"utf-8")
                    update_buff_arr.append(temp)

                #使用tushare接收数据
                buff_dr_result = ts.get_realtime_quotes(update_buff_arr)

  
                #将tushare的信息转换为我的格式
                CSZL_TypeChange(buff_result,buff_dr_result,update_cur,g_list_update_index,update_counter)
                CSZL_INFOUpdate(g_all_info,buff_result,update_cur,g_list_update_index)

                #CSZL_Kanalyseupdate(g_all_info,update_cur,g_list_update_index)
                #隐藏信息更新
                CSZL_SecretData_A_Update(buff_dr_result,update_cur,g_list_update_index)

                #数据指针更新
                g_list_update_index+=update_cur

                #如果下次更新量将要超过总数
                if (g_list_update_index+update_cur)>=list_max:
                    update_cur=list_max-g_list_update_index
                    #如果现在已经是最后一个数据
                    if g_list_update_index==list_max:
                        #总更新次数自加
                        update_counter+=1
                        g_list_update_index=1
                        update_cur=update_rate
                        update_start=True

            

                #===更新全局list===
                g_all_result=buff_result.copy()
        
                #===成功信息更新===

                INFO_all_routine=1
            

            except Exception as ex:
                INFO_all_routine=-1                
                wrongmessage="Allroutine FAIL at : %s \n" % ( time.ctime(time.time()))

                wrongEx=str(ex)
                Z_LOG_SAVE('AllWrongMessage.txt',wrongmessage+wrongEx)
                print (Exception,":",ex)

        else:
            INFO_all_routine=0


        sleeptime=random.randint(50,99)
        time.sleep(sleeptime/200)      

def CSZL_superAnalysePARTroutine():

    #先等全局更新线程一会儿
    time.sleep(5)

    global g_all_result
    global g_part_result
    global g_exit_flag
    global g_all_info
    #用于初始化的节点
    global z_init_nplist

    #在all滚完一次以后再执行
    global update_start

    global INFO_part_routine

    #part最多观察数量为20
    PART_LIST_MAX=20
    

    #如果退出flag被置就退出
    while g_exit_flag:
        
        if (CSZL_TimeCheck() and update_start or CSZLsuper.G_mode['RoutineTestFlag']):
        #if (CSZL_TimeCheck() ):
        
            try:
                #先吧原part_list的数据拿过来
                buff_part_result=g_part_result.copy()

                #得到part_result总长度
                part_list_cur=np.alen(buff_part_result)

                #如果列表大于20还是只更新20个(这里应该走不到)
                if part_list_cur>21:
                    part_list_cur=21

                #如果原来列表不是空那么先刷新原来列表中的数据
                if part_list_cur!=1:

                    #初始化缓存传入数组
                    update_buff_arr2=[]
                    #生成tushare输入的格式
                    for i in range(part_list_cur-1):
                        #temp=str(buff_part_result[1+i]['s_code']).zfill(6)
                        temp=str(buff_part_result[1+i]['s_code'],"utf-8")
                        update_buff_arr2.append(temp)

                    #使用tushare接收数据
                    buff_dr_result = ts.get_realtime_quotes(update_buff_arr2)

                    #将tushare的信息转换为我的格式
                    CSZL_TypeChange(buff_part_result,buff_dr_result,part_list_cur-1,update_index=1)
                    CSZL_partINFOUpdate(g_all_info,buff_part_result,part_list_cur-1,update_index=1)

                    #刷新特殊数据采集结构
                    CSZL_SecretData_B_Update(buff_dr_result,(part_list_cur-1))

                    #重新计算value
                    for i in range(part_list_cur-1):
                        #temp=str(buff_part_result[1+i]['s_code']).zfill(6)
                        all_index=buff_part_result[i+1]['s_key']
                        buff_part_result[i+1]['s_zValue']=CSZL_ValueCal(buff_part_result[i+1],g_all_info[all_index])


                #再吧新的all_list的数据拿过来
                buff_all_result=g_all_result.copy()

                #得到all_list的长度
                all_list_max=np.alen(buff_all_result)

                #从all_list中查找满足条件且不在part_list中的数据      
                for i in range(all_list_max-1):
                    #计算当前值
                    buff_all_result[i+1]['s_zValue']=CSZL_ValueCal(buff_all_result[i+1],g_all_info[i+1])
                    
                    cur_status=g_all_info[i+1]['s_InFastUpdataList']

                    #如果这个票的状态不是1
                    if (cur_status!=1 and cur_status!=3): 
                        if buff_all_result[i+1]['s_zValue']>4.5 :


                            z_temp_nplist = z_init_nplist.copy()
                            z_temp_nplist[0]=buff_all_result[i+1].copy()
                            buff_part_result=np.concatenate((buff_part_result,z_temp_nplist),axis=0)



        
                #将结果排序
                buff_hightolow=np.sort(buff_part_result, order='s_zValue')

                cur_long=np.alen(buff_part_result)

                #第二次筛选，筛选前20名踢出后超过20名的
                if cur_long >21:
                    for i in range(cur_long-21):
                        #超过20个的一个找到
                        cur_key=buff_hightolow[1]['s_key']
                        #如果这个原来是状态1那么就变成状态3，否则是状态2
                        if(g_all_info[cur_key]['s_InFastUpdataList']==1):
                            g_all_info[cur_key]['s_InFastUpdataList']=3
                        else:
                            g_all_info[cur_key]['s_InFastUpdataList']=2

                        #从列表中删掉
                        buff_hightolow=np.delete(buff_hightolow,1,axis=0)

                    #保证列表最大为21
                    cur_long=21

                for i in range(1,cur_long):

                    cur_key=buff_hightolow[i]['s_key']

                    g_all_info[cur_key]['s_InFastUpdataList']=1

                    if(g_all_info[cur_key]['s_ReachedFlag']!=1):
                        g_all_info[cur_key]['s_ReachedFlag']=1
                        g_all_info[cur_key]['s_ReachedPrice']=buff_hightolow[i]['s_now']
                        g_all_info[cur_key]['s_ReachedHour']=buff_hightolow[i]['s_UpdateHour']
                        g_all_info[cur_key]['s_ReachedMinute']=buff_hightolow[i]['s_UpdateMinute']

                        #g_all_info[cur_key]['s_Buy']=???

                #np.set_printoptions(precision=2,suppress=True)
                #print(buff_hightolow)
 

                #===更新全局partlist===
                g_part_result=buff_hightolow.copy()

                #正确信息打印
                INFO_part_routine=1


            #如果出错
            except Exception as ex:
                wrongmessage="PARTroutine FAIL at : %s \n" % ( time.ctime(time.time()))
                #print (wrongmessage)
                INFO_part_routine=-1
                wrongEx=str(ex)
                Z_LOG_SAVE('PARTWrongMessage.txt',wrongmessage+wrongEx)
                print (Exception,":",ex)

        else:
            INFO_part_routine=0
            #print ('Waiting......\n')

        sleeptime=random.randint(60,79)
        time.sleep(sleeptime/40)    
    
    return 0

def CSZL_ValueCal(StockResult,StockINFO):

    #cur_plus=StockResult['s_plus']
    cur_price=StockResult['s_now']
    cur_high=StockResult['s_high']
    cur_mktcap=StockResult['s_mktcap']
    cur_zdl=StockINFO['s_HisOutput1']
    cur_RP=StockINFO['s_RP']
    cur_pos=StockINFO['s_Posofall']
    cur_ztype=StockResult['s_curztype']

    LastValue=0


    if(cur_price==0):
        return LastValue
    
    if ((cur_high-cur_price)/cur_price)>0.01:
        LastValue-=0.75


    if ((-9.4)<StockResult['s_plus']<(-2)):
        #LastValue-=StockResult['s_plus']
        LastValue+=2
        if(cur_pos<0.2):
            LastValue+=4
    if(cur_ztype==9):
        LastValue+=2

        '''
        if (cur_mktcap<500000):
            LastValue+=2
        elif(cur_mktcap<1000000):
            LastValue+=cur_mktcap/500000*3
        elif(cur_mktcap<2000000):
            LastValue+=1
        elif(cur_mktcap<5000000):
            LastValue-=1
        elif(cur_mktcap>=5000000):
            LastValue-=2
        '''
    LastValue+=(cur_RP-60)/20

    LastValue+=cur_zdl*100

    if(StockResult['s_stflag']!=0):
        LastValue-=4

    return LastValue

#@CSZL_log
def CSZL_TypeChange(z_type_result,tushare_result,date_max,update_index=1,s_counter=0):
    """
    类型转换(我的type, tushare的type, 总共要更新几个数据, 更新的index,计数器)
    

    """
    global CurHour
    global CurMinute    #todo这里要改成直接用接收时间


    for i in range(date_max):
        try:
            #zstring=buff_result[g_list_update_index+i]['s_code']
            z_type_result[update_index+i]['s_counter']=s_counter
            #z_type_result[update_index+i]['s_UpdateFlag']=1
            
            h,m,s = tushare_result['time'][i].strip().split(":")

            receive_time=int(h)*10000+int(m)*100+int(s)
            #这里还需要考虑一下暂时先这样改180417
            if(receive_time<92600 or tushare_result['price'][i]==""):
                if(tushare_result['b1_v'][i]!=""):
                    z_type_result[update_index+i]['s_now']=tushare_result['b1_p'][i]
                else:
                    z_type_result[update_index+i]['s_now']=tushare_result['pre_close'][i]


                z_type_result[update_index+i]['s_high']=z_type_result[update_index+i]['s_now']
                z_type_result[update_index+i]['s_low']=z_type_result[update_index+i]['s_now']
                z_type_result[update_index+i]['s_open']=z_type_result[update_index+i]['s_now']
            else:

                z_type_result[update_index+i]['s_now']=tushare_result['price'][i]
                z_type_result[update_index+i]['s_high']=tushare_result['high'][i]
                z_type_result[update_index+i]['s_low']=tushare_result['low'][i]
                z_type_result[update_index+i]['s_open']=tushare_result['open'][i]

            z_type_result[update_index+i]['s_last']=tushare_result['pre_close'][i]

            #这里有bug似乎
            z_type_result[update_index+i]['s_Cname']=tushare_result['name'][i].encode("utf-8") 

            z_type_result[update_index+i]['s_UpdateHour']=CurHour
            z_type_result[update_index+i]['s_UpdateMinute']=CurMinute


            z_type_result[update_index+i]['s_curztype']=k_type_def2(z_type_result[update_index+i]['s_open'],z_type_result[update_index+i]['s_high'],z_type_result[update_index+i]['s_now'],z_type_result[update_index+i]['s_low'])
            #ztest222=float(1000000)/(float(tushare_result['price'][i])*z_type_result[update_index+i]['s_wholecap']+1)

            #z_type_result[update_index+i]['s_mktcap']=(float(tushare_result['price'][i])*z_type_result[update_index+i]['s_wholecap'])


            '''
            if z_type_result[update_index+i]['s_wholecap']==0:
                z_type_result[update_index+i]['s_mktcap']=0
            else:
                z_type_result[update_index+i]['s_mktcap']=1000000/(float(tushare_result['price'][i])*z_type_result[update_index+i]['s_wholecap']+1)
            '''

            if z_type_result[update_index+i]['s_now']==0 or z_type_result[update_index+i]['s_last']==0:
                z_type_result[update_index+i]['s_plus']=0
            else:
                z_type_result[update_index+i]['s_plus']=((z_type_result[update_index+i]['s_now']-z_type_result[update_index+i]['s_last'])/z_type_result[update_index+i]['s_last'])*100




        except Exception as ex:
            #print (Exception,":",ex)
            wrongEx=str(ex)
            #Z_LOG_SAVE('TypeChangeWrongMessage.txt',wrongmessage+wrongEx)

def CSZL_INFOUpdate(z_info_source,z_result_source,date_max,update_index=1):
    """
    将被剔除的3状态成员，变回普通成员
    
    加入g_info转换
    """

    for i in range(date_max):
        try:
            if(z_info_source[update_index+i]['s_InFastUpdataList']==3):
                z_info_source[update_index+i]['s_InFastUpdataList']=0
            CSZL_Kanalyseupdate(z_info_source[update_index+i],z_result_source[update_index+i])

        except Exception as ex:
            #print (Exception,":",ex)
            wrongEx=str(ex)
            #Z_LOG_SAVE('TypeChangeWrongMessage.txt',wrongmessage+wrongEx)
def CSZL_partINFOUpdate(z_info_source,z_result_source,date_max,update_index=1):
    """
    g_info更新
    
    ('s_stflag', float),('K_three_amount', float),('K_three_super', float),('K_three_superwrong', float),('s_open', float),
    ('s_2dayagetype', float),('s_1dayagetype', float),('s_curztype
    """

    for i in range(date_max):
        try:
            buff_g_index=z_result_source[update_index+i]['s_key']

            CSZL_Kanalyseupdate(z_info_source[buff_g_index],z_result_source[update_index+i])

        except Exception as ex:
            #print (Exception,":",ex)
            wrongEx=str(ex)
            #Z_LOG_SAVE('TypeChangeWrongMessage.txt',wrongmessage+wrongEx)

def CSZL_Kanalyseupdate(z_info_source,z_result_source):
    global KtypeThreeLoaded

    try:

        twodasage=int(z_info_source['s_2dayagetype'])
        onedasage=int(z_info_source['s_1dayagetype'])
        today=int(z_result_source['s_curztype'])
        '''
        if(z_info_source['s_code']=='603880'):
            sdfefs=4
        if(onedasage==13):
            sdfefs=4
        '''
        if(KtypeThreeLoaded[twodasage,onedasage,today,0]!=0):
            z_info_source['K_three_amount']=KtypeThreeLoaded[twodasage,onedasage,today,0]
            z_info_source['K_three_super']=KtypeThreeLoaded[twodasage,onedasage,today,5]
            z_info_source['K_three_superwrong']=KtypeThreeLoaded[twodasage,onedasage,today,7]
            z_info_source['s_HisOutput1']=KtypeThreeLoaded[twodasage,onedasage,today,1]/KtypeThreeLoaded[twodasage,onedasage,today,0]
        else:
            z_info_source['K_three_amount']=0
            z_info_source['K_three_super']=0
            z_info_source['K_three_superwrong']=0
            z_info_source['s_HisOutput1']=0

    except Exception as ex:
        print (Exception,":",ex)
        wrongEx=str(ex)
        #Z_LOG_SAVE('TypeChangeWrongMessage.txt',wrongmessage+wrongEx)


def CSZL_TimeCheck():
    global CurHour
    global CurMinute



    CurHour=int(time.strftime("%H", time.localtime()))
    CurMinute=int(time.strftime("%M", time.localtime()))

    caltemp=CurHour*100+CurMinute

    #return True

    if (caltemp>=915 and caltemp<=1132) or (caltemp>=1300 and caltemp<=1503) or CSZLsuper.G_mode['RoutineTestFlag']:
        return True
    else:
        return False        

def CSZL_ExitCheck():
    global CurHour
    global CurMinute


    CurHour=int(time.strftime("%H", time.localtime()))
    CurMinute=int(time.strftime("%M", time.localtime()))

    caltemp=CurHour*100+CurMinute


    if (caltemp>=1507 and caltemp<=1510):
        return True
    else:
        return False   


#@CSZL_log
def CSZL_HistoryDataAnalysis():
    """
    历史数据分析
    """

    global g_all_info
    global g_all_result
    global KtypeThreeLoaded

    cwd = os.getcwd()
    #初始化历史数据
    
    #测试数据准确性
    #z_three_test()

    if(CSZLsuper.G_mode['K_Data_UpdateModeFlag']):

        #获取历史数据
        #HistoryDataGet(Datas=2000,Path='ALL_History_data')
        #默认获取20天的数据
        HistoryDataGet()
        #CSZLsuperGET.HistoryDataGet("2017-04-04",10)
        #HistoryDataInit()

        #读取刚刚更新的20日内的k线数据
        
        TempPath = cwd + '\\data\\'+'History_data.npy'
        Last20_K_Data=np.load(TempPath)

        CSZL_CodelistToDatelist2(Last20_K_Data)
        

    #读取历史分析的k线模块数据
    TempPath = cwd + '\\output\\KtypeThree.npy'
    KtypeThreeLoaded=np.load(TempPath)

    #读取刚刚更新的20日内的k线数据
    TempPath = cwd + '\\data\\'+'History_data.npy'
    Last20_K_Data=np.load(TempPath)

    #读取长策略和短策略联合得出的分析结果
    TempPath = cwd + '\\output\\'+'HisAna.npy'
    HistoryAnaLoaded=np.load(TempPath)

    #CSZL_CodelistToDatelist2(Last20_K_Data)
    TempPath = cwd + '\\data\\History_data_Datebased.npy'
    Last20_K_Data_DateBased=np.load(TempPath)
    CSZL_DatebasedVolatilityClassifyProp2(Last20_K_Data_DateBased)

    #将读取的历史分析数据和进20日数据进行匹配分析

    x=len(g_all_result)         #4000
    y=Last20_K_Data.shape[1]    #7
    z=Last20_K_Data.shape[2]    #天数

    now=datetime.datetime.now()
    now=int(now.strftime('%Y%m%d'))   
    random.seed(now)

    for i in range(len(g_all_result)):
        try:
            temp=str(g_all_result[i]['s_code'],"utf-8")
            zzz=float(temp)
            zzz2=Last20_K_Data[(i,0,0)]

            assert zzz==zzz2

            if(zzz==zzz2 and zzz!=0):
                #初始化收盘价以及3日形态计数
                g_all_info[i]['s_2dayagetype']=0
                g_all_info[i]['s_1dayagetype']=0
          
                g_all_info[i]['s_RP']=int(random.random()*100)

                bufmaxminlist=Last20_K_Data[i,2,:]
                bufmaxminlist2=bufmaxminlist[bufmaxminlist>0]
                if(bufmaxminlist2.size==0):
                    continue
                sectionmax=max(bufmaxminlist2)

                bufmaxminlist=Last20_K_Data[i,4,:]
                bufmaxminlist2=bufmaxminlist[bufmaxminlist>0]
                sectionmin=min(bufmaxminlist2)

                


                #如果5日内不停牌
                for ii in range(15):

                    if(Last20_K_Data[i,1,19-ii]!=0):
                        twodasage=k_type_def(Last20_K_Data,i,17-ii)
                        onedasage=k_type_def(Last20_K_Data,i,18-ii)
                        today=k_type_def(Last20_K_Data,i,19-ii)
                        '''
                        twodasage=k_type_def(Last20_K_Data,i,17)
                        onedasage=k_type_def(Last20_K_Data,i,18)
                        today=k_type_def(Last20_K_Data,i,19)
                        g_all_info[i]['K_three_amount']=KtypeThreeLoaded[twodasage,onedasage,twodasage,0]
                        g_all_info[i]['K_three_super']=KtypeThreeLoaded[twodasage,onedasage,twodasage,5]
                        g_all_info[i]['K_three_superwrong']=KtypeThreeLoaded[twodasage,onedasage,twodasage,7]
                        g_all_info[i]['s_HisOutput1']=KtypeThreeLoaded[twodasage,onedasage,twodasage,4]

                        if((now)!=Last20_K_Data[i,6,19-ii]):
                            g_all_info[i]['s_2dayagetype']=onedasage
                            g_all_info[i]['s_1dayagetype']=today
                        else:
                            g_all_info[i]['s_2dayagetype']=twodasage
                            g_all_info[i]['s_1dayagetype']=onedasage


                        '''

                        g_all_info[i]['s_2dayagetype']=twodasage
                        g_all_info[i]['s_1dayagetype']=onedasage  



                        cur_close=Last20_K_Data[i,3,19-ii]
                        last_close=Last20_K_Data[i,3,18-ii]
                        last_plus=(cur_close-last_close)/last_close
                        sectionpos=(cur_close-sectionmin)/(sectionmax-sectionmin)

                        g_all_info[i]['s_Posofall']=sectionpos
                        '''
                        if((0.03<last_plus<0.07)and (0.6<sectionpos or 0.2>sectionpos)):

                            print("%6d %2.2f " % (zzz,cur_close))

                        break
                        '''
        
            else:
                #这里讲道理不会走到（用assert试试看）
                continue

            #g_all_info[i]['s_HisOutput1']=HistoryAnaLoaded[i,2]
                
            feigjiegse=5

        except Exception as ex:
            print (Exception,":",ex)




    #180301改成直接读取分析结果
    
    for z in range(len(g_all_result)):
        try:
            #ddd=g_all_info[z]['s_code']
            #eee=HistoryAnaLoaded[z,1]

            #g_all_info[z]['s_HisOutput1']=HistoryAnaLoaded[z,2]

            #g_all_info[z]['s_Posofall']=HistoryAnaLoaded[z,5]    #当前位置相对于历史位置
            g_all_info[z]['s_Posof666']=HistoryAnaLoaded[z,6]     #当前位置相对于666日位置
            g_all_info[z]['s_Posof166']=HistoryAnaLoaded[z,7]     #当前位置相对于166日位置

            #暂时放一放
            g_all_info[z]['s_HisOutput1']=0
            pass

        except Exception as ex:
            print (Exception,":",ex)


    zzzz=1


def CSZL_CodelistToDatelist2(K_Data,
    Datas=20,
    DayEnd=datetime.datetime.now().strftime("%Y-%m-%d")):

    x=K_Data.shape[0]    #4000
    y=K_Data.shape[1]    #7
    z=K_Data.shape[2]    #2000

    # 日期 代码 信息
    DateBasedList=np.zeros((z,x,y),dtype=float)

    days2=Datas*1.5+10


    timeArray = time.strptime(DayEnd, "%Y-%m-%d")

    timeNow = datetime.datetime(int(timeArray[0]), int(timeArray[1]), int(timeArray[2]), 12, 0, 0); 
    DayStart = (timeNow - datetime.timedelta(days = days2)).strftime("%Y-%m-%d")


    bufflist=ts.get_k_data('000001',start=DayStart, end=DayEnd, index=True) 

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
            cur_changedata=K_Data[ii,6,date_index]
            if(changedate3==cur_changedata):
                DateBasedList[i,ii,:]=K_Data[ii,:,date_index]
                DateBasedList[i,ii,6]=K_Data[ii,0,0]
                
            else:
                
                bufsearch=K_Data[ii,6,:]
                #从历史数据列表中寻找是否有对应值
                buff=np.argwhere(bufsearch==changedate3)
                #如果有指则重新定义历史数据位置
                if(buff!=None):
                    foundindex=int(buff)
                    date_index=foundindex
                    zzz2=K_Data[(ii,6,date_index)]

                    DateBasedList[i,ii,:]=K_Data[ii,:,date_index]
                    DateBasedList[i,ii,6]=K_Data[ii,0,0]
                    
                    searchcounter+=1
                else:
                    
                    updatecounter+=1
                    continue
        i+=1
        if(i>(K_Data.shape[2]-1)):
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

    txtFileA = cwd + '\\data\\History_data_Datebased.npy'
    np.save(txtFileA, DateBasedList)



def CSZL_DatebasedVolatilityClassifyProp2(DateBasedList):


    x=DateBasedList.shape[0]    #2000
    y=DateBasedList.shape[1]    #4000
    z=DateBasedList.shape[2]    #7  

    
    #新建5个计数器用来记录5个位置的值
    SectionCounter=[]
    SectionCounter2=[]
    for ii in range(y):
        temp=CSZLsuperTrain.Z_Counter()
        temp2=CSZLsuperTrain.RankCal(19)
        SectionCounter.append(temp)
        SectionCounter2.append(temp2)
        del temp
        del temp2



    avacounter=0


    for i in range(1,x):
        cur_date=DateBasedList[i,0,0]
        counter=DateBasedList[i,:,3]
        a=np.sum(counter!=0)
        if(a==0):
            continue

        todaylist=np.where(counter>0)
        todaylist2=todaylist[0]

        if(i==18):
            asdad=9

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


            
            testrank=RankList[2029]
            testper=int(float(testrank)/(float)(todaylist2.shape[0]+1)*20)
            testcode=DateBasedList[i,2029,6]

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

                    avg=SectionCounter2[cur_index].GetAvg2()

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
                    #next_close=DateBasedList[i+1,cur_index,3]
                    cur_rank=RankList[cur_index]
                    #当日的排名0~1，为了让最大值小于1往分母加1
                    cur_rank_per=float(cur_rank)/(float)(todaylist2.shape[0]+1)
                    fom_per=int(cur_rank_per*20)
                    #if(fom_per==10):
                        #sdfasdfasf=9

                    if(last_close==0 or cur_close==0 ):
                        continue

                    differper=abs(testper-fom_per)
                    #differper=fom_per-testper

                    SectionCounter[cur_index].Add(differper)
                    SectionCounter2[cur_index].Add(fom_per,differper)

                    avg=SectionCounter2[cur_index].GetAvg()
                    #avg=SectionCounter2[cur_index].GetAvg2()
                    AVG_RankList[cur_index,2]=code

                    if(avg!=0):
                        AVG_RankList[cur_index,0]=avg
                        #tomorrow_plus=(next_close-cur_close)/cur_close
                        #AVG_RankList[cur_index,1]=tomorrow_plus

                        #avg=SectionCounter2[cur_index].Add(fom_per)

                
                    cur_index_counter+=1
            #         

            #新建一个空的列表用于放置所有排序后的数据
            Rank20RankList=np.zeros((y,2),dtype=int)

            avg_rankbuff=AVG_RankList[:,0]
            avg_rankbuff2=np.where(avg_rankbuff>0)
            avg_rankbuff2=avg_rankbuff2[0]

            buffer2all=avg_rankbuff2.shape[0]

            if(buffer2all!=0):              
                
                avg_rankbuff3=avg_rankbuff[avg_rankbuff2]
                avg_rankbuff4=avg_rankbuff3.argsort()

                
                for cur_i in range(0,buffer2all):               
                    final_index=avg_rankbuff2[avg_rankbuff4[cur_i]]
                    Rank20RankList[final_index,0]=cur_i
                    
                    code=AVG_RankList[final_index,2]
                    Rank20RankList[final_index,1]=code
                    bufferf3=AVG_RankList[final_index,1]

                    sdjfisjiej=8

                for iii in range(0,y):

                    print("%d %d" % (Rank20RankList[iii,0],Rank20RankList[iii,1]))
                    #print("%2.4f %2.4f" % (percent))


                print("\n")
                dfseft=9

            avacounter+=1



        sadfsef=6



    finalsdafasf=34


def k_type_def(D_input,D_index,date_position,response_rate=0.005):

    return k_type_def2(D_input[(D_index,1,date_position)],D_input[(D_index,2,date_position)],D_input[(D_index,3,date_position)],D_input[(D_index,4,date_position)],response_rate)

def k_type_def2(start,high,end,low,response_rate=0.005):


    cur=start
    if(cur==0):
        return 0

    #实体长度
    whole=end-start
    #high=HistoryLoaded[(i,2,ii)]-HistoryLoaded[(i,1,ii)]
    #low=HistoryLoaded[(i,4,ii)]-HistoryLoaded[(i,1,ii)]
                    
    #最高价与收盘价的差redline，与开盘价的差redline2
    redline=high-end
    redline2=high-start
    #最低价与收盘价的差greenline，与开盘价的差greenline2
    greenline=low-end
    greenline2=low-start
                 
    #根据上述五个信息分析线形态共分12种，见excel表
    
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

    return cur_shape
  
STD_INPUT_HANDLE = -10  
STD_OUTPUT_HANDLE= -11  
STD_ERROR_HANDLE = -12  
  
FOREGROUND_BLACK = 0x0  
FOREGROUND_BLUE = 0x01 # text color contains blue.  
FOREGROUND_GREEN= 0x02 # text color contains green.  
FOREGROUND_RED = 0x04 # text color contains red.  
FOREGROUND_INTENSITY = 0x08 # text color is intensified.  
  
BACKGROUND_BLUE = 0x10 # background color contains blue.  
BACKGROUND_GREEN= 0x20 # background color contains green.  
BACKGROUND_RED = 0x40 # background color contains red.  
BACKGROUND_INTENSITY = 0x80 # background color is intensified.  
  
class Color:  
    ''''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp 
    for information on Windows APIs.'''  
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)  
      
    def set_cmd_color(self, color, handle=std_out_handle):  
        """(color) -> bit 
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY) 
        """  
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)  
        return bool  
      
    def reset_color(self):  
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)  
      
    def print_red_text(self, print_text):  
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)  
        print(print_text)  
        self.reset_color()  
          
    def print_green_text(self, print_text):  
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)  
        print(print_text)  
        self.reset_color()  
      
    def print_blue_text(self, print_text):   
        self.set_cmd_color(FOREGROUND_BLUE | FOREGROUND_INTENSITY)  
        print(print_text) 
        self.reset_color()  
            
    def print_red_text_with_blue_bg(self, print_text):  
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY| BACKGROUND_BLUE | BACKGROUND_INTENSITY)  
        print(print_text) 
        self.reset_color()  

def z_three_test():
    cwd = os.getcwd()

    clr = Color()

    TempPath = cwd + '\\output\\KtypeThree.npy'
    Ktype_counter=np.load(TempPath)
    for i in range(1,13):
        for ii in range(1,13):
            for iii in range(1,13):
                
                #print("%4.4f &4d %4d " % (Ktype_counter[i,ii,iii,5],cur_rank2),end="")
                if((Ktype_counter[i,ii,iii,5]-Ktype_counter[i,ii,iii,7])>=60):        
                    print("**",end="")
                elif((Ktype_counter[i,ii,iii,7]-Ktype_counter[i,ii,iii,5])>=60):
                    print("xx",end="")

                if(Ktype_counter[i,ii,iii,0]!=0):
                    print("%5d %2.4f %4d " % (Ktype_counter[i,ii,iii,0],Ktype_counter[i,ii,iii,1]/Ktype_counter[i,ii,iii,0],Ktype_counter[i,ii,iii,7]),end="")
                else:
                    print("%5d %2.4f %4d " % (Ktype_counter[i,ii,iii,0],0,Ktype_counter[i,ii,iii,7]),end="")
            print("\n")
        zzz=str(i)
        clr.print_red_text(zzz)
        print("\n") 
        
    sadfiosjdf=2


def HistoryDataGet(
    DayEnd=datetime.datetime.now().strftime("%Y-%m-%d"),
    Datas=20,
    Path='History_data.npy'):
    """
    截止日期("xxxx-xx-xx")
    获取天数(int)

    获取数据为截止日期前指定交易天数的数据,
    保存到data/History_data中无返回指

    """
    days2=Datas*1.5+10


    timeArray = time.strptime(DayEnd, "%Y-%m-%d")

    timeNow = datetime.datetime(int(timeArray[0]), int(timeArray[1]), int(timeArray[2]), 12, 0, 0); 
    DayStart = (timeNow - datetime.timedelta(days = days2)).strftime("%Y-%m-%d")
    

    HistoryDataSave=np.zeros((4000,7,Datas),dtype=float)

    if True:
        all=len(g_all_result)

        for z in range(all):
            try:
  
                if(z%30==0):
                    print(z/all)
                    print("\n")
              
                temp=str(g_all_result[z]['s_code'],"utf-8")
                #print(temp)
                HistoryDataSave[(z,0,0)]=temp
                kget=ts.get_k_data(temp,start=DayStart, end=DayEnd)

                Kdata=kget.tail(Datas)
                
                datamax=len(Kdata)

                x=0

                if(Kdata.empty==True):
                    continue

                #for x in range(0,datamax):
                for singledatezz in Kdata.date:


                    changedate=time.strptime(singledatezz,"%Y-%m-%d")
                    changedate2=time.strftime("%Y%m%d",changedate)
                    changedate3=int(changedate2)
                    HistoryDataSave[(z,6,x)]=changedate3


                    HistoryDataSave[(z,1,x)]=Kdata.open.data[x]
                    HistoryDataSave[(z,2,x)]=Kdata.high.data[x]
                    HistoryDataSave[(z,3,x)]=Kdata.close.data[x]
                    HistoryDataSave[(z,4,x)]=Kdata.low.data[x]
                    HistoryDataSave[(z,5,x)]=Kdata.volume.data[x]

                    x+=1


            except Exception as ex:
                sleeptime=random.randint(50,99)
                time.sleep(sleeptime/100)       
                wrongmessage="HistoryRoutine FAIL at : %s \n" % ( time.ctime(time.time()))
                print (wrongmessage)
                wrongEx=str(ex)
                Z_LOG_SAVE('HistoryWrongMessage.txt',wrongmessage+wrongEx)
                print (Exception,":",ex)
                z-=1

        cwd = os.getcwd()
        txtFile = cwd + '\\data\\'+Path
        np.save(txtFile, HistoryDataSave)

def CSZL_SecretDataInit():
    """
    初始化重要数据
    """
    global g_all_info

    global SecretData_A
    global SecretData_B
    
    #code,otherinfo + time(minute),(time+b1p1~s5p5)
    SecretData_A=np.zeros((4000,270,21),dtype=float)

    #todo used for highspeed_test
    #SecretData_C=np.zeros((100,101,21),dtype=float)

    for z in range(len(g_all_result)):
        try:
                
            temp=str(g_all_result[z]['s_code'],"utf-8")
            #print(temp)
            SecretData_A[(z,0,0)]=temp
            #index初始化
            SecretData_A[(z,0,1)]=1


        except Exception as ex:
            sleeptime=random.randint(50,99)
            time.sleep(sleeptime/100)
            print (Exception,":",ex)

    '''
    print(SecretData_A[(0,0,0)])
    print(SecretData_A[(1,0,0)])
    print(SecretData_A[(2,0,0)])
    '''

    #每日的时间分割(假设一天采集5000个数据)x每个时间点采集的数据条数(20条)
    #time1日期 time2详细时间 code代码 last昨收 20个值 保留
    SecretData_B=np.zeros((5000*20+1,30),dtype=float)
    



def CSZL_SecretData_A_Update(tushare_result,date_max,update_index=1):
    """
    重要数据更新
    """


    global CurHour
    global CurMinute


    global SecretData_A
    

    for i in range(date_max):

        #获取当前数据更新位置
        CurIndex=int(SecretData_A[(update_index+i,0,1)])

        #超范围检测
        if CurIndex>269:
            continue

        try:

            #更新时间记录
            SecretData_A[(update_index+i,CurIndex,0)]=str(CurHour*100+CurMinute)

            #更新常时数据
            SecretData_A[(update_index+i,CurIndex,1)]=Z_AvailableJudge(tushare_result['b1_v'][i])
            SecretData_A[(update_index+i,CurIndex,2)]=Z_AvailableJudge(tushare_result['b1_p'][i])
            SecretData_A[(update_index+i,CurIndex,3)]=Z_AvailableJudge(tushare_result['b2_v'][i])
            SecretData_A[(update_index+i,CurIndex,4)]=Z_AvailableJudge(tushare_result['b2_p'][i])
            SecretData_A[(update_index+i,CurIndex,5)]=Z_AvailableJudge(tushare_result['b3_v'][i])
            SecretData_A[(update_index+i,CurIndex,6)]=Z_AvailableJudge(tushare_result['b3_p'][i])
            SecretData_A[(update_index+i,CurIndex,7)]=Z_AvailableJudge(tushare_result['b4_v'][i])
            SecretData_A[(update_index+i,CurIndex,8)]=Z_AvailableJudge(tushare_result['b4_p'][i])
            SecretData_A[(update_index+i,CurIndex,9)]=Z_AvailableJudge(tushare_result['b5_v'][i])
            SecretData_A[(update_index+i,CurIndex,10)]=Z_AvailableJudge(tushare_result['b5_p'][i])

            SecretData_A[(update_index+i,CurIndex,11)]=Z_AvailableJudge(tushare_result['a1_v'][i])
            SecretData_A[(update_index+i,CurIndex,12)]=Z_AvailableJudge(tushare_result['a1_p'][i])
            SecretData_A[(update_index+i,CurIndex,13)]=Z_AvailableJudge(tushare_result['a2_v'][i])
            SecretData_A[(update_index+i,CurIndex,14)]=Z_AvailableJudge(tushare_result['a2_p'][i])
            SecretData_A[(update_index+i,CurIndex,15)]=Z_AvailableJudge(tushare_result['a3_v'][i])
            SecretData_A[(update_index+i,CurIndex,16)]=Z_AvailableJudge(tushare_result['a3_p'][i])
            SecretData_A[(update_index+i,CurIndex,17)]=Z_AvailableJudge(tushare_result['a4_v'][i])
            SecretData_A[(update_index+i,CurIndex,18)]=Z_AvailableJudge(tushare_result['a4_p'][i])
            SecretData_A[(update_index+i,CurIndex,19)]=Z_AvailableJudge(tushare_result['a5_v'][i])
            SecretData_A[(update_index+i,CurIndex,20)]=Z_AvailableJudge(tushare_result['a5_p'][i])


            #更新数据位置
            SecretData_A[(update_index+i,0,1)]=SecretData_A[(update_index+i,0,1)]+1


        except Exception as ex:

            wrongEx=str(ex)


def CSZL_SecretData_B_Update(tushare_result,date_max):
    """
    重要数据更新
    """

    global CurHour
    global CurMinute

    global SecretData_B
    

    for i in range(date_max):

        #获取当前数据更新位置

        B_CurIndex=int(SecretData_B[(0,0)])+1
        #超范围检测
        if B_CurIndex>(5000*20):
            continue

        try:

            #更新特殊数据

            timeArray = time.strptime(tushare_result['date'][i], "%Y-%m-%d")
            h,m,s = tushare_result['time'][i].strip().split(":")

            SecretData_B[(B_CurIndex,0)]=int(timeArray[0])*10000+int(timeArray[1])*100+int(timeArray[2])
            SecretData_B[(B_CurIndex,1)]=int(h)*10000+int(m)*100+int(s)
            SecretData_B[(B_CurIndex,2)]=int(tushare_result['code'][i])
            SecretData_B[(B_CurIndex,3)]=tushare_result['pre_close'][i]


            SecretData_B[(B_CurIndex,4)]=Z_AvailableJudge(tushare_result['b1_v'][i])
            SecretData_B[(B_CurIndex,5)]=Z_AvailableJudge(tushare_result['b1_p'][i])
            SecretData_B[(B_CurIndex,6)]=Z_AvailableJudge(tushare_result['b2_v'][i])
            SecretData_B[(B_CurIndex,7)]=Z_AvailableJudge(tushare_result['b2_p'][i])
            SecretData_B[(B_CurIndex,8)]=Z_AvailableJudge(tushare_result['b3_v'][i])
            SecretData_B[(B_CurIndex,9)]=Z_AvailableJudge(tushare_result['b3_p'][i])
            SecretData_B[(B_CurIndex,10)]=Z_AvailableJudge(tushare_result['b4_v'][i])
            SecretData_B[(B_CurIndex,11)]=Z_AvailableJudge(tushare_result['b4_p'][i])
            SecretData_B[(B_CurIndex,12)]=Z_AvailableJudge(tushare_result['b5_v'][i])
            SecretData_B[(B_CurIndex,13)]=Z_AvailableJudge(tushare_result['b5_p'][i])

            SecretData_B[(B_CurIndex,14)]=Z_AvailableJudge(tushare_result['a1_v'][i])
            SecretData_B[(B_CurIndex,15)]=Z_AvailableJudge(tushare_result['a1_p'][i])
            SecretData_B[(B_CurIndex,16)]=Z_AvailableJudge(tushare_result['a2_v'][i])
            SecretData_B[(B_CurIndex,17)]=Z_AvailableJudge(tushare_result['a2_p'][i])
            SecretData_B[(B_CurIndex,18)]=Z_AvailableJudge(tushare_result['a3_v'][i])
            SecretData_B[(B_CurIndex,19)]=Z_AvailableJudge(tushare_result['a3_p'][i])
            SecretData_B[(B_CurIndex,20)]=Z_AvailableJudge(tushare_result['a4_v'][i])
            SecretData_B[(B_CurIndex,21)]=Z_AvailableJudge(tushare_result['a4_p'][i])
            SecretData_B[(B_CurIndex,22)]=Z_AvailableJudge(tushare_result['a5_v'][i])
            SecretData_B[(B_CurIndex,23)]=Z_AvailableJudge(tushare_result['a5_p'][i])


            #更新数据位置

            SecretData_B[(0,0)]=SecretData_B[(0,0)]+1

        except Exception as ex:
            #print (Exception,":",ex)
            wrongEx=str(ex)
            #Z_LOG_SAVE('SecretDataUpdateWrongMessage.txt',wrongmessage+wrongEx)

def CSZL_SecretDataAnalyse():

    """
    暂时在这里做重要数据分析
    """

    #global SecretData_A

    cwd = os.getcwd()
    now=datetime.datetime.now()
    now=now.strftime('%Y%m%d')

    txtFileA = cwd + '\\data\\secret\\secretA'+now+'.npy' 
    testdata=np.load(txtFileA)

    print(testdata)

    for i in range(3000):
        print()
        if(testdata[(i,0,0)]==300409):

            for iii in range(100):
                for ii in range(21):
                    testprint=float(testdata[(i,iii,ii)])
                    print("%5.2f " % testprint,end="")
                print("\n")
            print("\n")
            #print("\n")
    #global SecretData_B

    #np.set_printoptions(threshold=np.inf)

    #np.set_printoptions(precision=2,suppress=True,threshold=100)
    #print(SecretData_A)



    z=1

def CSZL_SecretDataSave():
    """
    保存重要数据
    """
    global SecretData_A
    global SecretData_B
   
    cwd = os.getcwd()
    now=datetime.datetime.now()
    now=now.strftime('%Y%m%d')

    txtFileA = cwd + '\\data\\secret\\A\\secretA'+now+'.npy'
    txtFileB = cwd + '\\data\\secret\\B\\secretB'+now+'.npy'
    np.save(txtFileA, SecretData_A)
    np.save(txtFileB, SecretData_B)

def CSZL_CurDataOutput():
    """
    AI操作数据输出
    """

    global g_all_info

    global g_all_result

    all_list_max=np.alen(g_all_result)

    for i in range(all_list_max-1):
        if i==0:
            continue
        g_all_info[i]['s_plus']=g_all_result[i]['s_plus']
        g_all_info[i]['s_now']=g_all_result[i]['s_now']
        g_all_info[i]['s_high']=g_all_result[i]['s_high']
        g_all_info[i]['s_low']=g_all_result[i]['s_low']

    DataSave(g_all_info)
def DataSave(All_info):
    
    cwd = os.getcwd()
    now=datetime.datetime.now()
    now=now.strftime('%Y%m%d')


    txtFile1 = cwd + '\\output\\bot_history\\'+'z_saveinfo'+now+'.txt'

    with open(txtFile1,'w') as fobj:
        #fobj=open(txtFile1,'w')
        for singleinfo in All_info:
            temp1=singleinfo['s_code']
            temp2=singleinfo['s_ReachedFlag']
            temp3=singleinfo['s_ReachedHour']
            temp4=singleinfo['s_ReachedMinute']
            temp5=singleinfo['s_ReachedPrice']
            temp6=singleinfo['s_now']

            temp7=singleinfo['s_plus']
            temp8=singleinfo['s_last']
            temp9=singleinfo['s_high']
            temp10=singleinfo['s_low']

            tempall=str(temp1)+'\t'+str(temp2)+'\t'+str(temp3)+'\t'+str(temp4)+'\t'+str(temp5)+'\t'+str(temp6)+'\t'


            tempall2=str(temp7)+'\t'+str(temp8)+'\t'+str(temp9)+'\t'+str(temp10)
            fobj.write(tempall+tempall2+'\n')


def botlogic():
    
    data1 = {'a': [1, 2.0, 3, 4+6j],
             'b': ('string', u'Unicode string'),
             'c': None}

    selfref_list = [1, 2, 3]
    selfref_list.append(selfref_list)

    output = open('zdata.pkl', 'wb')

    # Pickle dictionary using protocol 0.
    pickle.dump(data1, output)

    output.close()




    sdfsdf=6

def BotInit():

    cwd = os.getcwd()
    txtFileA = cwd + '\\output\\bot_history\\Bots_ALL_buffer.pkl'


    if False:
        #打开历史数据文件
        pkl_file = open(txtFileA, 'rb')
        #反序列化回数组
        Bots_ALL = pickle.load(pkl_file)
        #关闭文件流
        pkl_file.close()

    
    supertest=Bot("",150000)


    supertest.buy(600000,1000,23.12)
    supertest.buy(600000,1000,23.12)
    supertest.buy(600001,1000,23.12)
    supertest.buy(600002,1000,23.12)
    supertest.buy(600000,1000,23.12)
    supertest.buy(600000,1000,23.12)

    #打开输出文件
    output = open(txtFileA, 'wb')
    #序列化保存
    pickle.dump(supertest, output)
    #关闭文件流
    output.close()


    sdfsdf=6



class Bot(object):
    name="初始姓名"

    Total_asset=100000;
    Max_Stock=10
    cur_Stock=0
    Stock_list=[]

    #初始化统计区间
    def __init__(self,name,_asset):
        #code rank
        self.Total_asset=_asset
        self.name=name
        #code 数量 成本 待定 待定 待定
        self.Stock_list=np.zeros((self.Max_Stock,6),dtype=float)

    def buy(self,code,qty,price):

        zzzbuf=self.Stock_list[:,0]
        buff=np.argwhere(zzzbuf==code)
        buff2=np.argwhere(zzzbuf==0)
        #如果有指则添加
        if(buff!=None):
            foundindex=int(buff)
            zzz2=self.Stock_list[foundindex,0]            
            self.Stock_list[foundindex,1]+=qty
            self.Total_asset-=qty*price
        #没有则新建
        elif(self.cur_Stock<self.Max_Stock):
            foundindex=int(buff2[0])
            self.Stock_list[foundindex,0]=code
            self.Stock_list[foundindex,1]+=qty

            self.Total_asset-=qty*price

            self.cur_Stock+=1

        #超出退回
        else:
            print("wrong")
            
            

    def sell(self,code,qty,price):
        i=0
        while True:
            if(self.Stock_list[i,0]==code):
                self.Stock_list[i,1]=self.Stock_list[i,1]-qty
                if(self.Stock_list[i,1]==0):
                    self.Stock_list[i,0]=0
                    self.Stock_list[i,1]=0
                    #self.Stock_list[i,2]=0
                    Total_asset+=qty*price
                elif(self.Stock_list[i,1]>0):
                    Total_asset+=qty*price

                else:
                    print("wrong")
                break

            if(i==(self.Max_Stock-1)):
                print("wrong")
                break
            i+=1
        while True:
            if(self.Stock_list[i,0]==0):
                self.Stock_list[i,0]=code
                self.Stock_list[i,1]=qty
                #self.Stock_list[i,2]=price
                Total_asset-=qty*price

                break
            if(i==(self.Max_Stock-1)):
                print("wrong")
                break
            i+=1









#暂时未使用功能

def Z_PRINT():
    """
    用来打印信息
    """

    global g_all_result
    np.set_printoptions(precision=2,suppress=True,threshold=10000)

    print(g_all_result)

def CSZL_YearCompoundInterest(AnReturn=1.035,TotalYear=20,EachCost=20000):
    """
    年利率计算
    """

    TotalCost=TotalYear*EachCost

    TotalGet=0


    for i in range(0,TotalYear):

        TotalGet=TotalGet+EachCost
        TotalGet=TotalGet*AnReturn



    print(TotalCost)
    print("")
    print(TotalGet)

def z_get(quote_name):
    """
    todo之后用这个来调用tushare接口
    """

    try:
        net_result = ts.get_realtime_quotes(quote_name)   
        return True,net_result
    except Exception as ex:
        print (Exception,":",ex)
    return False,0

def CSZL_DataProtect():
    """
    多线程数据保护
    """

    donecounter=0
    while donecounter<=100:
        if AllresultAvailableFlag:
            g_part_result=buff_hightolow.copy()
            break
        donecounter+=1
        time.sleep(0.2)
    else:
        if donecounter==100:
            return (-1)

