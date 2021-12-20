import random as rd
import math
import datetime
import pandas as pd
from WindPy import w
import numpy as np
w.start()



def saveDataIntoDisk(data_dict):
    allStockCodeList = data_dict['正股代码']
    allCBCodeList = data_dict['证券代码']
    allStartDates = data_dict['条件赎回起始日期']
    allEndDates = data_dict['今天日期与赎回截止日较小者']
    results = {}
    for index in range(0, len(allStockCodeList)):
        convertibleBondCode = allCBCodeList[index]
        startDate = allStartDates[index]
        endDate = allEndDates[index]
        dateList = w.tdays(startDate, endDate, "").Data[0]
        stockClosingPrice = w.wsd(allStockCodeList[index], "close", startDate, endDate, "").Data[0]
        convertiblePrice = w.wsd(allCBCodeList[index], "convprice", startDate, endDate, "").Data[0]
        results[convertibleBondCode] = {"日期":dateList, "收盘价": stockClosingPrice, "转股价": convertiblePrice}
        if(len(dateList) != len(stockClosingPrice) or len(dateList) != len(convertiblePrice)):
            print("长度不一致: " + convertibleBondCode)
        print("已完成：" + str(index))
    np.save('cbConvertPriceAndStockClosingPriceInfo.npy', results)     

def retrieveData():
    testInfo = np.load('cbConvertPriceAndStockClosingPriceInfo.npy', allow_pickle = True)
    data_dict = testInfo.item()
    return data_dict
    # print(data_dict)

def getAllDataReady(originalData):
    # data = pd.read_csv("D:/个人专题/可转债/赎回测试/allCBInfo.csv", encoding = 'gbk')
    data_dict_2 = originalData[["赎回触发计算时间区间", "赎回触发比例"]].to_dict(orient = 'records')
    keys = data["证券代码"].tolist()
    data2 = dict(zip(keys, data_dict_2))

    allDataDict = retrieveData()
    for key, value in allDataDict.items():
        result1 = data2[key]["赎回触发计算时间区间"]
        result2 = data2[key]["赎回触发比例"]
        value["赎回触发计算时间区间"] = result1
        value["赎回触发比例"] = result2
    return allDataDict

def checkIfTriggerRedeem(resultList, daysLimit, daysList, code):
    if(len(resultList) < 30):
        return False

    #30天sliding window遍历，testingPeriodStartIndex和testingPeriodEndIndex 分别为30天sliding window的起始和结束指针
    #首先查看第一个sliding window中价格超过界限的个数，若已符合要求，则返回True，若不符合要求，向右移动sliding window挨个查看
    #是否符合要求。向右移动时，不用重新遍历，只需查看去掉的首个和新加进来的元素是否符合要求，在前一个sliding window的结果上加减即可。

    previous = 0
    testingPeriodStartIndex = 0
    endTestingDateIndex = len(resultList) - 1
    duration = 30
    while(testingPeriodStartIndex < endTestingDateIndex - duration + 2):
        testingPeriodEndIndex = testingPeriodStartIndex + duration - 1
        if(testingPeriodStartIndex == 0):
            firstThirtyDaysResult = getDaysWithHigherPriceAboveLimit(resultList)
            if(firstThirtyDaysResult >= daysLimit):
                print(code + "前30天")
                return True
            else:
                testingPeriodStartIndex += 1
                previous = firstThirtyDaysResult
        else:
            firstNumber = resultList[testingPeriodStartIndex - 1]
            lastNumber = resultList[testingPeriodEndIndex]
            if(firstNumber):
                previous -= 1
            if(lastNumber):
                previous += 1
            if(previous >= daysLimit):
                print(code + " 开始日：" + str(daysList[testingPeriodStartIndex]) + " 结束日：" + str(daysList[testingPeriodEndIndex]))
                return True
            else:
                testingPeriodStartIndex += 1
    return False            


"""
检测某段时间内，股价不低于某价格的天数(用于检测是否触发赎回条款)
"""
def getDaysWithHigherPriceAboveLimit(priceList):
    numberOfHighPriceDate = 0
    for i in range(0, 30):
        if(priceList[i]):
            numberOfHighPriceDate += 1
    return numberOfHighPriceDate



"""
main
"""
data = pd.read_csv("D:/个人专题/可转债/赎回测试/allCBInfo.csv", encoding = 'gbk')
data_dict = data.to_dict(orient = 'list')
# saveDataIntoDisk(data_dict)
#获取存在本地的numpy文件
data1 = retrieveData()
allDataDict = getAllDataReady(data)

numberOfTriggerRedeem = 0

for key, value in allDataDict.items():
    date = value["日期"]
    closingPrice = value["收盘价"]
    convertPrice = value["转股价"]
    percentage = value["赎回触发比例"]/100
    #创建一个resultList，存储boolean type，每个boolean代表每一天的收盘价是否超过了转股价格乘以比例（赎回条款约定的）
    resultList = []

    for index in range(0, len(closingPrice)):
        if(closingPrice[index] >= convertPrice[index] * percentage):
            resultList.append(True)
        else:
            resultList.append(False)
    value["resultList"] = resultList
    
for key, value in allDataDict.items():    
    daysLimit = value["赎回触发计算时间区间"]
    oneBondResult = checkIfTriggerRedeem(value["resultList"], daysLimit, value["日期"], key)
    if(oneBondResult):
        numberOfTriggerRedeem += 1

print("trigger redeem 个数：" + str(numberOfTriggerRedeem))



    