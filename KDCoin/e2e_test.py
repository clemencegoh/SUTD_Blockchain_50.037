import requests
import ecdsa
import unittest
import re
from KDCoin import transaction


def extractFromText(_text):
    pattern = re.compile("Public Key: (.*)<br>Private Key: (.*)<br>")
    match = pattern.match(_text)
    # public, private
    return match.group(1), match.group(2)


# these tests have to be run after starting servers
class FullTests(unittest.TestCase):
    def setUp(self):
        self.trustedSession = requests.session()
        self.allArray = self.trustedSession.get("http://localhost:8080").json()["miners_list"]

        self.miner1 = {
            "Session": requests.session(),
            "Pub": "",
            "Priv": "",
            "Address": "http://localhost:8082"
        }
        resp1 = self.miner1["Session"].get(self.miner1["Address"] + "/new")
        self.miner1["Pub"], self.miner1["Priv"] = extractFromText(resp1.text)

        self.miner2 = {
            "Session": requests.session(),
            "Pub": "",
            "Priv": "",
            "Address": "http://localhost:8083"
        }
        resp2 = self.miner2["Session"].get(self.miner2["Address"] + "/new")
        self.miner2["Pub"], self.miner2["Priv"] = extractFromText(resp2.text)

    def test_register(self):
        self.neighbourArray = self.trustedSession.get("http://localhost:8080").json()["miners_list"]
        self.assertNotEqual(self.neighbourArray, [], "list should not be empty now")
        self.assertEqual(len(self.neighbourArray), 2, "Array should contain all miners")
        print(self.neighbourArray)

    def test_newTransaction(self):
        # retrieve private/public key
        t = transaction.Transaction(self.miner1["Pub"], self.miner2["Pub"], 10, "test")
        priv = ecdsa.SigningKey.from_string(bytes.fromhex(self.miner1["Priv"]))
        t.sign(priv)

        # broadcast transaction
        for i in self.allArray:
            print("Sending to:", i)
            self.miner1["Session"].post(i + "/newTx", json={
                "TX": t.to_json()
            })
        sender = t.data["Sender"]
        recv = t.data["Receiver"]
        self.assertEqual(sender, self.miner1["Pub"], "sender is not miner1")
        self.assertEqual(recv, self.miner2["Pub"], "receipent is not miner2")

        # check miner2 tx_list is not empty
        print(self.miner2["Session"].get(self.miner2["Address"] + "/state").text)


if __name__ == '__main__':
    unittest.main()
