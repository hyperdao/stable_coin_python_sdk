from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean,ForeignKey,BigInteger

Base = declarative_base()

class CdcChainTable(Base):
    __tablename__ = 'cdc_chain'
    chain_id = Column(String(128), primary_key=True, nullable=False)
    cdc_contract_address = Column(String(128), nullable=False)
    contract_register_block_num = Column(Integer, nullable=False)
    end_block_num = Column(Integer, nullable=False)
    end_block_id = Column(String(128), nullable=False)

class CdcTable(Base):
    __tablename__ = 'cdcs'
    cdcId = Column(String(128), primary_key=True, nullable=False)
    state = Column(Integer, nullable=False)
    stabilityFee = Column(BigInteger, default="")
    collateralAmount = Column(BigInteger, nullable=False)
    stableTokenAmount = Column(BigInteger, nullable=False)
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

    def __repr__(self):
        return "<CdcEvent(cdcId='%s', op='%s', block_number='%d')>" % (
            self.cdcId, self.op, self.block_number)

class StableTokenSupplyHistoryTable(Base):
    __tablename__ = 'StableTokenSupplyHistory'
    block_number = Column(Integer, primary_key=True, nullable=False)
    supply = Column(BigInteger, nullable=False)

class EventOpenCdcTable(Base):
    __tablename__ = 'OpenCdc'
    event_id = Column(Integer, ForeignKey("CdcEvent.event_id"),primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64), nullable=False)
    secSinceEpoch = Column(Integer, nullable=False)
    collateralAmount = Column(BigInteger, nullable=False)
    stableTokenAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventLiquidateTable(Base):
    __tablename__ = 'Liquidate'
    event_id = Column(Integer, ForeignKey("CdcEvent.event_id"),primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64), nullable=False)
    secSinceEpoch = Column(Integer, nullable=False)
    collateralAmount = Column(BigInteger, nullable=False)
    stableTokenAmount = Column(BigInteger, nullable=False)
    curPrice = Column(String(64), nullable=False)
    isBadDebt = Column(Boolean, nullable=False)
    liquidator = Column(String(64), nullable=False)
    auctionPrice = Column(String(64), nullable=False)
    returnAmount = Column(BigInteger, nullable=False)
    penaltyAmount = Column(BigInteger, nullable=False)
    isNeedLiquidation = Column(Boolean, nullable=False)
    stabilityFee = Column(BigInteger, nullable=False)
    repayStableTokenAmount = Column(BigInteger, nullable=False)
    auctionCollateralAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventAddCollateralTable(Base):
    __tablename__ = 'AddCollateral'
    event_id = Column(Integer, ForeignKey("CdcEvent.event_id"),primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    addAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventCloseCdcTable(Base):
    __tablename__ = 'CloseCdc'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64),  nullable=False)
    secSinceEpoch = Column(Integer, nullable=False)
    stabilityFee = Column(BigInteger, nullable=False)
    collateralAmount = Column(BigInteger, nullable=False)
    stableTokenAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventExpandLoanTable(Base):
    __tablename__ = 'ExpandLoan'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    repayFee  = Column(BigInteger, nullable=False)
    expandLoanAmount = Column(BigInteger, nullable=False)
    realGotAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventWidrawCollateralTable(Base):
    __tablename__ = 'WidrawCollateral'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    widrawCollateralAmount  = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventPayBackTable(Base):
    __tablename__ = 'PayBack'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    fee  = Column(BigInteger, nullable=False)
    repayPrincipal = Column(BigInteger, nullable=False)
    payBackAmount = Column(BigInteger, nullable=False)
    realPayBackAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventTransferCdcTable(Base):
    __tablename__ = 'TransferCdc'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    from_address = Column(String(64),  nullable=False)
    to_address = Column(String(64), nullable=False)
    block_number = Column(Integer, nullable=False)

########################################################################
class EventTakeBackCollateralByCdcTable(Base):
    __tablename__ = 'TakeBackCollateralByCdc'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    owner = Column(String(64),  nullable=False)
    returnAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)

class EventTakeBackCollateralByTokenTable(Base):
    __tablename__ = 'TakeBackCollateralByToken'
    event_id = Column(Integer,ForeignKey("CdcEvent.event_id"), primary_key=True, nullable=False)
    cdcId = Column(String(128), nullable=False, index=True)
    owner = Column(String(64),  nullable=False)
    returnAmount = Column(BigInteger, nullable=False)
    block_number = Column(Integer, nullable=False)