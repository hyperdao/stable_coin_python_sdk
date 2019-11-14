import json
import random
import time
import copy
import datetime
import pathlib

from hdao.hx_wallet_api import *
from hdao.utils import *
from hdao.hdao_cdc_op import CDCOperation
from hdao.hdao_price_feeder import *

############################## 参数 ################################################################
wallet_api = HXWalletApi(name="TestHdao", rpc_url='http://192.168.1.121:30088/')
mainAccount = "april"  # 有HX 和 抵押品资产
cdc_address = 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks'
assets = {"1.3.0":"HX","1.3.1":"BTC"}
stableTokenPrecision = 100000000
collateralPrecision = 100000000
HXPRECISION = 100000
##############################################################################################


accounts = {} # address => name
accountNames = {}  # name => address
cdcs = {} #userAddr => {trxid :cdcid}

def get_my_accounts():
    result = wallet_api.rpc_request("list_my_accounts", [])
    accounts.clear()
    names = []
    accountNames.clear()
    for i in range(0, len(result)):
        r = result[i]
        accounts[r["addr"]] = r["name"]
        accountNames[r["name"]] = r["addr"]
        names.append(r["name"])
    return names

def createAccounts(account_name_prefix,num):
    names = get_my_accounts()

    for i in range(0, num):
        user = account_name_prefix + str(i)
        if(user not in names):
            addr = wallet_api.rpc_request("wallet_create_account",[user])
            if(addr is None):
                raise RuntimeError("error!!! wallet_create_account "+user)
            accounts[addr] = user
            accountNames[user] = addr

################################################################
def token_balanceOf(tokenAddr,user):
    userAddr = accountNames[user]
    return int(wallet_api.rpc_request('invoke_contract_offline', [user, tokenAddr, "balanceOf", userAddr]))

def token_supply(tokenAddr,mainAccount):
    return int(wallet_api.rpc_request('invoke_contract_offline', [mainAccount, tokenAddr, "totalSupply", '']))

def token_transfer(tokenAddr,fromuser,touser,amount):
    fromuserAddr = accountNames[fromuser]
    touserAddr = accountNames[touser]
    return wallet_api.rpc_request('invoke_contract', [fromuser,0.0001, 100000, tokenAddr, "transfer", touserAddr+","+str(amount)])

#############################################################################################################################
def openCdc(user,cdcUser,collateralAsset,price,liquidationRatio,filepath,isMax=False):
    # open cdc
    r = False
    if (user not in cdcs.keys() ):
        cdcuserinfo = {}
        balances = get_account_balances(user, wallet_api)
        collateralAmount = 0
        if (collateralAsset in balances.keys()):
            collateralAmount = balances[collateralAsset]

        if(not isMax):
            collateralAmount = int(collateralAmount / 2)

        maxStableCoinAmount = int(price * collateralAmount / liquidationRatio)
        if (maxStableCoinAmount > 0):
            if(isMax):
                randStableCoinAmount = maxStableCoinAmount - 1
            else:
                randStableCoinAmount = random.randint(1, int(maxStableCoinAmount * 1.05))
            result = cdcUser.open_cdc(collateralAmount/collateralPrecision, randStableCoinAmount/stableTokenPrecision)
            r = True
            if (result is not None):
                trxid = result['trxid']
                cdcuserinfo['trxid'] = trxid
                cdcs[user] = cdcuserinfo
                print("open cdc txid:"+trxid+ " user:"+user + " collateralAmount:"+str(collateralAmount)+" randStableCoinAmount:"+str(randStableCoinAmount))
                with open(filepath, 'w') as f:
                    json.dump(cdcs,f)
            else:
                print("open cdc fail !!!   user:" + user + " collateralAmount:" + str(
                    collateralAmount) + " randStableCoinAmount:" + str(randStableCoinAmount))
    return r

def addCollateral(user,cdcUser,collateralAsset):
    # add
    r = False
    if (user in cdcs.keys() and "trxid" in cdcs[user].keys()):
        trxid = cdcs[user]['trxid']
        balances = get_account_balances(user, wallet_api)
        maxcollateralAmount = 0
        if (collateralAsset in balances.keys()):
            maxcollateralAmount = balances[collateralAsset]
        if(maxcollateralAmount>0):
            collateralAmount = random.randint(1,maxcollateralAmount+10)
            result = cdcUser.add_collateral(trxid,collateralAmount/collateralPrecision)
            r = True
            if result is not None:
                print("addCollateral txid:" + trxid + " user:" + user + " collateralAmount:" + str(collateralAmount))
            else:
                print("addCollateral fail !!!! txid:" + trxid + " user:" + user + " collateralAmount:" + str(collateralAmount))
    return r

def expandLoan(user,cdcUser,price,liquidationRatio):
    # generate_stable_coin
    r = False
    if (user in cdcs.keys()  and "trxid" in cdcs[user].keys()):
        trxid = cdcs[user]['trxid']
        result = cdcUser.get_cdc(trxid)
        if(result is not None):
            cdcinfo = json.loads(result)
            collateralAmount = cdcinfo['collateralAmount']
            stabilityFee = int(cdcinfo['stabilityFee'])
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            isNeedLiquidation = cdcinfo['isNeedLiquidation']
            maxStableCoinAmount = int((price * collateralAmount / liquidationRatio) - stabilityFee - stableTokenAmount)

            if(maxStableCoinAmount>0):
                stableCoinAmount = random.randint(1,int(maxStableCoinAmount*1.05))
                result = cdcUser.generate_stable_coin(trxid,stableCoinAmount/stableTokenPrecision)
                r = True
                if result is not None:
                    print("expandLoan txid:" + trxid + " user:" + user + " stableCoinAmount:" + str(stableCoinAmount))
                else:
                    print("expandLoan fail !!! txid:" + trxid + " user:" + user + " stableCoinAmount:" + str(stableCoinAmount))
    return r

def widrawCollateral(user,cdcUser,price,liquidationRatio):
    # withdraw
    r = False
    if (user in cdcs.keys()  and "trxid" in cdcs[user].keys()):
        trxid = cdcs[user]['trxid']
        result = cdcUser.get_cdc(trxid)
        if(result is not None):
            cdcinfo = json.loads(result)
            collateralAmount = cdcinfo['collateralAmount']
            stabilityFee = int(cdcinfo['stabilityFee'])
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            isNeedLiquidation = cdcinfo['isNeedLiquidation']
            maxStableCoinAmount = int((price * collateralAmount / liquidationRatio) - stabilityFee - stableTokenAmount)
            maxCollateralAmount = int(maxStableCoinAmount/price)
            if(maxCollateralAmount>0):
                collateralAmount = random.randint(1,int(maxCollateralAmount*1.05))
                result = cdcUser.withdraw_collateral(trxid,collateralAmount/collateralPrecision)
                r = True
                if result is not None:
                    print("widrawCollateral txid:" + trxid + " user:" + user + " collateralAmount:" + str(collateralAmount))
                else:
                    print("widrawCollateral fail!!! txid:" + trxid + " user:" + user + " collateralAmount:" + str(
                        collateralAmount))
    return r

def pay_back(user,cdcUser,tokenAddr,fromuser):
    # pay back
    r = False
    if (user in cdcs.keys()  and "trxid" in cdcs[user].keys()):
        trxid = cdcs[user]['trxid']
        result = cdcUser.get_cdc(trxid)
        if(result is not None):
            cdcinfo = json.loads(result)
            collateralAmount = cdcinfo['collateralAmount']
            stabilityFee = int(cdcinfo['stabilityFee'])
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            isNeedLiquidation = cdcinfo['isNeedLiquidation']
            totalNeedPayAmount = stableTokenAmount+stabilityFee
            if(totalNeedPayAmount > 0):
                payAmount = random.randint(1,int(totalNeedPayAmount*1.05))
                tokenbalance = token_balanceOf(tokenAddr,user)
                if(payAmount > tokenbalance):
                    r = token_transfer(tokenAddr,fromuser,user,(payAmount-tokenbalance))
                    #if r is not None:
                        #time.sleep(5)
                result = cdcUser.pay_back(trxid, payAmount/stableTokenPrecision)
                r = True
                if result is not None:
                    print("pay_back txid:" + trxid + " user:" + user + " payAmount:" + str(
                        payAmount))
                else:
                    print("pay_back fail !!! txid:" + trxid + " user:" + user + " payAmount:" + str(
                        payAmount))
    return r

def close_cdc(user,cdcUser,tokenAddr,fromuser,filepath):
    # close
    r = False
    if (user in cdcs.keys()  and "trxid" in cdcs[user].keys()):
        trxid = cdcs[user]['trxid']
        result = cdcUser.get_cdc(trxid)
        if (result is not None):
            cdcinfo = json.loads(result)
            collateralAmount = cdcinfo['collateralAmount']
            stabilityFee = int(cdcinfo['stabilityFee'])
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            isNeedLiquidation = cdcinfo['isNeedLiquidation']
            totalNeedPayAmount = stableTokenAmount + stabilityFee
            if (totalNeedPayAmount > 0):
                tokenbalance = token_balanceOf(tokenAddr, user)
                if (totalNeedPayAmount > tokenbalance):
                    r = token_transfer(tokenAddr, fromuser, user, (totalNeedPayAmount - tokenbalance))
                    #if r is not None:
                        #time.sleep(5)
                result = cdcUser.close_cdc(trxid)
                r = True
                if result is not None:
                    print("close_cdc txid:" + trxid + " user:" + user + " totalNeedPayAmount:" + str(
                            totalNeedPayAmount))
                    del cdcs[user]
                    with open(filepath, 'w') as f:
                        json.dump(cdcs, f)
                else:
                    print("close_cdc fail !!! txid:" + trxid + " user:" + user + " totalNeedPayAmount:" + str(
                        totalNeedPayAmount))
    return r


def checkAndLiquidate(usersNum,account_name_prefix,tokenAddr,filepath,cdcUsers,fromuser):
    # check
    count = 0
    lenPrefix = len(account_name_prefix)
    origcdcs = copy.deepcopy(cdcs)
    for user in origcdcs.keys():
        if(user.startswith(account_name_prefix)):
            istr = user[lenPrefix:]
            i = int(istr)
            cdcUser = cdcUsers[i]
            trxid = origcdcs[user]['trxid']
            result = cdcUser.get_liquidable_info(trxid)
            if (result is not None):
                cdcinfo = json.loads(result)
                #collateralAmount = cdcinfo['collateralAmount']
                #stabilityFee = cdcinfo['stabilityFee']
                #stableTokenAmount = cdcinfo['stableTokenAmount']
                isNeedLiquidation = cdcinfo['isNeedLiquidation']

                if(isNeedLiquidation):
                    isBadDebt = cdcinfo['isBadDebt']
                    if not isBadDebt:
                        repayStableTokenAmount = cdcinfo['repayStableTokenAmount']

                        idx = random.randint(0,usersNum-1)
                        liquidator = account_name_prefix + str(idx)
                        cdcLiquidator = cdcUsers[idx]

                        userTokenbalance = token_balanceOf(tokenAddr, user)
                        if(userTokenbalance>0):
                            token_transfer(tokenAddr, user, liquidator, userTokenbalance)
                            #time.sleep(5)
                        result = cdcUser.get_liquidable_info(trxid)
                        if (result is not None):
                            cdcinfo = json.loads(result)
                            repayStableTokenAmount = cdcinfo['repayStableTokenAmount']
                        tokenbalance = token_balanceOf(tokenAddr, liquidator)
                        if (repayStableTokenAmount > tokenbalance):
                            r = token_transfer(tokenAddr, fromuser, liquidator, (repayStableTokenAmount - tokenbalance))
                        #if r is not None:
                            # time.sleep(5)
                        result = cdcLiquidator.liquidate(trxid, repayStableTokenAmount/stableTokenPrecision, 1/collateralPrecision)
                        if result is not None:
                            count = count + 1
                            print("liquidate txid:" + trxid +" targetUser:" +user+ " liquidator:" + liquidator + " repayStableTokenAmount:" + str(
                                    repayStableTokenAmount))
                            del cdcs[user]
                            with open(filepath, 'w') as f:
                                json.dump(cdcs, f)
                            #time.sleep(5)
                        else:
                            print(
                                "liquidate fail !!! txid:" + trxid + "targetUser:" + user + " liquidator:" + liquidator + " repayStableTokenAmount:" + str(
                                    repayStableTokenAmount))
    return count


def closeAllUsersCdcs(usersNum,account_name_prefix,filepath,mainAccount):
    global cdcs
    if(len(cdcs) == 0):
        try:
            with open(filepath, 'r') as load_f:
                cdcs = json.load(load_f)
        except BaseException as e:
            logging.error(str(e))

    cdcUsers = []
    if(len(cdcs)==0):
        print("closeAllUsersCdcs , no cdcs!!!!")
        #return
    else:
        for i in range(0, usersNum):
            user = account_name_prefix + str(i)
            cdcUsers.append(CDCOperation(user, cdc_address, wallet_api))

    get_my_accounts()

    contract_info = json.loads(CDCOperation(mainAccount, cdc_address, wallet_api).get_contract_info())

    cdc_admin_addr = contract_info['admin']
    priceFeederAddr = contract_info['priceFeederAddr']
    stableTokenAddr = contract_info['stableTokenAddr']
    collateralAsset = contract_info['collateralAsset']
    liquidationRatio = float(contract_info['liquidationRatio'])
    annualStabilityFee = float(contract_info['annualStabilityFee'])

    YEARSECS = 31536000

    cdc_admin = accounts[cdc_admin_addr]
    cdcAdmin = CDCOperation(cdc_admin, cdc_address, wallet_api)
    priceFeederUser = PriceFeeder(cdc_admin, priceFeederAddr, wallet_api)
    feeders = json.loads(priceFeederUser.get_feeders())
    price_feeder = accounts[feeders[0]]
    priceFeeder = PriceFeeder(price_feeder, priceFeederAddr, wallet_api)


    fromuser = cdc_admin
    cdcFromUser = cdcAdmin

    origStableTokenSupply = token_supply(stableTokenAddr,mainAccount)

    totalDestoryedStableTokenAmount = 0
    lenPrefix = len(account_name_prefix)
    origcdcs = copy.deepcopy(cdcs)
    time.sleep(5)
    for user in origcdcs.keys():
        if(user.startswith(account_name_prefix)):
            i = int(user[lenPrefix:])
            cdcUser = cdcUsers[i]
            trxid = origcdcs[user]['trxid']
            result = cdcUser.get_cdc(trxid)
            if (result is not None):
                cdcinfo = json.loads(result)
                if(len(cdcinfo)==0):
                    continue
                collateralAmount = int(cdcinfo['collateralAmount'])
                stabilityFee = int(cdcinfo['stabilityFee'])
                stableTokenAmount = int(cdcinfo['stableTokenAmount'])
                isNeedLiquidation = cdcinfo['isNeedLiquidation']
                totalNeedPayAmount = stableTokenAmount + stabilityFee
                if (totalNeedPayAmount > 0):
                    tokenbalance = token_balanceOf(stableTokenAddr, user)
                    if (totalNeedPayAmount > tokenbalance):
                        fromusertokenbalance = token_balanceOf(stableTokenAddr, fromuser)
                        if(fromusertokenbalance <= (totalNeedPayAmount - tokenbalance)):
                            price = float(priceFeeder.get_price())
                            addCollateral(fromuser,cdcFromUser,collateralAsset)
                            #time.sleep(5)
                            expandLoan(fromuser,cdcFromUser,price,liquidationRatio)
                            #time.sleep(5)
                        r = token_transfer(stableTokenAddr, fromuser, user, (totalNeedPayAmount - tokenbalance + int(stableTokenAmount*20/YEARSECS*annualStabilityFee) ))
                        #if r is not None:
                            #time.sleep(5)
                        result = cdcUser.close_cdc(trxid)
                        if result is not None:
                            print("close_cdc txid:" + trxid + " user:" + user + " totalNeedPayAmount:" + str(
                                    totalNeedPayAmount)+" stableTokenAmount:"+str(stableTokenAmount))
                            totalDestoryedStableTokenAmount = totalDestoryedStableTokenAmount+stableTokenAmount
                            del cdcs[user]
                            with open(filepath, 'w') as f:
                                json.dump(cdcs, f)
                        else:
                            print("close_cdc fail !!! txid:" + trxid + " user:" + user + " totalNeedPayAmount:" + str(
                                totalNeedPayAmount) + " stableTokenAmount:" + str(stableTokenAmount))




    if (cdc_admin in cdcs.keys() and "trxid" in cdcs[cdc_admin].keys()):
        trxid = cdcs[cdc_admin]['trxid']
        result = cdcAdmin.get_cdc(trxid)
        if (result is not None):
            cdcinfo = json.loads(result)
            #collateralAmount = cdcinfo['collateralAmount']
            stabilityFee = int(cdcinfo['stabilityFee'])
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            #isNeedLiquidation = cdcinfo['isNeedLiquidation']
            totalNeedPayAmount = stableTokenAmount + stabilityFee
            result = cdcAdmin.close_cdc(trxid)
            if result is not None:
                print("close_cdc admin txid:" + trxid + " user:" + cdc_admin + " totalNeedPayAmount:" + str(
                    totalNeedPayAmount)+" stableTokenAmount:"+str(stableTokenAmount))
                totalDestoryedStableTokenAmount = totalDestoryedStableTokenAmount + stableTokenAmount
                del cdcs[cdc_admin]
                with open(filepath, 'w') as f:
                    json.dump(cdcs, f)
            else:
                print("close_cdc fail !!! txid:" + trxid + " user:" + cdc_admin + " totalNeedPayAmount:" + str(
                    totalNeedPayAmount) + " stableTokenAmount:" + str(stableTokenAmount))


    time.sleep(5)
    for i in range(0,usersnum):
        user = account_name_prefix + str(i)
        tokenbalance = token_balanceOf(stableTokenAddr, user)
        if(tokenbalance > 0):
            r = token_transfer(stableTokenAddr, user, fromuser, tokenbalance)

    currentStableTokenSupply = token_supply(stableTokenAddr, mainAccount)
    totalCdcStableTokenAmount = 0
    for user, cdc in cdcs.items():
        result = cdcAdmin.get_cdc(cdc['trxid'])
        if result is not None:
            cdcinfo = json.loads(result)
            if(len(cdcinfo)==0):
                continue
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            totalCdcStableTokenAmount = totalCdcStableTokenAmount + stableTokenAmount

    print(cdcs)
    print("totalDestoryedStableTokenAmount:"+str(totalDestoryedStableTokenAmount))
    print("origStableTokenSupply:" + str(origStableTokenSupply))
    print("now totalCdcStableTokenAmount:" + str(totalCdcStableTokenAmount))
    print("currentStableTokenSupply:" + str(currentStableTokenSupply))
    if ((origStableTokenSupply - totalDestoryedStableTokenAmount) != currentStableTokenSupply):
        raise RuntimeError("error !!!!! (origStableTokenSupply - totalDestoryedStableTokenAmount) != currentStableTokenSupply")
    if(totalCdcStableTokenAmount > 0):
        raise RuntimeError("error!!! close all cdcs fail!!!")

    cdcAdmin.set_annual_stability_fee("0.15")

    ###################### transfer all users HX,BTC to mainAccount  ##################################################################
    print("transfer all users HX,BTC to mainAccount")
    mainAccountAddr = accountNames[mainAccount]
    for i in range(0, usersNum):
        user = account_name_prefix + str(i)
        #userAddr = accountNames[user]
        userBalances = get_account_balances(user,wallet_api)
        if (collateralAsset in userBalances.keys()):
            amount = userBalances[collateralAsset]
            if (amount > 0):
                wallet_api.rpc_request('transfer_to_address',
                                       [user, mainAccountAddr, convertCoinWithPrecision(amount), collateralAsset, "",
                                        0.0001, 100000,
                                        True])

        if(("HX" in userBalances.keys()) and userBalances["HX"] > HXPRECISION):
            dhxAmount = (userBalances["HX"]-HXPRECISION)/HXPRECISION
            wallet_api.rpc_request('transfer_to_address',
                                   [user, mainAccountAddr, dhxAmount, "HX", "", 0.0001, 100000, True])

    adminBalances = get_account_balances(cdc_admin, wallet_api)
    if (collateralAsset in adminBalances.keys()):
        amount = adminBalances[collateralAsset]
        if (amount > 0):
            wallet_api.rpc_request('transfer_to_address',
                                   [cdc_admin, mainAccountAddr, convertCoinWithPrecision(amount), collateralAsset, "",
                                    0.0001, 100000,
                                    True])

    if (("HX" in adminBalances.keys()) and userBalances["HX"] > HXPRECISION):
        dhxAmount = (adminBalances["HX"] - HXPRECISION) / HXPRECISION
        wallet_api.rpc_request('transfer_to_address',
                               [cdc_admin, mainAccountAddr, dhxAmount, "HX", "", 0.0001, 100000, True])



# accountBalances (assetSymbol => amount)
def get_account_balances(account_name,wallet_api):
    result = wallet_api.rpc_request('get_account_balances',
                                    [account_name])
    accountBalances = {}
    for i in range(0, len(result)):
        asset_id = result[i]['asset_id']
        accountBalances[assets[asset_id]] = int(result[i]['amount'])
    return accountBalances

def testover(usersNum,cdc_address, mainAccount,loopnum,filepath,account_name_prefix,closeAllCdcsAtEnd):
    createAccounts(account_name_prefix,usersNum)

    if(mainAccount not in accountNames.keys()):
        raise RuntimeError('error!!! mainAccount not in accountNames')
    mainAccountAddr = accountNames[mainAccount]
    cdcUsers = []

    cdcTrxsCount = 0
    liquidateCount = 0
    contract_info = json.loads(CDCOperation(mainAccount, cdc_address, wallet_api).get_contract_info())

    cdc_admin_addr = contract_info['admin']
    priceFeederAddr = contract_info['priceFeederAddr']
    stableTokenAddr = contract_info['stableTokenAddr']
    collateralAsset = contract_info['collateralAsset']
    liquidationRatio = float(contract_info['liquidationRatio'])

    cdc_admin = accounts[cdc_admin_addr]
    cdcAdmin = CDCOperation(cdc_admin, cdc_address, wallet_api)
    priceFeederUser = PriceFeeder(cdc_admin,priceFeederAddr,wallet_api)
    feeders = json.loads(priceFeederUser.get_feeders())
    price_feeder = accounts[feeders[0]]
    priceFeeder = PriceFeeder(price_feeder,priceFeederAddr,wallet_api)

    cdcAdmin.set_annual_stability_fee("15")
    time.sleep(5)

    pricestr = priceFeeder.get_price()
    price = float(pricestr)
    initprice = price
    hign_price = initprice*2
    low_price = initprice/2
    print("initprice:" + str(initprice))

    origAdminToken = token_balanceOf(stableTokenAddr,cdc_admin)
    if(origAdminToken < 10000):
        raise RuntimeError("orig admin stable token balance must >= 10000")
    ######### add users/admin hx , empty users/tempaccount BTC
    hxAmount = 10
    mainAccountBalances = get_account_balances(mainAccount, wallet_api) # mainAccount hx must >= 1000
    if("HX" not in mainAccountBalances.keys() or mainAccountBalances["HX"] < 1000*100000):
        raise RuntimeError("mainAccount has no hx balance or balance < 1000")
    hxbalance = mainAccountBalances["HX"]
    hxAmount = int(hxbalance / (usersNum + 2))
    dhxAmount = convertCoinWithPrecision(hxAmount,5)

    origStableTokenSupply = token_supply(stableTokenAddr,mainAccount)

    cdcAdminBalances = get_account_balances(cdc_admin, wallet_api)
    if (("HX" not in cdcAdminBalances.keys()) or cdcAdminBalances["HX"] < hxAmount):
        wallet_api.rpc_request('transfer_to_address',
                               [mainAccount, cdc_admin_addr, dhxAmount, "HX", "", 0.0001, 100000, True])
    if (collateralAsset in cdcAdminBalances.keys()):
        amount = cdcAdminBalances[collateralAsset]
        if (amount > 0 and cdc_admin!= mainAccount):
            wallet_api.rpc_request('transfer_to_address',
                                   [cdc_admin, mainAccountAddr, convertCoinWithPrecision(amount), collateralAsset, "",
                                    0.0001, 100000,True])

    for i in range(0, usersNum):
        user = account_name_prefix + str(i)
        cdcUsers.append(CDCOperation(user, cdc_address, wallet_api))
        userAddr = accountNames[user]
        userBalances = get_account_balances(user,wallet_api)
        if(("HX" not in userBalances.keys()) or userBalances["HX"] < hxAmount):
            wallet_api.rpc_request('transfer_to_address',
                                   [mainAccount, userAddr, dhxAmount, "HX", "", 0.0001, 100000, True])

        if(collateralAsset in userBalances.keys()):
            amount = userBalances[collateralAsset]
            if(amount > 0):
                wallet_api.rpc_request('transfer_to_address',
                                       [user, mainAccountAddr, convertCoinWithPrecision(amount), collateralAsset, "", 0.0001, 100000,
                                        True])

    time.sleep(6)

    ############### transfer users/admin btc   mainAccount btc must >= 1
    mainAccountBalances = get_account_balances(mainAccount, wallet_api)
    if (collateralAsset not in mainAccountBalances.keys() or mainAccountBalances[collateralAsset]<100000000):
        raise RuntimeError("mainAccount has no collateralAsset balance")
    balance = mainAccountBalances[collateralAsset]
    collateralAmount = int(balance/(usersNum+2))
    if(collateralAmount <= 0):
        raise RuntimeError("collateralAmount <=0 " )
    print("avg user collateralAmount is "+str(collateralAmount))

    dCollateralAmount = convertCoinWithPrecision(collateralAmount)
    for i in range(0, usersNum):
        user = account_name_prefix + str(i)
        userAddr = accountNames[user]
        wallet_api.rpc_request('transfer_to_address',
                               [mainAccount, userAddr, dCollateralAmount, collateralAsset, "", 0.0001, 100000, True])
    if(cdc_admin != mainAccount):
        wallet_api.rpc_request('transfer_to_address',
                           [mainAccount, cdc_admin_addr, dCollateralAmount, collateralAsset, "", 0.0001, 100000, True])
    time.sleep(5)

    cdcAdmin.set_annual_stability_fee("15")

    p = pathlib.Path(filepath)
    if(not p.is_file()):
        fd = open(filepath, mode="w", encoding="utf-8")
        fd.close()
    else:
        with open(filepath, 'r') as f:
            global cdcs
            try:
                cdcs = json.load(f)
            except BaseException as e:
                logging.error(str(e))


    openCdc(cdc_admin,cdcAdmin,collateralAsset,price,liquidationRatio,filepath,True)

    # loop
    for i in range(0,loopnum):
        pricestr = priceFeeder.get_price()
        price = float(pricestr)

        # rand
        randnum = random.randint(0, usersNum - 1)
        randUser = account_name_prefix + str(randnum)
        randCdcUser = cdcUsers[randnum]

        op = random.randint(0,5)
        if(len(cdcs) < (usersnum*2/3)):
            op = 0
        opRes = False
        if(op==0):
            opRes=openCdc(randUser, randCdcUser, collateralAsset, price, liquidationRatio, filepath)
        elif(op==1):
            opRes=addCollateral(randUser, randCdcUser, collateralAsset)
        elif (op == 2):
            opRes=widrawCollateral(randUser,randCdcUser,price,liquidationRatio)
        elif (op == 3):
            opRes=pay_back(randUser,randCdcUser,stableTokenAddr,cdc_admin)
        elif(op ==4):
            opRes=expandLoan(randUser,randCdcUser,price,liquidationRatio)
        elif(op >= 5):
            opRes=close_cdc(randUser,randCdcUser,stableTokenAddr,cdc_admin,filepath)


        ##########################
        # liquidate
        '''
        if(i%4 == 3):
            time.sleep(5)
            count = checkAndLiquidate(usersnum,account_name_prefix,stableTokenAddr,filepath,cdcUsers,cdc_admin)
            liquidateCount = liquidateCount + count
        '''

        # feed price #######################################################################
        if(opRes):
            cdcTrxsCount = cdcTrxsCount + 1
            newprice = price
            if (price > hign_price):
                newprice = price * 0.92
            elif (price < low_price):
                newprice = price * 1.09
            else:
                randf = random.uniform(-0.0999, 0.0999)  # 含首尾
                newprice = price + price * randf
            newpricestr = str(newprice)

            r = priceFeeder.feed_price(newpricestr)
            if (r is not None):
                print("feed new price:" + newpricestr)
            time.sleep(5)

    cdcAdmin.set_annual_stability_fee("0.15")

    currentStableTokenSupply = token_supply(stableTokenAddr,mainAccount)
    totalCdcStableTokenAmount = 0
    for user,cdc in cdcs.items():
        result = cdcAdmin.get_cdc(cdc['trxid'])
        if result is not None:
            cdcinfo = json.loads(result)
            stableTokenAmount = int(cdcinfo['stableTokenAmount'])
            totalCdcStableTokenAmount = totalCdcStableTokenAmount + stableTokenAmount
    print("all cdcs:")
    print(cdcs)
    print("origStableTokenSupply:" + str(origStableTokenSupply))
    print("totalCdcStableTokenAmount:" + str(totalCdcStableTokenAmount))
    print("currentStableTokenSupply:"+str(currentStableTokenSupply))

    print("liquidateCount:" + str(liquidateCount))
    print("cdcTrxsCount:" + str(cdcTrxsCount))
    if((totalCdcStableTokenAmount + origStableTokenSupply) != currentStableTokenSupply):
        raise RuntimeError("error !!!!! (totalCdcStableTokenAmount + origStableTokenSupply) != currentStableTokenSupply")

    if(closeAllCdcsAtEnd):
        print("try close all cdcs at end:")
        closeAllUsersCdcs(usersnum, account_name_prefix, filepath, mainAccount)



###前提 ： cdc admin已有一些稳定币做流通  ; mainAccount hx must >= 1000HX   mainAccount BTC must >= 1BTC
######################################################################################################
if __name__ == '__main__':
    time1 = datetime.datetime.now()
    print("start time: ", time1)

    usersnum = 20
    loopnum = 800
    filepath = "cdcs.json"
    account_name_prefix = "at"
    try:
        closeAllCdcsAtEnd = True
        testover(usersnum,cdc_address,mainAccount,loopnum,filepath,account_name_prefix,closeAllCdcsAtEnd)
        #closeAllUsersCdcs(usersnum,account_name_prefix,filepath,mainAccount)
        print("test over ok")
    except RuntimeError as e:
        closeAllUsersCdcs(usersnum, account_name_prefix, filepath, mainAccount)
        print(e)
    except BaseException as e:
        closeAllUsersCdcs(usersnum, account_name_prefix, filepath, mainAccount)
        print(e)
    finally:
        with open(filepath, 'w') as f:
            #print(cdcs)
            json.dump(cdcs, f)

        time2 = datetime.datetime.now()
        print("end time: ", time2)

        using_time = time2 - time1
        print("using_time:", using_time)

