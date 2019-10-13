import sys
import json
import time
import decimal
import logging
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui_pcm_main import *
from open_cdc import OpenCdcDialog
from cdc_operations import CDCOperationsDialog
from utils import convertCoinWithPrecision
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_events import EventsCollector
from hdao.hdao_cdc_op import CDCOperation
from hdao.hdao_price_feeder import PriceFeeder


SYNC_STATE_TYPE = 'sync_state'
SYNC_ACCOUNT_TYPE = 'sync_account'
SYNC_CONTRACT_TYPE = 'sync_contract'

class DataSyncThread(QThread):
    sinSyncState = pyqtSignal(dict)

    def __init__(self, api, collector, cdcOp):
        super().__init__()
        self.api = api
        self.collector = collector
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

        self.config_file = './pcm_config.json'
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except:
            self.config = {
                'url_index': 0,
                'environment': 'test',
                'test': {
                    'collateral_contract': 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks',
                    'price_feeder_account': 'senator0',
                    'price_feeder_contract': 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1',
                    'usd_contract': ''
                },
                'production': {
                    'collateral_contract': 'HXCKbMNLRv1X9wtwus9Wsnd6vkz6NporbZ5L',
                    'price_feeder_account': 'senator0',
                    'price_feeder_contract': 'HXCHfD5WiSKb57rU5BLqSbz3uHRXdBvsy19B',
                    'usd_contract': 'HXCTmGbEzqYq2LADmxQ3tDHnADp1yp5L36ih'
                }
            }
        self.priceFeederAccount = self.config[self.config['environment']]['price_feeder_account']
        self.walletUrlBox.setCurrentIndex(self.config['url_index'])
        self.currentApiUrl = self.walletUrlBox.currentText()
        self.collateral_contract = self.config[self.config['environment']]['collateral_contract']
        self.api = HXWalletApi(name='PCM', rpc_url=self.currentApiUrl)
        self.accounts = []
        self.initWidgets()
        self._refreshAccountList()
        self.priceFeeder = PriceFeeder(
            self.priceFeederAccount, \
            self.config[self.config['environment']]['price_feeder_contract'], \
            self.api)
        self.syncThread = DataSyncThread(self.api, self.collector, self.cdcOp)
        self.sinScanStop.connect(self.syncThread.stop)
        self.syncThread.sinSyncState.connect(self.syncStateChange)
        self.syncThread.start()

    def initWidgets(self):
        self.btnRefresh.clicked.connect(self.refreshCdcs)
        self.btnChangeRatio.clicked.connect(lambda: self.cdcManagementAction(0))
        self.btnChangeFee.clicked.connect(lambda: self.cdcManagementAction(1))
        self.btnChangePenalty.clicked.connect(lambda: self.cdcManagementAction(2))
        self.btnChangeDiscount.clicked.connect(lambda: self.cdcManagementAction(3))
        self.btnChangePrice.clicked.connect(lambda: self.cdcManagementAction(4))
        self.btnOpenCdc.clicked.connect(self.openCdcDialog)
        self.cdcModel = QStandardItemModel(5,6)
        self.cdcModel.setHorizontalHeaderLabels(['CDC ID','BTC','HUSD', 'Stability Fee', 'state', 'block number'])
        self.tableView.setModel(self.cdcModel)
        self.tableView.doubleClicked.connect(lambda: self.existedCdcAction(0))
        self.btnPayback.clicked.connect(lambda: self.existedCdcAction(0))#'Payback'
        self.btnGenerate.clicked.connect(lambda: self.existedCdcAction(1))#'Generate'
        self.btnAdd.clicked.connect(lambda: self.existedCdcAction(2))#'AddCollateral'
        self.btnWithdraw.clicked.connect(lambda: self.existedCdcAction(3))#'Withdraw'
        self.btnLiquidate.clicked.connect(lambda: self.existedCdcAction(4))#'Liquidate'
        self.btnCloseCdc.clicked.connect(lambda: self.existedCdcAction(5))#'Close'
        self.collateralContractList.addItem(self.collateral_contract)
        self.walletUrlBox.currentIndexChanged.connect(self.changeUrl)

    def changeUrl(self):
        self.config['url_index'] = self.walletUrlBox.currentIndex()
        if self.config['url_index'] == 2:
            self.config['environment'] = 'production'
        else:
            self.config['environment'] = 'test'
        QMessageBox.information(self, 'Info', \
                        'URL changed. Restart Application to take effect.')
        

    def _refreshAccountList(self):
        self.accountList.clear()
        accounts = self.api.rpc_request('list_my_accounts', [])
        if accounts is None:
            return
        self.accounts = accounts
        self.collector = EventsCollector(self.accounts[0]['name'], self.collateral_contract, self.api)
        self.cdcOp = CDCOperation(self.accounts[0]['name'], self.collateral_contract, self.api)
        self.accountList.currentIndexChanged.connect(self.accountChange)
        self.priceFeederExist = False
        for a in self.accounts:
            if self.priceFeederAccount == a['name']:
                self.priceFeederExist = True
            self.accountList.addItem(a['name'])
        if not self.priceFeederExist:
            self.priceFeederAccount = self.accounts[0]['name']

    def cdcManagementAction(self, op):
        if not self.priceFeederExist:
            QMessageBox.warning(self, 'Warning', \
                        'No price feeder account in wallet.')
            return
        if op == 0:
            logging.debug('btnChangeRatio clicked')
            adminOp = CDCOperation(self.priceFeederAccount, self.collateral_contract, self.api)
            adminOp.set_liquidation_ratio(self.liquidationRatio.text())
        elif op == 1:
            logging.debug('btnChangeFee clicked')
            adminOp = CDCOperation(self.priceFeederAccount, self.collateral_contract, self.api)
            adminOp.set_annual_stability_fee(self.annualStabilityFee.text())
        elif op == 2:
            logging.debug('btnChangePenalty clicked')
            adminOp = CDCOperation(self.priceFeederAccount, self.collateral_contract, self.api)
            adminOp.set_liquidation_penalty(self.liquidationPenalty.text())
        elif op == 3:
            logging.debug('btnChangeDiscount clicked')
            adminOp = CDCOperation(self.priceFeederAccount, self.collateral_contract, self.api)
            adminOp.set_liquidation_discount(self.liquidationDiscount.text())
        elif op == 4:
            logging.debug('btnChangePrice clicked')
            self.priceFeeder.feed_price(self.currentPrice.text())
        else:
            logging.warning('unknown button is clicked')

    def openCdcDialog(self):
        dlg = OpenCdcDialog()
        dlg.openCdcSignal.connect(self.openCdcAction)
        dlg.exec_()

    def openCdcAction(self, arg):
        result = self.cdcOp.open_cdc(arg['btcAmount'], arg['usdAmount'])
        if result is not None and "trxid" in result:
            QMessageBox.information(self,"Success", "Open CDC success (%s)!" % result['trxid'])
        else:
            QMessageBox.warning(self,"Error", "Open CDC fail!")

    def existedCdcAction(self, action=0):
        r = self.tableView.currentIndex().row()
        if r < 0:
            QMessageBox.information(self, 'Info', 'Please select a CDC')
            return
        liquidateInfo = self.cdcOp.get_liquidable_info(self.cdcModel.data(self.cdcModel.index(r, 0)))
        if liquidateInfo is None:
            QMessageBox.information(self, 'Info', "Cannot get liquidation info, please retry later")
            return
        liquidateInfo = json.loads(liquidateInfo)
        if action == 4:
            if self.cdcModel.data(self.cdcModel.index(r, 4)) != 'OPEN':
                QMessageBox.information(self, 'Info', \
                    'The CDC (ID: %s) is [%s].' % (self.cdcModel.data(self.cdcModel.index(r, 0)), \
                        self.cdcModel.data(self.cdcModel.index(r, 4))))
            else:
                if not liquidateInfo['isNeedLiquidation'] or liquidateInfo['isBadDebt']:
                    QMessageBox.information(self, 'Info', \
                        'The CDC (ID: %s) cannot be liquidated.' % self.cdcModel.data(self.cdcModel.index(r, 0)))
            return
        data = {
            'cdc_id': self.cdcModel.data(self.cdcModel.index(r, 0)),
            'state': self.cdcModel.data(self.cdcModel.index(r, 4)),
            'available_usd': self.hUSDLineEdit.text(),
            'available_btc': self.bTCLineEdit.text(),
            'price': self.currentPrice.text(),
            'action': action,
            'liquidate': liquidateInfo
        }
        logging.debug(str(data))
        dlg = CDCOperationsDialog(args=data, parent=self)
        dlg.cdcOpSignal.connect(self.cdcTakeAction)
        dlg.exec_()

    def cdcTakeAction(self, arg):
        logging.debug(arg)
        cdcOp = CDCOperation(self.accountList.currentText(), self.collateral_contract, self.api)
        ret = ''
        if arg['action'] == 'Payback':
            ret = cdcOp.pay_back(arg['cdc_id'], arg['amount'])
        elif arg['action'] == 'Generate':
            ret = cdcOp.generate_stable_coin(arg['cdc_id'], arg['amount'])
        elif arg['action'] == 'AddCollateral':
            ret = cdcOp.add_collateral(arg['cdc_id'], arg['amount'])
        elif arg['action'] == 'Withdraw':
            ret = cdcOp.withdraw_collateral(arg['cdc_id'], arg['amount'])
        elif arg['action'] == 'Close':
            ret = cdcOp.close_cdc(arg['cdc_id'])
        elif arg['action'] == 'Liquidate':
            if arg['amount'] == '' or arg['amount2'] == '':
                QMessageBox.information(self, 'Info', \
                        'The CDC (ID: %s) cannot be liquidated.' % arg['cdc_id'])
                return
            self.cdcOp.liquidate(arg['cdc_id'], arg['amount'], arg['amount2'])
        else:
            pass
        if ret is None:
            retMessage = 'Fail to %s' % arg['action']
        else:
            retMessage = 'Success to %s' % arg['action']
        QMessageBox.information(self, 'Info', retMessage)
        logging.debug(ret)

    def closeEvent(self, e):
        self.sinScanStop.emit()
        self.syncThread.wait()
        with open(self.config_file, 'w') as wf:
            json.dump(self.config, wf)

    def accountChange(self, i):
        account = self.accounts[i]
        self.addressLineEdit.setText(account['addr'])
        balances = self.api.rpc_request('get_account_balances', [account['name']])
        account['balances'] = balances
        for b in account['balances']:
            if b['asset_id'] == '1.3.0':
                self.hXLineEdit.setText(convertCoinWithPrecision(b['amount'], 5))
            elif b['asset_id'] == '1.3.1':
                self.bTCLineEdit.setText(convertCoinWithPrecision(b['amount']))
        usdBalance = self.api.rpc_request('invoke_contract_offline', [account['name'], 'HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2', 'balanceOf', account['addr']])
        self.hUSDLineEdit.setText(convertCoinWithPrecision(0 if usdBalance is None else usdBalance ))
        cdcs = self.collector.query_cdc_by_address(account['addr'])
        self.cdcModel.removeRows(0, self.cdcModel.rowCount())
        for r in range(len(cdcs)):
            self.cdcModel.setItem(r, 0, QStandardItem(cdcs[r].cdc_id))
            self.cdcModel.setItem(r, 1, QStandardItem(convertCoinWithPrecision(cdcs[r].collateral_amount)))
            self.cdcModel.setItem(r, 2, QStandardItem(convertCoinWithPrecision(cdcs[r].stable_token_amount)))
            logging.debug("----------------------"+str(cdcs[r].stable_token_amount))
            self.cdcModel.setItem(r, 3, QStandardItem('N/A'))
            if cdcs[r].state == 1:
                self.cdcModel.setItem(r, 4, QStandardItem('OPEN'))
                #FIXME, database is not updated. The CLOSED cdc query from chain will return None.
                cdcInfo = self.cdcOp.get_cdc(cdcs[r].cdc_id)
                if cdcInfo is None:
                    continue
                cdcInfo = json.loads(cdcInfo)
                self.cdcModel.setItem(r, 3, QStandardItem(convertCoinWithPrecision(cdcInfo['stabilityFee'])))
            elif cdcs[r].state == 2:
                self.cdcModel.setItem(r, 4, QStandardItem('LIQUIDATED'))
            elif cdcs[r].state == 3:
                self.cdcModel.setItem(r, 4, QStandardItem('CLOSED'))
            self.cdcModel.setItem(r, 5, QStandardItem(str(cdcs[r].block_number)))
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
    
    def refreshCdcs(self):
        self.accountChange(self.accountList.currentIndex())

    def syncStateChange(self, stateChange):
        if stateChange['syncType'] == SYNC_STATE_TYPE:
            # self.syncLabel.setText(stateChange['data'])
            # self.syncLabel.adjustSize()
            self.statusBar().showMessage(stateChange['data'])
        elif stateChange['syncType'] == SYNC_CONTRACT_TYPE:
            self.cdcContractInfo = stateChange['data']
            self.collateralAdmin.setText(self.cdcContractInfo['admin'])
            self.collateralAsset.setText(self.cdcContractInfo['collateralAsset'])
            self.liquidationRatio.setText(self.cdcContractInfo['liquidationRatio'])
            self.annualStabilityFee.setText(self.cdcContractInfo['annualStabilityFee'])
            self.liquidationPenalty.setText(self.cdcContractInfo['liquidationPenalty'])
            self.liquidationDiscount.setText(self.cdcContractInfo['liquidationDiscount'])
            self.currentPrice.setText(self.priceFeeder.get_price())

