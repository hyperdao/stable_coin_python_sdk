import pytest
import time
import random
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_events import EventsCollector
from hdao.hdao_cdc_op import CDCOperation


class CDCOwner():
    def __init__(self, account):
        self.account = account
        self.walletApi = HXWalletApi(name=account, rpc_url='http://192.168.1.121:30088/')
        self.cdcOp = CDCOperation(account, 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.walletApi)

    def open_cdc(self):
        collateralAmount = random.uniform(0.000001, 0.000002)
        self.cdcOp.open_cdc(collateralAmount, collateralAmount)


class TestHdaoEvents():

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, function):
        self.api = HXWalletApi(name="TestHdaoEvents", rpc_url='http://192.168.1.121:30088/')
        self.cdcOp = CDCOperation('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.api)
        self.collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.api)

    def teardown_function(self):
        self.api = None
        self.collector = None
        self.cdc = None

    # def test_collect(self):
    #     self.collector.collect_event(969234)
    
    def test_cdc_query(self):
        cdcs = self.collector.query_cdc_by_address('HXNUeoaUVkUg9q2uokDwzdrxp1uE4L9VhTSs')
        assert(len(cdcs) == 1)
        assert(cdcs[0].cdc_id == '0694d145b7000d8d5b13f9f4c4acbee3533ca14a')
    
    def test_cdc_normal_operations(self):
        info = self.api.rpc_request("info", [])
        block_num = info['head_block_num']
        result = self.cdcOp.open_cdc(0.001, 0.001)
        assert("trxid" in result and result["trxid"] != "")
        confirmed = False
        cdc = None
        while not confirmed:
            time.sleep(3)
            self.collector.collect_event(block_num)
            cdcs = self.collector.query_cdc_by_address('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh')
            for c in cdcs:
                if c.block_number > block_num:
                    confirmed = True
                    cdc = c
                    break
        assert(cdc.collateral_amount == '100000' and cdc.collateral_amount == '100000')
        previousCdcId = cdc.cdc_id
        self.cdcOp.close_cdc(cdc.cdc_id)
        confirmed = False
        waitTimes = 0
        with pytest.raises(AssertionError):
            while waitTimes < 10:
                time.sleep(3)
                self.collector.collect_event(block_num)
                cdcs = self.collector.query_cdc_by_address('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh')
                for c in cdcs:
                    if c.cdc_id == previousCdcId:
                        if c.state == 3:
                            raise AssertionError
                        break
