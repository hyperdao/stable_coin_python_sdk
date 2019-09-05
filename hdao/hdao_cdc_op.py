import json
import decimal
from .utils import convertCoinWithPrecision

class CDCOperation:
    collateralPrecision = {
        'BTC': 100000000,
        'ETH': 100000000,
        'HX': 100000
    }

    def __init__(self, account, contract, wallet_api):
        self.account = account
        self.contract = contract
        self.wallet_api = wallet_api
        self.asset = ""
        self.precision = 100000000
        info = self.get_contract_info()
        info = json.loads(info)
        if info is not None or (info.has_key('state') and info['state'] != "NOT_INITED"):
            self.asset = info['collateralAsset']
            self.precision = CDCOperation.collateralPrecision[self.asset]
    
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
        collateralAmount = convertCoinWithPrecision(collateralAmount, 0)
        stableCoinAmount = decimal.Decimal(stableCoinAmount)*100000000
        if stableCoinAmount > 0:
            open_args = "openCdc,"+str(stableCoinAmount.quantize(decimal.Decimal('0')))
        else:
            open_args = ""
        return self.wallet_api.rpc_request('transfer_to_contract', [self.account, self.contract, collateralAmount, self.asset, open_args, 0.0001, 10000, True])

    def add_collateral(self, cdc_id, collateralAmount):
        if self.asset == "":
            return None
        collateralAmount = convertCoinWithPrecision(collateralAmount, 0)
        add_args = "addCollateral,"+str(cdc_id)
        return self.wallet_api.rpc_request('transfer_to_contract', [self.account, self.contract, collateralAmount, self.asset, add_args, 0.0001, 10000, True])

    def generate_stable_coin(self, cdc_id, amount):
        if self.asset == "":
            return None
        amount = (decimal.Decimal(amount) * self.precision).quantize(decimal.Decimal('0'))
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'expandLoan', 
            ",".join([cdc_id, str(amount)])])

    def withdraw_collateral(self, cdc_id, amount):
        if self.asset == "":
            return None
        amount = (decimal.Decimal(amount) * self.precision).quantize(decimal.Decimal('0'))
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'widrawCollateral', 
            ",".join([cdc_id, str(amount)])])

    def transfer_cdc(self, cdc_id, addr):
        if self.asset == "":
            return None
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'transferCdc', 
            ",".join([cdc_id, addr])])

    def pay_back(self, cdc_id, amount):
        if self.asset == "":
            return None
        amount = (decimal.Decimal(amount) * self.precision).quantize(decimal.Decimal('0'))
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'payBack', 
            ",".join([cdc_id, str(amount)])])

    def liquidate(self, cdc_id, stableCoinAmount, assetAmount):
        stableCoinAmount = (decimal.Decimal(stableCoinAmount) * self.precision).quantize(decimal.Decimal('0'))
        assetAmount = (decimal.Decimal(assetAmount) * self.precision).quantize(decimal.Decimal('0'))
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'liquidate', 
            ",".join([cdc_id, convertCoinWithPrecision(stableCoinAmount, 0), convertCoinWithPrecision(assetAmount, 0)])])

    def close_cdc(self, cdc_id):
        if self.asset == "":
            return None
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'closeCdc', 
            cdc_id])

    def set_annual_stability_fee(self, fee):
        if self.asset == "":
            return None
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'setAnnualStabilityFee', 
            fee])

    def set_liquidation_ratio(self, ratio):
        if self.asset == "":
            return None
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'setLiquidationRatio', 
            ratio])

    def set_liquidation_penalty(self, fee):
        if self.asset == "":
            return None
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'setLiquidationPenalty', 
            fee])

    def set_liquidation_discount(self, fee):
        if self.asset == "":
            return None
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'setLiquidationDiscount', 
            fee])

    def set_price_feeder_addr(self, addr):
        return self.wallet_api.rpc_request('invoke_contract', [
            self.account, 0.0001, 10000, 
            self.contract, 'setPriceFeederAddr', 
            addr])

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
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getCdc", cdc_id])

    def get_liquidable_info(self, cdc_id):
        return self.wallet_api.rpc_request('invoke_contract_offline', [self.account, self.contract, "getLiquidableInfo", cdc_id])



if __name__ == "__main__":
    from hx_wallet_api import HXWalletApi
    api = HXWalletApi(name="TestHdaoEvents", rpc_url='http://192.168.1.121:30088/')
    cdcOp = CDCOperation('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    info = cdcOp.close_cdc('a9f361bac02cec7cf7361f4e4c00b7dc76841544')
    print(info)
