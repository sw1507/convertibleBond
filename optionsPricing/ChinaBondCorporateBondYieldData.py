#coding:utf-8
from WindPy import w
import numpy as np
w.start()

import pandas as pd
import QuantLib as ql
import datetime
import numpy as np
import QuantLib as ql

"""
实现中债企业债数据从本地excel的获取，存np文件至本地并提取。
提取的数据格式为字典，其中每一个value代表原excel中一个日期一行的信息，key为日期，格式为字符串，value为dict，date list中的每一个值
为float型，单位为年。代表对于当前日期，这个duration对应的yield为yieldData中对应的数据。

具体格式如下：
{
    "YYYY-MM-DD":{
        "AAA":{'date':[], 'yieldData':[]},
        "AAA-":{'date':[], 'yieldData':[]},
        "AA+":{'date':[], 'yieldData':[]},
        "AA":{'date':[], 'yieldData':[]},
        "AA-":{'date':[], 'yieldData':[]},
        "A+":{'date':[], 'yieldData':[]},
        "A":{'date':[], 'yieldData':[]},
        "A-":{'date':[], 'yieldData':[]},
        "BBB+":{'date':[], 'yieldData':[]},
        "BBB":{'date':[], 'yieldData':[]},
    }
}
例子：
   {    
       'date': [0.0, 0.0833, 0.25, 0.2857, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 
   'yieldData': [2.6278, 4.0807, 4.6788, 4.9134, 5.0191, 5.0159, 5.4727, 5.5951, 5.7878, 5.8557, 5.9714]
   
   }

"""

class ChinaBondCorporateBondYieldData:
    def __init__(self):
        return

    #对于给定起始日期，获取一个list包含起始日期加上durations中每个duration的日期
    def getListOfDates(self, startingDate, durations):
        result = []
        for duration in durations:
            newDate = datetime.datetime.strptime(startingDate,'%Y-%m-%d') + datetime.timedelta(days = duration) 
            result.append(newDate)
        return result  

    #读取本地xls文件，更改数据格式后，存np文件至本地，以方便以后提取。
    def saveData(self):
        fileName = r'D:\个人专题\Quant\中债国债收益率曲线信息\中债企业债到期收益率(中债)(日)-1.xls'
        data = pd.read_excel(fileName)

        # toList为整个表的第一行整理为一个list
        categoryList = data.iloc[0:0]
        toList = list(data.iloc[0:0])
        totalNumberOfCols = len(toList) # 110列

        #newList为toList处理后，字段中只剩评级
        newList = []
        for i in range(1, len(toList)):
            newList.append(toList[i].split(":")[0].split("(")[1].replace(")",""))
        category = list(dict.fromkeys(newList)) # ['AAA', 'AAA-', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB']
        numberOfDataPerCategory = 11

        durations = [0, 30, 90, 180, 270, 365, 730, 1095, 1460, 1825, 2190]
        durationsBBB = durations[:-1] # [0, 30, 90, 180, 270, 365, 730, 1095, 1460, 1825]

        #转换第一列的日期格式为字符串"YYYY-MM-DD"
        if(type(data.iloc[0,0]) != str):
            data["指标名称"] = pd.to_datetime(data["指标名称"])
            data["指标名称"] = data["指标名称"].dt.strftime('%Y-%m-%d')
        data["指标名称"] = data["指标名称"].replace('/', '-', regex = True)

        #allDict以下部分处理结果为一个list[{'date':[x,x...x]}, {}...{}],每个元素为dict，第一个dict是AAA的信息，以此类推。
        allDict = []
        startingIndex = 1
        while(startingIndex < totalNumberOfCols):
            if(startingIndex < 100):
                oneDateInfoCut = data.iloc[:, np.r_[0, startingIndex : startingIndex + numberOfDataPerCategory]]
            else:
                oneDateInfoCut = data.iloc[:, np.r_[0, startingIndex : startingIndex + numberOfDataPerCategory - 1]]
            dictResult = oneDateInfoCut.set_index('指标名称').T.to_dict('list')
            allDict.append(dictResult)
            startingIndex += 11
        print("第一部分处理结束")
        

        #建立一个新的dict，key为日期
        allData = {}
        for key in allDict[0].keys():
            allData[key] = {}

        
        for categoryIndex in range(0, len(category)):
            #遍历allDict
            for key, value in allDict[categoryIndex].items():
                currentCategory = category[categoryIndex] #评级字段
                if(currentCategory == "BBB"):
                    dates = [0.0, 0.0833, 0.2500, 0.2857, 0.7500, 1.0, 2.0, 3.0, 4.0, 5.0]
                    # dates = self.getListOfDates(key, durationsBBB)
                else:
                    dates = [0.0, 0.0833, 0.2500, 0.2857, 0.7500, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
                    # dates = self.getListOfDates(key, durations)
                keyDict = allData[key]
                keyDict[currentCategory] = {"date" : dates, "yieldData" : value}
        # 存入本地
        np.save('chinaBondCorporateBondYieldData.npy', allData) 
        print('已读取数据并保存至本地')


    def getData(self):
        chinaBondInfo = np.load('chinaBondCorporateBondYieldData.npy', allow_pickle = True)
        data_dict = chinaBondInfo.item()
        return data_dict

    def getDataAtDate(self, pricingDate):
        allData = self.getData() 
        return allData[pricingDate]
    # 测试
    # print(allData['2021-04-25']['A+'])    


    """在一个降序数组中找到第一个小于目标数字的数的index"""
    def findFirstSmallerNumber(self, target, dataList):
        if(dataList == None or len(dataList) == 0):
            return -1
        left = 0
        right = len(dataList) - 1
        while(left < right):
            mid = (left + right)//2
            if(dataList[mid] > target):
                left = mid + 1
            else:
                right = mid
        if(dataList[right] <= target):
            return right
        else:
            return -1
    

    """
    使用线性插值法获取收益率
    参考：https://xueqiu.com/2680567071/134179761
    data格式为：{'date':[], 'yieldData':[]}
            例：{}
    """
    def getDiscountRate(self, dateListReversed, yieldListReversed, years):  
        if(years >= dateListReversed[0]):
            return yieldListReversed[0]
        result = 0
        firstSmallerNumberIndex = self.findFirstSmallerNumber(years, dateListReversed)
        result += yieldListReversed[firstSmallerNumberIndex]
        remainedYears = years - dateListReversed[firstSmallerNumberIndex]
        result += remainedYears * (yieldListReversed[firstSmallerNumberIndex - 1] - yieldListReversed[firstSmallerNumberIndex])/(dateListReversed[firstSmallerNumberIndex - 1] - dateListReversed[firstSmallerNumberIndex])
        return result

    """
    对一个list的每一天，对于给定的定价日以及这个定价日获取的中债企业债收益率数据
    采用线性插值法计算这个list上每一天对应的折现率
    pricingDate: string type
    """
    def getEachDayDiscountRate(self, listOfDates, pricingDate, credit):
        data = self.getData()[pricingDate][credit]
        result = [data['yieldData'][0]]

        dateListOriginal = data['date'] #  [6.0,     5.0,     4.0,     3.0,    2.0,   1.0,   0.75,  0.2857,  0.25,  0.0833,   0.0]
        dateListReversed = []
        for i in dateListOriginal:
            dateListReversed.append(i)
        dateListReversed.reverse()

        yieldListOriginal = data['yieldData'] # [5.9714, 5.8557, 5.7878, 5.5951, 5.4727, 5.0159, 5.0191, 4.9134, 4.6788, 4.0807, 2.6278]
        yieldListReversed = []
        for j in yieldListOriginal:
            yieldListReversed.append(j)
        yieldListReversed.reverse()

        for index in range(1, len(listOfDates)):
            currentDateNumberOfYears = index / 365
            currentDateDiscountRate = self.getDiscountRate(dateListReversed, yieldListReversed, currentDateNumberOfYears)
            result.append(currentDateDiscountRate)
        
        result_dict = dict(zip(listOfDates, result))
        
        return result_dict

