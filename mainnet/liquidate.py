# -*- coding:utf-8 -*-
import json
import logging
import time
import threading
import traceback
from hdao.hx_wallet_api import HXWalletApi
from hdao.cdc_data_table_structure import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from hdao.hdao_cdc_op import CDCOperation
import  sys

class Cdc_Liquidate():
    def __init__(self,wallet_api,db_path,cdc_contract_address, account,stableTokenPrecision,collateralPrecision,session,symbol,logger):
        self.wallet_api = wallet_api
        self.symbol = symbol
        #Base = declarative_base()
        #Base.metadata.create_all(engine)
        self.is_running = False
        self.Session = session
        self.account = account
        self.cdc_contract_address = cdc_contract_address
        self.stableTokenPrecision = stableTokenPrecision
        self.collateralPrecision = collateralPrecision
        self.liquidator = CDCOperation(account, cdc_contract_address, self.wallet_api,self.symbol)
        self.logger = logger

        account_addr = self.wallet_api.rpc_request("get_account_addr",[account])
        if(account_addr is None):
            raise RuntimeError("address is None, account:"+str(account))
        self.account_addr = account_addr
        rstr = self.wallet_api.rpc_request('invoke_contract_offline',
                                           [self.account, self.cdc_contract_address, "getInfo", ""])
        cdc_contract_info = json.loads(rstr)
        self.stableTokenAddr = cdc_contract_info["stableTokenAddr"]
        self.priceFeederAddr = cdc_contract_info["priceFeederAddr"]

    def scan_liquidate(self, session):
        r = session.execute("select * from cdcs where state=1")
        cdcs = r.fetchall()
        count = len(cdcs)
        if (count <= 0):
            self.logger.info("no need to start.")
            return

        balance = int(self.wallet_api.rpc_request('invoke_contract_offline',
                                                  [self.account, self.stableTokenAddr, "balanceOf", self.account_addr]))
        if (balance <= 0):
            raise RuntimeError("balance <= 0")

        for cdc in cdcs:
            c = CdcTable()
            cdcId = cdc['cdcId']
            resultstr = self.liquidator.get_liquidable_info(cdcId)
            if (resultstr is None):
                continue
            info = json.loads(resultstr)
            if (info['isNeedLiquidation'] and (not info['isBadDebt'])):
                ##liquidate
                repayStableTokenAmount = int(info['repayStableTokenAmount'])
                auctionCollateralAmount = int(info['auctionCollateralAmount'])
                if (balance < repayStableTokenAmount):
                    self.logger.error("not enough balance ,balance:" + str(balance) + " need repayStableTokenAmount:" + str(
                        repayStableTokenAmount))
                else:
                    self.logger.info("need to liguidate the cdcid:"+cdcId)
                    liquidateResult = self.liquidator.liquidate(cdcId,
                                                                repayStableTokenAmount / self.stableTokenPrecision,
                                                                auctionCollateralAmount / self.collateralPrecision)
                    if (liquidateResult is None):
                        self.logger.error(
                            "liquidate fail ; cdcId" + cdcId + "liquidator:" + self.account + " need repayStableTokenAmount:" + str(
                                repayStableTokenAmount))
                    else:
                        balance = balance - repayStableTokenAmount

    def run(self):
        session = self.Session()
        try:
            self.is_running = True
            while self.is_running == True:
                self.scan_liquidate(session)
                time.sleep(5)
        except BaseException as e:
            logging.error(str(e))
            traceback.print_exc()
        finally:
            session.close()
    def stop(self):
        self.is_running = False

class HDaoLiquidateFactor(threading.Thread) :
    '''need to be changed to a '''
    def loadConfigFile(self):
        with open(self.config_path, 'r') as f:
            try:
                self.jsonconfigs = json.load(f)
            except BaseException as e:
                self.logger.error(e)
                sys.exit(1)
            finally:
                f.close()

    def __init__(self,robot_config_filepath,api,session):
        threading.Thread.__init__(self)
        self.session = session
        self.api = api
        self.robots = []
        self.config_path = robot_config_filepath
        self.jsonconfigs = {}
        self.logger = logging.getLogger("liquidator_factory.log")
        self.logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("liquidator_factory.log")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Start print log")
    def stop(self):
        if len(self.robots) <=0 :
            self.logger.info("there is no need to stop")

        for robot in self.robots :
            robot.stop()
    def run(self):
        if len(self.robots ) > 0 :
            self.logger.info("error, robots has been started")
        try:
            self.loadConfigFile()
            liquidate_info = self.jsonconfigs["cdc_contract_info"]
            global_info = self.jsonconfigs["global_info"]
            for k, v in liquidate_info.items():
                robot = Cdc_Liquidate(self.api,global_info["SQLDB"],v["CDC_CONTRACT_ID"],global_info["ACCOUNT"],
                                       global_info["STABLEPRECISION"],v["COLLECTEALPRECISION"],self.session,k,self.logger)
                self.robots.append(robot)
        except:
            sys.exit(1)

        try:
            for robot in self.robots :
                robot.run()
        except:
            pass


