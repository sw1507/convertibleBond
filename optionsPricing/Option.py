from abc import ABCMeta,abstractmethod

class Option(object):
    __metaclass__ = ABCMeta #指定这是一个抽象类
    @abstractmethod  #抽象方法
    def option_payoff(self):
        pass

class OrdinaryOption:   
    def __init__(self, optionType, strikingPrice, multiplier, startDate = "", endDate = "", stockCode = "", optionCode = ""):
        self.optionType = optionType
        self.strikingPrice = strikingPrice
        self.multiplier = multiplier
        self.startDate = startDate
        self.endDate = endDate
        self.stockCode = stockCode
        self.optionCode = optionCode
    
    def option_payoff(self, stockPrice):
        """计算期权收益"""
        if self.optionType.lower() == 'call':
            return max((stockPrice - self.strikingPrice) * self.multiplier, 0.0)
        else:
            return max((self.strikingPrice - stockPrice) * self.multiplier, 0.0)