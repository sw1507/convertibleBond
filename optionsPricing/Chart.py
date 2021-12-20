import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator


class LineChart:

    def __init__(self, data_x, data_y1, y1Name,  data_y2 = [], y2Name = ""):
        self.data_x = data_x
        self.data_y1 = data_y1
        self.data_y2 = data_y2
        self.y1Name =  y1Name
        self.y2Name = y2Name

    def draw(self, chartTitle):
        """
        画折线图，比较定价结果和实际期权价格
        """
        #解决中文显示问题
        plt.rcParams['font.sans-serif']=['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        plt.plot(self.data_x, self.data_y1, color = 'red',linewidth = 2.0, label = self.y1Name)
        plt.plot(self.data_x, self.data_y2, color = 'blue',linewidth = 2.0, label = self.y2Name)
        
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.title(chartTitle)
        plt.xticks(rotation = 30)
        
        #设置网格线
        plt.grid(axis="y")

        #设置坐标间隔
        x_major_locator = MultipleLocator(5)
        y_major_locator = MultipleLocator(50)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        ax.yaxis.set_major_locator(y_major_locator)
        
        plt.legend()
        plt.show()