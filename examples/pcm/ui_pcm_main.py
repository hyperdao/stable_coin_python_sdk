# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pcm_main.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(984, 694)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 991, 641))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tableView = QtWidgets.QTableView(self.tab)
        self.tableView.setGeometry(QtCore.QRect(10, 370, 651, 231))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setObjectName("tableView")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 300, 651, 61))
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnOpenCdc = QtWidgets.QPushButton(self.groupBox_3)
        self.btnOpenCdc.setObjectName("btnOpenCdc")
        self.horizontalLayout.addWidget(self.btnOpenCdc)
        self.btnAdd = QtWidgets.QPushButton(self.groupBox_3)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnPayback = QtWidgets.QPushButton(self.groupBox_3)
        self.btnPayback.setObjectName("btnPayback")
        self.horizontalLayout.addWidget(self.btnPayback)
        self.btnWithdraw = QtWidgets.QPushButton(self.groupBox_3)
        self.btnWithdraw.setObjectName("btnWithdraw")
        self.horizontalLayout.addWidget(self.btnWithdraw)
        self.btnGenerate = QtWidgets.QPushButton(self.groupBox_3)
        self.btnGenerate.setObjectName("btnGenerate")
        self.horizontalLayout.addWidget(self.btnGenerate)
        self.btnCloseCdc = QtWidgets.QPushButton(self.groupBox_3)
        self.btnCloseCdc.setObjectName("btnCloseCdc")
        self.horizontalLayout.addWidget(self.btnCloseCdc)
        self.btnLiquidate = QtWidgets.QPushButton(self.groupBox_3)
        self.btnLiquidate.setObjectName("btnLiquidate")
        self.horizontalLayout.addWidget(self.btnLiquidate)
        self.btnRefresh = QtWidgets.QPushButton(self.groupBox_3)
        self.btnRefresh.setObjectName("btnRefresh")
        self.horizontalLayout.addWidget(self.btnRefresh)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(390, 10, 471, 251))
        self.groupBox_2.setObjectName("groupBox_2")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_2)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 431, 219))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.collateralAdmin = QtWidgets.QLineEdit(self.layoutWidget)
        self.collateralAdmin.setReadOnly(True)
        self.collateralAdmin.setObjectName("collateralAdmin")
        self.gridLayout.addWidget(self.collateralAdmin, 1, 1, 1, 1)
        self.collateralAsset = QtWidgets.QLineEdit(self.layoutWidget)
        self.collateralAsset.setReadOnly(True)
        self.collateralAsset.setObjectName("collateralAsset")
        self.gridLayout.addWidget(self.collateralAsset, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.liquidationRatio = QtWidgets.QLineEdit(self.layoutWidget)
        self.liquidationRatio.setObjectName("liquidationRatio")
        self.gridLayout.addWidget(self.liquidationRatio, 3, 1, 1, 1)
        self.liquidationPenalty = QtWidgets.QLineEdit(self.layoutWidget)
        self.liquidationPenalty.setObjectName("liquidationPenalty")
        self.gridLayout.addWidget(self.liquidationPenalty, 5, 1, 1, 1)
        self.liquidationDiscount = QtWidgets.QLineEdit(self.layoutWidget)
        self.liquidationDiscount.setObjectName("liquidationDiscount")
        self.gridLayout.addWidget(self.liquidationDiscount, 6, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.annualStabilityFee = QtWidgets.QLineEdit(self.layoutWidget)
        self.annualStabilityFee.setObjectName("annualStabilityFee")
        self.gridLayout.addWidget(self.annualStabilityFee, 4, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.layoutWidget)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 6, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)
        self.collateralContractList = QtWidgets.QComboBox(self.layoutWidget)
        self.collateralContractList.setObjectName("collateralContractList")
        self.gridLayout.addWidget(self.collateralContractList, 0, 1, 1, 1)
        self.currentPrice = QtWidgets.QLineEdit(self.layoutWidget)
        self.currentPrice.setObjectName("currentPrice")
        self.gridLayout.addWidget(self.currentPrice, 7, 1, 1, 1)
        self.btnChangePrice = QtWidgets.QPushButton(self.layoutWidget)
        self.btnChangePrice.setObjectName("btnChangePrice")
        self.gridLayout.addWidget(self.btnChangePrice, 7, 2, 1, 1)
        self.btnChangeDiscount = QtWidgets.QPushButton(self.layoutWidget)
        self.btnChangeDiscount.setObjectName("btnChangeDiscount")
        self.gridLayout.addWidget(self.btnChangeDiscount, 6, 2, 1, 1)
        self.btnChangePenalty = QtWidgets.QPushButton(self.layoutWidget)
        self.btnChangePenalty.setObjectName("btnChangePenalty")
        self.gridLayout.addWidget(self.btnChangePenalty, 5, 2, 1, 1)
        self.btnChangeFee = QtWidgets.QPushButton(self.layoutWidget)
        self.btnChangeFee.setObjectName("btnChangeFee")
        self.gridLayout.addWidget(self.btnChangeFee, 4, 2, 1, 1)
        self.btnChangeRatio = QtWidgets.QPushButton(self.layoutWidget)
        self.btnChangeRatio.setObjectName("btnChangeRatio")
        self.gridLayout.addWidget(self.btnChangeRatio, 3, 2, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 351, 181))
        self.groupBox.setObjectName("groupBox")
        self.formLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 20, 311, 141))
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
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.walletUrlBox = QtWidgets.QComboBox(self.tab_2)
        self.walletUrlBox.setGeometry(QtCore.QRect(118, 30, 221, 22))
        self.walletUrlBox.setEditable(True)
        self.walletUrlBox.setObjectName("walletUrlBox")
        self.walletUrlBox.addItem("")
        self.walletUrlBox.addItem("")
        self.walletUrlBox.addItem("")
        self.label_10 = QtWidgets.QLabel(self.tab_2)
        self.label_10.setGeometry(QtCore.QRect(33, 30, 71, 20))
        self.label_10.setObjectName("label_10")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 984, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setAutoFillBackground(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_3.setTitle(_translate("MainWindow", "CDC Operation"))
        self.btnOpenCdc.setText(_translate("MainWindow", "Open"))
        self.btnAdd.setText(_translate("MainWindow", "Add"))
        self.btnPayback.setText(_translate("MainWindow", "Payback"))
        self.btnWithdraw.setText(_translate("MainWindow", "Withdraw"))
        self.btnGenerate.setText(_translate("MainWindow", "Generate"))
        self.btnCloseCdc.setText(_translate("MainWindow", "Close"))
        self.btnLiquidate.setText(_translate("MainWindow", "Liquidate"))
        self.btnRefresh.setText(_translate("MainWindow", "Refresh"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Collateral Contract Info"))
        self.label_2.setText(_translate("MainWindow", "Collateral Contract:"))
        self.label_3.setText(_translate("MainWindow", "Admin:"))
        self.label_5.setText(_translate("MainWindow", "Liquidation Ratio:"))
        self.label_6.setText(_translate("MainWindow", "Annual Stability Fee:"))
        self.label_4.setText(_translate("MainWindow", "Collateral Asset:"))
        self.label_9.setText(_translate("MainWindow", "Current Price:"))
        self.label_8.setText(_translate("MainWindow", "Liquidation Discount:"))
        self.label_7.setText(_translate("MainWindow", "Liquidation Penalty:"))
        self.btnChangePrice.setText(_translate("MainWindow", "Change"))
        self.btnChangeDiscount.setText(_translate("MainWindow", "Change"))
        self.btnChangePenalty.setText(_translate("MainWindow", "Change"))
        self.btnChangeFee.setText(_translate("MainWindow", "Change"))
        self.btnChangeRatio.setText(_translate("MainWindow", "Change"))
        self.groupBox.setTitle(_translate("MainWindow", "Account Info"))
        self.label.setText(_translate("MainWindow", "Account:"))
        self.bTCLabel.setText(_translate("MainWindow", "BTC:"))
        self.hUSDLabel.setText(_translate("MainWindow", "HUSD:"))
        self.hXLabel.setText(_translate("MainWindow", "HX:"))
        self.addressLabel.setText(_translate("MainWindow", "Address:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "CDC Management"))
        self.walletUrlBox.setItemText(0, _translate("MainWindow", "http://192.168.1.121:30088/"))
        self.walletUrlBox.setItemText(1, _translate("MainWindow", "http://114.67.86.57:30088/"))
        self.walletUrlBox.setItemText(2, _translate("MainWindow", "http://127.0.0.1:50321/"))
        self.label_10.setText(_translate("MainWindow", "Wallet URL:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Settings"))
