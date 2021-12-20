"""
可转债的类
stockCode:标的股票代码
convertibleBondCode: 可转债代码
issueDate:可转债起息日
endDate:可转债摘牌日
convertStartDate:可转债转股期开始日
convertPrice:转股价格
faceValue:面值
duration：条款中要求的连续duration个交易日股价满足某条件
"""
class ConvertibleBond:   
    def __init__(self, stockCode, convertibleBondCode, issueDate, endDate, convertStartDate, 
                convertEndDate, convertPrice, faceValue, redumptionClause, sellBackClause, xiaXiuClause, duration):
        self.stockCode = stockCode
        self.convertibleBondCode = convertibleBondCode
        self.issueDate = issueDate
        self.endDate = endDate
        self.convertStartDate = convertStartDate
        self.convertEndDate = convertEndDate
        self.convertPrice = convertPrice
        self.faceValue = faceValue
        self.redumptionClause = redumptionClause
        self.sellBackClause = sellBackClause
        self.xiaXiuClause = xiaXiuClause
        self.duration = duration

"""
赎回条款：

例：“在本次发行的可转债转股期内，公司有权决定按照债券面值加当期应计利息的价格赎回全部或部分未转股的可
转债，在本次发行的可转债转股期内，如果公司 A 股股票连续 30 个交易日中至少有 15 个交易日的收盘价格
不低于当期转股价格的 130%（含 130%）。”

duration：条款中要求的连续duration个交易日股价满足某条件
redeemDaysLimit：条款中要求的连续duration个交易日至少有redeemDaysLimit个交易日股价满足某条件
redeemPriceLimit：赎回条款中规定的股价变化的比例
redeemProbability：触发赎回条款后的赎回概率
redeemStartDate：可转债转可赎回开始日
"""
class RedumptionClause:   
    def __init__(self, duration, redeemDaysLimit, redeemPricePercentageLimit, redeemStartDate = "", redeemEndDate = ""):
        self.redeemPricePercentageLimit = redeemPricePercentageLimit
        self.duration = duration
        self.redeemDaysLimit = redeemDaysLimit
        self.redeemStartDate = redeemStartDate
        self.redeemEndDate = redeemEndDate


"""
回售条款

例：“本次发行的可转债最后两个计息年度，如果公司A股股票在任何连续30个交易日的收盘价格低于当期转股价格的70%时，
可转债持有人有权将其持有的可转债全部或部分按债券面值加上当期应计利息的价格回售给公司。”

duration：条款中要求的连续duration个交易日股价满足某条件
sellBackDaysLimit：回售中要求的连续duration个交易日至少有sellBackDaysLimit个交易日股价满足某条件
sellBackPriceLimit：回售条款中规定的股价变化的比例
sellBackStartDate：可转债转可回售开始日
"""
class SellBackClause:
    def __init__(self, duration, sellBackDaysLimit, sellBackPricePercentageLimit, sellBackStartDate = "", sellBackEndDate = ""):
        self.sellBackPricePercentageLimit = sellBackPricePercentageLimit
        self.sellBackDaysLimit = sellBackDaysLimit
        self.sellBackStartDate = sellBackStartDate
        self.sellBackEndDate = sellBackEndDate
        self.duration = duration


"""
xiaXiuCoefficient：转股价下修比例
xiuZhengStartDate：可转债下修开始日
"""
class XiaxiuClause:
    def __init__(self, xiaXiuCoefficient, xiuZhengStartDate = ""):
        self.xiaXiuCoefficient = xiaXiuCoefficient      
        self.xiuZhengStartDate = xiuZhengStartDate