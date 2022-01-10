import random as rd
import math
import datetime
import pandas as pd
from WindPy import w
import numpy as np
w.start()
from CBPricingModel import ConvertibleBondPricingModel
from ConvertibleBond import ConvertibleBond, RedumptionClause, XiaxiuClause, SellBackClause
from ChinaBondCorporateBondYieldData import ChinaBondCorporateBondYieldData
from MC import MonteCarlo, StockPriceEngine
from Volatility import HistoricalVolatility
from ChinaBondTreasuryYieldData import ChinaBondTreasuryYieldData




resultList = []
for i in range(0, 1):

    """可转债代码"""
    CONVERTIBLE_BOND_CODE = "113555.SH"
    """债券面值"""
    FACE_VALUE = 100
    """可转债起息日"""
    ISSUE_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "carrydate").Data[0][0]
    """可转债摘牌日"""
    END_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "delist_date").Data[0][0]
    """标的股票代码"""
    STOCK_CODE = w.wsd(CONVERTIBLE_BOND_CODE, "underlyingcode", ISSUE_DATE, ISSUE_DATE, "").Data[0][0]
    """标的股票名称"""
    STOCK_NAME = w.wsd(CONVERTIBLE_BOND_CODE, "underlyingname", ISSUE_DATE, ISSUE_DATE, "").Data[0][0]
    print("可转债：" + CONVERTIBLE_BOND_CODE + ", " + "标的股票：" + STOCK_NAME + STOCK_CODE)

    """一年交易日天数"""
    TRADING_DAYS_PER_YEAR = 250
    """条款中要求的连续DURATION个交易日股价XXX"""
    DURATION = 30
    NUMBER_OF_SIMULATION = 1000
    PRICING_DATE_str = "2020-08-21"
    PRICING_DATE = datetime.datetime.strptime(PRICING_DATE_str, "%Y-%m-%d")
    #剩余期限（年）
    leftYearsToMaturity = w.wsd(CONVERTIBLE_BOND_CODE, "ptmyear", PRICING_DATE_str, PRICING_DATE_str, "").Data[0][0]
    print("剩余年限：" + str(leftYearsToMaturity))
    """
    债券评级：
    主体评级：对发债企业本身做整体信用评估，
    债项评级：同一企业发行不同的债券条款可能存在不同，债项评级是针对具体某一笔债务安全性的判断
    """
    creditRating = w.wsd(CONVERTIBLE_BOND_CODE, "creditrating", ISSUE_DATE, ISSUE_DATE, "").Data[0][0]

    """
    无风险利率:使用与可转债同期限的国债到期收益率作为无风险利率，东吴证券模型用此利率作为几何布朗运动的构建和未来价值的折现。
    """

    RISK_FREE_RATE = ChinaBondTreasuryYieldData().getRiskFreeRate(PRICING_DATE_str, leftYearsToMaturity)
    print("无风险利率：" + str(RISK_FREE_RATE))
    print("无风险利率的年数：" + str(leftYearsToMaturity))

    """根据债券评级获取相应的中债收益率作为折现率（定价日前一日的中债企业债收益率）"""
    corporateBondYieldObj = ChinaBondCorporateBondYieldData()
    listOfDates = w.tdays(PRICING_DATE, END_DATE, "").Data[0]
    allDiscountRates = corporateBondYieldObj.getEachDayDiscountRate(listOfDates, PRICING_DATE_str, creditRating)
    discountRate = allDiscountRates[PRICING_DATE] / 100
    print("所有日期的discount Rates已计算完毕")
    print("定价日的discount Rate：" + str(discountRate))

    # corporateBondYieldData = corporateBondYieldObj.getData()[PRICING_DATE_str][creditRating]
    # discountRate = corporateBondYieldObj.getDiscountRate(corporateBondYieldData, 0.5)/100
    # calculate discount rate for each date and save in data structure

    """可转债转股期开始日"""
    CONVERT_START_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_conversion_2_swapsharestartdate").Data[0][0]
    CONVERT_END_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_conversion_2_swapshareenddate").Data[0][0]
    INITIAL_CONVERT_PRICE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_conversion2_swapshareprice", 
                ISSUE_DATE, ISSUE_DATE, "").Data[0][0]

    """可转债回售期开始日"""
    SELLBACK_START_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_putoption_conditionalputbackstartenddate").Data[0][0]
    SELLBACK_END_DATE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_putoption_conditionalputbackenddate").Data[0][0]
    SELLBACK_DAYS_LIMIT = w.wsd(CONVERTIBLE_BOND_CODE, "clause_putoption_putbacktriggermaxspan").Data[0][0]
    SELLBACK_PRICE_LIMIT_PERCENTAGE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_putoption_redeem_triggerproportion").Data[0][0] / 100
    SELLBACK_PROBABILITY = 0.6

    """可转债赎回期开始日"""
    REDEEM_START_DATE = datetime.datetime.strptime("2015-08-03", "%Y-%m-%d")
    REDEEM_END_DATE = datetime.datetime.strptime("2021-02-01", "%Y-%m-%d")
    """赎回条款中规定的股价变化的比例"""
    REDUMPTION_STOCK_PRICE_LIMIT_PERCENTAGE = w.wsd(CONVERTIBLE_BOND_CODE, "clause_calloption_triggerproportion").Data[0][0]/100
    """赎回条款中的连续DURATION个交易日至少有HIGH_PRICE_DAYS_LIMIT个交易日股价满足某条件"""
    REDUMPTION_DAYS_LIMIT = w.wsd(CONVERTIBLE_BOND_CODE, "clause_calloption_redeemspan").Data[0][0]
    """触发赎回条款后的赎回概率"""
    REDUMPTION_PROBABILITY = 1

    """可转债修正开始日"""
    XIAXIU_COEFFICIENT = 1.1
    XIAXIU_START_DATE = ISSUE_DATE

    #获取从上市日至摘牌日的标的价格
    stockPriceWindData = w.wsd(STOCK_CODE, "close", ISSUE_DATE, END_DATE, "")
    stockPrice = {"价格":stockPriceWindData.Data[0], "日期":stockPriceWindData.Times, "价格日期格式": []}

    #获取中债收益率数据,返回格式为dict：{"YYYY-MM-DD":{'spotRateEndDate':[], 'spotRate':[]}}, 包含从2014年至2021年的数据
    # chinaBondYieldData = ChinaBondCorporateBondYieldData().getData()

    #建立各个clause的object
    redumptionClause = RedumptionClause(DURATION, REDUMPTION_DAYS_LIMIT, REDUMPTION_STOCK_PRICE_LIMIT_PERCENTAGE, REDEEM_START_DATE, REDEEM_END_DATE)
    sellBackClause = SellBackClause(DURATION, SELLBACK_DAYS_LIMIT, SELLBACK_PRICE_LIMIT_PERCENTAGE, SELLBACK_START_DATE, SELLBACK_END_DATE)
    xiaXiuClause = XiaxiuClause(XIAXIU_COEFFICIENT, XIAXIU_START_DATE)

    #建立一个可转债
    accruedInterests = w.wsd(CONVERTIBLE_BOND_CODE, "accruedinterest", ISSUE_DATE, END_DATE, "")
    convertibleBond = ConvertibleBond(STOCK_CODE, CONVERTIBLE_BOND_CODE, ISSUE_DATE, END_DATE,  
                                        CONVERT_START_DATE, CONVERT_END_DATE, INITIAL_CONVERT_PRICE, FACE_VALUE, redumptionClause, 
                                        sellBackClause, xiaXiuClause, DURATION)
    print("convertible bond object已生成")

    #获取要进行蒙特卡洛模拟的日期list，i.e 从定价日期至可转债到期日的日期list
    dateList = w.tdays(PRICING_DATE, END_DATE, "").Data[0]

    #计算波动率
    volatilityAndAnnualReturn = HistoricalVolatility(STOCK_CODE, TRADING_DAYS_PER_YEAR, PRICING_DATE + datetime.timedelta(days = -365), 
                                                            PRICING_DATE + datetime.timedelta(days = -1)).getVolatility()
    stockVolatility = volatilityAndAnnualReturn
    # annualHistoricalReturn = volatilityAndAnnualReturn[0]
    print("波动率为：" + str(stockVolatility))
    # print("年化收益率为：" + str(annualHistoricalReturn))
    print("定价日：" + PRICING_DATE_str)

    #获取标的股票价格的蒙特卡洛模拟结果, 从可转债起息日至最后一天上市日
    carryInterestStartDatePrice = w.wsd(STOCK_CODE, "close", PRICING_DATE, PRICING_DATE, "").Data[0][0]
    mc = MonteCarlo(convertibleBond.stockCode, carryInterestStartDatePrice, RISK_FREE_RATE, TRADING_DAYS_PER_YEAR, stockVolatility, NUMBER_OF_SIMULATION, dateList)
    mcData = mc.getPrice()

    # df = pd.read_csv('mc_result.csv')
    # df_list = df.T.values.tolist()
    # mcData = df_list[1:]
    
    mcDataWithDateInDt = {"价格": mcData, "日期": dateList}
    print("蒙特卡洛模拟已生成")
    print("蒙特卡洛模拟次数：" + str(len(mcData)))
    print("蒙特卡洛每条线长度：" + str(len(mcData[0])))
    mc.drawLineChart(mcData, dateList, STOCK_NAME)

    # #建立定价模型
    # model = ConvertibleBondPricingModel(convertibleBond, mcDataWithDateInDt, accruedInterests, REDUMPTION_PROBABILITY, SELLBACK_PROBABILITY, discountRate)
    # actualPrice = w.wsd(CONVERTIBLE_BOND_CODE, "close", PRICING_DATE, PRICING_DATE, "").Data[0][0]
    # resultList.append(model.getValue())
    # print("定价已完成" + str(i + 1))
    # print("估值结果" + str(model.getValue()) + "实际价格：" + str(actualPrice)) 

    # """将蒙特卡洛模拟价格打印至csv文件"""
    # keys = np.arange(1, NUMBER_OF_SIMULATION + 1, 1).tolist()
    # mc_df = pd.DataFrame(dict(zip(keys, mcData)))
    # mc_df.to_csv("mc_result.csv")
    # print("已打印至csv")

# dict = {"result" : resultList}
# df = pd.DataFrame(dict)
# df.to_csv("CBPricing100Times-113555SH.csv")

