import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_pcm_main import *
from hdao.hx_wallet_api import HXWalletApi

class PcmMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(PcmMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.default_api_url = 'http://192.168.1.121:30088/'
        self.api = HXWalletApi(name='PCM', rpc_url=self.default_api_url)
        self.initWidgets()

    def initWidgets(self):
        self.accountList.currentIndexChanged.connect(self.accountChange)
        accounts = self.api.rpc_request('list_my_accounts', [])
        self.accounts = accounts['result'] if accounts is not None else None
        for a in self.accounts:
            balances = self.api.rpc_request('get_account_balances', [a['name']])
            a['balances'] = balances['result']
            self.accountList.addItem(a['name'])
        
    def accountChange(self, i):
        account = self.accounts[i]
        self.addressLineEdit.setText(account['addr'])
        for b in account['balances']:
            if b['asset_id'] == '1.3.0':
                self.hXLineEdit.setText(str(b['amount']))
            elif b['asset_id'] == '1.3.1':
                self.bTCLineEdit.setText(str(b['amount']))
