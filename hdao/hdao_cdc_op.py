import json

class CDCOperation:
    def __init__(self, account, contract, wallet_api):
        self.account = account
        self.contract = contract
        self.wallet_api = wallet_api
        self.asset = ""
        info = self.get_contract_info()
        info = json.loads(info)
        if info is not None or (info.has_key('state') and info['state'] != "NOT_INITED"):
            self.asset = info['collateralAsset']
    
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

    def open_cdc(self, collateralAmount, stableCoinAmount):
        if self.asset == "":
            return None
        if stableCoinAmount > 0:
            open_args = "openCdc,"+str(decimal.Decimal(stableCoinAmount).quantize(Decimal('0.00000001')))
        else:
            open_args = ""
        return self.wallet_api.rpc_request('transfer_to_contract', [self.account, self.contract, collateralAmount, self.asset, open_args, 0.0001, 10000, True])

    def add_collateral(self, cdc_id, collateralAmount):
        add_args = "addCollateral,"+str(cdc_id)
        return self.wallet_api.rpc_request('transfer_to_contract', [self.account, self.contract, collateralAmount, self.asset, add_args, 0.0001, 10000, True])

    def generate_stable_coin(self, cdc_id, amount):
        args = ",".join([cdc_id, str(decimal.Decimal(amount).quantize(Decimal('0.00000001')))])
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'expandLoan', args])

    def withdraw_collateral(self, cdc_id, amount):
        args = ",".join([cdc_id, str(decimal.Decimal(amount).quantize(Decimal('0.00000001')))])
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'widrawCollateral', args])

    def transfer_cdc(self, cdc_id, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'transferCdc', ",".join([cdc_id, addr])])

    def pay_back(self, cdc_id, amount):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'payBack', ",".join([cdc_id, str(amount)])])

    def liquidate(self, cdc_id, stableCoinAmount, assetAmount):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'liquidate', ",".join([cdc_id, stableCoinAmount, assetAmount])])

    def close_cdc(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'closeCdc', cdc_id])

    def set_annual_stability_fee(self, fee):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'setAnnualStabilityFee', str(fee)])

    def set_liquidation_penalty(self, fee):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'setLiquidationPenalty', str(fee)])

    def set_liquidation_discount(self, fee):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'setLiquidationDiscount', str(fee)])

    def set_price_feeder_addr(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'setPriceFeederAddr', addr])

    def change_admin(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'changeAdmin', addr])

    def global_liquidate(self):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'globalLiquidate', ""])

    def take_back_collateral_by_cdc(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'takeBackCollateralByCdc', cdc_id])

    def take_back_collateral_by_token(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'takeBackCollateralByToken', cdc_id])

    def close_contract(self):
        return self.wallet_api.rpc_request('invoke_contract', [self.account, 0.0001, 10000, self.contract, 'closeContract', ""])

    # offline APIs
    def get_contract_info(self):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getInfo", ""])

    def get_cdc(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getPrice", cdc_id])

    def get_liquidable_info(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getLiquidableInfo", cdc_id])



if __name__ == "__main__":
    pass