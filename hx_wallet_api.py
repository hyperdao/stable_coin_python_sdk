import requests
import json
import logging
import base64


class HXWalletApi:
    HTTP_RPC_USER = 'user'
    HTTP_RPC_PASSWORD = 'password'
    HTTP_RPC_URL = 'http://localhost:50321/'

    def __init__(self, name):
        self.name = name

    def rpc_request(self, method, args):
        basic_auth = "Basic " + base64.b64encode("%s:%s" % (HXWalletApi.HTTP_RPC_USER, HXWalletApi.HTTP_RPC_PASSWORD))
        args_j = json.dumps(args)
        payload =  "{\r\n \"id\": 1,\r\n \"method\": \"%s\",\r\n \"params\": %s\r\n}" % (method, args_j)
        headers = {
            'User-Agent': 'Web Client',
            'Content-Type': 'application/json',
            # 'Authorization': basic_auth,
            'cache-control': "no-cache",
        }
        count = 0
        while True:
            try:
                logging.info("payload: %s" % payload)
                response = requests.request("POST", url=HXWalletApi.HTTP_RPC_URL, data=payload, headers=headers)
                try:
                    rep = response.json()
                except Exception as ex:
                    logging.warning("Not json response: %s, %s" % (ex, response.text))
                    return None
                if "result" in rep:
                    logging.warning(" response: %s" % (response.text))
                    return rep
            except Exception as ex:
                print(ex)
                count += 1
                if count > 10:
                    return None


if __name__ == "__main__":
    hxWallet = HXWalletApi('HX')
    hxWallet.rpc_request('info', [])