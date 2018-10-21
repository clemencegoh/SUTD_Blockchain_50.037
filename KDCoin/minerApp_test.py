import unittest
import requests
import time
import re
import json
import sys, os
from KDCoin import transaction, keyPair


def extractBalanceFromState(_response_text):
    pattern = re.compile('Balance: (.*)<br>Pool')
    balance = pattern.match(_response_text).group(1)

    # extract data:
    data = json.loads(balance)
    return data


class TestMinerApp(unittest.TestCase):

    def test_single_miner(self):
        # define variables
        miner1_address = "http://localhost:8082"

        # create new miner
        miner1 = requests.session()
        miner1.get(miner1_address + "/new")

        # allow up to 4 seconds to finish
        time.sleep(4)

        response = miner1.get(miner1_address + "/state")
        current_balance = extractBalanceFromState(response.text)

        # verify initial balance is correct
        for k, v in current_balance.items():
            self.assertEqual(v, 100, "Balance should be 100")

        # create transaction
        miner1.post(miner1_address + "/pay?pub_key=clemence")


if __name__ == '__main__':
    unittest.main()