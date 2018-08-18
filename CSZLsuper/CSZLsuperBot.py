#coding=utf-8

#序列化和反序列化
import pickle,pprint
import os
import numpy as np
import math

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
    txtFileB = cwd + '\\output\\bot_history\\Bots_read.csv'

    if False:
        #打开历史数据文件
        pkl_file = open(txtFileA, 'rb')
        #反序列化回数组
        Bots_ALL = pickle.load(pkl_file)
        #关闭文件流
        pkl_file.close()

    InitStrategy()

    supertest=VirtualTransaction()
    writeList2CSV(supertest.His_list,txtFileB)

    #打开输出文件
    output = open(txtFileA, 'wb')
    #序列化保存
    pickle.dump(supertest, output)
    #关闭文件流
    output.close()


    sdfsdf=6



class Bot(object):
    #机器人的姓名
    name="初始姓名"
    #初始资金
    Init_asset=1000000
    #总资金
    Total_asset=1000000
    #最多可持有股票数
    Max_Stock=10
    #当前持有股票数
    cur_Stock=0
    #持仓列表
    Stock_list=[]
    #操作列表
    His_list=[]

    #初始化统计区间
    def __init__(self,name,_asset):

        #确定机器人的资金量
        self.Total_asset=_asset
        self.Init_asset=_asset
        #确定机器人的姓名
        self.name=name
        #code 持有数量 成本 可卖数量 当前价 盈亏比率
        self.Stock_list=np.zeros((self.Max_Stock,6),dtype=float)

    def _buy(self,code,qty,price):
        #todo整数限制，时间限制
        #如果钱不够
        if((self.Total_asset-qty*price)>0):

            #读取持有列表
            zzzbuf=self.Stock_list[:,0]
            #寻找这个票是否已经持有
            buff=np.argwhere(zzzbuf==code)
            #寻找空位
            buff2=np.argwhere(zzzbuf==0)
            #如果有则添加
            if(buff!=None):
                foundindex=int(buff)
                zzz2=self.Stock_list[foundindex,0]            
                self.Stock_list[foundindex,1]+=qty
                self.Total_asset-=qty*price
                return True
            #没有则新建
            elif(self.cur_Stock<self.Max_Stock):
                #光标转换到空位
                foundindex=int(buff2[0])
                self.Stock_list[foundindex,0]=code
                self.Stock_list[foundindex,1]+=qty

                self.Total_asset-=qty*price

                self.cur_Stock+=1
                return True

            #超出购买个数上限
            else:
                print("超出购买上限")
                return False
        else:
            print("余额不足")
            return False

    def buy(self,code,qty,price):
        if(self._buy(code,qty,price)):
            #第一个代表买还是卖
            self.hisupdate(1,code,qty,price)
            
    def _sell(self,code,qty,price):
        i=0
        while True:
            #如果找到
            if(self.Stock_list[i,0]==code):
                #卖出可卖数量有效计算
                remainqty=self.Stock_list[i,3]-qty
                #卖出有效
                if(remainqty>=0):
                    #持有数量减少
                    self.Stock_list[i,1]-=qty
                    #金钱增加
                    self.Total_asset+=qty*price
                    #为0则清空
                    if(self.Stock_list[i,1]==0):
                        self.clear(i)
                        return True
                    #可卖数量减少
                    self.Stock_list[i,3]-=qty
                    
                    return True
                else:
                    print("卖出错误")
                    return False
       
            #如果快结束还没找到
            if(i==(self.Max_Stock-1)):
                print("超出最多持股数量")
                return False
            i+=1

    def sell(self,code,qty,price):
        if(self._sell(code,qty,price)):
            #第一个代表买还是卖
            self.hisupdate(2,code,qty,price)
    #过一个交易日
    def daypass(self):
        #所有不可卖出变为可卖出
        self.Stock_list[:,3]=self.Stock_list[:,1]

    def clear(self,index):
        self.Stock_list[index,:]=0
        #减一个位置
        self.cur_Stock-=1
    def hisupdate(self,buyflag,code,qty,price):
        
        zzz=[buyflag,code,qty,price,self.Total_asset]
        self.His_list.append(zzz)



def writeList2CSV(myList,filePath):
    try:
        file=open(filePath,'w')
        file.write("买卖标志,代码编号,数量,价格,剩余资金\n") 
        for items in myList:
            for item in items:
                ccc=str(item)
                file.write(ccc)
                file.write(",")
            file.write("\n") 
    except Exception :
        print("数据写入失败，请检查文件路径及文件编码是否正确")
    finally:
        file.close();# 操作完成一定要关闭

def InitStrategy():

    InitChoiceList=np.zeros((10,4),dtype=float)

    for i in range(InitChoiceList.shape[0]):
        InitChoiceList[i,0]=600000+i


    #分值
    InitChoiceList[0,1]=13
    InitChoiceList[1,1]=23
    InitChoiceList[2,1]=55
    InitChoiceList[3,1]=27
    InitChoiceList[4,1]=85
    InitChoiceList[5,1]=81
    InitChoiceList[6,1]=22
    InitChoiceList[7,1]=64
    InitChoiceList[8,1]=97
    InitChoiceList[9,1]=18
    #价格
    InitChoiceList[0,2]=23.54
    InitChoiceList[1,2]=5.78
    InitChoiceList[2,2]=55.21
    InitChoiceList[3,2]=12.43
    InitChoiceList[4,2]=8.54
    InitChoiceList[5,2]=6.32
    InitChoiceList[6,2]=10.11
    InitChoiceList[7,2]=123.54
    InitChoiceList[8,2]=30.32
    InitChoiceList[9,2]=18.88

    xxx=ChoiceStrategy(1,InitChoiceList)

    yyy=FundAllocationStrategyBuy(1,xxx,500000,1000000)


def ChoiceStrategy(type,InputList):
    '''
    1 只选一个
    2 选3个
    3 尽可能多选
    '''
    ChoiceList=[]

    #输入二维列表code point

    #先按point排序
    buffsort=InputList[:,1]

    bufflist=np.argsort(-buffsort)


    if(type==1):
        ChoiceList.append([float(InputList[bufflist[0],0]),
        float(InputList[bufflist[0],1]),
        float(InputList[bufflist[0],2])])


    elif(type==2):
        ChoiceList.append([float(InputList[bufflist[1],0]),
        float(InputList[bufflist[1],1]),
        float(InputList[bufflist[1],2])])
        ChoiceList.append([float(InputList[bufflist[2],0]),
        float(InputList[bufflist[2],1]),
        float(InputList[bufflist[2],2])])
        ChoiceList.append([float(InputList[bufflist[0],0]),
        float(InputList[bufflist[0],1]),
        float(InputList[bufflist[0],2])])

    elif(type==3):    
        for ddd in InputList:
            ChoiceList.append([float(ddd[0]),float(ddd[1]),float(ddd[2])])
    else:
        "无此策略类型"

    return ChoiceList



def  FundAllocationStrategyBuy(type,codelist,available_asset,total_asset):
    '''
    1永远满仓
    2平时半仓,满足条件时满仓todo
    3平时空仓,满足条件时满仓todo
    '''
    buylist=[]    

    buf_asset=available_asset

    if(type==1):
        cishu=len(codelist)
        single=available_asset/cishu
        
        for curlist in codelist:
            #先获取这个code可买入价格
            price=curlist[2]
            qty=round(single/price/100)*100
            if(qty>0 and qty*price<=buf_asset):
                #写入购买列表
                buylist.append([curlist[0],qty,price])
                #减去金额
                buf_asset-=qty*price
            elif(qty>=100 and (qty-100)*price<=buf_asset):
                #写入购买列表
                buylist.append([curlist[0],(qty-100),price])
                #减去金额
                buf_asset-=(qty-100)*price
            else:
                #金额不足
                break
              

    elif(type==2):
        cishu=len(codelist)
        single=available_asset
    elif(type==3):    
        cishu=len(codelist)
        single=available_asset
    else:
        "无此策略类型"


    return buylist
def  FundAllocationStrategySell(type,codelist,available_asset,total_asset):
    '''
    1全部清空
    2清一半
    3todo
    '''
    
    if(type==1):
        cishu=len(codelist)
        single=available_asset/cishu
        
        for curlist in codelist:
            #先获取这个code可买入价格
            price=10
            qty=round(available_asset/cishu/100)*100


    elif(type==2):
        cishu=len(codelist)
        single=available_asset
    elif(type==3):    
        cishu=len(codelist)
        single=available_asset
    else:
        "无此策略类型"


    Outlist

def VirtualTransaction():
    supertest=Bot("测试随机机器人",1000000)
    

    xxx=supertest.buy(600000,1000,23.12)
    xxx=supertest.buy(600000,1000,23.12)
    xxx=supertest.buy(600111,100,123.12)
    xxx=supertest.buy(600002,1000,23.12)
    xxx=supertest.buy(300000,500,6.12)
    xxx=supertest.buy(600000,1000,23.12)
    supertest.daypass()
    xxx=supertest.sell(600000,700,20.12)
    xxx=supertest.sell(600000,1700,20.12)
    xxx=supertest.sell(600111,100,20.12)
    xxx=supertest.buy(600000,1000,23.12)
    xxx=supertest.buy(600222,1000,23.12)
    return supertest