import pytest, json
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_cdc_op import CDCOperation
from .config import USER1, CDC_CONTRACT_ID, HX_TESTNET_RPC


class TestCdcOp():
    def setup_method(self, function):
        self.api = HXWalletApi(name=function.__name__, rpc_url=HX_TESTNET_RPC)
        self.cdc = CDCOperation(USER1['account'], CDC_CONTRACT_ID, self.api)

    def teardown_function(self):
        self.api = None
        self.cdc = None

    def test_info(self):
        info = self.cdc.get_contract_info()
        info = json.loads(info)
        assert(info['admin'] == 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W')
        assert(info['proxy'] == 'HXCexPawducWo8S5uPTtMbzoN31tpxGxwV3H')
        assert(info['state'] == 'COMMON')
        assert(info['collateralAsset'] == 'BTC')
        assert(info['priceFeederAddr'] == 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1')
        assert(info['stableTokenAddr'] == 'HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2')
        assert(info['liquidationRatio'] == '1.25')
        assert(info['annualStabilityFee'] == '0.15')
        assert(info['liquidationPenalty'] == '0.13')
        assert(info['liquidationDiscount'] == '0.03')
        assert(info['annualStabilityFeeList'] == ["1564047710,0.15"])
        assert(int(info['totalLiquidationPenalty']) >= 0)
        assert(int(info['totalCollectedStablityFee']) >= 0)


