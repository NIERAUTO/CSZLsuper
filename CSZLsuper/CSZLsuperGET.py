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


z_init_nplist=[]
g_all_result=[]
g_part_result=[]
g_all_info=[]

SecretData_A=[]


g_list_update_index=0   #全局更新数据位置
g_exit_flag=True
update_start=False

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
    CMD界面显示
    """

    global g_exit_flag

    global INFO_all_routine
    global g_list_update_index

    global INFO_part_routine

    global g_part_result



    print("INFO DISPLAY START")
    time.sleep(2)   


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
                #print("NO1:%s with score %f \n"%(str(g_part_result[cur_long-1]['s_Cname'],"utf-8"),g_part_result[cur_long-1]['s_zValue']))
                #print("NO2:%s with score %f \n"%(str(g_part_result[cur_long-2]['s_Cname'],"utf-8"),g_part_result[cur_long-2]['s_zValue']))
                #print("NO3:%s with score %f \n"%(str(g_part_result[cur_long-3]['s_Cname'],"utf-8"),g_part_result[cur_long-3]['s_zValue']))

                for i in range(20):
                    print("NO%d:%s with score %f \n"%(i+1,str(g_part_result[cur_long-1-i]['s_Cname'],"utf-8"),g_part_result[cur_long-1-i]['s_zValue']))

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

def CSZL_superinit():

    global g_all_result
    global g_part_result
    global g_exit_flag
    global g_list_update_index
    global g_all_info
    global z_init_nplist


    #初始化选项
    getinput=int(input("是否初始化列表数据:1表示初始化 2表示不初始化\n"))
    if(getinput==1):
        CurDatalistCreate()


    #======初始化总得到的数据 g_all_result======#
    #初始化typedef s_high
    z_useful_stock_type=np.dtype(([('s_key', int), ('s_code', 'S6'), ('s_plus', float),('s_now', float),
    ('s_last', float),('s_high', float),('s_low', float),
    ('s_stflag', float),('s_s2', float),('s_s3', float),('s_s4', float),('s_s5', float),
    ('s_b1', float),('s_b2', float),('s_b3', float),('s_b4', float),('s_b5', float),
    ('s_vol', float),('s_wholecap', float),('s_mktcap', float),('s_10Value', float),
    ('s_InFastUpdataList', int),('s_counter', int),('s_useful', int),('s_zValue', float),
    ('s_UpdateHour', int),('s_UpdateMinute', int),('s_ReachedHour', int),('s_ReachedMinute', int),
    ('s_ReachedFlag', int),('s_ReachedPrice', float),('s_Buy', int),('s_Cname', 'S40'),
    ('s_per', float),('s_pb', float),('s_turnoverratio', float),('s_reserve1', float),
    ('s_reserve2', float),('s_reserve3', float),('s_reserve4', float)
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
        elif(zzz[1]=='S'or zzz[1]=='*'):
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
                CSZL_INFOUpdate(g_all_info,update_cur,g_list_update_index)
                #隐藏信息更新
                CSZL_SecretDataUpdate(buff_dr_result,update_cur,g_list_update_index)

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
        
        if (CSZL_TimeCheck() and update_start):
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

                    #重新计算value
                    for i in range(part_list_cur-1):
                        #temp=str(buff_part_result[1+i]['s_code']).zfill(6)
                        buff_part_result[i+1]['s_zValue']=CSZL_ValueCal(buff_part_result[i+1],g_all_info[i+1])


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

        sleeptime=random.randint(50,99)
        time.sleep(sleeptime/10)    
    
    return 0

def CSZL_ValueCal(StockResult,StockINFO):

    #cur_plus=StockResult['s_plus']
    cur_price=StockResult['s_now']
    cur_high=StockResult['s_high']
    cur_mktcap=StockResult['s_mktcap']
    cur_10Value=StockINFO['s_10Value']


    LastValue=0


    if(cur_price==0):
        return LastValue
    
    if ((cur_high-cur_price)/cur_price)>0.01:
        LastValue-=2


    if (StockResult['s_plus']>=2.5) and (StockResult['s_plus']<6):
        LastValue+=StockResult['s_plus']
    

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

    if(cur_10Value>0):
        LastValue+=0.5  
    elif(cur_mktcap<0):
        LastValue-=0.5  

    if(StockResult['s_stflag']!=0):
        LastValue-=4

    return LastValue

#@CSZL_log
def CSZL_TypeChange(z_type_result,tushare_result,date_max,update_index=1,s_counter=0):
    """
    类型转换(我的type, tushare的type, 总共要更新几个数据, 更新的index,计数器)
    

    """
    global CurHour
    global CurMinute


    for i in range(date_max):
        try:
            #zstring=buff_result[g_list_update_index+i]['s_code']
            z_type_result[update_index+i]['s_counter']=s_counter
            #z_type_result[update_index+i]['s_UpdateFlag']=1
            
            z_type_result[update_index+i]['s_last']=tushare_result['pre_close'][i]
            z_type_result[update_index+i]['s_now']=tushare_result['price'][i]
            z_type_result[update_index+i]['s_high']=tushare_result['high'][i]
            z_type_result[update_index+i]['s_low']=tushare_result['low'][i]
            #这里有bug似乎
            z_type_result[update_index+i]['s_Cname']=tushare_result['name'][i].encode("utf-8") 


            z_type_result[update_index+i]['s_UpdateHour']=CurHour
            z_type_result[update_index+i]['s_UpdateMinute']=CurMinute

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
            Z_LOG_SAVE('TypeChangeWrongMessage.txt',wrongmessage+wrongEx)

def CSZL_INFOUpdate(z_info_source,date_max,update_index=1):
    """
    将被剔除的3状态成员，变回普通成员
    

    """

    for i in range(date_max):
        try:
            if(z_info_source[update_index+i]['s_InFastUpdataList']==3):
                z_info_source[update_index+i]['s_InFastUpdataList']=0


        except Exception as ex:
            #print (Exception,":",ex)
            wrongEx=str(ex)
            Z_LOG_SAVE('TypeChangeWrongMessage.txt',wrongmessage+wrongEx)

def CSZL_TimeCheck():
    global CurHour
    global CurMinute



    CurHour=int(time.strftime("%H", time.localtime()))
    CurMinute=int(time.strftime("%M", time.localtime()))

    caltemp=CurHour*100+CurMinute

    #return True

    if (caltemp>=916 and caltemp<=1135) or (caltemp>=1300 and caltemp<=1505):
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

    #初始化历史数据
    getinput=int(input("是否初始化历史总数据:1表示初始化 2表示不初始化\n"))

    if(getinput==1):
        HistoryDataInit()


    global g_all_info

    cwd = os.getcwd()
    txtFile1 = cwd + '\\data\\'+'History_data.npy'   
    HistoryLoaded=np.load(txtFile1)

    #对应的列表第4个第3项数据，第8天的(倒数第二天)
    
    for z in range(len(g_all_result)):
        try:
            value=0
            div=1
            for x in range(50):
                if HistoryLoaded[(z,1,x)]!=0:

                    value+=abs((HistoryLoaded[(z,3,x)]-HistoryLoaded[(z,1,x)])/HistoryLoaded[(z,1,x)])
                    div+=1
            value=value/div
            '''
            if(value<0.01):
                tes2t=2
            test=g_all_info[z]['s_code']
            '''
            g_all_info[z]['s_10Value']=value
            

        except Exception as ex:
            print (Exception,":",ex)
def HistoryDataInit():
    """
    历史数据保存
    """
    
    DayNow=datetime.datetime.now()
    #这里改时间
    NDayAgo = (datetime.datetime.now() - datetime.timedelta(days = 100))
    otherStyleTime = NDayAgo.strftime("%Y-%m-%d")
    otherStyleTime2 = DayNow.strftime("%Y-%m-%d")

    HistoryData10=np.zeros((4000,6,50),dtype=float)
    '''
    zempty=ts.get_k_data("888888",start=otherStyleTime, end=otherStyleTime2)
    z222=ts.get_k_data("888888",start=otherStyleTime, end=otherStyleTime2)

    z333=z222.tail(10)


    if(len(z333)==10):
        print('sadf')

    

    eee=z333.close.data[0]

    eee2=z333.close.data[9]

    


    for datas in eee:
        zzz=datas
        print(zzz)

    eee2=z333.close.data[1]

    for x in range(0,10):
        #zmctest1105[(z,0,x)]=z333.open[x]
        print(z333.open[x])

        #zmctest1105[(z,0,x)]=z333.open[x]
    '''


    if True:

        for z in range(len(g_all_result)):
            try:
                
                temp=str(g_all_result[z]['s_code'],"utf-8")
                #print(temp)
                HistoryData10[(z,0,0)]=temp
                z222=ts.get_k_data(temp,start=otherStyleTime, end=otherStyleTime2)

                z333=z222.tail(50)
                datamax=len(z333)

                for x in range(0,datamax):
                    #zmctest1105[(z,0,x)]=g_all_result[z]['s_code']
                    HistoryData10[(z,1,x)]=z333.open.data[datamax-x-1]
                    HistoryData10[(z,2,x)]=z333.high.data[datamax-x-1]
                    HistoryData10[(z,3,x)]=z333.close.data[datamax-x-1]
                    HistoryData10[(z,4,x)]=z333.low.data[datamax-x-1]
                    HistoryData10[(z,5,x)]=z333.volume.data[datamax-x-1]
                    #zmctest1105[(z,5,x)]=z333.amount.data[x]

            except Exception as ex:
                sleeptime=random.randint(50,99)
                time.sleep(sleeptime/100)       
                wrongmessage="HistoryRoutine FAIL at : %s \n" % ( time.ctime(time.time()))
                print (wrongmessage)
                wrongEx=str(ex)
                Z_LOG_SAVE('HistoryWrongMessage.txt',wrongmessage+wrongEx)
                print (Exception,":",ex)

        cwd = os.getcwd()
        txtFile = cwd + '\\data\\'+'History_data.npy'
        np.save(txtFile, HistoryData10)

def CSZL_SecretDataInit():
    """
    初始化重要数据
    """


    global SecretData_A
    #global SecretData_B
    
    #code,otherinfo + time(minute),(time+b1p1~s5p5)
    SecretData_A=np.zeros((4000,270,21),dtype=float)

    #SecretData_B=np.zeros((4000,241,21),dtype=float)

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

def CSZL_SecretDataUpdate(tushare_result,date_max,update_index=1):
    """
    重要数据更新
    """


    global CurHour
    global CurMinute


    global SecretData_A
    #global SecretData_B
    

    for i in range(date_max):

        #获取当前数据更新位置
        CurIndex=int(SecretData_A[(update_index+i,0,1)])
        #超范围检测
        if CurIndex>269:
            continue

        try:

            
            #z2=update_index+i

            #更新时间记录
            SecretData_A[(update_index+i,CurIndex,0)]=str(CurHour*100+CurMinute)
            test=Z_AvailableJudge(tushare_result['b1_v'][i])
            #更新数据
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
            #print (Exception,":",ex)
            wrongEx=str(ex)
            Z_LOG_SAVE('SecretDataUpdateWrongMessage.txt',wrongmessage+wrongEx)

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
    #global SecretData_B
    

    cwd = os.getcwd()
    now=datetime.datetime.now()
    now=now.strftime('%Y%m%d')

    txtFileA = cwd + '\\data\\secret\\secretA'+now+'.npy'
    np.save(txtFileA, SecretData_A)


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
    txtFile1 = cwd + '\\output\\'+'z_saveinfo.txt'

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

class CSZL_Train:
    def CSZL_TrainMain():
    
        z222=ts.get_k_data('600000',start='2018-01-16', end='2018-01-17',ktype='5')

        print(z222)
        #print(z222.date[1])
        #print(z222.open.data[1])

        data=CSZL_Train.CSZL_TrainInputInit()
        CSZL_TrainFilter(data)


    def CSZL_TrainInputInit():
        global SecretData_A

        #code time mkt availableflag

        InputData=np.zeros((4000,4),dtype=float)

        while(True):
            z=random.randint(0,3999)

        for i in range(x):
            print(i)
            for ii in range(y):
                print(i)

        return InputData
    
    def CSZL_TrainFilter(InputData):
        x=InputData.shape[0]
        y=InputData.shape[1]

        for i in range(x):
            print(i)
            for ii in range(y):
                print(i)

        aa=1

    def CSZL_TrainResult(InputData):
        x=InputData.shape[0]
        y=InputData.shape[1]

        for i in range(x):
            print(i)
            for ii in range(y):
                print(i)

        aa=1

    def CSZL_TrainBack(InputData):
        x=InputData.shape[0]
        y=InputData.shape[1]

        for i in range(x):
            print(i)
            for ii in range(y):
                print(i)

        aa=1


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

