import requests
import datetime
import time
import sys
import threading
import decimal
from hdao.hdao_price_feeder import PriceFeeder
from hdao.hx_wallet_api import *

import logging

# ok   https://www.okex.com/api/spot/v3/instruments/BTC-USDT/ticker
# {"best_ask":"9545.2","best_bid":"9545.1","instrument_id":"BTC-USDT","product_id":"BTC-USDT","last":"9545","ask":"9545.2","bid":"9545.1","open_24h":"9148.5","high_24h":"9906.4","low_24h":"9130.3","base_volume_24h":"47433.4","timestamp":"2019-10-28T06:17:18.417Z","quote_volume_24h":"452603436.8"}

# zb   http://api.zb.plus/data/v1/ticker?market=btc_usdt
# {"date":"1572243631111","ticker":{"high":"9885.5","vol":"24604.4496","last":"9558.91","low":"9130.24","buy":"9559.47","sell":"9559.9"}}

#wallet_api_url = 'http://192.168.1.121:30088/'
#account_name = 'senator0'
#priceFeeder_contract_address2 =  'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1'
#priceFeeder_contract_address = "HXCTkW3MD8te4uoyndoRvtds7HoFvhhH2EWr"
#symbolPair = 'btcusdt'

#https://fxhapi.feixiaohao.com/public/v1/ticker?start=0&limit=1
#[{"id":"bitcoin","name":"Bitcoin","symbol":"BTC","rank":1,"logo":"https://s1.bqiapp.com/coin/20181030_72_webp/bitcoin_200_200.webp?v=1566978037","logo_png":"https://s1.bqiapp.com/coin/20181030_72_png/bitcoin_200_200.png?v=1566978037","price_usd":9413.0,"price_btc":1.00,"volume_24h_usd":10225294245.0,"market_cap_usd":168502467433.0,"available_supply":17901187.0,"total_supply":17901187.0,"max_supply":21000000.0,"percent_change_1h":-0.01,"percent_change_24h":0.24,"percent_change_7d":14.05,"last_updated":1572340444}]
#https://fxhapi.feixiaohao.com/public/v1/ticker?start=1&limit=1
#[{"id":"ethereum","name":"Ethereum","symbol":"ETH","rank":2,"logo":"https://s1.bqiapp.com/coin/20181030_72_webp/ethereum_200_200.webp?v=1561100400","logo_png":"https://s1.bqiapp.com/coin/20181030_72_png/ethereum_200_200.png?v=1561100400","price_usd":185.48,"price_btc":0.0197,"volume_24h_usd":3115208107.0,"market_cap_usd":19864874826.0,"available_supply":107100935.0,"total_supply":107100935.0,"max_supply":107100935.0,"percent_change_1h":-0.22,"percent_change_24h":1.74,"percent_change_7d":6.55,"last_updated":1572340097}]

class FeederInfo:
    def __init__(self):
        self.account = ""
        self.websites = []

class ContractFeedingInfo:
    def __init__(self):
        self.symbolPair = ""
        self.wallet_api_url = ""
        self.priceFeeder_contract_address = ""
        self.feeders = [FeederInfo()]
        self.feeder_names = ["1","2"]
        self.interval = 1

class PriceGrab:
    def __init__(self,symbolPair,websiteInfo):
        self.logger = logging.getLogger("priceFeedingRobot")
        self.symbolPair = symbolPair
        self.exchangeWebSiteName = websiteInfo['name']
        self.url= websiteInfo['url']
        self.accessPriceKeys = websiteInfo['accessPriceKeys']
        self.muti_factor = websiteInfo['muti_factor']


    def grab_price(self):
        try:
            response = requests.get(self.url)
            result = response.text
            if(result is None or len(result)==0):
                self.logger.info(response)
                self.logger.error("error when grab_price get url:"+self.url)
                return None
            jsonresult = json.loads(result)
            for i in range(0,len(self.accessPriceKeys)):
                if(i==0):
                    price = jsonresult[self.accessPriceKeys[i]]
                else:
                    price = price[self.accessPriceKeys[i]]

            if(price is None):
                return None
            if(self.muti_factor!=1):
                price = (decimal.Decimal(str(price))*self.muti_factor).quantize(decimal.Decimal('0.00000001'))
            return str(price)
        except BaseException as e:
            self.logger.error(e)
            return None


class APriceFeeder:
    def __init__(self,symbolPair,priceFeeder_contract_address,accountName,wallet_api_url,exchangeWebSites):
        self.logger = logging.getLogger("priceFeedingRobot")
        self.priceGrabs = []
        for websiteInfo in exchangeWebSites:
            self.priceGrabs.append(PriceGrab(symbolPair,websiteInfo))
        wallet_api = HXWalletApi(name = 'priceFeeder_service', rpc_url = wallet_api_url)
        self.walletPriceFeederApi = PriceFeeder(accountName, priceFeeder_contract_address, wallet_api)
        account_addr = wallet_api.rpc_request("get_account_addr", [accountName])
        if(account_addr is None):
            raise RuntimeError("no account:"+accountName)
        self.account_addr = account_addr
        self.account = accountName



    def setPriceGrab(self,exchangeWebSiteName,symbolPair):
        self.priceGrab = PriceGrab(exchangeWebSiteName, symbolPair)

    def setWalletPriceFeederApi(self,accountName,wallet_api_url,priceFeeder_contract_address):
        wallet_api = HXWalletApi(name = 'priceFeeder_service', rpc_url = wallet_api_url)
        self.walletPriceFeederApi = PriceFeeder(accountName, priceFeeder_contract_address, wallet_api)

    def feedPrice(self):
        maxChangeRatio = 0.099999

        pricestr = None
        for priceGrab in self.priceGrabs:
            pricestr = priceGrab.grab_price()
            if(pricestr is not None):
                break
            else:
                self.logger.error("grab price fail ! from exchangeUrl:"+priceGrab.url)
        if(pricestr is None ):
            self.logger.error("grab price from all setted exchanges fail !!! please check network !!!" )
            return False

        r = self.walletPriceFeederApi.get_feedPrices()
        feedPrices = json.loads(r)
        origPriceStr = feedPrices[self.account_addr]
        price = float(pricestr)
        origPrice = float(origPriceStr)
        if(price> origPrice):
            while(price > origPrice*(1+maxChangeRatio)):
                newPrice = origPrice*(1+maxChangeRatio)
                r = self.walletPriceFeederApi.feed_price(str(newPrice))
                if (r is None):
                    return False
                self.logger.info(" feeder:"+self.account+"feed price exceed max change ratio 0.1  feed new price:"+str(newPrice)  + "orig price:"+str(origPrice)+"\tcontract:" + self.walletPriceFeederApi.contract )
                origPrice = newPrice
            r = self.walletPriceFeederApi.feed_price(pricestr)
            if (r is None):
                return False
            self.logger.info(" feeder:"+self.account +"\tfeed price:" + pricestr +"\tcontract:" + self.walletPriceFeederApi.contract)

        else:
            while (price < origPrice * (1 - maxChangeRatio)):
                newPrice = origPrice * (1 - maxChangeRatio)
                r = self.walletPriceFeederApi.feed_price(str(newPrice))
                if (r is None):
                    return False
                self.logger.info(" feeder:"+self.account+"feed price exceed max change ratio 0.1  feed new price:" + str(newPrice) + "orig price:"+str(origPrice)+"\tcontract:" + self.walletPriceFeederApi.contract )
                origPrice = newPrice
            r = self.walletPriceFeederApi.feed_price(pricestr)
            if (r is None):
                return False
            self.logger.info(
                " feeder:" + self.account + "\tfeed price:" + pricestr + "\tcontract:" + self.walletPriceFeederApi.contract)
        return True



class ContractPriceFeedingRobot(threading.Thread):
    def __init__(self,contractFeedingInfo,exchangeWebSitesInfo):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("priceFeedingRobot")
        self.contractAddr = contractFeedingInfo.priceFeeder_contract_address
        self.contractFeedingInfo = contractFeedingInfo
        self.aPriceFeeders = []
        self.running = False
        self.startTime = None
        self.stopTime = None
        self.successFeedCount = 0
        self.failFeedCount = 0
        symbolPair = contractFeedingInfo.symbolPair
        symbolPairExchangeWebSitesInfo = exchangeWebSitesInfo[symbolPair]
        webnames = symbolPairExchangeWebSitesInfo.keys()
        priceFeeder_contract_address = contractFeedingInfo.priceFeeder_contract_address

        wallet_api_url = contractFeedingInfo.wallet_api_url
        for feeder in self.contractFeedingInfo.feeders:
            account = feeder["account"]
            websites = feeder["websites"]
            websitesInfos = []
            for webname in websites:
                if(webname in webnames):
                    websitesInfos.append(symbolPairExchangeWebSitesInfo[webname])
            if(len(websitesInfos)==0):
                raise RuntimeError("no exchange web sites contract:"+priceFeeder_contract_address + " account:"+account)
            aPriceFeeder = APriceFeeder(symbolPair, priceFeeder_contract_address, account, wallet_api_url, websitesInfos)
            self.aPriceFeeders.append(aPriceFeeder)


    def run(self):  # 把要执行的代码写到run函数里面
        self.running = True
        interval = self.contractFeedingInfo.interval
        self.logger.info("Starting feeding price to contract:" + self.contractFeedingInfo.priceFeeder_contract_address + " interval:"+str(interval) + " start time:"+str(datetime.datetime.now()))

        isContinue = True
        self.startTime = datetime.datetime.now()
        feedersCount = len(self.aPriceFeeders)
        rounds = 0
        while(isContinue and self.running):
            for aPriceFeeder in self.aPriceFeeders:
                r = aPriceFeeder.feedPrice()
                if(r==False):
                    self.logger.error("feed price fail! contract:"+ self.contractFeedingInfo.priceFeeder_contract_address + " account:"+aPriceFeeder.account)
                    self.failFeedCount = self.failFeedCount + 1
                else:
                    self.successFeedCount = self.successFeedCount + 1

            rounds = rounds + 1
            time.sleep(interval)
            if ((self.failFeedCount > 5) and  self.failFeedCount/(self.failFeedCount+self.successFeedCount) >= 1/feedersCount):
                self.logger.error("run wrong !!! failFeedCount/(failFeedCount+successFeedCount) >= 1/feedersCount")
                self.logger.error("please check ! end feeding price to contract:" + self.contractFeedingInfo.priceFeeder_contract_address + " interval:" + str(
                    interval) + " start time:" + str(datetime.datetime.now()))
                isContinue = False

        self.logger.info("end feeding price to contract:" + self.contractFeedingInfo.priceFeeder_contract_address + " interval:" + str(
                interval) + " end time:" + str(datetime.datetime.now()))
        if(self.running):
            self.running = False
        self.stopTime = datetime.datetime.now()
        self.logger.info("total time:"+str(self.stopTime-self.startTime) + " failFeedCount:" + str(self.failFeedCount) + " successFeedCount:" + str(self.successFeedCount)+ " feedersCount:"+str(feedersCount) + " roundsCount:"+str(rounds))

    def stop(self):
        self.running = False
        self.stopTime = datetime.datetime.now()


#######################################################################################################
class PriceFeedingRobot:
    def loadConfigFile(self):
        with open(self.robot_config_filepath, 'r') as f:
            try:
                self.jsonconfigs = json.load(f)
            except BaseException as e:
                self.logger.error(e)
                sys.exit(1)
            finally:
                f.close()

    def __init__(self,robot_config_filepath):
        self.logger = logging.getLogger("priceFeedingRobot")
        self.robots = []
        self.jsonconfigs = {}
        self.robot_config_filepath = robot_config_filepath

        self.logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("priceFeedingRobot_log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Start print log")



    def stop(self):
        if (len(self.robots) > 0):
            for robot in self.robots:
                robot.stop()
                self.logger.info("stop price feeding of contract:" + robot.contractAddr)
            self.robots.clear()

    def start(self):
        if(len(self.robots)>0):
            self.logger.warning("already started now, can't start again")
            return
        try:
            self.loadConfigFile()
            feedingContractsInfo = self.jsonconfigs["feedingContractsInfo"]
            exchangeWebSitesInfo = self.jsonconfigs["exchangeWebSitesInfo"]
            for i in range(0, len(feedingContractsInfo)):
                contractFeedingInfo = ContractFeedingInfo()
                contractFeedingInfo.__dict__ = feedingContractsInfo[i]
                robot = ContractPriceFeedingRobot(contractFeedingInfo, exchangeWebSitesInfo)
                #robot.setDaemon(True)
                self.robots.append(robot)
                # robot.join()
        except BaseException as e:
            self.logger.error(e)
            sys.exit(1)

        try:
            for robot in self.robots:
                robot.start()
        except BaseException as e:
            self.logger.error(e)
            sys.exit(1)

    def restart(self):
        self.logger.info("restart robots")
        self.stop()
        self.start()

    def is_Unnormal(self):
        for robot in self.robots:
            if(not robot.is_alive()):
                self.logger.error("error!!!! thread exit unnormal feeding contract:"+robot.contractAddr)
                return True
        return False


#########################################################
if __name__ == '__main__':
    filepath = "robot_config.json"
    r = PriceFeedingRobot(filepath)
    r.start()


    while(True):
        time.sleep(3)
        if(r.is_Unnormal()):
            r.restart()

    '''
    isExit = False
    while(not isExit):
        val = input("input commond:")
        if(val == "stop"):
            r.stop()
        elif(val == "start"):
            r.start()
        elif (val == "restart"):
            r.restart()
        elif (val == "exit"):
            isExit = True
        else:
            self.logger.info("input command: [stop,start,restart,exit]")
    '''



