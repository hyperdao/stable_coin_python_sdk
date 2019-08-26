# stable_coin_python_sdk
Python SDK for HyperDao Stable Coin System


# Install

1. Using ```pip```

```
pip install hdao-python-sdk
```

2. Install from source

```
git clone https://github.com/hyperdao/stable_coin_python_sdk
cd stable_coin_python_sdk
python setup.py install
```

# Usage

# Test

HyperDao stable coin system depends on HyperExchange mainnet. So the test cases should be run with HyperExchange testnet setup.
Please set the configuraions in ```config.py``` before runing tests.

```
HX_TESTNET_RPC = 'http://192.168.1.121:30088/'
CDC_CONTRACT_ID = 'HXCSSGDHqaJDLto13BSZpAbrZoJf4RrGCtks'
FEEDER_CONTRACT_ID = 'HXCGba6bUaGeBtUQRGpHUePHVXzF1ygMAxR1'
PRICE_FEEDER = {'account': 'senator0', 'address': 'HXNWj42PcH3Q2gEQ9GnVV2y87qsXd8MCL85W'}
USER1 = {'account': 'da', 'address': 'HXNYM7NT7nbNZPdHjzXf2bkDR53riKxV9kgh'}
```

## Steps to run tests

```
cd tests
pytest
```