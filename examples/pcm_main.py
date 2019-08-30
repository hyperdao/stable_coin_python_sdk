import sys
import json
import time
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui_pcm_main import *
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_events import EventsCollector
from hdao.hdao_cdc_op import CDCOperation


class ScanThread(QThread):
    sinSyncState = pyqtSignal(str)

    def __init__(self, api):
        super().__init__()
        self.api = api
        self.stopFlag = False
        self.state_file = './pcm_state.json'
        try:
            with open(self.state_file, "r") as f:
                self.state = json.load(f)
        except:
            self.state = {'start_block': 1}
        if 'start_block' not in self.state or self.state['start_block'] is None:
            self.state = {'start_block': 1}

    def run(self):
        self.collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.api)
        print(str(self.state))
        start_block = self.state['start_block']
        end_block = start_block
        while not self.stopFlag:
            if end_block <= start_block:
                info = self.api.rpc_request('info', [])
                if info is not None:
                    end_block = int(info['head_block_num'])
                    step = end_block - start_block
                else:
                    step = 100
            self.sinSyncState.emit('%d / %d' % (start_block, end_block))
            step = end_block - start_block if end_block - start_block < 100 else 100
            end_block = self.collector.collect_event(start_block, step)
            self.state['start_block'] = end_block
            start_block = end_block
            with open(self.state_file, 'w') as wf:
                json.dump(self.state, wf)
            if end_block - start_block < 10:
                time.sleep(5)
    
    def stop(self):
        self.stopFlag = True

class PcmMainWindow(QMainWindow, Ui_MainWindow):
    sinScanStop = pyqtSignal()

    def __init__(self, parent=None):
        super(PcmMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.default_api_url = 'http://192.168.1.121:30088/'
        self.collateral_contract = 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks'
        self.api = HXWalletApi(name='PCM', rpc_url=self.default_api_url)
        self.collector = EventsCollector('da', self.collateral_contract, self.api)
        self.scanThread = ScanThread(self.api)
        self.sinScanStop.connect(self.scanThread.stop)
        self.scanThread.sinSyncState.connect(self.syncStateChange)
        self.scanThread.start()
        self.cdcOp = CDCOperation('da', self.collateral_contract, self.api)
        self.initWidgets()

    def initWidgets(self):
        self.cdcModel = QStandardItemModel(5,6)
        self.cdcModel.setHorizontalHeaderLabels(['cdc id','BTC','USD', 'Stability Fee', 'state', 'block number'])
        self.tableView.setModel(self.cdcModel)
        self.collateralContractList.addItem(self.collateral_contract)
        cdcContractInfo = self.cdcOp.get_contract_info()
        if cdcContractInfo is not None:
            cdcContractInfo = json.loads(cdcContractInfo)
            self.collateralAdmin.setText(cdcContractInfo['admin'])
            self.collateralAsset.setText(cdcContractInfo['collateralAsset'])
            self.liquidationRatio.setText(cdcContractInfo['liquidationRatio'])
            self.annualStabilityFee.setText(cdcContractInfo['annualStabilityFee'])
            self.liquidationPenalty.setText(cdcContractInfo['liquidationPenalty'])
            self.liquidationDiscount.setText(cdcContractInfo['liquidationDiscount'])
        self.accountList.currentIndexChanged.connect(self.accountChange)
        accounts = self.api.rpc_request('list_my_accounts', [])
        self.accounts = accounts if accounts is not None else None
        for a in self.accounts:
            balances = self.api.rpc_request('get_account_balances', [a['name']])
            a['balances'] = balances
            self.accountList.addItem(a['name'])

    def closeEvent(self, e):
        #TODO, not graceful shutdown
        self.sinScanStop.emit()

    def accountChange(self, i):
        account = self.accounts[i]
        self.addressLineEdit.setText(account['addr'])
        for b in account['balances']:
            if b['asset_id'] == '1.3.0':
                self.hXLineEdit.setText(str(b['amount']))
            elif b['asset_id'] == '1.3.1':
                self.bTCLineEdit.setText(str(b['amount']))
        cdcs = self.collector.query_cdc_by_address(account['addr'])
        for r in range(len(cdcs)):
            cdcInfo = self.cdcOp.get_cdc(cdcs[r].cdc_id)
            if cdcInfo is None:
                continue
            cdcInfo = json.loads(cdcInfo)
            self.cdcModel.setItem(r, 0, QStandardItem(cdcs[r].cdc_id))
            self.cdcModel.setItem(r, 1, QStandardItem(cdcs[r].collateral_amount))
            self.cdcModel.setItem(r, 2, QStandardItem(cdcs[r].stable_token_amount))
            self.cdcModel.setItem(r, 3, QStandardItem(cdcInfo['stabilityFee']))
            if cdcs[r].state == 1:
                self.cdcModel.setItem(r, 4, QStandardItem('OPEN'))
            elif cdcs[r].state == 2:
                self.cdcModel.setItem(r, 4, QStandardItem('CLOSED'))
            self.cdcModel.setItem(r, 5, QStandardItem(cdcs[r].block_number))
    
    def syncStateChange(self, state):
        self.syncLabel.setText(state)
        self.syncLabel.adjustSize()
