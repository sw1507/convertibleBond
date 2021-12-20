import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from matplotlib.font_manager import FontProperties
from abc import ABCMeta,abstractmethod
import pandas as pd
import numpy as np
from random import gauss
from math import exp, sqrt
import math
import datetime
import matplotlib.pyplot as plt
from WindPy import w
import Ipynb_importer
from Option import OrdinaryOption
w.start()

class ValueOption(object):
    __metaclass__ = ABCMeta #指定这是一个抽象类
    @abstractmethod  #抽象方法
    def getValue(self):
        pass

class LongstaffPricingModel(ValueOption): 
    
    def __init__(self, option, discountFactor, stockPrices):
        self.option = option
        self.discountFactor = discountFactor
        self.stockPrices = stockPrices
        self.totalTradingDays = len(stockPrices[0])

    def getValue(self):
#         DISCOUNT_FACTOR = 0.94176
        self.strikingPrice = self.option.strikingPrice
        self.optionType = self.option.optionType
#         stockPrices = [[1, 1.09, 1.08, 1.34], 
#                       [1, 1.16, 1.26, 1.54], 
#                       [1, 1.22, 1.07, 1.03], 
#                       [1, 0.93, 0.97, 0.92], 
#                       [1, 1.11, 1.56, 1.52],
#                       [1, 0.76, 0.77, 0.9], 
#                       [1, 0.92, 0.84, 1.01],
#                       [1, 0.88, 1.22, 1.34]]
#         totalTradingDays = len(stockPrices[0])

        #一个二维数组，代表每条path每个时间点上，每一个点的行权收益
        optionPayOffData = self.getOptionPayOffData(self.stockPrices, self.option)

        #创建一个二维数组，用来存储每条path每个时间点上是否行权的信息，1为行权，0为不行权
        exersizeTimeTable = [[0 for i in range(self.totalTradingDays)] for i in range(len(self.stockPrices))]

        #创建一个二维数组，用来存储每条path每个时间点上的real cash flow
        cashFlowTable = [[0 for i in range(self.totalTradingDays)] for i in range(len(self.stockPrices))]
        ##########################################################################################################
       
        #更新行权时间表中最后一列
        dateIndex = self.totalTradingDays - 1
        for pathIndex in range(0, len(optionPayOffData)):
            exerciseDayPayoff = optionPayOffData[pathIndex][dateIndex]
            if(exerciseDayPayoff > 0):
                exersizeTimeTable[pathIndex][dateIndex] = 1
        #更新CF table最后一列
        self.updateCashFlowTable(exersizeTimeTable, cashFlowTable, optionPayOffData)
        
        #循环
        for dateIndex in range(self.totalTradingDays - 2, 0, -1):
            #check倒数第二天中，in the money的情况
            regression_X = []
            regression_Y = []
            regression_pathIndex = []
        #     dateIndex = totalTradingDays - 2       
            for pathIndex in range(0, len(optionPayOffData)):
                payoff = optionPayOffData[pathIndex][dateIndex]
                if(payoff > 0):
                    regression_pathIndex.append(pathIndex)
                    regression_X.append(self.stockPrices[pathIndex][dateIndex])
                    if(dateIndex == self.totalTradingDays - 2):
                        regression_Y.append((optionPayOffData[pathIndex][dateIndex + 1]) * self.discountFactor)
                    else:
                        regression_Y.append((cashFlowTable[pathIndex][dateIndex + 1]) * self.discountFactor)

            
            if(len(regression_X) > 0):#如果需要做regression的数据array不为空，才做regression
                
                #regression：T3和T2
                # print("regreesionX: " + str(regression_X) + " regressionY: " + str(regression_Y))
                regressionResult = self.leastSquaresRegression(regression_X, regression_Y, 2)        
                # print("x列index：" + str(dateIndex) + "regression结果： " + str(regressionResult))
                #根据regression结果，做出比较，若payOffAtCurrent>payOffContinuation则current行权，并更新exerciseTimeTable该点为1，该点后面所有1改为0，因为期权整个期间只能行权一次
                #并更新cash flow table
                for i in range(0, len(regression_Y)):
                    pathIndex = regression_pathIndex[i]#在大表中的path index
                    payOffContinuation = regression_X[i] * regression_X[i] * regressionResult[0] + regression_X[i] * regressionResult[1] + regressionResult[2]
                    payOffAtCurrent = optionPayOffData[pathIndex][dateIndex]
                    if(payOffAtCurrent > payOffContinuation):
                        exersizeTimeTable[pathIndex][dateIndex] = 1
                        self.updateFollowingsToZero(exersizeTimeTable, pathIndex, dateIndex)
                        self.updateCashFlowTable(exersizeTimeTable, cashFlowTable, optionPayOffData)



        #计算价格
        totalPrice = 0
        for rowIndex in range(0, len(exersizeTimeTable)):
            currentRow = exersizeTimeTable[rowIndex]
            for i in range(1, len(currentRow)):
                if(currentRow[i] == 1):
                    totalPrice = totalPrice + self.getDiscountedNumber(self.discountFactor, cashFlowTable[rowIndex][i], i)    
                    break
        optionPrice = totalPrice / len(self.stockPrices)
        # print("cash flow表格： ")
        # print(pd.DataFrame(cashFlowTable))
        return optionPrice
    
    def getOptionPayOffData(self, stockPrices, option):
        """
        获取期权所有蒙特卡洛模拟价格路径中，每个点的行权收益。
        返回：二维数组
        """
        #新建一个二维数组，与stockPrice size一样，用来存储期权收益数据
        optionPayoffData = [[0 for i in range(len(stockPrices[0]))] for i in range(len(stockPrices))]

        #遍历optionPayoffData所有数字更新每个数字为在该点行权的期权收益。
        for pathIndex in range(0, len(stockPrices)):
            for dateIndex in range(0, len(stockPrices[0])):
                optionPayoffData[pathIndex][dateIndex] = self.option.option_payoff(stockPrices[pathIndex][dateIndex])
        return optionPayoffData
    
    def leastSquaresRegression(self, x, y, highestPower):
        """
        对x，y最最小二乘
        输入：x，y 均为list
        输出：list, 为回归的结果的所有系数，顺序从高次到低次排列。
        """
        factors = np.polyfit(x, y, highestPower)
        return factors
    
    def updateCashFlowTable(self, whenToExerciseTable, cashFlowTable, payOffTable):
        for pathIndex in range(0, len(cashFlowTable)):
            for dateIndex in range(0, len(cashFlowTable[0])):
                if(whenToExerciseTable[pathIndex][dateIndex] == 1):
                    cashFlowTable[pathIndex][dateIndex] = payOffTable[pathIndex][dateIndex]
                else:
                    cashFlowTable[pathIndex][dateIndex] = 0
                    
    def updateFollowingsToZero(self, whenToExerciseTable, currentRowIndex, currentColumnIndex):
        currentRow = whenToExerciseTable[currentRowIndex]
        for i in range(currentColumnIndex + 1, len(currentRow)):
            if(currentRow[i] == 1):
                currentRow[i] = 0
                
    def getDiscountedNumber(self, discountFactor, originalNumber, dateIndex):
        discountResult = originalNumber
        for i in range(0, dateIndex):
            discountResult = discountResult * discountFactor
        return discountResult  