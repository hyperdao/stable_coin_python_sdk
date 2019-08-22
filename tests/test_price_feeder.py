import pytest
import decimal
import json
import time
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_price_feeder import PriceFeeder


class TestPriceFeeder():
    def setup_method(self, function):
        self.api = HXWalletApi(name=function.__name__, rpc_url='http://192.168.1.121:30088/')
        self.pf = PriceFeeder('senator0', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)

    def teardown_function(self):
        self.api = None


    def test_get_state(self):
        owner = self.pf.get_state()
        assert(owner == 'COMMON')

    def test_get_base_asset(self):
        owner = self.pf.get_base_asset()
        assert(owner == 'BTC')

    def test_get_quote_asset(self):
        owner = self.pf.get_quote_asset()
        assert(owner == 'HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2')

    def test_feed_price(self):
        previousPrice = self.pf.get_price()
        assert(previousPrice != None)
        previousPrice = decimal.Decimal(previousPrice)
        newPrice = previousPrice + decimal.Decimal('0.1')
        self.pf.feed_price(newPrice)
        time.sleep(6)
        currentPrice = self.pf.get_price()
        currentPrice = decimal.Decimal(currentPrice)
        assert(currentPrice == newPrice)
        self.pf.feed_price(previousPrice)

    def test_change_owner(self):
        previousOwner = self.pf.get_owner()
        assert(previousOwner == 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W')
        self.pf.change_owner('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh')
        time.sleep(6)
        currentOwner = self.pf.get_owner()
        assert(currentOwner == 'HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh')
        newPf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', self.api)
        newPf.change_owner(previousOwner)

    def test_change_feeder(self):
        feeders = json.loads(self.pf.get_feeders())
        assert('HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W' in feeders)
        assert('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh' not in feeders)
        self.pf.add_feeder('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh')
        time.sleep(6)
        feeders = json.loads(self.pf.get_feeders())
        assert('HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W' in feeders)
        assert('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh' in feeders)
        self.pf.remove_feeder('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh')
        time.sleep(6)
        feeders = json.loads(self.pf.get_feeders())
        assert('HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W' in feeders)
        assert('HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh' not in feeders)
