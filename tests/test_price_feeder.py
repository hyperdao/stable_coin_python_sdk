import pytest
import decimal
import json
import time
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_price_feeder import PriceFeeder
from .config import HX_TESTNET_RPC, FEEDER_CONTRACT_ID, PRICE_FEEDER, USER1


class TestPriceFeeder():
    def setup_method(self, function):
        self.api = HXWalletApi(name=function.__name__, rpc_url=HX_TESTNET_RPC)
        self.pf = PriceFeeder(PRICE_FEEDER['account'], FEEDER_CONTRACT_ID, self.api)

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
        assert(previousOwner == PRICE_FEEDER['address'])
        self.pf.change_owner(USER1['address'])
        time.sleep(6)
        currentOwner = self.pf.get_owner()
        assert(currentOwner == USER1['address'])
        newPf = PriceFeeder(USER1['account'], USER1['address'], self.api)
        newPf.change_owner(previousOwner)

    def test_change_feeder(self):
        feeders = json.loads(self.pf.get_feeders())
        assert(PRICE_FEEDER['address'] in feeders)
        assert(USER1['address'] not in feeders)
        self.pf.add_feeder(USER1['address'])
        time.sleep(6)
        feeders = json.loads(self.pf.get_feeders())
        assert(PRICE_FEEDER['address'] in feeders)
        assert(USER1['address'] in feeders)
        self.pf.remove_feeder(USER1['address'])
        time.sleep(6)
        feeders = json.loads(self.pf.get_feeders())
        assert(PRICE_FEEDER['address'] in feeders)
        assert(USER1['address'] not in feeders)
