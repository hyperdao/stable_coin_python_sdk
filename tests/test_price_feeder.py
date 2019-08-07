import pytest
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_price_feeder import PriceFeeder


def test_get_owner():
    api = HXWalletApi(name='test_get_owner', rpc_url='http://192.168.1.121:8077/')
    pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', api)
    owner = pf.get_owner()
    assert(owner['result'] == 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W')

def test_get_state():
    api = HXWalletApi(name='test_get_state', rpc_url='http://192.168.1.121:8077/')
    pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', api)
    owner = pf.get_state()
    assert(owner['result'] == 'COMMON')

def test_get_price():
    api = HXWalletApi(name='test_get_price', rpc_url='http://192.168.1.121:8077/')
    pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', api)
    owner = pf.get_price()
    assert(owner['result'] == '2.5')

def test_get_base_asset():
    api = HXWalletApi(name='test_get_base_asset', rpc_url='http://192.168.1.121:8077/')
    pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', api)
    owner = pf.get_base_asset()
    assert(owner['result'] == 'BTC')

def test_get_quote_asset():
    api = HXWalletApi(name='test_get_quote_asset', rpc_url='http://192.168.1.121:8077/')
    pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', api)
    owner = pf.get_quote_asset()
    assert(owner['result'] == 'HXCcuGJV3cVnwMPk4S524ADcC9PWxRA3qKR2')