import json
import logging
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean,ForeignKey
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy import and_
#from sqlalchemy.orm import *

Base = declarative_base()

class CdcChainTable(Base):
    __tablename__ = 'cdc_chain'
    chain_id = Column(String(128), primary_key=True, nullable=False)
    end_block_num = Column(Integer, nullable=False)
    end_block_id = Column(String(128), nullable=False)

class CdcTable(Base):
    __tablename__ = 'cdcs'
    cdcId = Column(String(128), primary_key=True, nullable=False)
    state = Column(Integer, nullable=False)
    stabilityFee = Column(String(128), default="")
    collateralAmount = Column(String(128), nullable=False)
    stableTokenAmount = Column(String(128), nullable=False)
    owner = Column(String(128), nullable=False)
    liquidator = Column(String(128), default="")
    block_number = Column(Integer, nullable=False)
    #last_event_id = relationship('CdcEventTable', backref='cdc_op_history', uselist=False)
    last_event_id = Column(Integer, ForeignKey("CdcEvent.event_id"))

    def __repr__(self):
        return "<Cdc(cdcId='%s', collateralAmount='%s', stableTokenAmount='%s')>" % (
            self.cdcId, self.collateralAmount, self.stableTokenAmount)


class CdcEventTable(Base):
    __tablename__ = 'CdcEvent'
    event_id = Column(Integer, primary_key=True, nullable=False)
    tx_id = Column(String(128), primary_key=True, nullable=False)
    op = Column(String(16), nullable=False)
    block_number = Column(Integer, nullable=False)

    def __repr__(self):
        return "<CdcEvent(cdcId='%s', op='%s', block_number='%d')>" % (
            self.cdcId, self.op, self.block_number)

class EventOpenCdcTable(Base):
    __tablename__ = 'OpenCdc'
    event_id = Column(Integer, ForeignKey("CdcEvent.event_id"),primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64), nullable=False)
    secSinceEpoch = Column(Integer, nullable=False)
    collateralAmount = Column(Integer, nullable=False)
    stableTokenAmount = Column(Integer, nullable=False)


class EventLiquidateTable(Base):
    __tablename__ = 'Liquidate'
    event_id = Column(Integer, ForeignKey("CdcEvent.event_id"),primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64), nullable=False)
    secSinceEpoch = Column(Integer, nullable=False)
    collateralAmount = Column(Integer, nullable=False)
    stableTokenAmount = Column(Integer, nullable=False)
    curPrice = Column(String(64), nullable=False)
    isBadDebt = Column(Boolean, nullable=False)
    liquidator = Column(String(64), nullable=False)
    auctionPrice = Column(String(64), nullable=False)
    returnAmount = Column(Integer, nullable=False)
    penaltyAmount = Column(Integer, nullable=False)
    isNeedLiquidation = Column(Boolean, nullable=False)
    stabilityFee = Column(Integer, nullable=False)
    repayStableTokenAmount = Column(Integer, nullable=False)
    auctionCollateralAmount = Column(Integer, nullable=False)

class EventAddCollateralTable(Base):
    __tablename__ = 'AddCollateral'
    event_id = Column(Integer, ForeignKey("CdcEvent.event_id"),primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    addAmount = Column(Integer, nullable=False)

class EventCloseCdcTable(Base):
    __tablename__ = 'CloseCdc'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64),  nullable=False)
    secSinceEpoch = Column(Integer, nullable=False)
    stabilityFee = Column(Integer, nullable=False)
    collateralAmount = Column(Integer, nullable=False)
    stableTokenAmount = Column(Integer, nullable=False)

class EventExpandLoanTable(Base):
    __tablename__ = 'ExpandLoan'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    repayFee  = Column(Integer, nullable=False)
    expandLoanAmount = Column(Integer, nullable=False)
    realGotAmount = Column(Integer, nullable=False)

class EventWidrawCollateralTable(Base):
    __tablename__ = 'WidrawCollateral'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    widrawCollateralAmount  = Column(Integer, nullable=False)

class EventPayBackTable(Base):
    __tablename__ = 'PayBack'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    fee  = Column(Integer, nullable=False)
    repayPrincipal = Column(Integer, nullable=False)
    payBackAmount = Column(Integer, nullable=False)
    realPayBackAmount = Column(Integer, nullable=False)

class EventTransferCdcTable(Base):
    __tablename__ = 'TransferCdc'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    to_address = Column(String(64), nullable=False)

########################################################################
class EventTakeBackCollateralByCdcTable(Base):
    __tablename__ = 'TakeBackCollateralByCdc'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    owner = Column(String(64),  nullable=False)
    returnAmount = Column(Integer, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventTakeBackCollateralByTokenTable(Base):
    __tablename__ = 'TakeBackCollateralByToken'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64),  nullable=False)
    returnAmount = Column(Integer, nullable=False)
    block_number = Column(Integer, nullable=False)


engine = create_engine('sqlite:///cdcs.db', echo=True, poolclass=SingletonThreadPool,
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

####################################################################
class HdaoEventsCollector:

    def __init__(self, account, contract, wallet_api):
        self.account = account
        self.contract = contract
        self.walletApi = wallet_api
        self.session = Session()
        self.batchGetNum = 1000

    def query_cdc_by_address(self, address):
        return self.session.query(CdcTable).filter_by(owner=address).first()

    def query_cdc_by_id(self, cdcId):
        return self.session.query(CdcTable).filter_by(cdcId=cdcId).first()

    def query_cdc_chain_by_id(self,chain_id):
        res = self.session.query(CdcChainTable).filter_by(chain_id=chain_id).all()
        if(res is None or len(res)==0):
            return None
        else:
            return res[0]

    def query_cdc(self, options):
        if 'start' not in options:
            options['start'] = 0
        if 'limit' not in options:
            options['limit'] = 10
        if 'address' in options and options['address'] != '':
            address = options['address']
        else:
            address = None
        if 'state' in options and options['state'] != '':
            state = options['state']
        else:
            state = None
        if address is None and state is None:
            return self.session.query(CdcTable). \
                offset(options['start']).limit(options['limit']).all()
        elif address is None and state is not None:
            return self.session.query(CdcTable). \
                filter_by(state=options['state']). \
                offset(options['start']).limit(options['limit']).all()
        elif address is not None and state is None:
            return self.session.query(CdcTable). \
                filter_by(owner=options['address']). \
                offset(options['start']).limit(options['limit']).all()
        elif address is not None and state is not None:
            return self.session.query(CdcTable). \
                filter(and_(CdcTable.owner == options['address']), CdcTable.state == options['state']). \
                offset(options['start']).limit(options['limit']).all()

    #def query_cdc_op_by_id(self, cdcId):
    #    return self.session.query(CdcEventTable).filter_by(cdcId=cdcId).order_by(
    #       CdcEventTable.block_number.desc()).all()

    def batch_add_events(self,chain_id,start_block,range,head_block_num,start_event_id):
        events = self.walletApi.rpc_request("get_contract_events_in_range",
                                       [self.contract, start_block, range])
        event_count = 0
        end_block_num = start_block+range
        if(head_block_num > head_block_num):
            end_block_num = head_block_num
        if(start_block > head_block_num ):
            logging.info("wrong start_block > head_block_num , batch_add_events start_block:"+str(start_block)+" range:"+str(range)+" head_block_num:" +str(head_block_num))
            return
        r = self.walletApi.rpc_request("get_block",[end_block_num])
        end_block_id = r['block_id']
        event_id = start_event_id
        for event in events:
            cdcInfo = json.loads(event['event_arg'])
            txid = event['trx_id']
            if event['event_name'] in (
                    'OpenCdc', 'TransferCdc', 'Liquidate', 'CloseCdc', 'AddCollateral', 'ExpandLoan',
                    'WidrawCollateral',
                    'PayBack'):
                if(self.session.query(CdcEventTable).filter_by(tx_id=txid).count()>0):
                    continue
                #self.session.query(CdcEventTable).filter_by(tx_id=txid).delete()

                self.session.add(CdcEventTable(
                    event_id = event_id,
                    tx_id=txid,
                    op=event['event_name'],
                    block_number=event['block_num']
                ))
                if event['event_name'] == 'OpenCdc':
                    self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).delete()
                    self.session.add(CdcTable(
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
                                          secSinceEpoch = cdcInfo['secSinceEpoch'])
                    self.session.add(e)

                elif event['event_name'] == 'AddCollateral':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.collateralAmount = str(int(cdc.collateralAmount) + int(cdcInfo['addAmount']))
                        self.session.add(cdc)
                        e = EventAddCollateralTable(event_id=event_id,
                                              cdcId=cdcInfo['cdcId'],
                                            addAmount=cdcInfo['addAmount'])
                        self.session.add(e)
                elif event['event_name'] == 'WidrawCollateral':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.collateralAmount = str(int(cdc.collateralAmount) - int(cdcInfo['widrawCollateralAmount']))
                        self.session.add(cdc)
                        e = EventWidrawCollateralTable(event_id=event_id,
                                                cdcId=cdcInfo['cdcId'],
                                                from_address=cdcInfo['from_address'],
                                                widrawCollateralAmount=cdcInfo['widrawCollateralAmount'])
                        self.session.add(e)
                elif event['event_name'] == 'ExpandLoan':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.stableTokenAmount = str(int(cdc.stableTokenAmount) + int(cdcInfo['realGotAmount']))
                        self.session.add(cdc)
                        e = EventExpandLoanTable(event_id=event_id,
                                                cdcId=cdcInfo['cdcId'],
                                                 from_address=cdcInfo['from_address'],
                                                 realGotAmount=cdcInfo['realGotAmount'],
                                                 expandLoanAmount=cdcInfo['expandLoanAmount'],
                                                 repayFee=cdcInfo['repayFee'])
                        self.session.add(e)
                elif event['event_name'] == 'PayBack':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.stableTokenAmount = str(int(cdc.stableTokenAmount) - int(cdcInfo['repayPrincipal']))
                        self.session.add(cdc)
                        e = EventPayBackTable(event_id=event_id,
                                                 cdcId=cdcInfo['cdcId'],
                                                 from_address=cdcInfo['from_address'],
                                                 payBackAmount=cdcInfo['payBackAmount'],
                                                 realPayBackAmount=cdcInfo['realPayBackAmount'],
                                                 repayPrincipal=cdcInfo['repayPrincipal'],
                                                 fee=cdcInfo['fee'])
                        self.session.add(e)
                elif event['event_name'] == 'TransferCdc':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        if cdc.owner != cdcInfo['from_address']:
                            logging.error("Not match owner error: %s(%s => %s)" % (
                                cdcInfo['cdcId'], cdc.owner, cdcInfo['from_address']))
                        cdc.owner = cdcInfo['to_address']
                        self.session.add(cdc)
                        e = EventTransferCdcTable(event_id=event_id,
                                                 cdcId=cdcInfo['cdcId'],
                                                 from_address=cdcInfo['from_address'],
                                                  to_address=cdcInfo['to_address'])
                        self.session.add(e)
                elif event['event_name'] == 'Liquidate':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.liquidator = cdcInfo['liquidator']
                        cdc.state = 2
                        self.session.add(cdc)
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
                                                auctionCollateralAmount=cdcInfo['auctionCollateralAmount'])
                        self.session.add(e)
                elif event['event_name'] == 'CloseCdc':
                    cdc = self.session.query(CdcTable).filter_by(cdcId=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: " + cdcInfo['cdcId'])
                    else:
                        cdc.state = 3
                        self.session.add(cdc)
                        e = EventCloseCdcTable(event_id=event_id,
                                              cdcId=cdcInfo['cdcId'],
                                              owner=cdcInfo['owner'],
                                               stabilityFee=cdcInfo['stabilityFee'],
                                               secSinceEpoch=cdcInfo['secSinceEpoch'],
                                               collateralAmount=cdcInfo['collateralAmount'],
                                               stableTokenAmount=cdcInfo['stableTokenAmount'])
                        self.session.add(e)
                event_count = event_count + 1
                event_id = event_id + 1

        self.session.query(CdcChainTable).filter_by(chain_id=chain_id).delete()
        self.session.add(CdcChainTable(
            chain_id=chain_id,
            end_block_num=end_block_num,
            end_block_id = end_block_id
        ))
        self.session.commit()
        logging.info("batch add events_count: " +str(event_count) + " start_block:"+str(start_block) + " end_block_num:"+str(start_block+range) +" end_block_id:"+str(end_block_num))
        return event_count


    def collect_event(self,end_block=0):
        try:
            start_block = 0
            info = self.walletApi.rpc_request("info", [])
            head_block_num = info['head_block_num']
            if(end_block == 0 or end_block<head_block_num):
                end_block = head_block_num
            chain_id = info['chain_id']
            if(chain_id is None or len(chain_id)<1):
                logging.error("chain_id is empty" )
                return

            cdc_chain = self.query_cdc_chain_by_id(chain_id)
            if(cdc_chain is None):
                logging.info("try collect from first")
                r = self.walletApi.rpc_request("get_simple_contract_info", [self.contract])
                registered_block = r['registered_block']
                start_block = registered_block
                self.session.add(CdcChainTable(
                    chain_id=chain_id,
                    end_block_num=0,
                    end_block_id=" "
                ))
            else:
                start_block = cdc_chain.end_block_num + 1

            batchGetNum = self.batchGetNum
            temp_start_block_num = start_block
            temp_end_block_num = end_block
            start_event_id = self.session.query(CdcEventTable).count()
            if(start_event_id is None or start_event_id<0):
                logging.error("self.session.query(CdcEventTable).count() wrong")
                return
            total_events__count = 0
            while(temp_start_block_num <= end_block):
                if((end_block - temp_start_block_num + 1 ) > batchGetNum):
                    temp_end_block_num = temp_start_block_num + batchGetNum
                else:
                    temp_end_block_num = end_block

                #......
                range = temp_end_block_num-temp_start_block_num
                event_count  = 0
                if(range==0):
                    event_count = self.batch_add_events(chain_id, temp_start_block_num,1,head_block_num,start_event_id)
                    total_events__count = total_events__count + event_count
                    break
                else:
                    event_count = self.batch_add_events(chain_id, temp_start_block_num, range, head_block_num, start_event_id)
                    total_events__count = total_events__count + event_count
                temp_start_block_num = temp_end_block_num
                start_event_id = start_event_id + event_count
        except BaseException as e:
            print(e)
        finally:
            self.session.close()
        print("--------total_events__count:"+str(total_events__count))


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    from hdao.hx_wallet_api import HXWalletApi

    api = HXWalletApi(name='events', rpc_url='http://192.168.1.121:30088/')
    collector = HdaoEventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    time1 = datetime.datetime.now()
    collector.collect_event()

    time2 = datetime.datetime.now()
    r = time2- time1
    print(r)