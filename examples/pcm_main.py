import sys
import json
import time, decimal
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui_pcm_main import *
from open_cdc import OpenCdcDialog
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_events import EventsCollector
from hdao.hdao_cdc_op import CDCOperation



SYNC_STATE_TYPE = 'sync_state'
SYNC_ACCOUNT_TYPE = 'sync_account'
SYNC_CONTRACT_TYPE = 'sync_contract'

class ScanThread(QThread):
    sinSyncState = pyqtSignal(dict)

    def __init__(self, api, cdcOp):
        super().__init__()
        self.api = api
        self.cdcOp = cdcOp
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
        start_block = self.state['start_block']
        end_block = start_block
        while not self.stopFlag:
            self.refreshGuiState()
            if end_block <= start_block:
                info = self.api.rpc_request('info', [])
                if info is not None:
                    end_block = int(info['head_block_num'])
                    step = end_block - start_block
                else:
                    step = 100
            self.sinSyncState.emit({
                'syncType': SYNC_STATE_TYPE,
                'data': '%d / %d' % (start_block, end_block)
            })
            step = end_block - start_block if end_block - start_block < 100 else 100
            end_block = self.collector.collect_event(start_block, step)
            self.state['start_block'] = end_block
            start_block = end_block
            with open(self.state_file, 'w') as wf:
                json.dump(self.state, wf)
            if end_block - start_block < 10:
                time.sleep(5)

    def refreshGuiState(self):
        cdcContractInfo = self.cdcOp.get_contract_info()
        if cdcContractInfo is not None:
            self.sinSyncState.emit({
                'syncType': SYNC_CONTRACT_TYPE,
                'data': json.loads(cdcContractInfo)
            })


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
        self.cdcOp = CDCOperation('da', self.collateral_contract, self.api)
        self.scanThread = ScanThread(self.api, self.cdcOp)
        self.sinScanStop.connect(self.scanThread.stop)
        self.scanThread.sinSyncState.connect(self.syncStateChange)
        self.scanThread.start()
        self.initWidgets()

    def initWidgets(self):
        self.btnOpenCdc.clicked.connect(self.openCdcDialog)
        self.cdcModel = QStandardItemModel(5,6)
        self.cdcModel.setHorizontalHeaderLabels(['cdc id','BTC','USD', 'Stability Fee', 'state', 'block number'])
        self.tableView.setModel(self.cdcModel)
        self.tableView.doubleClicked.connect(self.existedCdcAction)
        self.collateralContractList.addItem(self.collateral_contract)
        self.accountList.currentIndexChanged.connect(self.accountChange)
        accounts = self.api.rpc_request('list_my_accounts', [])
        self.accounts = accounts if accounts is not None else None
        for a in self.accounts:
            self.accountList.addItem(a['name'])

    def openCdcDialog(self):
        dlg = OpenCdcDialog()
        dlg.openCdcSignel.connect(self.openCdcAction)
        dlg.exec_()

    def openCdcAction(self, arg):
        print(arg)
        result = self.cdcOp.open_cdc(arg['btcAmount'], arg['usdAmount'])
        if result is not None and "trxid" in result:
            QMessageBox.information(self,"Success", "Open CDC success (%s)!" % result['trxid'])
        else:
            QMessageBox.warning(self,"Error", "Open CDC fail!")

    def existedCdcAction(self):
        print(self.tableView.currentIndex().row())
        pass

    def closeEvent(self, e):
        self.sinScanStop.emit()
        self.scanThread.wait()

    def accountChange(self, i):
        account = self.accounts[i]
        self.addressLineEdit.setText(account['addr'])
        balances = self.api.rpc_request('get_account_balances', [account['name']])
        account['balances'] = balances
        for b in account['balances']:
            if b['asset_id'] == '1.3.0':
                hxAmount = decimal.Decimal(b['amount']) / 100000
                self.hXLineEdit.setText(str(hxAmount.quantize(decimal.Decimal('0.00000001'))))
            elif b['asset_id'] == '1.3.1':
                btcAmount = decimal.Decimal(b['amount']) / 100000000
                self.bTCLineEdit.setText(str(btcAmount.quantize(decimal.Decimal('0.00000001'))))
        usdBalance = self.api.rpc_request('invoke_contract_offline', ['da', 'HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2', 'balanceOf', account['addr']])
        usdBalance = decimal.Decimal(usdBalance) / 100000000
        self.hUSDLineEdit.setText(str(usdBalance.quantize(decimal.Decimal('0.00000001'))))
        cdcs = self.collector.query_cdc_by_address(account['addr'])
        self.cdcModel.removeRows(0, self.cdcModel.rowCount())
        for r in range(len(cdcs)):
            self.cdcModel.setItem(r, 0, QStandardItem(cdcs[r].cdc_id))
            self.cdcModel.setItem(r, 1, QStandardItem(cdcs[r].collateral_amount))
            self.cdcModel.setItem(r, 2, QStandardItem(cdcs[r].stable_token_amount))
            self.cdcModel.setItem(r, 3, QStandardItem('N/A'))
            if cdcs[r].state == 1:
                self.cdcModel.setItem(r, 4, QStandardItem('OPEN'))
                cdcInfo = self.cdcOp.get_cdc(cdcs[r].cdc_id)
                cdcInfo = json.loads(cdcInfo)
                self.cdcModel.setItem(r, 3, QStandardItem(cdcInfo['stabilityFee']))
            elif cdcs[r].state == 2:
                self.cdcModel.setItem(r, 4, QStandardItem('LIQUIDATED'))
            elif cdcs[r].state == 3:
                self.cdcModel.setItem(r, 4, QStandardItem('CLOSED'))
            self.cdcModel.setItem(r, 5, QStandardItem(str(cdcs[r].block_number)))
    
    def syncStateChange(self, stateChange):
        if stateChange['syncType'] == SYNC_STATE_TYPE:
            self.syncLabel.setText(stateChange['data'])
            self.syncLabel.adjustSize()
            self.statusBar().showMessage(stateChange['data'])
        elif stateChange['syncType'] == SYNC_CONTRACT_TYPE:
            self.cdcContractInfo = stateChange['data']
            self.collateralAdmin.setText(self.cdcContractInfo['admin'])
            self.collateralAsset.setText(self.cdcContractInfo['collateralAsset'])
            self.liquidationRatio.setText(self.cdcContractInfo['liquidationRatio'])
            self.annualStabilityFee.setText(self.cdcContractInfo['annualStabilityFee'])
            self.liquidationPenalty.setText(self.cdcContractInfo['liquidationPenalty'])
            self.liquidationDiscount.setText(self.cdcContractInfo['liquidationDiscount'])
