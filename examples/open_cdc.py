from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal
from ui_open_cdc import *


class OpenCdcDialog(QDialog, Ui_OpenCdcDialog):
    openCdcSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(OpenCdcDialog, self).__init__(parent)
        self.setupUi(self)

        self.setWindowModality(Qt.ApplicationModal)
        self.accepted.connect(self.openCdc)

    def openCdc(self):
        self.openCdcSignal.emit({'btcAmount': self.btcAmount.text(), 'usdAmount': self.usdAmount.text()})
        self.destroy()