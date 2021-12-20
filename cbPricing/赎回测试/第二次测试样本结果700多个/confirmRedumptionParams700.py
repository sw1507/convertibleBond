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
        np.save('D:\个人专题\可转债\赎回测试\第二次测试样本结果700多个\cbConvertPriceAndStockClosingPriceInfo-2ndPart.npy', results) 
        print("已完成：" + str(index + 1) + " " + str(convertibleBondCode))    

def retrieveData():
    testInfo = np.load('D:\个人专题\可转债\赎回测试\第二次测试样本结果700多个\cbConvertPriceAndStockClosingPriceInfo-final.npy', allow_pickle = True)
    data_dict = testInfo.item()
    return data_dict
    # print(data_dict)

def getAllDataReady():
    data = pd.read_csv("D:/个人专题/可转债/赎回测试/第二次测试样本结果700多个/allConvertibleBonds633.csv", encoding = 'gbk')
    data_dict_2 = data[["赎回触发计算最大时间区间", "赎回触发计算时间区间", "赎回触发比例"]].to_dict(orient = 'records')
    keys = data["证券代码"].tolist()
    data2 = dict(zip(keys, data_dict_2))

    allDataDict = retrieveData()
    for key, value in allDataDict.items():
        result1 = data2[key]["赎回触发计算时间区间"]
        result2 = data2[key]["赎回触发比例"]
        result3 = data2[key]["赎回触发计算最大时间区间"]
        value["赎回触发计算时间区间"] = result1
        value["赎回触发比例"] = result2
        value["赎回触发计算最大时间区间"] = result3 
    return allDataDict


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
def checkIfTriggerRedeem(resultList, daysLimit, daysList, code, duration):
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
            firstThirtyDaysResult = getDaysWithHigherPriceAboveLimit(resultList)
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
                return {"code": code, "result" : True, "startDate" : daysList[slidingWindowStart], "endDate": daysList[slidingWindowEnd]}
            else:
                slidingWindowStart += 1
    return {"code": code, "result" : False, "startDate" : "", "endDate": ""}            


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
check在转股期内,公司股票在任意连续X个交易日中的收盘价不低于转股价格的Z%时
T T T F F T T T T T
          L
                    R

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
    if(right - left >= daysLimit):
        return {"code": code, "result" : True, "startDate": daysList[left], "endDate": daysList[right - 1]}
    else:
        return {"code": code, "result": False, "startDate": "", "endDate": ""}


"""
main
"""
# data = pd.read_csv("D:/个人专题/可转债/赎回测试/第二次测试样本结果700多个/allConvertibleBonds633-2ndPart.csv", encoding = 'gbk')
# data_dict = data.to_dict(orient = 'list')
# saveDataIntoDisk(data_dict)

# allDataDict = getAllDataReady()

# 所有样本信息直接从cbConvertPriceAndStockClosingPriceInfo-final.npy提取就行
data = retrieveData()
numberOfTriggerRedeem = 0
totalNumberOfCB = len(data)

#11.4 100087.SH 的closingPrice全是None，需要查看原因。另外需要确认cbConvertPriceAndStockClosingPriceInfo-final.npy
#里面的信息是否都是有效的。


for key, value in data.items():
    # print(str(key))
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
print("resultList执行结束")

#遍历所有可转债，查看其是否触发赎回条件，收集结果
#创建一个空的字典，用来储存结果
resultDict = {"code":[], "result":[], "startDate":[], "endDate":[]}

index = 1
for key, value in data.items():    
    daysLimit = value["赎回触发计算时间区间"]
    if(value['赎回触发计算时间区间'] != value['赎回触发计算最大时间区间']):
        duration = value["赎回触发计算最大时间区间"]
        oneBondResult = checkIfTriggerRedeem(value["resultList"], daysLimit, value["日期"], key, duration)
    else:
        oneBondResult = checkConsecutives(value["resultList"], daysLimit, value["日期"], key)
    
    resultDict["code"].append(oneBondResult["code"])
    resultDict["result"].append(oneBondResult["result"])
    resultDict["startDate"].append(oneBondResult["startDate"])
    resultDict["endDate"].append(oneBondResult["endDate"])
    print("结果打印完毕：" + str(index) + " / " + str(totalNumberOfCB) + ": " + str(key))
    index += 1
result_df = pd.DataFrame(resultDict)
result_df.to_csv("D:/个人专题/可转债/赎回测试/第二次测试样本结果700多个/redumptionTestResult.csv")

    # if(oneBondResult):
    #     numberOfTriggerRedeem += 1

# print("trigger redeem 个数：" + str(numberOfTriggerRedeem))



    