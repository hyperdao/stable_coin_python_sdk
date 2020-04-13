from  mainnet.collect_event import *
from mainnet.config import *
from mainnet.feeder import *
from mainnet.liquidate import *
from hdao.hx_wallet_api import *
import threading


exitFlag = 0

class hdaoThread (threading.Thread):
    def __init__(self, name, func):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
    def run(self):
      func.run()

if __name__ == '__main__':
    '''need to launch all program 
    '''
    session = sessionmaker(engine)
    api = HXWalletApi(rpc_url=HX_TESTNET_RPC)
    collector = HdaoEventsCollector('da', CDC_CONTRACT_ID, api)
    feeder = PriceFeedingRobot("robot_config.json")
    liquidator = Cdc_Liquidate_Robot(api, SQLITE_CDS_DATA, CDC_CONTRACT_ID, PRICE_FEEDER["account"], STABLETOKENPRECISION,
                        COLLECTEALPRECISION,Session)


    t1 = hdaoThread("collector",collector)
    t2 = hdaoThread("feeder",feeder)
    t3 = hdaoThread("liquidator",liquidator)
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

