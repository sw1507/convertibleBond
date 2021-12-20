#coding:utf-8
import pandas as pd
import datetime
import numpy as np
import QuantLib as ql

# """
# 结果已存为dict格式，存储于C:\Users\wangsu\allChinaBondData.npy
#     {
#         "20xx-01-01":{
#             'spotRateEndDate': [每个spotRate对应的endDate,为Timestamp格式]
#             'spotRate': [2.9057, 3.6228, 3.3351, 3.2039, 3.2425, 3.2537, 3.3145, 3.3759, 3.4481, 3.5221, 3.5633, 3.5931]
#         }   
#     }

# """
class ChinaBondTreasuryYieldData:
    def __init__(self):
        return

    def saveData(self):
        fileName_2021 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2021.xlsx'
        fileName_2020 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2020.xlsx'
        fileName_2019 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2019.xlsx'
        fileName_2018 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2018.xlsx'
        fileName_2017 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2017.xlsx'
        fileName_2016 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2016.xlsx'
        fileName_2015 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2015.xlsx'
        fileName_2014 = r'D:\个人专题\Quant\中债国债收益率曲线信息\2014.xlsx'
        
        chinaBondInfoDict = {}
        allFileNames = [fileName_2021,fileName_2020, fileName_2019, fileName_2018, 
                        fileName_2017, fileName_2016, fileName_2015, fileName_2014]
        
        for fileName in allFileNames:
            data = pd.read_excel(fileName)

            # 重设第一列日期格式，统一为YYYY-MM-DD格式的字符串
            if(type(data.iloc[0,0]) != str):
                data["日期"] = pd.to_datetime(data["日期"])
                data["日期"] = data["日期"].dt.strftime('%Y-%m-%d')
            data["日期"] = data["日期"].replace('/', '-', regex = True)

            data_df = data[(data["标准期限说明"] == '0d') | (data["标准期限说明"] == '1m') | (data["标准期限说明"] == '3m') 
                        | (data["标准期限说明"] == '6m') | (data["标准期限说明"] == '9m') | (data["标准期限说明"] == '1y') 
                        | (data["标准期限说明"] == '2y') | (data["标准期限说明"] == '3y') | (data["标准期限说明"] == '4y') 
                        | (data["标准期限说明"] == '5y') | (data["标准期限说明"] == '6y') | (data["标准期限说明"] == '7y')]
            data_df = data_df[["日期", "标准期限(年)", "收益率(%)"]]

            #把日期格式转化为ql.datetime格式
            # data_df["endDateQLDatetime"] = data_df["endDateDatetime"].apply(lambda x : ql.Date(x.day, x.month, x.year))

            #重命名所有列名
            newColumnName = ["date", "years", "rate"]
            data_df.columns = newColumnName

            #更改收益率一列的数据格式（加上百分号）
            data_df["rate"] = data_df["rate"] / 100
        
            # chinaBondInfoDict = {}
            totalRowNumber = data_df.shape[0]
            previousDate = data_df.iloc[0, 0]
            startRowNumber = 0

            for rowIndex in range(0, totalRowNumber):
                currentDate = data_df.iloc[rowIndex, 0]
                if(currentDate != previousDate):
                    oneDateInfoCut = data_df.iloc[startRowNumber:rowIndex, 1:3]

                    chinaBondInfoDict[previousDate] = oneDateInfoCut.to_dict(orient = "list")
                    startRowNumber = rowIndex
                previousDate = currentDate
            finalCut = data_df.iloc[startRowNumber:rowIndex + 1, 1:]
            chinaBondInfoDict[previousDate] = finalCut.to_dict(orient = "list")
        
        #把dict文件存入本地
        np.save('allChinaBondData.npy', chinaBondInfoDict)    

        
    def getData(self):
        chinaBondInfo = np.load('allChinaBondData.npy', allow_pickle = True)
        # 把所有timestamp转化为ql.datetime格式
        originalDict = chinaBondInfo.item()
        # for key in originalDict.keys():
        #     newList = []
        #     originalDates = originalDict[key]['spotRateEndDate']
        #     for date in originalDates:
        #         newList.append(ql.Date(date.day, date.month, date.year))
        #     originalDict[key]["spotRateEndDateQL"] = newList    
        return originalDict
    
    def getDataAtOneDate(self, pricingDate):
        chinaBondInfo = np.load('allChinaBondData.npy', allow_pickle = True)
        # 把所有timestamp转化为ql.datetime格式
        originalDict = chinaBondInfo.item()
        # for key in originalDict.keys():
        #     newList = []
        #     originalDates = originalDict[key]['spotRateEndDate']
        #     for date in originalDates:
        #         newList.append(ql.Date(date.day, date.month, date.year))
        #     originalDict[key]["spotRateEndDateQL"] = newList    
        return originalDict[pricingDate]

    """
    使用线性插值法获取收益率
    参考：https://xueqiu.com/2680567071/134179761
    data格式为：{'years':[], 'rate':[]}   years为1个月，3个月，1年， 2年等等换算成年。
            例：{}
    date 格式为string
    """
    def getRiskFreeRate(self, date, targetYears):  
        #最大只能处理7年的
        if(targetYears > 7):
            targetYears = 7

        currentDateData = self.getDataAtOneDate(date)
        dateListOriginal = currentDateData["years"]

        #获取dateListReversed 和 yieldListReversed
        dateListReversed = []
        for i in dateListOriginal:
            dateListReversed.append(i)
        dateListReversed.reverse()

        yieldListOriginal = currentDateData['rate'] # [5.9714, 5.8557, 5.7878, 5.5951, 5.4727, 5.0159, 5.0191, 4.9134, 4.6788, 4.0807, 2.6278]
        yieldListReversed = []
        for j in yieldListOriginal:
            yieldListReversed.append(j)
        yieldListReversed.reverse()

        #用线性插值法找到targetYears对应的无风险利率
        if(targetYears >= dateListReversed[0]):
            return yieldListReversed[0]
        result = 0
        firstSmallerNumberIndex = self.findFirstSmallerNumber(targetYears, dateListReversed)
        result += yieldListReversed[firstSmallerNumberIndex]
        remainedYears = targetYears - dateListReversed[firstSmallerNumberIndex]
        result += remainedYears * (yieldListReversed[firstSmallerNumberIndex - 1] - yieldListReversed[firstSmallerNumberIndex])/(dateListReversed[firstSmallerNumberIndex - 1] - dateListReversed[firstSmallerNumberIndex])
        return result


    """在一个降序数组中找到第一个小于目标数字的数的index"""
    def findFirstSmallerNumber(self, target, dataList):
        if(dataList == None or len(dataList) == 0):
            return -1
        left = 0
        right = len(dataList) - 1
        while(left < right):
            mid = (left + right)//2
            if(dataList[mid] > target):
                left = mid + 1
            else:
                right = mid
        if(dataList[right] <= target):
            return right
        else:
            return -1


        # testDate = "2021-01-04"
        # testDate_ts = pd.to_datetime(testDate)
        # testDate_content = dictChinaBondInfo[testDate_ts]
        # print(testDate_content)
        # print(dictChinaBondInfo.keys())
        # data_df.to_csv("xxxxx.csv")
        # pd.concat([data_df, pd.DataFrame(endDateResult)], axis=1).to_csv("endDate1111.csv")
        
        
        # endDateIndex.append(row[0])
        # endDateData_df = pd.DataFrame({"index":endDateIndex, "endDateResult":endDateResult})
        
            # print(str(row[1]) + "  " + str(row[2]) + "  " +str(row[5]) + "  " + str(row[6]) + "  " + str(endDate))
        # print(data_df.shape[0])
        
        
        # data_df["endDateDatetime"] = pd.Series(endDateResult)
        # print(len(pd.Series(endDateResult)))
        # data_df.to_csv("tzzs_data2.csv")
        # data_df['endDateDatetime'] = data_df['startDateDatetime'] + pd.Timedelta(days = 1)

        
        # data_df['duration'] = np.where(data_df['标准期限说明'] == '0d', 0, 
        #                               (data_df['标准期限说明'] == '1m', 30, 
        #                               (data_df['标准期限说明'] == '2m', 60, 
        #                               (data_df['标准期限说明'] == '3m', 90, 
        #                               (data_df['标准期限说明'] == '6m', 180, 
        #                               (data_df['标准期限说明'] == '9m', 270, 
        #                               (data_df['标准期限说明'] == '1y', 365, 
        #                               (data_df['标准期限说明'] == '2y', 730, 
        #                               (data_df['标准期限说明'] == '3y', 1095, 
        #                               (data_df['标准期限说明'] == '5y', 1825, 
        #                               (data_df['标准期限说明'] == '7y', 2555, "")))))))))  )   )
        # data_df['duration'] = np.where(data_df['标准期限说明'] == '0d', 0, 1)

        # print(data_df.head(20))

        # for item in data_df.itertuples(): 
        #     print(str(item[1]) + " ," + str(item[2]) + ", "  + str(item[3]))
            # date = item[1].replace("/", "-")
            # if date not in chinaBondYieldData.keys():
            #     chinaBondYieldData["date"] = {}
            #     chinaBondYieldData["date"][]

    """
    {
    "2021-01-04":{"0d":0.6282
                  "1m":1.5995
                  "2m":2.1496
                  "3m":2.1518
                  "6m":
                  "9m":

                    }



    }
    
    """
    
