import pytest
import time
import random
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_events import EventsCollector
from hdao.hdao_cdc_op import CDCOperation
from .config import USER1, CDC_CONTRACT_ID, HX_TESTNET_RPC


# class CDCOwner():
#     def __init__(self, account):
#         self.account = account
#         self.walletApi = HXWalletApi(name=account, rpc_url=HX_TESTNET_RPC)
#         self.cdcOp = CDCOperation(account, CDC_CONTRACT_ID, self.walletApi)

#     def open_cdc(self):
#         collateralAmount = random.uniform(0.000001, 0.000002)
#         self.cdcOp.open_cdc(collateralAmount, collateralAmount)


class TestHdaoEvents():

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, function):
        self.api = HXWalletApi(name="TestHdaoEvents", rpc_url=HX_TESTNET_RPC)
        self.cdcOp = CDCOperation(USER1['account'], CDC_CONTRACT_ID, self.api)
        self.collector = EventsCollector(USER1['account'], CDC_CONTRACT_ID, self.api)

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
    
    def test_cdc_op_query(self):
        cdcs = self.collector.query_cdc_op_by_id('ee80006bb468a434af71c38cb62e1afac6a51c52')
        assert(len(cdcs) == 2)
        assert(cdcs[0].cdc_id == 'ee80006bb468a434af71c38cb62e1afac6a51c52')

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
            cdcs = self.collector.query_cdc_by_address(USER1['address'])
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
                cdcs = self.collector.query_cdc_by_address(USER1['address'])
                for c in cdcs:
                    if c.cdc_id == previousCdcId:
                        if c.state == 3:
                            raise AssertionError
                        break
