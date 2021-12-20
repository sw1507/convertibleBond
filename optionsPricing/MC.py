from abc import ABCMeta,abstractmethod
from math import exp, sqrt
from random import gauss
import pandas as pd
import matplotlib.pyplot as plt
from WindPy import w
import datetime
w.start()

class StockPriceEngine(object):
    __metaclass__ = ABCMeta #指定这是一个抽象类
    @abstractmethod  #抽象方法
    def getPrice(self):
        pass

"""
生成蒙特卡洛模拟结果

stockCode:要进行模拟的股票代码
firstClosingPrice:第一天的收盘价
riskFreeRate:无风险利率
tradingDaysPerYear:每年交易日天数
stockVolatility:股票价格波动率
numberOfSimulation: 要模拟的天数
dateList: 进行模拟的日期序列（包括第一天的日期）

输出：例子，生成了4天的价格，模拟数为3

[
    [2, 2.0018405761017006, 2.000274159348316, 2.001849073956059], 
    [2, 2.003498921171049, 2.0026746830410094, 2.006232794664794], 
    [2, 1.9977164491636243, 1.9944997637641124, 1.9965097519729]
]

"""
class MonteCarlo(StockPriceEngine):
    def __init__(self, stockCode, firstClosingPrice, riskFreeRate, tradingDaysPerYear, stockVolatility, numberOfSimulation, dateList):    
        self.stockCode = stockCode
        self.firstClosingPrice = firstClosingPrice
        self.riskFreeRate = riskFreeRate
        self.tradingDaysPerYear = tradingDaysPerYear
        self.stockVolatility = stockVolatility
        self.numberOfSimulation = numberOfSimulation
        self.dateList = dateList
    
    def getPrice(self):
        results = []
        for i in range(0, self.numberOfSimulation):
            result = self.getOnePredict(self.stockCode, self.firstClosingPrice, self.dateList, 
                                        self.riskFreeRate, self.tradingDaysPerYear, self.stockVolatility)
            results.append(result)
        return results    
    
    def getOnePredict(self, stockCode, firstClosingPrice, dateList, riskFreeRate, tradingDaysPerYear, stockVolatility):
        """
        对于某股票/指数，获取其在某一段时间每一天的预测价格
        stockCode：股票/指数代码
        firstClosingPrice：要预测的时间段，第一天的收盘价，取自wind
        dateList：要预测的时间段（包含上述的第一天）
        riskFreeRate：无风险利率
        tradingDaysPerYear：一年交易日天数
        """
        result = [firstClosingPrice]
        previousDayClosingPrice = firstClosingPrice

        for dateIndex in range(1, len(dateList)):
            testingDate_dt = dateList[dateIndex]
            predictedPrice = self.calculate_S_T(previousDayClosingPrice, self.stockVolatility, riskFreeRate, 1 / 365)
            result.append(predictedPrice)
            previousDayClosingPrice = predictedPrice
        return result
    
    def getOnePredict_dongwu(self, stockCode, firstClosingPrice, dateList, riskFreeRate, tradingDaysPerYear, stockVolatility):
        """
        与上面function功能一样，方法为东吴证券的蒙卡价格预测计算公式。
        
        对于某股票/指数，获取其在某一段时间每一天的预测价格
        stockCode：股票/指数代码
        firstClosingPrice：要预测的时间段，第一天的收盘价，取自wind
        dateList：要预测的时间段（包含上述的第一天）
        riskFreeRate：无风险利率
        tradingDaysPerYear：一年交易日天数
        """
        result = [firstClosingPrice]
        previousDayClosingPrice = firstClosingPrice

        for dateIndex in range(1, len(dateList)):
            testingDate_dt = dateList[dateIndex]
            predictedPrice = self.calculate_S_T_dongwu(previousDayClosingPrice, self.stockVolatility, riskFreeRate)
            result.append(predictedPrice)
            previousDayClosingPrice = predictedPrice
        return result

    def calculate_S_T(self, stockClosingPrice, stockPriceVolatility, riskFreeRate, daysToExpire):
        """模拟epsilon，计算S_T
        stockClosingPrice：测试当日的标的价格
        """
        return stockClosingPrice * exp((riskFreeRate - 0.5 * stockPriceVolatility ** 2) * daysToExpire + 
                                       stockPriceVolatility * sqrt(daysToExpire) * gauss(0.0, 1.0))


    def calculate_S_T_new(self, stockClosingPrice, stockPriceVolatility, annualReturn, daysToExpire):
        """模拟epsilon，计算S_T
        stockClosingPrice：测试当日的标的价格
        """
        return stockClosingPrice * exp((annualReturn - 0.5 * stockPriceVolatility ** 2) * daysToExpire + 
                                       stockPriceVolatility * sqrt(daysToExpire) * gauss(0.0, 1.0))

    def calculate_S_T_dongwu(self, stockClosingPrice, stockPriceVolatility, riskFreeRate):
        randomNumber = gauss(0,1)
        
        result = stockClosingPrice * (1 + riskFreeRate + stockPriceVolatility * randomNumber)
        print("r: " + str(riskFreeRate) + " v: " + str(stockPriceVolatility) + " random: " + str(randomNumber) + " price: " + str(result))
        return result

    def printResult(self):
        print(pd.DataFrame(self.results))
    
    """
    将蒙特卡洛模拟的数据画成linechart显示出来
    """
    def drawLineChart(self, data, dates, optionName):
        #解决中文显示问题
        plt.rcParams['font.sans-serif']=['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        #指定像素
        plt.figure(dpi = 200)
        
        plt.xlabel('日期')
        plt.ylabel('模拟价格')
        plt.title(optionName + '价格模拟')
        plt.xticks(rotation = 30)   
        

        for i in range(0, len(data)):
            plt.plot(dates, data[i], linewidth = 0.5)
            print("第" + str(i + 1) + "条线已画")
        
        #去掉上轴和右轴
        axes = plt.gca()
        axes.spines['right'].set_color('none')
        axes.spines['top'].set_color('none')

        #设置x轴数据显示范围
        axes.set_xlim(dates[0] + datetime.timedelta(days = -1), dates[-1])
        #设置
        plt.show()