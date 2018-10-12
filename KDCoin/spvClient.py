from KDCoin.transaction import Transaction
from KDCoin.keyPair import GenerateKeyPair
import requests
import json

# Single Client
# Functionalities: i) Create Transactions, ii) Verify transactions validated

receiver_private_key, receiver_public_key = GenerateKeyPair()

class SPVClient:

    def __init__(self, privatekey, publickey):
        self.privatekey = privatekey
        self.publickey = publickey


#Creates transaction and sign with private key
    def createTransaction(self, amount, comment):
        transaction_tobemade = Transaction(self.publickey, receiver_public_key,
                                                   amount, comment, self.privatekey)
        print(transaction_tobemade.data)
        transaction_tobemade.sign(self.privatekey)

        if (transaction_tobemade.validate()):
            print('got into here')

        # json_tobesent = transaction_tobemade.to_json(transaction_tobemade.data)
            json_tobesent = transaction_tobemade.__str__()

            #Send json to server
            t1 = requests.post('http://127.0.0.1:8081/createTransaction',
                               headers = {'Content-Type': 'application/json'},
                               json = json_tobesent)
            return True
        else:
            return False

#Check acc balance of specified spvclient
    def checkBalance(self):
        #Object type 'VerifyingKey' is not JSON serializable
        publickeyinfo = {'publickey_tobechecked': str(self.publickey)}
        json_tobesent = json.dumps(publickeyinfo)

        requests.get('http://127.0.0.1:8081/clientCheckBalance',
                     headers = {'Content-Type': 'application/json'}, json = json_tobesent)

sender_privatekey , sender_publickey = GenerateKeyPair()
newclient = SPVClient(sender_privatekey , sender_publickey)
#Send Transaction
newclient.createTransaction(100,'demo')
#Check Balance
newclient.checkBalance()