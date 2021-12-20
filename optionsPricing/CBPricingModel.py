import math
import datetime
from abc import ABCMeta,abstractmethod
import random
import numpy as np
from WindPy import w
w.start()

class ValueCB(object):
    __metaclass__ = ABCMeta #指定这是一个抽象类
    @abstractmethod  #抽象方法
    def getValue(self):
        pass


class ConvertibleBondPricingModel(ValueCB): 
    """
    stockPrices: 格式为dict  {"价格": mcData, "日期": dateList}，
                 stockPrices格式：{"价格": [[],[],[]], "日期": dateList}
                 mcData：Monte Carlo生成的所有data, a list of list
    stockPrices日期中的第一天，为定价日。
    """
    def __init__(self, bond, stockPrices, accruedInterests, redumptionProb, sellBackProb, riskFreeRate):
        self.bond = bond
        self.stockPrices = stockPrices
        self.accruedInterests = accruedInterests
        self.redumptionProb = redumptionProb
        self.sellBackProb = sellBackProb
        self.riskFreeRate = riskFreeRate
        

    def getValue(self):
        #首先 获取转股开始日的index
        pricingDate = self.stockPrices["日期"][0]
        convertStartDate = self.bond.convertStartDate
        sellBackStartDate = self.bond.sellBackClause.sellBackStartDate

        # 若开始转股日在定价日之前，转股开始日index为0，否则为正常的index
        convertStartDateIndex = max(self.getDateIndex(self.stockPrices["日期"], convertStartDate), 0)
        sellBackStartDateIndex = max(self.getDateIndex(self.stockPrices["日期"], sellBackStartDate), 0)
        print("转股开始日的index：" + str(sellBackStartDateIndex) + "， 回售开始日的index： " + str(convertStartDateIndex))
        
        presentValueSum = 0
        
        for mcLineIndex in range(0, len(self.stockPrices["价格"])): #遍历蒙特卡洛模拟上的每一条线
            currentLine = self.stockPrices["价格"][mcLineIndex]
            
            #创建2个list，每个值为boolean类型，代表从时刻0到当前时点的时间段中，是否满足赎回/回售条款。
            ifFullfillRedumptionConditionList = [False for i in range(0, len(currentLine))]
            ifFullfillSellBackConditionList = [False for i in range(0, len(currentLine))]
            numberOfDaysFromPricingToBondEndDate = len(currentLine)
            #目前的currentDate是否已经过了有可能回售的第一天
            arriveFirstDate = False 
            #是否已下修过转股价,目前的假设是只能下修一次，若下修过就不能再下修了。
            hasXiaXiu = False
            currentLineConvertPrice = self.bond.convertPrice

            #遍历蒙特卡洛模拟一条线上的每个交易日
            oneLineValue = 0
            for dateIndex in range(0, len(currentLine) - 1):
                currentDate = self.stockPrices["日期"][dateIndex]

                #检查从转股开始日到currentDate这段时期是否满足赎回条款。
                #只有当转股开始日到当前日期这段期间>=30天的时候，才有可能满足赎回条款，否则，直接check下一天的情况。
                if(dateIndex >= 29 and dateIndex - convertStartDateIndex >= 29):
                    stockPriceLimit = currentLineConvertPrice * self.bond.redumptionClause.redeemPricePercentageLimit
                    highPriceDaysLimit = self.bond.redumptionClause.redeemDaysLimit
                    prevAnswer = ifFullfillRedumptionConditionList[dateIndex - 1]
                    currAnswer = self.checkIfTriggerRedeem(currentLine, dateIndex -29, dateIndex, self.bond, currentLineConvertPrice)
                    # print("index: " + str(dateIndex) + "prev: " + str(prevAnswer) + ", currAnswer: " + str(currAnswer))
                    # if(prevAnswer):
                    #     print(str(dateIndex) + "赎回结果 prev: True")
                    # if(currAnswer):
                    #     print(str(dateIndex) + "赎回结果 curr: True")
                    isRedeem =  prevAnswer or currAnswer
                    ifFullfillRedumptionConditionList[dateIndex] = isRedeem
                    if(isRedeem):
                        value = self.bond.faceValue / currentLineConvertPrice * currentLine[dateIndex]
                        presentValue = self.getPresentValue(value, self.riskFreeRate, dateIndex/365)
                        oneLineValue = presentValue
                        print(str(mcLineIndex + 1) + ": " + "赎回，" + str(oneLineValue) + ", " + str(value) + "dateIndex: " + 
                            str(dateIndex + 1) + ", stockPriceLimit: " + str(stockPriceLimit) + ", highPriceDaysLimit: " + 
                            str(highPriceDaysLimit) + ", covnertPrice: " + str(currentLineConvertPrice) + ", " + "redeemPercentage: " + str(self.bond.redumptionClause.redeemPricePercentageLimit))
                        break
                
                # 2. check是否处于回售条款中约定的可回售期限内。
                # 回售条款：在可转债最后两个计息年度，股票在任何连续30个交易日的收盘价低于转股价的70%时，可回售
                sellBackPriceLimit = currentLineConvertPrice * self.bond.sellBackClause.sellBackPricePercentageLimit
                sellBack = False
                if(dateIndex >= 29 and dateIndex - sellBackStartDateIndex >= 29):           
                    if (arriveFirstDate):
                        sellBack = ifFullfillSellBackConditionList[dateIndex - 1] or self.checkPreviousThirtyDays(currentLine, dateIndex, sellBackPriceLimit)
                    else:
                        #check从回售期开始日到currentDate是否存在连续30日，每天价格都低于XXX
                        sellBack = self.checkConsecutives(currentLine, sellBackStartDateIndex, dateIndex, 30, sellBackPriceLimit)
                        arriveFirstDate = True

                    # # 查看是否满足回售条件，若满足，生成随机随机变量u
                    # if(pricingDate > self.bond.sellBackClause.sellBackStartDate):
                    #     sellBack = self.checkIfTriggerSellBack(currentLine, 0, dateIndex, self.bond)
                    # else:
                    #     #获取回售起始日在dateList中的index
                    #     sellBackStartDateIndex = self.getDateIndex(self.stockPrices["日期"], self.bond.sellBackClause.sellBackStartDate)
                    #     sellBack = self.checkIfTriggerSellBack(currentLine, sellBackStartDateIndex, dateIndex, self.bond)
                    
                if(sellBack):
                    #生成（0,1）随机变量u
                    u = random.random()
                    if(u < self.sellBackProb):
                        if(hasXiaXiu == False):
                            #下修转股价
                            currentLineConvertPrice = self.getReversedDownConvertiblePrice(dateIndex, currentLine, 
                                                    self.bond.xiaXiuClause.xiaXiuCoefficient, currentLineConvertPrice)
                            hasXiaXiu = True
                            print(str(dateIndex) + ", " + str(dateIndex) + "下修转股价" + str(currentLineConvertPrice))                        
                    else:
                        #回售，value为回售价格现值
                        #需要判断accruedInterests是否为nan，accuredInterest可能会出现的情况是取到的数列不为nan，但某日的值是nan
                        sellBackPrice = self.bond.faceValue
                        if(self.accruedInterests.ErrorCode != 0 and (not np.isnan(self.accruedInterests.Data[0][dateIndex]))):
                            sellBackPrice += self.accruedInterests[dateIndex]
                        presentValue = self.getPresentValue(sellBackPrice, self.riskFreeRate, dateIndex / 365)
                        oneLineValue = presentValue
                        print(str(mcLineIndex) + ", " + str(mcLineIndex + 1) + ": " + "回售，" + str(oneLineValue))
                        
                        break

                # 3. 可转债存续到到期日未被转股或回售，一直存续至到期日的可转债价值为到期赎回价值和转股价值的最大值
                # 即 𝒎𝒂𝒙((𝑭𝑽+𝑰)∗(𝟏+𝒖),𝑺t×𝑭𝑽/𝑿)，FV为债券面值，I为到期票息，u为到期赎回的上浮比例，St为到期日的股票价格，X为转股价
                # if(dateIndex == len(self.stockPrices["日期"])):

                if(dateIndex == len(currentLine) - 2):
                    redumptionValue = self.bond.faceValue 
                    if(self.accruedInterests.ErrorCode != 0 and (not np.isnan(self.accruedInterests.Data[0][dateIndex]))):
                        redumptionValue += self.accruedInterests.Data[0][dateIndex]
                    # print("accured Interest: " + str(accruedInterest) + ", date: " + str(currentDate))
                    convertValue = currentLine[dateIndex] * self.bond.faceValue / currentLineConvertPrice
                    oneLineValue = self.getPresentValue(max(redumptionValue, convertValue), self.riskFreeRate, numberOfDaysFromPricingToBondEndDate/365)
                    print(str(mcLineIndex + 1) + ": " + "持有至到期，" + str(oneLineValue))
            presentValueSum += oneLineValue

        convertibleBondValue = presentValueSum / len(self.stockPrices["价格"])
        return convertibleBondValue
        
    """
    查看可转债从转股期开始日至测试日是否触发赎回条款。
    即在转股期内，若公司股票连续 X 个交易日中至少有 Y 个交易日的收盘价格不低于当期转股价格的 Z%，则触发赎回条款。

    例：国金转债赎回条款：
    在本次发行的可转债转股期内，公司有权决定按照债券面值加当期应计利息的价格赎回全部或部分未转股的可转债，在本次发行的可转债转股期内，
    如果公司 A 股股票连续 30 个交易日中至少有 15 个交易日的收盘价格不低于当期转股价格的 130%（含 130%）。”

    data:日期和股价，字典格式{"日期":[], "价格":[]}，可转债标的股票的日期和收盘价
    duration: 连续duration个交易日中，出现至少Y个交易日收盘价高于某值
    pricingDateIndex：测试日的index
    convertStartDateIndex: 转股开始日期的index
    highPriceDaysLimit: 连续X个交易日中，出现至少highPriceDaysLimit个交易日收盘价较高
    stockPriceLimitPercentage: 赎回条款中要求的转股价格的百分比
    currentConvertiblePrie: 当期转股价格
    redeemProbLimit:触发赎回条款后，会进行赎回的概率

    目前endTestingDateIndex就是测试日，目前肯定是在可赎回的期限内的（前面已经判断过了）
    startTestingDateIndex为pricing date
    查看pricing date到currentDate，这段时间，是否满足赎回条件。即是否存在一个duration，这个duration里存在至少连续的n天股价满足一定条件
    """
    def checkIfTriggerRedeem(self, priceList, startTestingDateIndex, endTestingDateIndex, bond, currentConvertPrice):
        # print(type(bond.convertPrice)) 
        # print(type(bond.redumptionClause.redeemPricePercentageLimit))
        stockPriceLimit = currentConvertPrice * bond.redumptionClause.redeemPricePercentageLimit
        highPriceDaysLimit = bond.redumptionClause.redeemDaysLimit
        duration = bond.redumptionClause.duration

        if(endTestingDateIndex - startTestingDateIndex + 1 < duration):
            return False

        #30天sliding window遍历，testingPeriodStartIndex和testingPeriodEndIndex 分别为30天sliding window的起始和结束指针
        #首先查看第一个sliding window中价格超过界限的个数，若已符合要求，则返回True，若不符合要求，向右移动sliding window挨个查看
        #是否符合要求。向右移动时，不用重新遍历，只需查看去掉的首个和新加进来的元素是否符合要求，在前一个sliding window的结果上加减即可。
        previous = 0
        testingPeriodStartIndex = startTestingDateIndex
        while(testingPeriodStartIndex < endTestingDateIndex - duration + 2):
            testingPeriodEndIndex = testingPeriodStartIndex + duration - 1
            if(testingPeriodStartIndex == startTestingDateIndex):
                firstThirtyDaysResult = self.getDaysWithHigherPriceAboveLimit(priceList, testingPeriodStartIndex, testingPeriodEndIndex, stockPriceLimit)
                if(firstThirtyDaysResult >= bond.redumptionClause.redeemDaysLimit):
                    return True
                else:
                    testingPeriodStartIndex += 1
                    previous = firstThirtyDaysResult
            else:
                firstNumber = priceList[testingPeriodStartIndex - 1]
                lastNumber = priceList[testingPeriodEndIndex]
                if(firstNumber >= stockPriceLimit):
                    previous -= 1
                if(lastNumber >= stockPriceLimit):
                    previous += 1
                
                if(previous >= highPriceDaysLimit):
                    return True
                else:
                    testingPeriodStartIndex += 1
        return False            
        # if(ifTriggerRedumptionClause):
        #     #生成（0,1）随机变量u
        #     u = red.random()
        #     if(u < redeemProbLimit):
        #         return True
        #     else:
        #         return False
        # else:
        #     return False

    """
    检测是否回售，首先检测是否触发回售条款，若触发回售条款，生成随机数u,若u大于p下修，则回售，否则下修转股价
    例：国金转债回售条款：
    如果公司A股股票在任何连续30个交易日的收盘价格低于当期转股价格的70%时，
    可转债持有人有权将其持有的可转债全部或部分按债券面值加上当期应计利息的价格回售给公司。

    data:日期和股价，字典格式{"日期":[], "价格":[]}，可转债标的股票的日期和收盘价
    duration: 连续duration个交易日中，出现至少Y个交易日收盘价低于某值
    pricingDateIndex：测试日的index
    convertStartDateIndex: 转股开始日期的index
    highPriceDaysLimit: 连续X个交易日中，出现至少highPriceDaysLimit个交易日收盘价低于某值
    stockPriceLimitPercentage: 回售条款中要求的转股价格的百分比
    currentConvertiblePrie: 当期转股价格
    sellBackProbLimit: 下修概率p下修。即所有触发回售条款的，不一定都会下修转股价，故规定p下修，
                        例如p下修为70%，意味着达到回售条款的情况下，有70%的概率会下修转股价。
    """
    # def checkIfTriggerSellBack(self, data, startDateIndex, endDateIndex, bond, currentConvertPrice):
    #     stockPriceLimit = currentConvertPrice * bond.sellBackClause.sellBackPricePercentageLimit
    #     # if(len(data["价格"]) < bond.duration):
    #     #     return False
        
    #     if(endDateIndex - startDateIndex + 1 < bond.duration):
    #         return False

    #     #30天sliding window遍历，testingPeriodStartIndex和testingPeriodEndIndex 分别为30天sliding window的起始和结束指针
    #     #首先查看第一个sliding window中价格超过界限的个数，若已符合要求，则返回True，若不符合要求，向右移动sliding window挨个查看
    #     #是否符合要求。向右移动时，不用重新遍历，只需查看去掉的首个和新加进来的元素是否符合要求，在前一个sliding window的结果上加减即可。
    #     previous = 0
    #     testingPeriodStartIndex = startDateIndex
    #     while(testingPeriodStartIndex < endDateIndex - bond.duration + 2):
    #         testingPeriodEndIndex = testingPeriodStartIndex + bond.duration - 1
    #         if(testingPeriodStartIndex == startDateIndex):
    #             firstThirtyDaysResult = self.getDaysWithLowerPriceThanLimit(data, testingPeriodStartIndex, testingPeriodEndIndex, stockPriceLimit)
    #             if(firstThirtyDaysResult >= bond.sellBackClause.sellBackDaysLimit):
    #                 return True
    #             else:
    #                 testingPeriodStartIndex += 1
    #                 previous = firstThirtyDaysResult
    #         else:
    #             firstNumber = data[testingPeriodStartIndex - 1]
    #             lastNumber = data[testingPeriodEndIndex]

    #             if(firstNumber < stockPriceLimit):
    #                 previous -= 1
    #             if(lastNumber < stockPriceLimit):
    #                 previous += 1
    #             if(previous >= bond.sellBackClause.sellBackDaysLimit):
    #                 return True
    #             else:
    #                 testingPeriodStartIndex += 1
    #     return False           
        # if(ifTriggerSellBack):
        #     #生成（0,1）随机变量u
        #     u = red.random()
        #     if(u < sellBackProbLimit):
        #         return True
        #     else:
        #         return False
        # return False
    
    # """
    # 查看可转债从转股期开始日至定价日是否触发赎回/回售条款。
    # 是checkIfRedeem和checkIfSellBack函数的helper function

    # data:日期和股价，字典格式{"日期":[], "价格":[]}，可转债标的股票的日期和收盘价
    # duration: 连续duration个交易日中，出现至少Y个交易日收盘价高于/低于某值
    # pricingDateIndex：测试日的index
    # convertStartDateIndex: 转股开始日期的index
    # highPriceDaysLimit: 连续X个交易日中，出现至少highPriceDaysLimit个交易日收盘价高于/低于某值
    # stockPriceLimitPercentage: 赎回/回售条款中要求的转股价格的百分比
    # currentConvertiblePrie: 当期转股价格
    # classification: 字符串，"回售"或"赎回"，
    #                 赎回：查找一段时间内价格高于某值的个数
    #                 回售：查找一段时间内价格低于某值的个数
    # """
    # def checkIfTriggerClause(data, pricingDateIndex, convertStartDateIndex, bond, classification):
    #     if(classification == "赎回"):
    #         stockPriceLimit = bond.convertPrice * bond.redumptionClause.redeemPricePercentageLimit
    #     if(classification == "回售"):
    #         stockPriceLimit = bond.convertPrice * bond.sellBackClause.sellBackPricePercentageLimit
        
    #     if(len(data["价格"]) < bond.duration):
    #         return False

    #     if(pricingDateIndex - convertStartDateIndex + 1 < bond.duration):
    #         return False

    #     #30天sliding window遍历，testingPeriodStartIndex和testingPeriodEndIndex 分别为30天sliding window的起始和结束指针
    #     #首先查看第一个sliding window中价格超过界限的个数，若已符合要求，则返回True，若不符合要求，向右移动sliding window挨个查看
    #     #是否符合要求。向右移动时，不用重新遍历，只需查看去掉的首个和新加进来的元素是否符合要求，在前一个sliding window的结果上加减即可。
    #     previous = 0
    #     testingPeriodStartIndex = convertStartDateIndex
    #     while(testingPeriodStartIndex < pricingDateIndex - duration + 2):
    #         testingPeriodEndIndex = testingPeriodStartIndex + duration - 1
    #         if(testingPeriodStartIndex == convertStartDateIndex):
    #             if(classification == "赎回"):
    #                 firstThirtyDaysResult = getDaysWithHigherPriceAboveLimit(data["价格"], testingPeriodStartIndex, testingPeriodEndIndex, stockPriceLimit)
    #             if(classification == "回售"):
    #                 firstThirtyDaysResult = getDaysWithLowerPriceThanLimit(data["价格"], testingPeriodStartIndex, testingPeriodEndIndex, stockPriceLimit)
    #             if(firstThirtyDaysResult >= highPriceDaysLimit):
    #                 return True
    #             else:
    #                 testingPeriodStartIndex += 1
    #                 previous = firstThirtyDaysResult
    #         else:
    #             firstNumber = data["价格"][testingPeriodStartIndex - 1]
    #             lastNumber = data["价格"][testingPeriodEndIndex]
    #             if(classification == "赎回"):
    #                 if(firstNumber >= stockPriceLimit):
    #                     previous -= 1
    #                 if(lastNumber >= stockPriceLimit):
    #                     previous += 1
    #             if(classification == "回售"):
    #                 if(firstNumber < stockPriceLimit):
    #                     previous -= 1
    #                 if(lastNumber < stockPriceLimit):
    #                     previous += 1
    #             if(previous >= highPriceDaysLimit):
    #                 return True
    #             else:
    #                 testingPeriodStartIndex += 1
    #     return False            
    

    """
    检测某段时间内，股价不低于某价格的天数(用于检测是否触发赎回条款)
    """
    def getDaysWithHigherPriceAboveLimit(self, priceList, startDateIndex, endDateIndex, stockPriceLimit):
        numberOfHighPriceDate = 0
        for i in range(startDateIndex, endDateIndex + 1):
            if(priceList[i] >= stockPriceLimit):
                numberOfHighPriceDate += 1
        return numberOfHighPriceDate


    # """
    # 检测某段时间内，股价低于某价格的天数(用于检测是否触发回售条款)
    # """
    # def getDaysWithLowerPriceThanLimit(self, priceList, startDateIndex, endDateIndex, stockPriceLimit):
    #     numberOfLowPriceDate = 0
    #     for i in range(startDateIndex, endDateIndex + 1):
    #         if(priceList[i] < stockPriceLimit):
    #             numberOfLowPriceDate += 1
    #     return numberOfLowPriceDate
    

    # #计算现值
    # def getDiscountedNumber(self, riskFreeRate, futureValue, startDateIndex, endDateIndex):
    #         return futureValue / math.exp(riskFreeRate * ((endDateIndex - startDateIndex) / 365)) 

    """
    获取下修的转股价格
    计算逻辑为表决日前二十个交易日的均价与前一交易日价格的较大者，乘以reverseDownCoefficient。这个结果与当前转股价的较小者。
    """
    def getReversedDownConvertiblePrice(self, currentDateIndex, data, reverseDownCoefficient, currentConvertiblePrie):
        previousSum = 0
        index = currentDateIndex - 1
        while(index >= currentDateIndex - 20):
            previousSum += data[index]
            index -= 1
        return min(reverseDownCoefficient * max(previousSum / 20, data[currentDateIndex - 1]), currentConvertiblePrie)

    # """
    # 找出转股期/回售期/赎回期开始日在data中的index并返回
    # """
    # def getStartIndex(self, stockPrices, bond, classification):
    #     startDateIndex = 0
    #     for i in range(0, len(stockPrices["价格"])):
    #         if(classification == "转股期"):
    #             if(stockPrices["日期"][i] == bond.convertStartDate):
    #                 startDateIndex = i
    #                 break
    #         if(classification == "赎回期"):
    #             if(stockPrices["日期"][i] == bond.redumptionClause.redeemStartDate):
    #                 startDateIndex = i
    #                 break
    #         if(classification == "回售期"):
    #             if(stockPrices["日期"][i] == bond.sellBackClause.sellBackStartDate):
    #                 startDateIndex = i
    #                 break
    #     return startDateIndex    

    # def checkIfWithinDateRange(self, currentDate, startDate, endDate):
    #     return (currentDate <= endDate and currentDate >= startDate)

    
    # """        
    # 对所有利息除了最后一次发放利息，计算终值并返回
    # （因为通常兑现条款如下：本公司将以本次发行的可转债的票面面值上浮6.6%的价格
    # （含最后一期年度利息）向投资者赎回全部未转股的可转债。）
    # cashFlowList：所有利息list

    # """
    # def getInterestFutureValue(self, cashFlowList, riskFreeRate):
    #     interestsNeedToCalculateFV = cashFlowList[0:-1]
    #     totalNumberCF = len(cashFlowList)
    #     totalFutureValue = 0
    #     for i in range(0, len(cashFlowList)):
    #         futureValue = cashFlowList[i] * math.pow((1 + riskFreeRate), totalNumberCF - i - 1)
    #         totalNumberCF += futureValue
    #     return totalFutureValue 


    # def getValueAtMaturity(self, convertibleBond, paybackPercentage, riskFreeRate, stockPrice, convertPrice):
    #     bondFutureValue = convertibleBond.faceValue * (1 + paybackPercentage) + self.getInterestFutureValue(
    #                         convertibleBond.interestList, riskFreeRate)
    #     stockFutureValue = convertibleBond.faceValue / convertPrice * stockPrice[-1]
    #     max(self.getPresentValue(bondFutureValue), self.getPresentValue(stockFutureValue))



    #计算现值（复利）：future value除以 e^(rt)，为计算该数的现值，用连续复利方式
    # duration: 单位为年
    def getPresentValue(self, futureValue, riskFreeRate, duration):
        return futureValue / math.exp(riskFreeRate * duration)
    


    #获取一个date在一个dateList中的index，dateList为顺序从小到大排列
    def getDateIndex(self, dateList, date):
        if(date < dateList[0]):
            return -1
        #wind函数：查看两个date之间有多少个交易日（包含这两个日期）
        daysDiff = w.tdayscount(dateList[0], date, "").Data[0][0] 
        return daysDiff - 1

    #check 一个list中，从start到end index是否存在连续duration天，每天小于priceLimit的
    def checkConsecutives(self, arr, convertStartIndex, currentDateIndex, duration, priceLimit):
        if(currentDateIndex - convertStartIndex + 1 < duration):
            return False
        else:
            start = convertStartIndex
            end = convertStartIndex
            while(end < len(arr) - 1):
                if(arr[end] < priceLimit):
                    end += 1
                    if(end - start >= duration):
                        return True
                else:
                    start = end + 1
                    end = start
            return False
    
    def checkPreviousThirtyDays(self, arr, currentIndex, priceLimit):
        for i in range(currentIndex, currentIndex - 30, -1):
            if(arr[currentIndex] >= priceLimit):
                return False
        return True
    
    # def pricingForDuration(startDate, endDate, pricingStock):
 
