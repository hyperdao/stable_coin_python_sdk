import pytest
from hdao.hx_wallet_api import HXWalletApi


def test_info():
    api = HXWalletApi('test_info')
    response = api.rpc_request('info', [])
    assert(response['chain_id'] == '2e13ba07b457f2e284dcfcbd3d4a3e4d78a6ed89a61006cdb7fdad6d67ef0b12')