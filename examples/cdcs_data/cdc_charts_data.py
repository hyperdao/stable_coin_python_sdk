#from cdcs_data import
from hdao.hx_wallet_api import HXWalletApi
from cdc_events_colletor import EventLiquidateTable
from cdc_events_colletor import EventOpenCdcTable
from cdc_events_colletor import CdcTable
from cdc_events_colletor import CdcChainTable
from cdc_events_colletor import EventCloseCdcTable
from cdc_events_colletor import EventPayBackTable
from cdc_events_colletor import EventExpandLoanTable
from cdc_events_colletor import StableTokenSupplyHistoryTable

from sqlalchemy.sql import operators
from sqlalchemy import func
from sqlalchemy import and_
import json


import logging
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool



#wallet_rpc_url = 'http://192.168.1.121:30088/'
#sqlite_db_path = 'sqlite:///cdcs.db'
class Cdc_Charts_Data:
    def __init__(self,wallet_rpc_url,sqlite_db_path):
        self.walletApi = HXWalletApi(name='events', rpc_url=wallet_rpc_url)
        Base = declarative_base()
        engine = create_engine(sqlite_db_path, echo=True, poolclass=SingletonThreadPool,
                               connect_args={'check_same_thread': False})
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)


    def get_liquidate_chart_data(self,interlval_blocks):
        session = self.Session()
        try:
            r = session.query(func.count('*').label("count"),func.sum(EventLiquidateTable.stableTokenAmount).label("sum"),
                                              operators.op(EventLiquidateTable.block_number, '/', interlval_blocks).label(
                                                  "blockn")).group_by("blockn").order_by("blockn").all() # week
            return r
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()


    def get_opencdc_chart_data(self,interlval_blocks):
        session = self.Session()
        try:
            r = session.query(func.count('*').label("count"),func.sum(EventOpenCdcTable.stableTokenAmount).label("sum"),
                                              operators.op(EventOpenCdcTable.block_number, '/', interlval_blocks).label(
                                                  "blockn")).group_by("blockn").order_by("blockn").all() # week
            return r
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()

    def get_payback_chart_data(self,interlval_blocks):
        session = self.Session()
        try:
            r = session.query(func.count('*').label("count"),func.sum(EventPayBackTable.repayPrincipal).label("sum"),
                                              operators.op(EventPayBackTable.block_number, '/', interlval_blocks).label(
                                                  "blockn")).group_by("blockn").order_by("blockn").all()
            return r
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()

    def get_expandLoan_chart_data(self,interlval_blocks):
        session = self.Session()
        try:
            r = session.query(func.count('*').label("count"),func.sum(EventExpandLoanTable.expandLoanAmount).label("sum"),
                                              operators.op(EventExpandLoanTable.block_number, '/', interlval_blocks).label(
                                                  "blockn")).group_by("blockn").order_by("blockn").all()

            return r
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()

    def get_closecdc_chart_data(self,interlval_blocks):
        session = self.Session()
        try:
            r = session.query(func.count('*').label("count"),func.sum(EventCloseCdcTable.stableTokenAmount).label("sum"),
                                              operators.op(EventCloseCdcTable.block_number, '/', interlval_blocks).label(
                                                  "blockn")).group_by("blockn").order_by("blockn").all()
            return r
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()

    def get_supply_history_data(self,startblocknum=None):
        session = self.Session()
        try:
            if (startblocknum is None):
                return session.query(StableTokenSupplyHistoryTable.block_number,StableTokenSupplyHistoryTable.supply).order_by(StableTokenSupplyHistoryTable.block_number.asc()).all()
            else:
                return session.query(StableTokenSupplyHistoryTable.block_number,StableTokenSupplyHistoryTable.supply).filter(operators.op(StableTokenSupplyHistoryTable.block_number, '>=', startblocknum)).order_by(StableTokenSupplyHistoryTable.block_number.asc()).all()
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()

    #return  sum(CdcTable.collateralAmount),sum(CdcTable.stableTokenAmount)
    def get_cdc_sum_collateral_and_stableToken(self):
        session = self.Session()
        try:
            r= session.query(func.sum(CdcTable.collateralAmount),func.sum(CdcTable.stableTokenAmount)).first()
            return r
        except BaseException as e:
            print(e)
            return (0,0)
        finally:
            session.close()


    def get_cdc_count_by_tokenAmount_data(self,low,hign=None):
        session = self.Session()
        try:
            if(hign is not None):
                return session.query(func.count('*').label("count")).filter(CdcTable.state==1,CdcTable.stableTokenAmount>=low,CdcTable.stableTokenAmount<hign).first() 
            else:
                return session.query(func.count('*').label("count")).filter(CdcTable.state == 1,
                                                                            CdcTable.stableTokenAmount >= low).first()
        except BaseException as e:
            print(e)
            return []
        finally:
            session.close()


    ############################################################################################################################
    def get_bars_data(self,per_blocks,startblockn=None,endblocknum=None):
        barItems = ['liquidate', 'payback', 'expandloan', 'opencdc', 'closecdc']
        result = {}
        session = self.Session()
        res = session.query(CdcChainTable.contract_register_block_num,CdcChainTable.end_block_num).first()
        if (res is None or len(res) == 0):
            raise RuntimeError("db is empty, please collect event data first")
            return
        if (startblockn is None):
            startblockn = res[0]
        if(endblocknum is None):
            endblocknum = res[1]

        rangen = int((endblocknum - startblockn) / per_blocks) + 1
        x_blocks = []
        x_value = int(startblockn / per_blocks)
        for i in range(0, rangen):
            x_blocks.append(x_value)
            x_value = x_value + 1

        x_readable_vs = []
        for i in range(0, rangen):
            info = self.walletApi.rpc_request("get_block", [x_blocks[i] * per_blocks])
            timestamp = info['timestamp']
            j = i + 1
            if (i == rangen - 1):
                info = self.walletApi.rpc_request("get_block", [endblocknum])
                end_timestamp = info['timestamp']
                x_readable_vs.append(timestamp + "~" + end_timestamp)
            else:
                x_readable_vs.append(timestamp)

            if (i != 0):
                x_readable_vs[i - 1] = x_readable_vs[i - 1] + "~" + timestamp

        result['x_values'] = x_readable_vs

        for bitem in barItems:
            counts_values = []
            sum_values = []
            for i in range(0,rangen):
                counts_values.append(0)
                sum_values.append(0)
            res = []
            if (bitem == 'liquidate'):
                res = self.get_liquidate_chart_data(per_blocks)
            elif (bitem == 'payback'):
                res = self.get_payback_chart_data(per_blocks)
            elif (bitem == 'expandloan'):
                res = self.get_expandLoan_chart_data(per_blocks)
            elif (bitem == 'closecdc'):
                res = self.get_closecdc_chart_data(per_blocks)
            elif (bitem == 'opencdc'):
                res = self.get_opencdc_chart_data(per_blocks)
            else:
                continue

            for v in res:
                blockn = v[2]
                idx = blockn - x_blocks[0]
                if (idx < 0 or idx > len(x_blocks)):
                    raise RuntimeError("wrong idx:" + str(idx) + " blockn:" + str(blockn))
                counts_values[idx] = v[0]
                sum_values[idx] = v[1] / 100000000

            result['y_values_'+bitem+"_count"] = counts_values
            result['y_values_' + bitem + "_sum"] = sum_values
        return result

    def get_collateral_rate(self):
        session = self.Session()
        cdc_contract_address = session.query(CdcChainTable.cdc_contract_address).first()[0]
        if (cdc_contract_address is None or len(cdc_contract_address) == 0):
            raise RuntimeError("db is empty, please collect event data first")
            return

        r = self.get_cdc_sum_collateral_and_stableToken()
        if(r[0]<=0 or r[1]<=0):
            return None
        sum_collateral = r[0]
        sum_stableToken = r[1]
        accounts = self.walletApi.rpc_request('list_my_accounts', [""])

        account = accounts[0]["name"]
        cdcInfo = self.walletApi.rpc_request('invoke_contract_offline', [account, cdc_contract_address, "getInfo", ""])
        priceFeederAddr = json.loads(cdcInfo)['priceFeederAddr']
        price = self.walletApi.rpc_request('invoke_contract_offline', [account, priceFeederAddr, "getPrice", ""])
        rate =  sum_collateral*float(price)/sum_stableToken
        return rate


if __name__ == "__main__":
    wallet_rpc_url = 'http://192.168.1.121:30088/'
    sqlite_db_path = 'sqlite:///cdcs.db'
    c = Cdc_Charts_Data(wallet_rpc_url,sqlite_db_path)
    one_hour_blocks = int(60*60/5)
    r = c.get_liquidate_chart_data(one_hour_blocks)
    print(r)




