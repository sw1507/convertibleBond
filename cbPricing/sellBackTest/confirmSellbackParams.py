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
    allStartDates = data_dict['条件回售起始日期']
    allEndDates = data_dict['今天日期与回售截止日较小者']
    results = {}
    for index in range(0, len(allStockCodeList)):
        convertibleBondCode = allCBCodeList[index]
        startDate = allStartDates[index]
        endDate = allEndDates[index]

        dateListData = w.tdays(startDate, endDate, "").Data
        if(dateListData != None):
            dateList = dateListData[0]

        stockClosingPriceData = w.wsd(allStockCodeList[index], "close", startDate, endDate, "").Data
        if(stockClosingPriceData != None):
            stockClosingPrice = stockClosingPriceData[0]

        convertiblePriceData = w.wsd(allCBCodeList[index], "convprice", startDate, endDate, "").Data
        if(convertiblePriceData != None):
            convertiblePrice = convertiblePriceData[0]

        results[convertibleBondCode] = {"日期":dateList, "收盘价": stockClosingPrice, "转股价": convertiblePrice}
        if(len(dateList) != len(stockClosingPrice) or len(dateList) != len(convertiblePrice)):
            print("长度不一致: " + convertibleBondCode)
        np.save('D:\个人专题\可转债\回售测试\cbConvertPriceAndStockClosingPriceInfo-sellBack.npy', results) 
        print("已完成：" + str(index + 1) + " " + str(convertibleBondCode))    

def retrieveData():
    testInfo = np.load('D:\个人专题\可转债\回售测试\cbConvertPriceAndStockClosingPriceInfo-sellBack.npy', allow_pickle = True)
    data_dict = testInfo.item()
    return data_dict
    # print(data_dict)

def getAllDataReady():
    data = pd.read_csv("D:/个人专题/可转债/回售测试/allConvertibleBonds-sellBack.csv", encoding = 'gbk')
    data_dict_2 = data[["回售触发计算最大时间区间", "回售触发计算时间区间", "回售触发比例"]].to_dict(orient = 'records')
    keys = data["证券代码"].tolist()
    data2 = dict(zip(keys, data_dict_2))

    allDataDict = retrieveData()
    for key, value in allDataDict.items():
        result1 = data2[key]["回售触发计算时间区间"]
        result2 = data2[key]["回售触发比例"]
        result3 = data2[key]["回售触发计算最大时间区间"]
        value["回售触发计算时间区间"] = result1
        value["回售触发比例"] = result2
        value["回售触发计算最大时间区间"] = result3 
    np.save('D:\个人专题\可转债\回售测试\cbConvertPriceAndStockClosingPriceInfo-sellBack-fianl.npy', allDataDict)     
    # return allDataDict


#11.3怀疑有问题，为什么没有duration，与model中的这个方法不一样。另外样本分为两种，1）连续X天 2）连续X个交易日中至少Y天
"""
check是否满足赎回条件： 任何连续duration个交易日中有至少daysLimit个交易日的收盘价不低于xxx
返回boolean

previous = 0

连续10天中至少有5天
0 1 2 3 4 5 6 7 8  9  10  11  12  13 14  15  16
T T T F F F T F T  F  X   X   X   X  X   X   X 
ss
                                          et
                  se
"""
def checkIfTriggerSellback(resultList, daysLimit, daysList, code, duration):
    if(len(resultList) < duration):
        return {"code": code, "result": False, "startDate" : "", "endDate" : ""}

    #30天sliding window遍历，slidingWindowStart和slidingWindowEnd 分别为30天sliding window的起始和结束指针
    #首先查看第一个sliding window中价格超过界限的个数，若已符合要求，则返回True，若不符合要求，向右移动sliding window挨个查看
    #是否符合要求。向右移动时，不用重新遍历，只需查看去掉的首个和新加进来的元素是否符合要求，在前一个sliding window的结果上加减即可。

    previous = 0
    slidingWindowStart = 0
    endTestingDateIndex = len(resultList) - 1
    
    while(slidingWindowStart < endTestingDateIndex - duration + 2):
        slidingWindowEnd = slidingWindowStart + duration - 1
        if(slidingWindowStart == 0):
            firstThirtyDaysResult = getDaysWithLowerPriceAboveLimit(resultList)
            if(firstThirtyDaysResult >= daysLimit):
                # print(code + "前30天")
                return {"code": code, "result" : True, "startDate" : daysList[slidingWindowStart], "endDate": daysList[slidingWindowEnd]}
            else:
                slidingWindowStart += 1
                previous = firstThirtyDaysResult
        else:
            firstNumber = resultList[slidingWindowStart - 1]
            lastNumber = resultList[slidingWindowEnd]
            if(firstNumber):
                previous -= 1
            if(lastNumber):
                previous += 1
            if(previous >= daysLimit):
                # print(code + " 开始日：" + str(daysList[slidingWindowStart]) + " 结束日：" + str(daysList[slidingWindowEnd]))
                return {"code": code, "result" : True, "startDate" : daysList[slidingWindowEnd - daysLimit + 1], "endDate": daysList[slidingWindowEnd]}
            else:
                slidingWindowStart += 1
    return {"code": code, "result" : False, "startDate" : "", "endDate": ""}            


"""
检测某段时间内，股价低于某价格的天数(用于检测是否触发回售条款)
"""
def getDaysWithLowerPriceAboveLimit(priceList):
    numberOfLowPriceDate = 0
    for i in range(0, 30):
        if(priceList[i]):
            numberOfLowPriceDate += 1
    return numberOfLowPriceDate


"""
check在回售期内,公司股票在任意连续X个交易日中的收盘价低于转股价格的Z%时

"""
def checkConsecutives(resultList, daysLimit, daysList, code):
    if(len(resultList) < daysLimit):
        return {"code": code, "result": False, "startDate": "", "endDate": ""}
    left = 0
    right = 0
    while(left < len(resultList) and right < len(resultList)):
        if(resultList[right]):
            right += 1
        else:
            numberOfConsecutives = right - left
            if(numberOfConsecutives >= daysLimit):
                return {"code": code, "result" : True, "startDate": daysList[left], "endDate": daysList[right - 1]}
            else:
                left = right + 1
                right = left
        numberOfConsecutives = right - left
        if(numberOfConsecutives >= daysLimit):
            return {"code": code, "result" : True, "startDate": daysList[left], "endDate": daysList[right - 1]}
                
    if(right - left >= daysLimit):
        return {"code": code, "result" : True, "startDate": daysList[left], "endDate": daysList[right - 1]}
    else:
        return {"code": code, "result": False, "startDate": "", "endDate": ""}

"""
遍历一遍dict每个key，只要对应的值中的收盘价里有NoneType，删除整个key-value，为了确保dict中所有数据为有效数据。
"""
def deleteItemWithNoneType(originalData):
    keysThatNeedToBeDropped = []
    for key in originalData.keys():
        closingPrice = originalData[key]['收盘价']
        for price in closingPrice:
            if(price == None):
                keysThatNeedToBeDropped.append(key)
                break
    for keyNeedToBeDropped in keysThatNeedToBeDropped:
        originalData.pop(keyNeedToBeDropped)
    return originalData

"""
main
"""

"""
#获取并存储基础数据的部分
data = pd.read_csv("D:/个人专题/可转债/回售测试/allConvertibleBonds-sellBack.csv", encoding = 'gbk')
data_dict = data.to_dict(orient = 'list')
saveDataIntoDisk(data_dict)
getAllDataReady()
"""

"""以下为测算部分"""
# 所有样本信息直接从cbConvertPriceAndStockClosingPriceInfo-sellBack-final.npy提取就行
#at office
#testInfo = np.load('D:\个人专题\可转债\回售测试\cbConvertPriceAndStockClosingPriceInfo-sellBack-final.npy', allow_pickle = True)

#at home
testInfo = np.load(r'C:\Users\Su Wang\Desktop\首创\git\convertibleBond\cbPricing\sellBackTest\cbConvertPriceAndStockClosingPriceInfo-sellBack-final.npy', allow_pickle = True)
originalData = testInfo.item()
data = deleteItemWithNoneType(originalData)
numberOfTriggerRedeem = 0
totalNumberOfCB = len(data)



for key, value in data.items():
    date = value["日期"]
    closingPrice = value["收盘价"]
    convertPrice = value["转股价"]
    percentage = value["回售触发比例"]/100
    #创建一个resultList，存储boolean type，每个boolean代表每一天的收盘价是否低于了转股价格乘以比例（回售条款约定的）
    resultList = []

    for index in range(0, len(closingPrice)):
        if(closingPrice[index] < convertPrice[index] * percentage):
            resultList.append(True)
        else:
            resultList.append(False)
    value["resultList"] = resultList

#遍历所有可转债，查看其是否触发赎回条件，收集结果
#创建一个空的字典，用来储存结果
resultDict = {"code":[], "result":[], "startDate":[], "endDate":[]}

index = 1
for key, value in data.items():    
    daysLimit = value["回售触发计算时间区间"]
    if(value['回售触发计算时间区间'] != value['回售触发计算最大时间区间']):
        duration = value["回售触发计算最大时间区间"]
        oneBondResult = checkIfTriggerSellback(value["resultList"], daysLimit, value["日期"], key, duration)
    else:
        oneBondResult = checkConsecutives(value["resultList"], daysLimit, value["日期"], key)
    
    resultDict["code"].append(oneBondResult["code"])
    resultDict["result"].append(oneBondResult["result"])
    resultDict["startDate"].append(oneBondResult["startDate"])
    resultDict["endDate"].append(oneBondResult["endDate"])
    print("结果打印完毕：" + str(index) + " / " + str(totalNumberOfCB) + ": " + str(key))
    index += 1
result_df = pd.DataFrame(resultDict)
# result_df.to_csv("D:/个人专题/可转债/回售测试/sellBackTestResult.csv")
result_df.to_csv(r"C:\Users\Su Wang\Desktop\首创\git\convertibleBond\cbPricing\sellBackTest\sellBackTestResult-2.csv")

    # if(oneBondResult):
    #     numberOfTriggerRedeem += 1

# print("trigger redeem 个数：" + str(numberOfTriggerRedeem))



    