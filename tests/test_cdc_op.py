import pytest
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_cdc_op import CDCOperation


class TestCdcOp():
    def setup_method(self, function):
        self.api = HXWalletApi(name=function.__name__, rpc_url='http://192.168.1.121:8077/')
        self.cdc = CDCOperation('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.api)

    def teardown_function(self):
        self.api = None
        self.cdc = None

    def test_info(self):
        cdc = CDCOperation('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.api)
        info = cdc.get_contract_info()
        assert(info == "{\"admin\":\"HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W\",\"proxy\":\"HXCexPawducWo8S5uPTtMbzoN31tpxGxwV3H\",\"state\":\"COMMON\",\"collateralAsset\":\"BTC\",\"priceFeederAddr\":\"HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1\",\"stableTokenAddr\":\"HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2\",\"liquidationRatio\":\"1.25\",\"annualStabilityFee\":\"0.15\",\"liquidationPenalty\":\"0.13\",\"liquidationDiscount\":\"0.03\",\"annualStabilityFeeList\":[\"1564047710,0.15\"],\"totalLiquidationPenalty\":0,\"totalCollectedStablityFee\":0}")

