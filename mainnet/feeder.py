import requests
import datetime
import time
import sys
import threading
import decimal
from hdao.hdao_price_feeder import PriceFeeder
from hdao.hx_wallet_api import *



class FeederInfo:
    def __init__(self):
        self.account = ""
        self.websites = []

class ContractFeedingInfo:
    def __init__(self):
        self.symbolPair = ""
        self.wallet_api_url = ""
        self.priceFeeder_contract_address = ""
        self.feeders = [FeederInfo()]
        self.feeder_names = ["1","2"]
        self.interval = 1
