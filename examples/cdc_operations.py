from PyQt5.QtWidgets import QDialog
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
        self.cdcActionBox.currentIndexChanged.connect(self.actionChange)
        logging.debug(args['action'])
        self.cdcActionBox.setCurrentIndex(args['action'])
        self.lblHint.setText('Available USD: %s' % args['available_usd'])
        self.lblHint.setStyleSheet('color: blue;')

    def actionChange(self, i):
        if i > 3:
            self.cdcActionArg.setEnabled(False)
        else:
            self.cdcActionArg.setEnabled(True)

    def takeAction(self):
        print(self.stateBox.text())
        if self.stateBox.text() == 'CLOSED' or self.stateBox.text() == 'LIQUIDATED':
            self.cdcOpSignal.emit({'action': '', 'arg': ''})
        else:
            self.cdcOpSignal.emit({
                'action': self.cdcActionBox.currentText(),
                'cdc_id': self.cdcIdBox.text(),
                'amount': self.cdcActionArg.text()
            })
        self.destroy()