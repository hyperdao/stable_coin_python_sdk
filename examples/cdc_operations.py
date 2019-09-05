from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt, pyqtSignal
import decimal
import json
import logging
from ui_cdc_operations import *
from utils import convertCoinWithPrecision


class CDCOperationsDialog(QDialog, Ui_CdcOperationsDialog):
    cdcOpSignal = pyqtSignal(dict)

    def __init__(self, args, parent=None):
        super(CDCOperationsDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.accepted.connect(self.takeAction)
        self.args = args
        self.cdcIdBox.setText(args['cdc_id'])
        cdcInfo = parent.cdcOp.get_cdc(args['cdc_id'])
        self.stateBox.setText(args['state'])
        if args['state'] == 'CLOSED' or args['state'] == 'LIQUIDATED':
            self.cdcActionBox.setEnabled(False)
            self.cdcActionArg.setEnabled(False)
        if cdcInfo is not None and cdcInfo != "{}":
            cdcInfo = json.loads(cdcInfo)
            self.collateralBox.setText(convertCoinWithPrecision(cdcInfo['collateralAmount']))
            self.generatedBox.setText(convertCoinWithPrecision(cdcInfo['stableTokenAmount']))
            self.stabilityFeeBox.setText(convertCoinWithPrecision(cdcInfo['stabilityFee']))
            collateralAsset = decimal.Decimal(cdcInfo['collateralAmount']) * decimal.Decimal(args['price'])
            debtAsset = decimal.Decimal(cdcInfo['stableTokenAmount']) + decimal.Decimal(cdcInfo['stabilityFee'])
            ratio = collateralAsset / debtAsset
            self.ratioBox.setText("{0:.4f}".format(ratio))
        self.cdcActionArg.setValidator(QDoubleValidator())
        self.cdcActionArg2.setVisible(False)
        self.cdcActionBox.currentIndexChanged.connect(self.actionChange)
        self.cdcActionBox.setCurrentIndex(args['action'])
        if self.cdcActionBox.currentIndex() == 0:
            self.cdcActionBox.currentIndexChanged.emit(args['action'])
        self.lblHint.setText('Available USD: %s' % args['available_usd'])
        self.lblHint.setStyleSheet('color: blue;')

    def actionChange(self, i):
        self.cdcActionArg2.setVisible(False)
        if i > 4:
            self.cdcActionArg.setEnabled(False)
            self.cdcActionArg.setPlaceholderText('N/A')
        else:
            self.cdcActionArg.setEnabled(True)
            if i == 0:
                maxAvailable = convertCoinWithPrecision(
                    decimal.Decimal(self.generatedBox.text()) + decimal.Decimal(self.stabilityFeeBox.text()), 0)
                self.cdcActionArg.setPlaceholderText('Max: %s' % maxAvailable)
            elif i == 1:
                collateralAsset = decimal.Decimal(self.collateralBox.text()) * decimal.Decimal(self.args['price']) / decimal.Decimal(1.5)
                maxAvailable = convertCoinWithPrecision(
                    collateralAsset - decimal.Decimal(self.generatedBox.text()) - decimal.Decimal(self.stabilityFeeBox.text()), 0)
                self.cdcActionArg.setPlaceholderText('Max: %s' % maxAvailable)
            elif i == 2:
                maxAvailable = self.args['available_btc']
                self.cdcActionArg.setPlaceholderText('Max: %s' % maxAvailable)
            elif i == 3:
                withdrawAsset = decimal.Decimal(self.collateralBox.text()) - \
                    decimal.Decimal(1.5) * \
                        (decimal.Decimal(self.generatedBox.text()) + decimal.Decimal(self.stabilityFeeBox.text())) / \
                        decimal.Decimal(self.args['price'])
                maxAvailable = convertCoinWithPrecision(withdrawAsset, 0)
                self.cdcActionArg.setPlaceholderText('Max: %s' % maxAvailable)
            if i == 4:
                if not self.args['liquidate']['isNeedLiquidation'] or self.args['liquidate']['isBadDebt']:
                    self.cdcActionArg.setEnabled(False)
                    self.cdcActionArg2.setEnabled(False)
                else:
                    self.cdcActionArg2.setVisible(True)
                    self.cdcActionArg.setPlaceholderText('Max Pay: %s' % convertCoinWithPrecision(self.args['liquidate']['repayStableTokenAmount']))
                    self.cdcActionArg2.setPlaceholderText('Max Get: %s' % convertCoinWithPrecision(self.args['liquidate']['auctionCollateralAmount']))

    def takeAction(self):
        if self.stateBox.text() == 'CLOSED' or self.stateBox.text() == 'LIQUIDATED':
            self.cdcOpSignal.emit({'action': '', 'arg': ''})
        else:
            self.cdcOpSignal.emit({
                'action': self.cdcActionBox.currentText(),
                'cdc_id': self.cdcIdBox.text(),
                'amount': self.cdcActionArg.text(),
                'amount2': self.cdcActionArg2.text()
            })
        self.destroy()