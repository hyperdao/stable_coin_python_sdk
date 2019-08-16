import json

class EventsCollector:
    OP_TYPE_CONTRACT_REGISTER = 76
    OP_TYPE_CONTRACT_UPGRADE = 77
    OP_TYPE_CONTRACT_INVOKE = 79
    OP_TYPE_CONTRACT_TRANSFER = 81

    def __init__(self, account, contract, wallet_api):
        self.account = account
        self.contract = contract
        self.wallet_api = wallet_api
        self.history_cdcs = []
        self.addr2Cdcs = {}

    def collect_event(self, block=1):
        start_block = int(block)
        while True and start_block < 971000:
            # if start_block % 100 == 0:
            #     print(start_block)
            block = self.wallet_api.rpc_request("get_block", [start_block])
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
    
    def _get_contract_invoke_object(self, op, txid, block):
        invoke_obj = self.wallet_api.rpc_request("get_contract_invoke_object", [txid])
        if invoke_obj is None:
            return False
        for obj in invoke_obj:
            for event in obj['events']: # Inited, Mint, DestoryAndTrans, ExpandLoan, AddCollateral, WidrawCollateral, PayBack
                print('event: '+event['event_name'])
                if event['event_name'] == 'OpenCdc':
                    cdc = json.loads(event['event_arg'])
                    if cdc['owner'] in self.addr2Cdcs:
                        self.addr2Cdcs[cdc['owner']].add(cdc['cdcId'])
                    else:
                        self.addr2Cdcs[cdc['owner']] = {cdc['cdcId']}
                elif event['event_name'] == 'TransferCdc':
                    transferInfo = json.loads(event['event_arg'])
                    if transferInfo['from_address'] in self.addr2Cdcs and transferInfo['cdcId'] in self.addr2Cdcs[transferInfo['from_address']]:
                        self.addr2Cdcs[transferInfo['from_address']].remove(transferInfo['cdcId'])
                        self.addr2Cdcs[transferInfo['to_address']].add(transferInfo['cdcId'])
                    else:
                        print("Incorrect cdc owner: "+transferInfo['cdcId'])
                elif event['event_name'] == 'Liquidate':
                    cdcInfo = json.loads(event['event_arg'])
                    self.history_cdcs.append(cdcInfo)
                    if cdcInfo['owner'] in self.addr2Cdcs and cdcInfo['cdcId'] in self.addr2Cdcs[cdcInfo['owner']]:
                        self.addr2Cdcs[cdcInfo['owner']].remove(cdcInfo['cdcId'])
                    else:
                        print("Incorrect cdc owner: "+transferInfo['cdcId'])
                elif event['event_name'] == 'CloseCdc':
                    self.history_cdcs.append(cdcInfo)
                    cdcInfo = json.loads(event['event_arg'])
                    if cdcInfo['owner'] in self.addr2Cdcs and cdcInfo['cdcId'] in self.addr2Cdcs[cdcInfo['owner']]:
                        self.addr2Cdcs[cdcInfo['owner']].remove(cdcInfo['cdcId'])
                    else:
                        print("Incorrect cdc owner: "+transferInfo['cdcId'])
                else:
                    print("Unprocessed event:"+event['event_name'])
                    continue
        return False


if __name__ == "__main__":
    from hx_wallet_api import HXWalletApi
    api = HXWalletApi(name='events', rpc_url='http://192.168.1.121:8077/')
    collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    collector.collect_event(969234)