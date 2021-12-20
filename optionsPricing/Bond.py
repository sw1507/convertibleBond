import QuantLib as ql
from ChinaBondTreasuryYieldData import ChinaBondTreasuryYieldData
from ChinaBondCorporateBondYieldData import ChinaBondCorporateBondYieldData
import datetime

"""
https://blog.csdn.net/ndhtou222/article/details/109831509
Docs:https://quantlib-python-docs.readthedocs.io/en/latest/
"""

"""
Bond类
stockCode:代码
issueDate:债券起息日,字符串格式"YYYY-MM-DD"
endDate:债券到期日,字符串格式"YYYY-MM-DD"
couponRate: 
faceValue:面值
yieldData: 收益率信息

"""
class Bond:   

    def __init__(self, issueDate, endDate, couponRate, faceValue, yieldData, rating, couponFrequencyPerYear):
        """
        issueDate: 字符串格式
        endDate: 字符串格式
        couponRate: 票息利率, 格式为decimal
        faceValue:
        yieldData: 用于构建spotRates用的，spotRates要求的格式是a list of decimals.
        rating:
        couponFrequencyPerYear:每年付息次数，annual为1，semiAnnual为2
        """
        self.issueDate = issueDate
        self.endDate = endDate
        self.couponRate = couponRate
        self.faceValue = faceValue
        self.yieldData = yieldData
        self.rating = rating
        self.couponFrequencyPerYear = couponFrequencyPerYear
        
    def getValue(self, pricingDate):
        #定义当前日期（本例子是2015年1月15日）
        pricingDate_dt = datetime.datetime.strptime(pricingDate, '%Y-%m-%d')
        todaysDate = ql.Date(pricingDate_dt.day, pricingDate_dt.month, pricingDate_dt.year)
        ql.Settings.instance().evaluationDate = todaysDate

        #获取中债收益率数据, dict格式
        # chinaBondData = ChinaBondYieldData().getData()
        
        #即期利率对应日期
        spotDates = self.convertListOfDatesToQLDates(self.yieldData[pricingDate][self.rating]["date"])
        print(spotDates)
        
        #即期利率，初始设定为0
        spotRates = self.divideSpotRatesByOneHundred(self.yieldData[pricingDate][self.rating]["yieldData"])
        print(spotRates)

        #天数计数规则
        dayCount = ql.Thirty360()

        #例子是美国国债，因此设定为美国日历
        calendar = ql.China()

        #插值方法为线性
        interpolation = ql.Linear()

        #计息方式为复利
        compounding = ql.Compounded

        #计息频率为年
        compoundingFrequency = ql.Annual

        #即期利率假设满足零息债券收益率曲线
        spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation, compounding, compoundingFrequency)

        #利率的期限结构
        spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

        #发行日期
        issueDate_dt = datetime.datetime.strptime(self.issueDate,'%Y-%m-%d')
        issueDate_ql = ql.Date(issueDate_dt.day, issueDate_dt.month, issueDate_dt.year)

        #到期日期
        matureDate_dt = datetime.datetime.strptime(self.endDate,'%Y-%m-%d')
        maturityDate_ql = ql.Date(matureDate_dt.day, matureDate_dt.month, matureDate_dt.year)

        #付息期限
        if(self.couponFrequencyPerYear == 1):
            tenor = ql.Period(ql.Annual)
        else:
            tenor = ql.Period(ql.Semiannual)
        
        #日历
        calendar = ql.China()

        #遇到假期的调整情况
        bussinessConvention = ql.Unadjusted

        #日期的生成规则（向后推）
        dateGeneration = ql.DateGeneration.Backward

        #是否月最后一日
        monthEnd = False

        #生成时间表
        schedule = ql.Schedule(issueDate_ql, maturityDate_ql, tenor, calendar, bussinessConvention, bussinessConvention, dateGeneration, monthEnd)
        print(list(schedule))

        #息票率
        dayCount = ql.Thirty360()
        coupons = [self.couponRate]

        #构建固定利率债券
        settlementDays = 0
        faceValue = 100
        fixedRateBond = ql.FixedRateBond(settlementDays, self.faceValue, schedule, coupons, dayCount)
        
        # 以期限结构作为输入值，创建债券定价引擎
        # 使用贴现模型进行估值
        bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
        fixedRateBond.setPricingEngine(bondEngine)
        
        # 债券估值
        # print(f'固定利率债券估值为：{fixedRateBond.NPV():.4f}')
        return fixedRateBond.NPV()

    def convertListOfDatesToQLDates(self, datesList):
        result = []
        for date in datesList:
            result.append(ql.Date(date.day, date.month, date.year))
        return result


    def divideSpotRatesByOneHundred(self, spotRateList):
        result = []
        for rate in spotRateList:
            result.append(rate/100)
        return result