from math import nan

import numpy as np

import Chart
import pandas as pd
import datetime
import numpy as np
import time
import random
import numpy.random as npr

#测试
"""


"""
# ISSUE_DATE = "2018-08-31"
# END_DATE = "2023-08-09"
# COUPON_RATE = 0.0405
# FACE_VALUE = 100
# RATING = "AAA"
# PRICING_DATE = "2021-01-20"
# COUNPON_FREQ = 1
# dateList = w.tdays(PRICING_DATE, "2021-01-25", "").Data[0]

# cbChinaBondObj = ChinaBondCorporateBondYieldData()
# # # cbChinaBondObj.saveData()
# YIELD_DATA = cbChinaBondObj.getData()

# testBond = Bond(ISSUE_DATE, END_DATE, COUPON_RATE, FACE_VALUE, YIELD_DATA, RATING, COUNPON_FREQ)
# value = testBond.getValue(PRICING_DATE)
# print(value)

# mcData = MonteCarlo("000001.SZ", 2, 0.05, 250, 0.02, 3, dateList).getPrice()
# mcDataWithDateInDt = {"价格": mcData, "日期": dateList}
# print(mcDataWithDateInDt)


# df1 = pd.DataFrame(np.random.randint(10, size=(5, 4)), columns=['A', 'B', 'C', 'D'])
# df2 = pd.DataFrame(np.random.randint(10, size=(5, 4)), columns=['A', 'B', 'C', 'D'])
# df3 = df1 * df2
# print(df1)
# print(df2)
# print(df3)

# accruedInterests = w.wsd("110045.SH", "accruedinterest", "2021-05-24", "2021-06-22", "").Data[0]
# print(accruedInterests)

# clause_conversion_2_swapshareenddate
# PRICING_DATE = "2018-03-21"
# END_DATE = "2021-07-13"
# ISSUE_DATE = "2018-07-13"
# CONVERTIBLE_BOND_CODE = "110030.SH"
# INITIAL_CONVERT_PRICE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_conversion2_swapshareprice", 
#             ISSUE_DATE, ISSUE_DATE, "")



# STOCK_CODE = w.wsd(CONVERTIBLE_BOND_CODE, "underlyingcode", ISSUE_DATE, ISSUE_DATE, "").Data[0][0]
# print(STOCK_CODE)
# CONVERT_START_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_conversion_2_swapsharestartdate").Data[0][0]
# CONVERT_END_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_conversion_2_swapshareenddate").Data[0][0]
# print(CONVERT_START_DATE)
# print(CONVERT_END_DATE)


# df.to_csv("result1111.csv")
# keys = np.arange(1,101,1).tolist()
# print(keys)

# df = pd.read_csv('mc_result.csv')
# df_list = df.T.values.tolist()
# list_result = df_list[1:]
# print(list_result)


# print(excel.values.tolist())
# def deleteEmptyString(data):
#     return data.strip(b'\x00'.decode())

# firstPartdf = excel.iloc[:, [0,1,2]]
# secondPartdf = excel.iloc[:, [3,4]]
# thirdPartdf = excel.iloc[:, [5,6,7]]

# firstNew = firstPartdf.applymap(deleteEmptyString)
# thirdNew = thirdPartdf.applymap(deleteEmptyString)

# result = pd.concat([firstNew, secondPartdf, thirdNew], axis = 1)

# print(result.values.tolist())


# chinaBondYieldData = ChinaBondCorporateBondYieldData().saveData()
# obj = ChinaBondCorporateBondYieldData()

# CONVERTIBLE_BOND_CODE = "110040.SH"
# ISSUE_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "carrydate").Data[0][0]
# END_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "delist_date").Data[0][0]

# I = 100
# xValue = npr.standard_normal(I)
# yValue = np.zeros(100)
# print(type(xValue))
# plt.scatter(xValue, yValue, s=20, c="#ff1212", marker='o')
# plt.show()
# print(e)
# print(yValue)



# obj = ChinaBondCorporateBondYieldData()
# obj.getData()
# creditRating = w.wsd(CONVERTIBLE_BOND_CODE, "creditrating", ISSUE_DATE, ISSUE_DATE, "").Data[0][0]
# print("Rating: " +creditRating)
# PRICING_DATE = "2018-03-21"
# listOfDates = w.tdays("2018-03-21", "2018-05-21", "").Data[0]
# allDiscountRates = obj.getEachDayDiscountRate(listOfDates, PRICING_DATE, creditRating)
# print(allDiscountRates)
# from random import gauss
# STOCK_CODE = "600036.SH"
# TRADING_DAYS_PER_YEAR = 252
# obj = HistoricalVolatility(STOCK_CODE, TRADING_DAYS_PER_YEAR, "2018-01-01", "2020-12-31")
# result = obj.getVolatilitySimpleMethod()
# result_original = obj.getVolatility()
# testList = []
# for i  in range(0, 100):
#     testList.append(gauss(0.0, 1.0))
# plt.scatter(testList, yValue, s=20, c="#ff1212", marker='o')
# plt.show()

#print(gauss(0,1))



# import numpy.random as npr
# date = pd.DatetimeIndex(start = '2020-1-2', end = '2022-12-31', freq = 'B')
# n = len(date);I = 100 #生成需要预测的维度，n天100次
# dt = 1 / 252 #St和St-1之间的时间间隔
# result = np.zeros((n, I))
# result[0] = 20.35 #datareader可找到2020年1月2日的股价，作为S0
# print(result)

# for t in range(1, n):
# 	e = npr.standard_normal(I) #生成100个服从正态分布的ε
# 	result[t] = result[t - 1] * np.exp((miu - 0.5 * sigma**2) * dt + sigma * e * np.sqrt(dt))
# result = pd.DataFrame(result, index = date)
# result.tail() 
# 华泰证券股票预期年收益率为0.0569,收益率的年化波动率为0.3637


# closingPrice = w.wsd("600185.SH", "close", "2017-03-21", "2018-03-20", "").Data[0]
# df = pd.DataFrame(closingPrice)
# R = np.log(df / df.shift(1))
# print(R)
# miu = R.mean() * 252
# sigma = R.std() * np.sqrt(252)
# print (str(miu) + ", " + str(sigma))

# obj = ChinaBondTreasuryYieldData()
# testDate = "2021-01-04"
# print(obj.getRiskFreeRate(testDate, 7))

# df = pd.read_csv('CBPricing100Times.csv')
# data = df['result']
# plt.hist(data)
# plt.show()

# df = pd.read_csv('CBPricing100Times-113555SH.csv')
# data = df['result']
# plt.hist(data)
# plt.show()


# testInfo1 = np.load('D:\个人专题\可转债\赎回测试\第二次测试样本结果700多个\cbConvertPriceAndStockClosingPriceInfo.npy', allow_pickle = True)
# data_dict1 = testInfo1.item()
# testInfo2 = np.load('D:\个人专题\可转债\赎回测试\第二次测试样本结果700多个\cbConvertPriceAndStockClosingPriceInfo-2ndPart.npy', allow_pickle = True)
# data_dict2 = testInfo2.item()
# dict3 ={}
# dict3.update(data_dict1)
# dict3.update(data_dict2)

# np.save('D:\个人专题\可转债\赎回测试\第二次测试样本结果700多个\cbConvertPriceAndStockClosingPriceInfo-combined.npy', dict3) 

def checkIfTriggerRedeem(resultList, daysLimit, duration):
    if(len(resultList) < duration):
        return False

    #30天sliding window遍历，testingPeriodStartIndex和testingPeriodEndIndex 分别为30天sliding window的起始和结束指针
    #首先查看第一个sliding window中价格超过界限的个数，若已符合要求，则返回True，若不符合要求，向右移动sliding window挨个查看
    #是否符合要求。向右移动时，不用重新遍历，只需查看去掉的首个和新加进来的元素是否符合要求，在前一个sliding window的结果上加减即可。

    previous = 0
    testingPeriodStartIndex = 0
    endTestingDateIndex = len(resultList) - 1
    # duration = 30
    while(testingPeriodStartIndex < endTestingDateIndex - duration + 2):
        testingPeriodEndIndex = testingPeriodStartIndex + duration - 1
        if(testingPeriodStartIndex == 0):
            firstThirtyDaysResult = getDaysWithHigherPriceAboveLimit(resultList, duration)
            if(firstThirtyDaysResult >= daysLimit):
                # print(code + "前30天")
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
                # print(code + " 开始日：" + str(daysList[testingPeriodStartIndex]) + " 结束日：" + str(daysList[testingPeriodEndIndex]))
                return True
            else:
                testingPeriodStartIndex += 1
    return False       


def getDaysWithHigherPriceAboveLimit(priceList, duration):
    numberOfHighPriceDate = 0
    for i in range(0, duration):
        if(priceList[i]):
            numberOfHighPriceDate += 1
    return numberOfHighPriceDate



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


testInfo = np.load(r'C:\Users\Su Wang\Desktop\首创\git\convertibleBond\cbPricing\sellBackTest\cbConvertPriceAndStockClosingPriceInfo-sellBack-final.npy', allow_pickle = True)
originalData = testInfo.item()
data = deleteItemWithNoneType(originalData)
numberOfTriggerRedeem = 0
totalNumberOfCB = len(data)

for key, value in data.items():
    print(str(key))
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
print("resultList执行结束")




oneStockData = originalData["110037.SH"]
dates = oneStockData["日期"]
closingPrice = oneStockData["收盘价"]
convertPrice = oneStockData["转股价"]
dataMap = {"日期" : dates, "收盘价":closingPrice, "转股价":convertPrice, "result":oneStockData["resultList"]}
df_test = pd.DataFrame(dataMap)
df_test.to_csv(r'C:/Users/Su Wang/Desktop/首创/test128029.csv')
