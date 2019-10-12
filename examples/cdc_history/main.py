#coding=utf-8

import click
import os
# import datetime
import logging
import json
import time
import requests
from flask import Flask
from flask_cors import cross_origin, CORS
from flask import make_response
from flask_jsonrpc import JSONRPC
from hdao.hdao_events import EventsCollector
from hdao.hx_wallet_api import HXWalletApi


app = Flask(__name__)
CORS(app)

@cross_origin
@app.route('/api', methods=['OPTIONS'])
def options_api():
    rst = make_response('')
    rst.headers['Access-Control-Allow-Origin'] = '*'
    rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE,OPTIONS'
    allow_headers = "Referer,Accept,Origin,User-Agent,Content-Type,X-TOKEN"
    rst.headers['Access-Control-Allow-Headers'] = allow_headers
    return rst

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.cli.command('scan')
def scan():
    state_file = './cdc_history_state.json'
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except:
        state = {'start_block': 1}
    if 'start_block' not in state or state['start_block'] is None:
        state = {'start_block': 1}
    api = HXWalletApi(name='cdc_service', rpc_url='http://192.168.1.121:30088/')
    collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', api)
    start_block = state['start_block']
    end_block = start_block
    while True:
        if end_block <= start_block:
            info = api.rpc_request('info', [])
            if info is not None:
                end_block = int(info['head_block_num'])
                step = end_block - start_block
            else:
                step = 100
        step = end_block - start_block if end_block - start_block < 100 else 100
        logging.info('Scan block from {0} to {1}...'.format(start_block, start_block+step))
        end_block = collector.collect_event(start_block, step)
        state['start_block'] = end_block
        start_block = end_block
    
        url = 'http://api.zb.plus/data/v1/ticker?market=btc_usdt'
        try:
            r = requests.get(url)
        except:
            pass
        else:
            state['btc_usdt'] = r.json()
        url = 'http://api.zb.plus/data/v1/ticker?market=hx_usdt'
        try:
            r = requests.get(url)
        except:
            pass
        else:
            state['hx_usdt'] = r.json()
        state['hx_usdt'] = r.json()
        print(r.json())
        with open(state_file, 'w') as wf:
            json.dump(state, wf)
        if end_block - start_block < 10:
            time.sleep(5)


@jsonrpc.method('hdao.cdc.query(options=dict)', validate=True)
def hdao_cdc_query(options):
    collector = EventsCollector('', '', None)
    data = collector.query_cdc(options)
    i = 0
    cdcs = []
    for d in data:
        cdcs.append({
            'cdc_id':d.cdc_id, 
            'state': d.state, 
            'stablility_fee': d.stablility_fee,
            'collateral_amount': d.collateral_amount, 
            'stable_token_amount': d.stable_token_amount,
            'owner': d.owner,
            'liquidator': d.liquidator,
            'block_number': d.block_number})
    return {
        'options': options,
        'total': len(data),
        'data': cdcs
    }

@jsonrpc.method('hdao.cdc.ticker.query(asset=str)', validate=True)
def hdao_cdc_ticker_query(asset):
    state_file = './cdc_history_state.json'
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except:
        return {'price': 0}
    else:
        if asset == 'btc':
            return {'price': state['btc_usdt']['ticker']['last']}
        elif asset == 'hx':
            return {'price': state['hx_usdt']['ticker']['last']}



@jsonrpc.method('hdao.cdc.history.query(cdc_id=str, start=int, limit=int)', validate=True)
def hdao_cdc_history_query(cdc_id, start=1, limit=10):
    collector = EventsCollector('', '', None)
    data = collector.query_cdc_op_by_id(cdc_id)
    i = 0
    ops = []
    for d in data:
        i += 1
        if i < start:
            continue
        elif len(ops) >= limit:
            break
        ops.append({
            'cdc_id': d.cdc_id,
            'tx_id': d.tx_id,
            'op': d.op,
            'op_content': d.op_content,
            'block_number': d.block_number
        })
    return {
        'cdc_id': cdc_id,
        'start': start,
        'limit': limit,
        'total': len(data),
        'data': ops
    }
