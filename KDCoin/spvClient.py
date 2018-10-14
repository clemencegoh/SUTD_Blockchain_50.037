from transaction import Transaction
from keyPair import GenerateKeyPair
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
        transaction_tobemade = Transaction(self.publickey, receiver_public_key,
                                                   amount, comment, self.privatekey)
        print(transaction_tobemade.data)
        transaction_tobemade.sign(self.privatekey)
        return transaction_tobemade

    # Check acc balance of specified spvclient
    def checkBalance(self, _address):
        # get blockchain from miner
        blockchain = ""

        response = requests.get(_address + '/blockchain',
                     headers={'Content-Type': 'application/json'}, json=blockchain)

        # not sure if this is needed
        blockchain = response.json()

        balance = blockchain["current_block"]["state"]["Balance"][self.publickey]
        return balance

    def getMiners(self, _trusted_server):
        response = requests.get(_trusted_server)
        return response.json()["miners_list"]

# sender_privatekey , sender_publickey = GenerateKeyPair()
# newclient = SPVClient(sender_privatekey , sender_publickey)
# #Send Transaction
# newclient.createTransaction(100,'demo')
# #Check Balance
# newclient.checkBalance()