from MC import MonteCarlo
from Model import LongstaffPricingModel
from Option import OrdinaryOption
from Volatility import HistoricalVolatility
import pandas as pd
import datetime
import Chart
from WindPy import w
w.start()

STOCK_CODE = "000300.SH"
OPTION_CODE = "IO2006-P-4400.CFE"
OPTION_TYPE = "PUT"
STRIKING_PRICE = 4400
RISK_FREE_RATE = 2.6300 / 100
TRADING_DATES_PER_YEAR = 240
SIMULATIONS = 100
OPTION_START_DATE = "2019-12-23"
OPTION_STRIKE_DATE = "2020-06-19"
PRICING_DATE = "2019-12-23"
MULTIPLIER = 1
CHART_TITLE = OPTION_CODE + "期权定价对比(Longstaff + Monte Carlo)" + str(SIMULATIONS)

optionObj = OrdinaryOption(OPTION_TYPE, STRIKING_PRICE, MULTIPLIER, OPTION_START_DATE, OPTION_STRIKE_DATE, STOCK_CODE, OPTION_CODE)

#计算波动率
OPTION_START_DATE_dt = datetime.datetime.strptime(OPTION_START_DATE,"%Y-%m-%d")
stockVolatility = HistoricalVolatility(STOCK_CODE, TRADING_DATES_PER_YEAR, OPTION_START_DATE_dt + datetime.timedelta(days = -365), 
                                                        OPTION_START_DATE_dt + datetime.timedelta(days = -1)).getVolatility()
print("波动率：" + str(stockVolatility))

def valueOptionAtOneDate(pricingDate, option, tradingDaysPerYear, riskFreeRate, numberOfSimulation, stockVolatility):
    PRICING_DATE_dt = datetime.datetime.strptime(pricingDate,"%Y-%m-%d")
    
    #获取测试日期的实际期权价格                                                    
    actualPrice = w.wsd(option.optionCode, "close", pricingDate, pricingDate, "").Data[0][0]

    #从测试日到期权行权日的日期序列
    dateList = w.tdays(pricingDate, option.endDate, "").Data[0]

    #获取测试日的标的价格
    pricingDateStockPrice = w.wsd(option.stockCode, "close", pricingDate, pricingDate, "").Data[0][0]

    # mc.printResult()
    # pd.DataFrame(stockPrices).to_csv("monteCarloData.csv")

    discountFactor = 1 / (1 + riskFreeRate)
    stockPrices = MonteCarlo(option.stockCode, pricingDateStockPrice, riskFreeRate, tradingDaysPerYear, 
                            stockVolatility, numberOfSimulation, dateList).getPrice()
    model = LongstaffPricingModel(option, discountFactor, stockPrices)
    return [model.getValue(), actualPrice]

actualData = []
predictedData = []
testingDateList = []
testList = w.tdays(OPTION_START_DATE, OPTION_STRIKE_DATE, "").Data[0]
for date in testList:
    testingDateList.append(date.strftime("%Y-%m-%d"))

for date in testingDateList:
    result = valueOptionAtOneDate(date, optionObj, TRADING_DATES_PER_YEAR, RISK_FREE_RATE, SIMULATIONS, stockVolatility)
    predictedData.append(result[0])
    actualData.append(result[1])
    print(date + "： 预测已结束")

chart = Chart.LineChart(testingDateList, predictedData, "预测数据", actualData, "实际数据")
chart.draw(CHART_TITLE)

pd.DataFrame({"Date":testingDateList, "predicted Data": predictedData, "actual data" : actualData}).to_csv("定价结果"+ CHART_TITLE + ".csv")
# result = valueOptionAtOneDate(PRICING_DATE, optionObj, TRADING_DATES_PER_YEAR, RISK_FREE_RATE, SIMULATIONS)
# print(result[0], result[1])







# actualOptionPrice = w.wsd(OPTION_CODE, "close", PRICING_DATE, PRICING_DATE, "").Data[0][0]


# stockPrices = [[1, 1.09, 1.08, 1.34], [1, 1.16, 1.26, 1.54], [1, 1.22, 1.07, 1.03], 
#                 [1, 0.93, 0.97, 0.92], [1, 1.11, 1.56, 1.52],[1, 0.76, 0.77, 0.9], 
#                 [1, 0.92, 0.84, 1.01],[1, 0.88, 1.22, 1.34]]
# stockPrices = w.wsd("000300.SH", "close", OPTION_START_DATE, OPTION_STRIKE_DATE, "").Data

