from KDCoin import transaction
import requests
import json


# Single Client
# Functionalities: i) Create Transactions, ii) Verify transactions validated
class SPVClient:
    def __init__(self, privatekey, publickey):
        self.privatekey = privatekey
        self.publickey = publickey

    # Creates transaction and sign with private key
    def createTransaction(self, receiver_public_key, amount, comment):
        transaction_tobemade = transaction.Transaction(
            self.publickey,
            receiver_public_key,
            amount,
            comment)
        transaction_tobemade.sign(self.privatekey)

        return transaction_tobemade

    def broadcastTransaction(self, _tx, _address):
        requests.post(_address,
                     data=json.dumps({
                         "TX": _tx
                     }))

    # Check acc balance of specified spvclient
    def checkBalance(self, _address):
        # get block from miner
        block = None

        response = requests.get(_address + '/block',
                     headers={'Content-Type': 'application/json'})

        # not sure if this is needed
        block = response.json()["Block"]

        balance = block["State"]["Balance"][self.publickey]
        return balance

    def getMiners(self, _trusted_server):
        response = requests.get(_trusted_server)
        return response.json()["miners_list"]

