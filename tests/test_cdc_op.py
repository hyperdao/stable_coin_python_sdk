import pytest
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
        assert(info == "{\"admin\":\"HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W\",\"proxy\":\"HXCexPawducWo8S5uPTtMbzoN31tpxGxwV3H\",\"state\":\"COMMON\",\"collateralAsset\":\"BTC\",\"priceFeederAddr\":\"HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1\",\"stableTokenAddr\":\"HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2\",\"liquidationRatio\":\"1.25\",\"annualStabilityFee\":\"0.15\",\"liquidationPenalty\":\"0.13\",\"liquidationDiscount\":\"0.03\",\"annualStabilityFeeList\":[\"1564047710,0.15\"],\"totalLiquidationPenalty\":0,\"totalCollectedStablityFee\":0}")

