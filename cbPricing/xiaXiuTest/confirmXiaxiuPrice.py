import math
import datetime
import pandas as pd
from WindPy import w
import numpy as np
w.start()

def calculateRequiredXiaXiuPrice(convertibleBondCode, xiaXiuDate):
    stockCode = w.wss(convertibleBondCode, "underlyingcode").Data[0][0]
    amountAndVolume = w.wsd(stockCode, "amt,volume", w.tdaysoffset(-20, xiaXiuDate, "").Data[0][0], xiaXiuDate, "")
    amountList = amountAndVolume.Data[0]
    volumeList = amountAndVolume.Data[1]
    tradingAveragePriceList = [a/b for a,b in zip(amountList, volumeList)]
    averagePriceDuration = np.mean(tradingAveragePriceList)
    lastDayAvg = amountList[len(amountList) - 1]/volumeList[len(volumeList) - 1]
    return min(averagePriceDuration, lastDayAvg)




result = calculateRequiredXiaXiuPrice("100567.SH", datetime.datetime.strptime("2004/7/26", "%Y/%m/%d"))
print(result)
