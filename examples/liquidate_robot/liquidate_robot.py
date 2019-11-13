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

class Cdc_Liquidate_Robot(threading.Thread):
    def __init__(self,wallet_rpc_url,db_path,cdc_contract_address, account,stableTokenPrecision,collateralPrecision):
        threading.Thread.__init__(self)
        self.wallet_api = HXWalletApi(name='events', rpc_url=wallet_rpc_url)
        #Base = declarative_base()
        engine = create_engine(db_path, echo=True, poolclass=SingletonThreadPool,
                               connect_args={'check_same_thread': False})
        #Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)
        self.account = account
        self.cdc_contract_address = cdc_contract_address
        self.stableTokenPrecision = stableTokenPrecision
        self.collateralPrecision = collateralPrecision
        self.liquidator = CDCOperation(account, cdc_contract_address, self.wallet_api)
        account_addr = self.wallet_api.rpc_request("get_account_addr",[account])
        if(account_addr is None):
            raise RuntimeError("address is None, account:"+str(account))
        self.account_addr = account_addr
        rstr = self.wallet_api.rpc_request('invoke_contract_offline',
                                           [self.account, self.cdc_contract_address, "getInfo", ""])
        cdc_contract_info = json.loads(rstr)
        self.stableTokenAddr = cdc_contract_info["stableTokenAddr"]
        self.priceFeederAddr = cdc_contract_info["priceFeederAddr"]



    def scan_liquidate(self,session):
        r = session.execute('select * from cdcs where state=1')
        cdcs = r.fetchall()
        count = len(cdcs)
        if(count <=0):
            return

        balance = int(self.wallet_api.rpc_request('invoke_contract_offline',
                                                  [self.account, self.stableTokenAddr, "balanceOf", self.account_addr]))
        if(balance <= 0):
            raise RuntimeError("balance <= 0")
            return

        for cdc in cdcs:
            c = CdcTable()
            cdcId = cdc['cdcId']
            resultstr = self.liquidator.get_liquidable_info(cdcId)
            if(resultstr is None):
                continue
            info = json.loads(resultstr)
            if(info['isNeedLiquidation'] and (not info['isBadDebt'])):
                ##liquidate
                repayStableTokenAmount = int(info['repayStableTokenAmount'])
                auctionCollateralAmount = int(info['auctionCollateralAmount'])
                if(balance < repayStableTokenAmount):
                    logging.error("not enough balance ,balance:"+str(balance)+" need repayStableTokenAmount:"+str(repayStableTokenAmount))
                else:
                    liquidateResult = self.liquidator.liquidate(cdcId,repayStableTokenAmount/self.stableTokenPrecision, auctionCollateralAmount/self.collateralPrecision)
                    if(liquidateResult is None):
                        logging.error(
                            "liquidate fail ; cdcId" + cdcId + "liquidator:"+ self.account+ " need repayStableTokenAmount:" + str(
                                repayStableTokenAmount))
                    else:
                        balance = balance - repayStableTokenAmount


    def run(self):
        try:
            session = self.Session()
            while (True):
                self.scan_liquidate(session)
                time.sleep(5)
        except BaseException as e:
            logging.error(str(e))
            traceback.print_exc()
        finally:
            session.close()


if __name__ == "__main__":
    wallet_rpc_url = 'http://192.168.1.121:30088/'
    sqlite_db_path = 'sqlite:///../cdcs_data/cdcs.db'
    account = 'senator0'
    cdc_contract_address = "HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks"
    stableTokenPrecision = 100000000
    collateralPrecision = 100000000

    robot = Cdc_Liquidate_Robot(wallet_rpc_url,sqlite_db_path,cdc_contract_address,account,stableTokenPrecision,collateralPrecision)
    robot.start()



