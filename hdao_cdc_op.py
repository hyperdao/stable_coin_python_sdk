from hx_wallet_api import HXWalletApi

class CDCOperation:
    def __init__(self, account, contract, wallet_api):
        HXWalletApi.__init__("PriceFeeder")
        self.account = account
        self.contract = contract
        self.wallet_api = wallet_api
    
    # online APIs
    def init_config(self, collateralAsset, collateralizationRatio,\
            annualStabilityFee, liquidationRatio, liquidationPenalty,\
            liquidationDiscount, priceFeederAddr, stableCoinAddr, proxyAddr):
        return self.wallet_api.rpc_request('invoke_contract',\
            [
                self.account,
                0.0001,
                10000,
                self.contract,
                'init_config',
                ",".join([
                    collateralAsset,
                    collateralizationRatio,
                    annualStabilityFee,
                    liquidationRatio,
                    liquidationPenalty,
                    liquidationDiscount,
                    priceFeederAddr,
                    stableCoinAddr,
                    proxyAddr
                ])
            ]
        )

    def open_cdc(self, amount):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'add_feeder', addr])

    def add_collateral(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'remove_feeder', addr])

    def liquidate(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'liquidate', addr])

    def close_cdc(self, cdc_id):
        strPrice = str(decimal.Decimal(price).quantize(Decimal('0.00000001')))
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'closeCdc', strPrice])

    # offline APIs
    def get_contract_info(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getInfo", ""])

    def state(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "state", ""])

    def get_cdc(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getPrice", cdc_id])

    def get_liquidable_info(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getLiquidableInfo", cdc_id])



if __name__ == "__main__":
    pass