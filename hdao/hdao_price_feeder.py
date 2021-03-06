# encoding: utf-8
import decimal
from hdao.hx_wallet_api import HXWalletApi
class PriceFeeder:
    def __init__(self, account, contract, wallet_api):
        self.account = account
        self.contract = contract
        self.wallet_api = wallet_api
    
    # online APIs
    def init_config(self, baseAsset, quoteAsset, init_price, maxChangeRatio):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'init_config', ",".join([baseAsset, quoteAsset, init_price, maxChangeRatio])])

    def add_feeder(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'add_feeder', addr])

    def remove_feeder(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'remove_feeder', addr])

    def change_owner(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'change_owner', addr])

    def feed_price(self, price):
        strPrice = str(decimal.Decimal(price).quantize(decimal.Decimal('0.00000001')))
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'feed_price', strPrice])

    # offline APIs
    def get_owner(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "owner", ""])

    def get_state(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "state", ""])

    def get_price(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getPrice", ""])

    def get_feeders(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "feeders", ""])

    def get_base_asset(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "baseAsset", ""])

    def get_quote_asset(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "quotaAsset", ""])

    def get_feedPrices(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "feedPrices", ""])


if __name__ == "__main__":
    api = HXWalletApi("HDao", rpc_url="http://127.0.0.1:9089/")
    feeder = PriceFeeder("lepus","HXCTPssTWYEK5oYvD1L9XgAsPLqTiPnnCKsH",api)
    r = feeder.init_config("BTC","HXCapbR3MJhgG8byC87WrTGtCPjgArocUWjC","10000.12","0.11")
    print(r)

