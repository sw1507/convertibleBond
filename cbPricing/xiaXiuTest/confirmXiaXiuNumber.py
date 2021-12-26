import random as rd
import math
import datetime
import pandas as pd
from WindPy import w
import numpy as np
w.start()

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

#查看一个可转债所有的转债价格，和前一天的对比，看是否有下修，有的话，把日期放入一个list中，最后返回list
def countNumberOfCBThatHasHadXiaXiu(convertibleBondCode, convertPriceList):
    resultList = []
    if(len(convertPriceList) >= 2):
        previousDatePrice = convertPriceList[0]
        for i in range(1, len(convertPriceList)):
            currentDatePrice = convertPriceList[i]
            if(currentDatePrice < previousDatePrice):
                resultList.append(date[i])
            previousDatePrice = currentDatePrice
    return resultList
    



#main
testInfo = np.load(r'C:\Users\Su Wang\Desktop\首创\git\convertibleBond\cbPricing\sellBackTest\cbConvertPriceAndStockClosingPriceInfo-sellBack-final.npy', allow_pickle = True)
originalData = testInfo.item()
data = deleteItemWithNoneType(originalData)
df = pd.read_csv(r'C:\Users\Su Wang\Desktop\首创\git\convertibleBond\cbPricing\xiaXiuTest\xiaXiuToBeConfirm.csv')
cbCodeList = df['code'].tolist()
whetherHadXiaXiuResult = []


for cbCode in cbCodeList:
    value = data[cbCode]
    date = value["日期"]
    convertPrice = value["转股价"]
    whetherHadXiaXiuResult.append(countNumberOfCBThatHasHadXiaXiu(cbCode, convertPrice))


resultDict = {"code": cbCodeList, "dateHadXiaXiu": whetherHadXiaXiuResult}    
result_df = pd.DataFrame(resultDict)
result_df.to_csv(r"C:\Users\Su Wang\Desktop\首创\git\convertibleBond\cbPricing\xiaXiuTest\xiaXiuResult.csv")
