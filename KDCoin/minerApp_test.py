import unittest
import requests
import time
import json
from KDCoin import transaction, keyPair


class TestMinerApp(unittest.TestCase):
    address = "http://localhost:8082"

    def test_add_block(self):
        # create new miner
        print("calling...")
        s = requests.session()
        s.get(self.address + "/new")

        time.sleep(5)  # let the miner build the block

        priv, pub = keyPair.GenerateKeyPair()
        # create new transaction
        t = transaction.Transaction(pub, pub,
                                    10, _comment="Reward",
                                    _reward=True)
        t.sign(priv)
        print("Trying to send:", t.data)

        s.post(self.address + "/newTx",
                      data=json.dumps({
                          "TX": t.data
                      }))

        # check state
        req = s.get(self.address + "/state")
        print(req.text)


if __name__ == '__main__':
    unittest.main()