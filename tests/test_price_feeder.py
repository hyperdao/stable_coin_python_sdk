import pytest
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_price_feeder import PriceFeeder


def test_get_owner():
    api = HXWalletApi(name='test_get_owner', rpc_url='http://192.168.1.121:8077/')
    pf = PriceFeeder('da', 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1', api)
    owner = pf.get_owner()
    assert(owner['result'] == 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W')