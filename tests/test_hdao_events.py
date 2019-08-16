import pytest
from hdao.hx_wallet_api import HXWalletApi
from hdao.hdao_events import EventsCollector


class TestHdaoEvents():
    def setup_method(self, function):
        self.api = HXWalletApi(name=function.__name__, rpc_url='http://192.168.1.121:8077/')
        self.collector = EventsCollector('da', 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks', self.api)

    def teardown_function(self):
        self.api = None
        self.collector = None
        self.cdc = None

    def test_collect(self):
        self.collector.collect_event(969234)