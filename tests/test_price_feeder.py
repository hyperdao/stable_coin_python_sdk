import pytest
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_price_feeder import PriceFeeder


api = None

class TestPriceFeeder():
    def setup_method(self, function):
        self.api = HXWalletApi(name=function.__name__, rpc_url='http://192.168.1.121:8077/')

    def teardown_function(self):
        self.api = None


    def test_get_owner(self):
        pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)
        owner = pf.get_owner()
        assert(owner == 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W')

    def test_get_state(self):
        pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)
        owner = pf.get_state()
        assert(owner == 'COMMON')

    def test_get_price(self):
        pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)
        owner = pf.get_price()
        assert(owner == '2.5')

    def test_get_base_asset(self):
        pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)
        owner = pf.get_base_asset()
        assert(owner == 'BTC')

    def test_get_quote_asset(self):
        pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)
        owner = pf.get_quote_asset()
        assert(owner == 'HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2')