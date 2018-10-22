from KDCoin import SPVApp, spvClient
import requests
import unittest
import json


class SpvTest(unittest.TestCase):
    def test_create_client(self):
        client_addr = "http://localhost:8081"
        client = requests.session()
        client.get(client_addr)
        client.get(client_addr+"/new")
        client.post(client_addr +
                    "/createTransaction?pub_key={}&amount={}&comment={}".
                    format("random_client", 10, "test payment"))


if __name__=='__main__':
    unittest.main()
