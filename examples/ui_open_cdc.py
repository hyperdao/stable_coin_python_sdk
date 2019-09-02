# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'open_cdc.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OpenCdcDialog(object):
    def setupUi(self, OpenCdcDialog):
        OpenCdcDialog.setObjectName("OpenCdcDialog")
        OpenCdcDialog.resize(366, 213)
        self.buttonBox = QtWidgets.QDialogButtonBox(OpenCdcDialog)
        self.buttonBox.setGeometry(QtCore.QRect(100, 150, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(OpenCdcDialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 30, 321, 101))
        self.groupBox.setObjectName("groupBox")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(40, 30, 243, 48))
        self.layoutWidget.setObjectName("layoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.layoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.btcAmount = QtWidgets.QLineEdit(self.layoutWidget)
        self.btcAmount.setObjectName("btcAmount")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.btcAmount)
        self.label_10 = QtWidgets.QLabel(self.layoutWidget)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.usdAmount = QtWidgets.QLineEdit(self.layoutWidget)
        self.usdAmount.setObjectName("usdAmount")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.usdAmount)

        self.retranslateUi(OpenCdcDialog)
        self.buttonBox.accepted.connect(OpenCdcDialog.accept)
        self.buttonBox.rejected.connect(OpenCdcDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(OpenCdcDialog)

    def retranslateUi(self, OpenCdcDialog):
        _translate = QtCore.QCoreApplication.translate
        OpenCdcDialog.setWindowTitle(_translate("OpenCdcDialog", "Open CDC"))
        self.groupBox.setTitle(_translate("OpenCdcDialog", "Open CDC"))
        self.label_9.setText(_translate("OpenCdcDialog", "BTC Amount:"))
        self.label_10.setText(_translate("OpenCdcDialog", "USD Amount:"))
