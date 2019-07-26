import pytest
from hdao.hx_wallet_api import HXWalletApi


def test_info():
    api = HXWalletApi('test_info')
    response = api.rpc_request('info', [])
    assert('result' in response)