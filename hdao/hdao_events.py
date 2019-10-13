import json
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy import and_


Base = declarative_base()

class CdcTable(Base):
    __tablename__ = 'cdcs'
    cdc_id = Column(String(128), primary_key=True, nullable=False)
    state = Column(Integer, nullable=False)
    stablility_fee = Column(String(128), default="")
    collateral_amount = Column(String(128), nullable=False)
    stable_token_amount = Column(String(128), nullable=False)
    owner = Column(String(128), nullable=False)
    liquidator = Column(String(128), default="")
    block_number = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Cdc(cdcId='%s', collateralAmount='%s', stableTokenAmount='%s')>" % (
            self.cdc_id, self.collateral_amount, self.stable_token_amount)

class CdcOpHistoryTable(Base):
    __tablename__ = 'cdc_op_history'
    cdc_id = Column(String(128), nullable=False, index=True)
    tx_id = Column(String(128), primary_key=True, nullable=False)
    op = Column(String(16), nullable=False)
    op_content = Column(String(1024), nullable=False)
    block_number = Column(Integer, nullable=False)

    def __repr__(self):
        return "<CdcOpHistory(cdcId='%s', op='%s', block_number='%d')>" % (
            self.cdc_id, self.op, self.block_number)


engine = create_engine('sqlite:///cdcs.db', echo=True, poolclass=SingletonThreadPool, connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
    

class EventsCollector:
    OP_TYPE_CONTRACT_REGISTER = 76
    OP_TYPE_CONTRACT_UPGRADE = 77
    OP_TYPE_CONTRACT_INVOKE = 79
    OP_TYPE_CONTRACT_TRANSFER = 81

    def __init__(self, account, contract, wallet_api):
        self.account = account
        self.contract = contract
        self.walletApi = wallet_api
        self.session = Session()

    def query_cdc_by_address(self, address):
        return self.session.query(CdcTable).filter_by(owner=address).first()
    
    def query_cdc_by_id(self, cdc_id):
        return self.session.query(CdcTable).filter_by(cdc_id=cdc_id).first()

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
            state =options['state']
        else:
            state = None
        if address is None and state is None:
            return self.session.query(CdcTable).\
                offset(options['start']).limit(options['limit']).all()
        elif address is None and state is not None:
            return self.session.query(CdcTable).\
                filter_by(state=options['state']).\
                offset(options['start']).limit(options['limit']).all()
        elif address is not None and state is None:
            return self.session.query(CdcTable).\
                filter_by(owner=options['address']).\
                offset(options['start']).limit(options['limit']).all()
        elif address is not None and state is not None:
            return self.session.query(CdcTable).\
                filter(and_(CdcTable.owner==options['address']), CdcTable.state==options['state']).\
                offset(options['start']).limit(options['limit']).all()

    def query_cdc_op_by_id(self, cdc_id):
        return self.session.query(CdcOpHistoryTable).filter_by(cdc_id=cdc_id).order_by(CdcOpHistoryTable.block_number.desc()).all()

    def collect_event(self, block=1, step=100):
        start_block = int(block)
        end_block = start_block + step
        while start_block < end_block:
            # if start_block % 100 == 0:
            #     print(start_block)
            block = self.walletApi.rpc_request("get_block", [start_block])
            if block is None:
                break
            start_block += 1
            if len(block['transactions']) <= 0:
                continue
            tx_count = 0
            for t in block['transactions']:
                for op in t['operations']:
                    if (op[0] == EventsCollector.OP_TYPE_CONTRACT_INVOKE or op[0] == 80 \
                        or op[0] == EventsCollector.OP_TYPE_CONTRACT_TRANSFER) \
                        and op[1]['contract_id'] == self.contract:
                        ret = self._get_contract_invoke_object(op, block['transaction_ids'][tx_count], block)
                        if ret:
                            return
                tx_count += 1
        self.session.commit()
        self.session.close()
        return start_block
    
    def _get_contract_invoke_object(self, op, txid, block):
        invoke_obj = self.walletApi.rpc_request("get_contract_invoke_object", [txid])
        if invoke_obj is None:
            return False
        for obj in invoke_obj:
            for event in obj['events']: # Inited, Mint, DestoryAndTrans, ExpandLoan, AddCollateral, WidrawCollateral, PayBack
                logging.debug('event: '+event['event_name'])
                if event['event_name'] in ('OpenCdc', 'TransferCdc', 'Liquidate', 'CloseCdc', 'AddCollateral', 'ExpandLoan', 'WidrawCollateral', 'PayBack'):
                    cdcInfo = json.loads(event['event_arg'])
                    self.session.query(CdcOpHistoryTable).filter_by(tx_id=txid).delete()
                    self.session.add(CdcOpHistoryTable(
                        cdc_id=cdcInfo['cdcId'],
                        tx_id=txid,
                        op=event['event_name'],
                        op_content=event['event_arg'],
                        block_number=block['number']
                    ))
                else:
                    logging.info("Unprocessed event:"+event['event_name'])
                    continue
                if event['event_name'] == 'OpenCdc':
                    self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).delete()
                    self.session.add(CdcTable(
                        cdc_id=cdcInfo['cdcId'], 
                        owner=cdcInfo['owner'], 
                        collateral_amount=cdcInfo['collateralAmount'], 
                        stable_token_amount=cdcInfo['stableTokenAmount'], 
                        state=1, block_number=block['number']))
                elif event['event_name'] == 'AddCollateral':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.collateral_amount = str(int(cdc.collateral_amount) + int(cdcInfo['addAmount']))
                    self.session.add(cdc)
                elif event['event_name'] == 'WidrawCollateral':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.collateral_amount = str(int(cdc.collateral_amount) - int(cdcInfo['widrawCollateralAmount']))
                    self.session.add(cdc)
                elif event['event_name'] == 'ExpandLoan':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.stable_token_amount = str(int(cdc.stable_token_amount) + int(cdcInfo['realGotAmount']))
                    self.session.add(cdc)
                elif event['event_name'] == 'PayBack':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.stable_token_amount = str(int(cdc.stable_token_amount) - int(cdcInfo['repayPrincipal']))
                    self.session.add(cdc)
                elif event['event_name'] == 'TransferCdc':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        if cdc.owner != cdcInfo['from_address']:
                            logging.error("Not match owner error: %s(%s => %s)" % (cdcInfo['cdcId'], cdc.owner, cdcInfo['from_address']))
                        cdc.owner = cdcInfo['to_address']
                    self.session.add(cdc)
                elif event['event_name'] == 'Liquidate':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.liquidator = cdcInfo['liquidator']
                        cdc.state = 2
                        self.session.add(cdc)
                elif event['event_name'] == 'CloseCdc':
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.state = 3
                        self.session.add(cdc)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    from hx_wallet_api import HXWalletApi
    api = HXWalletApi(name='events', rpc_url='http://192.168.1.121:30088/')
    collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    collector.collect_event(1411286, 100000)