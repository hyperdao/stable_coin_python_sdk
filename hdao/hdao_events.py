import json
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String


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

# class CdcOpHistoryTable(Base):
#     __tablename__ = 'cdc_op_history'
#     cdc_id = Column(String(128), primary_key=True, nullable=False)
#     op = Column(String(16), nullable=False)
#     collateral_amount = Column(String(128), nullable=False)
#     stable_token_amount = Column(String(128), nullable=False)
#     owner = Column(String(128), nullable=False)
#     liquidator = Column(String(128), default="")
#     block_number = Column(Integer, nullable=False)

#     def __repr__(self):
#         return "<CdcOp(cdcId='%s', collateralAmount='%s', stableTokenAmount='%s')>" % (
#             self.cdc_id, self.collateral_amount, self.stable_token_amount)


engine = create_engine('sqlite:///cdcs.db', echo=True)
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
        return self.session.query(CdcTable).filter_by(owner=address).all()

    def query_cdc_by_id(self, cdc_id):
        return self.session.query(CdcTable).filter_by(cdc_id=cdc_id).first()

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
    
    def _get_contract_invoke_object(self, op, txid, block):
        invoke_obj = self.walletApi.rpc_request("get_contract_invoke_object", [txid])
        if invoke_obj is None:
            return False
        for obj in invoke_obj:
            for event in obj['events']: # Inited, Mint, DestoryAndTrans, ExpandLoan, AddCollateral, WidrawCollateral, PayBack
                logging.debug('event: '+event['event_name'])
                if event['event_name'] == 'OpenCdc':
                    cdcInfo = json.loads(event['event_arg'])
                    self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).delete()
                    self.session.add(CdcTable(
                        cdc_id=cdcInfo['cdcId'], 
                        owner=cdcInfo['owner'], 
                        collateral_amount=cdcInfo['collateralAmount'], 
                        stable_token_amount=cdcInfo['stableTokenAmount'], 
                        state=1, block_number=block['number']))
                elif event['event_name'] == 'TransferCdc':
                    transferInfo = json.loads(event['event_arg'])
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=transferInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+transferInfo['cdcId'])
                    else:
                        if cdc.owner != transferInfo['from_address']:
                            logging.error("Not match owner error: %s(%s => %s)" % (transferInfo['cdcId'], cdc.owner, transferInfo['from_address']))
                        cdc.owner = transferInfo['to_address']
                    self.session.add(cdc)
                elif event['event_name'] == 'Liquidate':
                    cdcInfo = json.loads(event['event_arg'])
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.liquidator = cdcInfo['liquidator']
                        cdc.state = 2
                        self.session.add(cdc)
                elif event['event_name'] == 'CloseCdc':
                    cdcInfo = json.loads(event['event_arg'])
                    cdc = self.session.query(CdcTable).filter_by(cdc_id=cdcInfo['cdcId']).first()
                    if cdc is None:
                        logging.error("Not found cdc error: "+cdcInfo['cdcId'])
                    else:
                        cdc.state = 3
                        self.session.add(cdc)
                else:
                    logging.info("Unprocessed event:"+event['event_name'])
                    continue
        return False


if __name__ == "__main__":
    from hx_wallet_api import HXWalletApi
    api = HXWalletApi(name='events', rpc_url='http://192.168.1.121:30088/')
    collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    collector.collect_event(1290000, 100000)