from abc import ABCMeta,abstractmethod
import Ipynb_importer
from WindPy import w
import math
from math import exp, sqrt
import numpy as np
import pandas as pd
w.start()

class StockVolatility(object):
    __metaclass__ = ABCMeta #抽象类
    @abstractmethod  #抽象方法
    def getVolatility(self):
        pass

class HistoricalVolatility(StockVolatility):
    
    def __init__(self, stockCode, tradingDaysPerYear, startDate, endDate):    
        self.stockCode = stockCode
        self.tradingDaysPerYear = tradingDaysPerYear
        self.startDate = startDate
        self.endDate = endDate

    def getVolatility(self):
        """
        计算标的在一段时间内的年化波动率
        stockCode: 标的代码
        startDate: 开始日期
        endDate: 结束日期
        tradingDaysPerYear: 一年交易日天数
        计算方法： 
        """
        closingPrice = w.wsd(self.stockCode, "close", self.startDate, self.endDate, "").Data[0]

        dailyReturn = [0]
        continuousCompoundReturn = [0]
        for i in range(1, len(closingPrice)):
            dailyReturn.append(closingPrice[i] / closingPrice[i - 1])
            continuousCompoundReturn.append(math.log(dailyReturn[i]))

        continuousCompoundReturnAvg = sum(continuousCompoundReturn) / len(closingPrice) # miu

        # calculate (LN(R) - miu) ^ 2
        thetaFangList = [0]
        for j in continuousCompoundReturn:
            thetaFangList.append(pow(j - continuousCompoundReturnAvg, 2))
        variance =  sum(thetaFangList) / (len(closingPrice) - 1) # 样本方差theta^2
        standardDeviation = pow(variance, 0.5)   #标准差，即波动率
        annualVolatility = standardDeviation * sqrt(self.tradingDaysPerYear)
        print(annualVolatility)
        return annualVolatility


        """
        计算股票一段时间的年化收益率的简单写法
        R = np.log(df/df.shift(1))
        miu = R.mean() * 252
        sigma = R.std() * np.sqrt(252)
        sigma为年化波动率，与上一个方法计算的annualVolatility结果相等。
        miu：年化收益率
        """
    def getVolatilitySimpleMethod(self):
        closingPrice = w.wsd(self.stockCode, "close", self.startDate, self.endDate, "").Data[0]
        df = pd.DataFrame(closingPrice)
        R = np.log(df / df.shift(1))
        miu = R.mean() * 252
        sigma = R.std() * np.sqrt(252)
        return [miu, sigma]