# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'meteogram_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from plot_meteogram import plot

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(937, 798)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(117, 117, 117);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image = QtWidgets.QLabel(self.centralwidget)
        self.image.setGeometry(QtCore.QRect(10, 20, 721, 761))
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("Meteogram_plotter_openImage.JPG"))
        self.image.setScaledContents(True)
        self.image.setObjectName("image")
        self.siteIDbox = QtWidgets.QLineEdit(self.centralwidget)
        self.siteIDbox.setGeometry(QtCore.QRect(770, 160, 121, 20))
        self.siteIDbox.setAutoFillBackground(False)
        self.siteIDbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.siteIDbox.setObjectName("siteIDbox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(770, 130, 131, 20))
        self.label.setObjectName("label")
        self.hoursBox = QtWidgets.QSpinBox(self.centralwidget)
        self.hoursBox.setGeometry(QtCore.QRect(800, 220, 42, 22))
        self.hoursBox.setAutoFillBackground(True)
        self.hoursBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.hoursBox.setObjectName("hoursBox")
        self.hoursBox.setValue(24)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(780, 200, 101, 20))
        self.label_2.setObjectName("label_2")
        self.plotButton = QtWidgets.QPushButton(self.centralwidget)
        self.plotButton.setGeometry(QtCore.QRect(770, 270, 131, 31))
        self.plotButton.setAutoFillBackground(False)
        self.plotButton.setStyleSheet("background-color: rgb(195, 195, 195);")
        self.plotButton.setObjectName("plotButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.plotButton.clicked.connect(self.createMeteogram)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Plot Meteogram"))
        self.label.setText(_translate("MainWindow", "4-Letter ASOS/AWOS ID:"))
        self.label_2.setText(_translate("MainWindow", "Hours to Display:"))
        self.plotButton.setText(_translate("MainWindow", "Plot Meteogram"))

    def createMeteogram(self):
        siteID = self.siteIDbox.text()
        hours = self.hoursBox.value()
        if len(siteID) != 4:
            self.badSiteAlert(siteID)
        elif hours < 3 or hours > 99:
            self.badHoursAlert(hours)
        else:
            if plot(siteID,int(hours)):
                self.image.setPixmap(QtGui.QPixmap("metar.jpeg"))
            else:
                self.badSiteAlert(siteID)

    def badSiteAlert(self,input):
        alert = QtWidgets.QMessageBox()
        alert.setIcon(QtWidgets.QMessageBox.Critical)
        alert.setText("Error: Invalid Station ID")
        alert.setInformativeText((input + " is not a valid Station ID."))
        alert.setWindowTitle("Error Alert")
        alert.setStandardButtons(QtWidgets.QMessageBox.Ok)
        alert.exec_()

    def badHoursAlert(self,hours):
        alert = QtWidgets.QMessageBox()
        alert.setIcon(QtWidgets.QMessageBox.Critical)
        alert.setText("Error: Invalid Hours Requested")
        alert.setInformativeText(("Input hours must be greater than 3\n and less than 100."))
        alert.setWindowTitle("Error Alert")
        alert.setStandardButtons(QtWidgets.QMessageBox.Ok)
        alert.exec_()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

