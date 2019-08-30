# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pcm_main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(30, 210, 741, 311))
        self.tableView.setObjectName("tableView")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(70, 20, 331, 141))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.accountList = QtWidgets.QComboBox(self.formLayoutWidget)
        self.accountList.setEditable(True)
        self.accountList.setObjectName("accountList")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.accountList)
        self.bTCLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.bTCLabel.setObjectName("bTCLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.bTCLabel)
        self.bTCLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.bTCLineEdit.setObjectName("bTCLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.bTCLineEdit)
        self.hUSDLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.hUSDLabel.setObjectName("hUSDLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.hUSDLabel)
        self.hUSDLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.hUSDLineEdit.setObjectName("hUSDLineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.hUSDLineEdit)
        self.hXLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.hXLabel.setObjectName("hXLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.hXLabel)
        self.hXLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.hXLineEdit.setObjectName("hXLineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.hXLineEdit)
        self.addressLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.addressLabel.setObjectName("addressLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.addressLabel)
        self.addressLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.addressLineEdit.setObjectName("addressLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.addressLineEdit)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Account:"))
        self.bTCLabel.setText(_translate("MainWindow", "BTC:"))
        self.hUSDLabel.setText(_translate("MainWindow", "HUSD:"))
        self.hXLabel.setText(_translate("MainWindow", "HX:"))
        self.addressLabel.setText(_translate("MainWindow", "Address:"))

