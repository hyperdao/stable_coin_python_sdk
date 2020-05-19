import json
import logging
import datetime
import time
import traceback
from sqlalchemy import func
from mainnet.config import *
import  threading
import  sys
#engine = create_engine('sqlite:///cdcs.db', echo=True, poolclass=SingletonThreadPool,
#                       connect_args={'check_same_thread': False})



####################################################################
class HdaoEventsCollector:

    def __init__(self, account, contract, wallet_api,session,batchGetNum=None):
        self.account = account
        self.contract = contract
        self.walletApi = wallet_api
        #self.session = Session()
        if(batchGetNum is not None):
            self.batchGetNum = batchGetNum
        else:
            self.batchGetNum = 2000
        r = self.walletApi.rpc_request("get_simple_contract_info", [self.contract])
        self.registered_block_num = r['registered_block']


    def query_last_stable_token_supply(self,session):
        block_number = session.query(func.max(StableTokenSupplyHistoryTable.block_number)).first()[0]
        if(block_number is None):
            return 0
        else:
            supply = session.query(StableTokenSupplyHistoryTable.supply).filter_by(block_number=block_number).first()[0]
            return supply


    def query_cdc_chain_by_id(self,chain_id,session):
        res = session.query(CdcChainTable).filter_by(chain_id=chain_id).all()
        if(res is None or len(res)==0):
            return None
        else:
            return res[0]


    ######################################################################################################################################

    #def query_cdc_op_by_id(self, cdcId):
    #    return session.query(CdcEventTable).filter_by(cdcId=cdcId).order_by(
    #       CdcEventTable.block_number.desc()).all()

    def batch_add_events(self,session,chain_id,start_block,range,head_block_num,start_event_id):
        events = self.walletApi.rpc_request("get_contract_events_in_range",
                                       [self.contract, start_block, range])
        event_count = 0
        end_block_num = start_block+range
        if(head_block_num < end_block_num):
            end_block_num = head_block_num
        if(start_block > head_block_num ):
            logging.info("wrong start_block > head_block_num , batch_add_events start_block:"+str(start_block)+" range:"+str(range)+" head_block_num:" +str(head_block_num))
            return
        r = self.walletApi.rpc_request("get_block",[end_block_num])
        end_block_id = r['block_id']
        event_id = start_event_id
        nowSupply = self.query_last_stable_token_supply(session)

        for event in events:
            cdcInfo = json.loads(event['event_arg'])
            txid = event['trx_id']
            if event['event_name'] in (
                    'OpenCdc', 'TransferCdc', 'Liquidate', 'CloseCdc', 'AddCollateral', 'ExpandLoan',
                    'WidrawCollateral',
                    'PayBack'):
                if(session.query(CdcEventTable).filter_by(tx_id=txid).count()>0):
                    continue
                #session.query(CdcEventTable).filter_by(tx_id=txid).delete()

                session.add(CdcEventTable(
                    event_id = event_id,
                    tx_id=txid,
                    op=event['event_name']
                ))
                if event['event_name'] == 'OpenCdc':
                    session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).delete()
                    session.add(CdcTable(
                        cdcId=cdcInfo['cdcId'],
                        owner=cdcInfo['owner'],
                        collateralAmount=cdcInfo['collateralAmount'],
                        stableTokenAmount=cdcInfo['stableTokenAmount'],
                        state=1, block_number=event['block_num'],
                        last_event_id = event_id))
                    e = EventOpenCdcTable(event_id=event_id,
                                          cdcId=cdcInfo['cdcId'],
                                          owner=cdcInfo['owner'],
                                          collateralAmount=cdcInfo['collateralAmount'],
                                          stableTokenAmount=cdcInfo['stableTokenAmount'],
                                          secSinceEpoch = cdcInfo['secSinceEpoch'],
                                          block_number=event['block_num'])
                    session.add(e)
                    if(cdcInfo['stableTokenAmount'] > 0):
                        nowSupply = nowSupply + cdcInfo['stableTokenAmount']
                        session.query(StableTokenSupplyHistoryTable).filter_by(block_number=event['block_num']).delete()
                        e = StableTokenSupplyHistoryTable(
                                              supply=nowSupply,
                                              block_number=event['block_num'])
                        session.add(e)

                elif event['event_name'] == 'AddCollateral':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.collateralAmount = str(int(cdc.collateralAmount) + int(cdcInfo['addAmount']))
                        session.add(cdc)
                        e = EventAddCollateralTable(event_id=event_id,
                                              cdcId=cdcInfo['cdcId'],
                                            addAmount=cdcInfo['addAmount'],
                                            block_number=event['block_num'])
                        session.add(e)
                elif event['event_name'] == 'WidrawCollateral':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.collateralAmount = str(int(cdc.collateralAmount) - int(cdcInfo['widrawCollateralAmount']))
                        session.add(cdc)
                        e = EventWidrawCollateralTable(event_id=event_id,
                                                cdcId=cdcInfo['cdcId'],
                                                from_address=cdcInfo['from_address'],
                                                widrawCollateralAmount=cdcInfo['widrawCollateralAmount'],
                                                block_number=event['block_num'])
                        session.add(e)
                elif event['event_name'] == 'ExpandLoan':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.stableTokenAmount = str(int(cdc.stableTokenAmount) + int(cdcInfo['realGotAmount']))
                        session.add(cdc)
                        e = EventExpandLoanTable(event_id=event_id,
                                                cdcId=cdcInfo['cdcId'],
                                                 from_address=cdcInfo['from_address'],
                                                 realGotAmount=cdcInfo['realGotAmount'],
                                                 expandLoanAmount=cdcInfo['expandLoanAmount'],
                                                 repayFee=cdcInfo['repayFee'],
                                                 block_number=event['block_num'])
                        session.add(e)

                        nowSupply = nowSupply + cdcInfo['expandLoanAmount']
                        session.query(StableTokenSupplyHistoryTable).filter_by(
                            block_number=event['block_num']).delete()
                        e = StableTokenSupplyHistoryTable(
                                                          supply=nowSupply,
                                                          block_number=event['block_num'])
                        session.add(e)
                elif event['event_name'] == 'PayBack':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.stableTokenAmount = str(int(cdc.stableTokenAmount) - int(cdcInfo['repayPrincipal']))
                        session.add(cdc)
                        e = EventPayBackTable(event_id=event_id,
                                                 cdcId=cdcInfo['cdcId'],
                                                 from_address=cdcInfo['from_address'],
                                                 payBackAmount=cdcInfo['payBackAmount'],
                                                 realPayBackAmount=cdcInfo['realPayBackAmount'],
                                                 repayPrincipal=cdcInfo['repayPrincipal'],
                                                 fee=cdcInfo['fee'],
                                                block_number=event['block_num'])
                        session.add(e)

                        nowSupply = nowSupply - cdcInfo['repayPrincipal']
                        session.query(StableTokenSupplyHistoryTable).filter_by(
                            block_number=event['block_num']).delete()
                        e = StableTokenSupplyHistoryTable(
                                                          supply=nowSupply,
                                                          block_number=event['block_num'])
                        session.add(e)
                elif event['event_name'] == 'TransferCdc':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        if cdc.owner != cdcInfo['from_address']:
                            logging.error("Not match owner error: %s(%s => %s)" % (
                                cdcInfo['cdcId'], cdc.owner, cdcInfo['from_address']))
                        cdc.owner = cdcInfo['to_address']
                        session.add(cdc)
                        e = EventTransferCdcTable(event_id=event_id,
                                                 cdcId=cdcInfo['cdcId'],
                                                 from_address=cdcInfo['from_address'],
                                                  to_address=cdcInfo['to_address'],
                                                  block_number=event['block_num'])
                        session.add(e)
                elif event['event_name'] == 'Liquidate':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.liquidator = cdcInfo['liquidator']
                        cdc.state = 2
                        session.add(cdc)
                        e = EventLiquidateTable(event_id=event_id,
                                                cdcId=cdcInfo['cdcId'],
                                                owner=cdcInfo['owner'],
                                                collateralAmount=cdcInfo['collateralAmount'],
                                                stableTokenAmount=cdcInfo['stableTokenAmount'],
                                                secSinceEpoch=cdcInfo['secSinceEpoch'],
                                                curPrice=cdcInfo['secSinceEpoch'],
                                                isBadDebt=cdcInfo['isBadDebt'],
                                                liquidator=cdcInfo['liquidator'],
                                                auctionPrice=cdcInfo['auctionPrice'],
                                                returnAmount=cdcInfo['returnAmount'],
                                                stabilityFee=cdcInfo['stabilityFee'],
                                                penaltyAmount=cdcInfo['penaltyAmount'],
                                                isNeedLiquidation=cdcInfo['isNeedLiquidation'],
                                                repayStableTokenAmount=cdcInfo['repayStableTokenAmount'],
                                                auctionCollateralAmount=cdcInfo['auctionCollateralAmount'],
                                                block_number=event['block_num'])
                        session.add(e)

                        nowSupply = nowSupply - cdcInfo['stableTokenAmount']
                        session.query(StableTokenSupplyHistoryTable).filter_by(
                            block_number=event['block_num']).delete()
                        e = StableTokenSupplyHistoryTable(
                                                          supply=nowSupply,
                                                          block_number=event['block_num'])
                        session.add(e)
                elif event['event_name'] == 'CloseCdc':
                    cdc = session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.state = 3
                        session.add(cdc)
                        e = EventCloseCdcTable(event_id=event_id,
                                              cdcId=cdcInfo['cdcId'],
                                              owner=cdcInfo['owner'],
                                               stabilityFee=cdcInfo['stabilityFee'],
                                               secSinceEpoch=cdcInfo['secSinceEpoch'],
                                               collateralAmount=cdcInfo['collateralAmount'],
                                               stableTokenAmount=cdcInfo['stableTokenAmount'],
                                               block_number=event['block_num'])
                        session.add(e)

                        nowSupply = nowSupply - cdcInfo['stableTokenAmount']
                        session.query(StableTokenSupplyHistoryTable).filter_by(
                            block_number=event['block_num']).delete()
                        e = StableTokenSupplyHistoryTable(
                                                          supply=nowSupply,
                                                          block_number=event['block_num'])
                        session.add(e)
                event_count = event_count + 1
                event_id = event_id + 1

        session.query(CdcChainTable).filter_by(chain_id=chain_id).delete()
        session.add(CdcChainTable(
            chain_id=chain_id,
            cdc_contract_address=self.contract,
            contract_register_block_num=self.registered_block_num,
            end_block_num=end_block_num,
            end_block_id = end_block_id
        ))
        session.commit()
        logging.info("batch add events_count: " +str(event_count) + " start_block:"+str(start_block) + " end_block_num:"+str(start_block+range) +" end_block_id:"+str(end_block_num))
        return event_count

    #end_block 含   [start_block_num, end_block_num]
    def collect_event(self,end_block=0):
        try:
            session = Session()
            start_block = 0
            info = self.walletApi.rpc_request("info", [])
            head_block_num = info['head_block_num']
            if(end_block == 0 or end_block<head_block_num):
                end_block = head_block_num
            chain_id = info['chain_id']
            if(chain_id is None or len(chain_id)<1):
                logging.error("chain_id is empty" )
                return

            cdc_chain = self.query_cdc_chain_by_id(chain_id,session)
            if(cdc_chain is None):
                logging.info("try collect from first")

                start_block = self.registered_block_num
                session.add(CdcChainTable(
                    chain_id=chain_id,
                    cdc_contract_address=self.contract,
                    contract_register_block_num=self.registered_block_num,
                    end_block_num=0,
                    end_block_id=" "
                ))

                session.query(StableTokenSupplyHistoryTable).delete()
                e = StableTokenSupplyHistoryTable(
                    supply=0,
                    block_number=self.registered_block_num)
                session.add(e)

            else:
                start_block = cdc_chain.end_block_num + 1
                if(start_block > head_block_num):
                    logging.info("already colleted to head blocknum:"+str(cdc_chain.end_block_num))
                    return
                block = self.walletApi.rpc_request("get_block", [start_block])
                if(block['previous'] != cdc_chain.end_block_id):
                    logging.warning("chain forked , try delete all data and re collect !!!!" )
                    self.delete_all(session)

                    logging.info("try collect from first")
                    start_block = self.registered_block_num
                    session.add(CdcChainTable(
                        chain_id=chain_id,
                        cdc_contract_address=self.contract,
                        contract_register_block_num=self.registered_block_num,
                        end_block_num=0,
                        end_block_id=" "
                    ))
                    session.query(StableTokenSupplyHistoryTable).delete()
                    e = StableTokenSupplyHistoryTable(
                        supply=0,
                        block_number=self.registered_block_num)
                    session.add(e)

            logging.info("start collect from blocknum:" + str(start_block)+" to blocknum:"+str(end_block))

            batchGetNum = self.batchGetNum
            temp_start_block_num = start_block
            temp_end_block_num = end_block
            start_event_id = session.query(CdcEventTable).count()
            if(start_event_id is None or start_event_id<0):
                logging.error("session.query(CdcEventTable).count() wrong")
                return
            total_events__count = 0
            while(temp_start_block_num <= end_block):
                if((end_block - temp_start_block_num + 1 ) > batchGetNum):
                    temp_end_block_num = temp_start_block_num + batchGetNum
                else:
                    temp_end_block_num = end_block

                range = temp_end_block_num-temp_start_block_num
                event_count  = 0
                if(range==0):
                    event_count = self.batch_add_events(session,chain_id, temp_start_block_num,1,head_block_num,start_event_id)
                    total_events__count = total_events__count + event_count
                    break
                else:
                    event_count = self.batch_add_events(session,chain_id, temp_start_block_num, range, head_block_num, start_event_id)
                    total_events__count = total_events__count + event_count
                temp_start_block_num = temp_end_block_num
                start_event_id = start_event_id + event_count
                print("--------total_events__count:" + str(total_events__count))
        except BaseException as e:
            print(e)
            traceback.print_exc()
        finally:
            session.close()


    def delete_all(self,session=None):
        need_close_session = False
        if(session is None):
            need_close_session = True
            session = Session()

        session.execute('delete from StableTokenSupplyHistory')
        session.execute('delete from WidrawCollateral')
        session.execute('delete from CloseCdc')
        session.execute('delete from AddCollateral')
        session.execute('delete from OpenCdc')
        session.execute('delete from Liquidate')
        session.execute('delete from ExpandLoan')
        session.execute('delete from TakeBackCollateralByCdc')
        session.execute('delete from TakeBackCollateralByToken')
        session.execute('delete from TransferCdc')
        session.execute('delete from PayBack')
        session.execute('delete from cdcs')
        session.execute('delete from CdcEvent')
        session.execute('delete from cdc_chain')

        '''
        session.query(StableTokenSupplyHistoryTable).delete()
        session.query(EventWidrawCollateralTable).delete()
        session.query(EventCloseCdcTable).delete()
        session.query(EventAddCollateralTable).delete()
        session.query(EventOpenCdcTable).delete()
        session.query(EventLiquidateTable).delete()
        session.query(EventExpandLoanTable).delete()
        session.query(EventTakeBackCollateralByCdcTable).delete()
        session.query(EventTakeBackCollateralByTokenTable).delete()
        session.query(EventTransferCdcTable).delete()
        session.query(EventPayBackTable).delete()
        session.query(CdcTable).delete()
        session.query(CdcEventTable).delete()
        session.query(CdcChainTable).delete()
        '''
        session.commit()

        r = session.query(CdcTable).all()
        if(need_close_session):
            session.close()
        logging.info("delete_all cdc data down!!!")
    def run(self):
        while True:
            self.collect_event()
            time.sleep(1)

'''
if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    from hdao.hx_wallet_api import HXWalletApi

    api = HXWalletApi(name='events', rpc_url='http://192.168.1.121:30088/')
    collector = HdaoEventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    time1 = datetime.datetime.now()
    collector.collect_event()
    time2 = datetime.datetime.now()
    r = time2 - time1
    print(r)
    
    while(True):
        collector.collect_event()
        time.sleep(5)
'''

class HDaoEventCollectorFactory(threading.Thread) :
    '''need to be changed to a '''
    def loadConfigFile(self):
        with open(self.config_path, 'r') as f:
            try:
                self.jsonconfigs = json.load(f)
            except BaseException as e:
                #self.logger.error(e)
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
    def stop(self):
        if len(self.robots) <=0 :
            print("there is no need to stop")

        for robot in self.robots :
            robot.stop()
    def run(self):
        if len(self.robots ) > 0 :
            print("error, robots has been started")
        try:
            self.loadConfigFile()
            cdc_event_info = self.jsonconfigs["cdc_contract_info"]
            global_info = self.jsonconfigs["global_info"]
            for k,v in  cdc_event_info.items():
                robot = HdaoEventsCollector(global_info["ACCOUNT"],v["CDC_CONTRACT_ID"],self.api,self.session)
                self.robots.append(robot)
        except:
            print("xxxx")
            sys.exit(1)

        try:
            for robot in self.robots :
                robot.run()
        except:
            pass

