# encoding: utf-8

import requests
import json
import logging
import base64


class HXWalletApi:
    def __init__(self, name, rpc_user='user', rpc_password='password', rpc_url='http://localhost:50321/'):
        self.name = name
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.rpc_url = rpc_url

    def rpc_request(self, method, args):
        auth_str = "%s:%s" % (self.rpc_user, self.rpc_password)
        basic_auth = "Basic " + str(base64.b64encode(auth_str.encode('utf-8')))
        args_j = json.dumps(args)
        payload =  "{\r\n \"id\": 1,\r\n \"method\": \"%s\",\r\n \"params\": %s\r\n}" % (method, args_j)
        headers = {
            'User-Agent': 'Web Client',
            'Content-Type': 'application/json',
            'Authorization': basic_auth,
            'cache-control': "no-cache",
        }
        count = 0
        while True:
            try:
                logging.debug("payload: %s" % payload)
                response = requests.request("POST", url=self.rpc_url, data=payload, headers=headers)
                try:
                    rep = response.json()
                except Exception as ex:
                    logging.warning("Not json response: %s, %s" % (ex, response.text))
                    return None
                logging.debug("response: %s" % (response.text))
                if "result" in rep:
                    return rep['result']
                else:
                    return None
            except Exception as ex:
                print(ex)
                count += 1
                if count > 10:
                    return None


if __name__ == "__main__":
    hxWallet = HXWalletApi('HX')
    hxWallet.rpc_request('info', [])