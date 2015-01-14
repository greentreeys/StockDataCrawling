#Main Program
#This .py file realize the automatic crawling of fund data from Sina, and calculate profit

from __future__ import division
from PyQt4 import QtGui, QtCore, Qt
import UI_fund as UI
import sys

from HTMLParser import HTMLParser
import urllib2
from FundDataParser_HistoricalData import fundDataParser as fundDataPaser_Historical
from FundDataParser_Current import fundDataParser_Current as fundDataPaser_Current

from deleteSymbol import deleteSymbol
from string2array import string2array

import numpy as np
import matplotlib.pyplot as plt


class fundGUI(QtGui.QMainWindow):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = UI.Ui_FundGUI()
        self.ui.setupUi(self)

        self.ui.quitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)

        self.FundList = ['531008', '720002', '217022', '000017',   '530020', "160625", "163113"]
        self.FundName = ['建信增利债券', '财通债券', '招商债券',  '财通可持续','建信转债债券', '鹏华非银行分级', '申万行业指数']
        self.Invest = np.array([1000, 1500, 2000, 2000,  1000, 1000, 5000])
        self.ProcessingFee_initla = np.array([0.003,  0.003, 0.006, 0.003,  0.003, 0.003, 0.006])
        self.ProcessingFee_end = np.array([ 0.001, 0.001, 0.015, 0.005,  0.001,  0.005, 0.005])
        self.NetValue_Buying = np.array([1.35, 1.104, 1.118,  1.794,   1.471, 1.0000, 1.5049])
        self.Share = self.Invest*(1-self.ProcessingFee_initla) / self.NetValue_Buying
        self.NumInvest = len(self.FundList)

        self.add_530020_1 = [2000, 1.4870]
        self.add_530020_2 = [1000, 1.552]
        self.add_160625 = [3500, 1.081]

        self.Share[4] = self.Share[4] + (self.add_530020_1[0]*(1-self.ProcessingFee_initla[4]))/self.add_530020_1[1]\
                        +(self.add_530020_2[0]*(1-self.ProcessingFee_initla[4]))/self.add_530020_2[1]
        self.Share[5] = self.Share[5] + (self.add_160625[0]*(1-self.ProcessingFee_initla[5]))/self.add_160625[1]
        self.Invest[4] = self.Invest[4] + self.add_530020_1[0] + self.add_530020_2[0]
        self.Invest[5] = self.Invest[5] + self.add_160625[0]

        self.Share[6] = self.Share[6] * 1.560364
        self.Share[3] = 0
        self.Invest[3] = 0


        self.ui.pushButton_refresh.clicked.connect(self.dataAnalyze)



    def dataAnalyze(self):
        parser = fundDataPaser_Historical()

        CurrentMoney = np.zeros(self.NumInvest)
        Profit = np.zeros(self.NumInvest)
        TodayProfit = np.zeros(self.NumInvest)
        ProfitRate = np.zeros(self.NumInvest)
        RedemptedMoney = np.zeros(self.NumInvest)
        netValueAll = np.zeros((0, 20))
        rateAll = np.zeros((0, 20))
        cumuValueAll =np.zeros((0, 20))
        for index, fundNo in enumerate(self.FundList):
            result = parser.get(fundNo)

            date = result['date']
            date = date[::-1]
            netValue = result['netValue']
            cumuValue = result['cumuValue']
            rate = result['rate']

            # date = deleteSymbol(date)
            netValue = deleteSymbol(netValue)
            cumuValue = deleteSymbol(cumuValue)
            rate = deleteSymbol(rate)

            netValue = string2array(netValue)
            cumuValue = string2array(cumuValue)
            rate = string2array(rate)

            netValueAll = np.append(netValueAll, netValue, axis = 0)
            cumuValueAll = np.append(cumuValueAll, cumuValue, axis = 0)
            rateAll = np.append(rateAll, rate, axis = 0)


            CurrentMoney[index] = netValue[0, -1]*self.Share[index]
            Profit[index] = CurrentMoney[index] - self.Invest[index]
            TodayProfit[index] = self.Share[index]*netValue[0, -1]*rate[0, -1] / 100
            ProfitRate[index] = Profit[index]*100 / self.Invest[index]
            RedemptedMoney[index] = CurrentMoney[index]*(1-self.ProcessingFee_end[index])

            tableContent = [fundNo, CurrentMoney[index], Profit[index], TodayProfit[index], ProfitRate[index],\
                            netValue[0, -1], rate[0, -1],self.Share[index], RedemptedMoney[index]]

            for column in xrange(0, 9): #str(tableContent[column]))
                item = QtGui.QTableWidgetItem(str(tableContent[column]))
                self.ui.table.setItem(index, column, item)


        TotalProfit =  np.sum(Profit)
        TotalTodayProfit = np.sum(TodayProfit)
        TotalMoney =  np.sum(CurrentMoney)
        TotalMoney_redempted = np.sum(RedemptedMoney)

        for index, d in enumerate(date):

            if str(d) == "2014/11/28":
                buyDate = index
                break
            else:
                buyDate = -1


    ############show on GUI############
        self.ui.lineEdit_UpdatedTime.setText(str(date[-1]))
        self.ui.lineEdit_TotalMoney.setText(str(TotalMoney))
        self.ui.lineEdit_TotalProfit.setText(str(TotalProfit))
        self.ui.lineEdit_TodayProfit.setText(str(TotalTodayProfit))
        self.ui.lineEdit_TotalRedempted.setText(str(TotalMoney_redempted))




def main():
    app = QtGui.QApplication(sys.argv)
    ex = fundGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
