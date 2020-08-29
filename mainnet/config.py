# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.orm import sessionmaker
from hdao.cdc_data_table_structure import *
HX_TESTNET_RPC = 'http://192.168.1.121:30088/'
CDC_CONTRACT_ID = 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks'
FEEDER_CONTRACT_ID = 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1'
PRICE_FEEDER = {'account': 'senator0', 'address': 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W'}
USER1 = {'account': 'da', 'address': 'HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh'}

engine = create_engine('sqlite:///cdcs.db', echo=True, poolclass=SingletonThreadPool,
                       connect_args={'check_same_thread': False})

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)