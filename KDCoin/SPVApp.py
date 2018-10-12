import requests
from KDCoin.spvClient import SPVClient
import json

#Broadcast to this transaction to all miners
#Takes transaction object created by spvClient
#POST REQUEST
def postTransaction(transaction_tobeposted):
    # Validation process here: Check if transaction came from correct sender
    if (transaction_tobeposted.validate()):
        print('got into here')
        json_tobesent = transaction_tobeposted.to_json(transaction_tobeposted.data)
        print(json_tobesent)

        #Send json to server
        t1 = requests.post('http://127.0.0.1:8080/createTransaction',
                       headers = {'Content-Type': 'application/json'},
                       json = json_tobesent)

#Check acc balance of Specified spvClient
def checkBalance(accountpublickey):
    #Check against blockchain of any miner, using accountpublickey
    publickeyinfo = {'publickey_tobechecked': accountpublickey}
    json_tobesent = json.dumps(publickeyinfo)

    requests.get('http://127.0.0.1:8080/clientCheckBalance',
                 headers = {'Content-Type': 'application/json'}, json = json_tobesent)

#Demo
newclient = SPVClient()

# Send Transaction
transaction_tobeposted  = newclient.createTransaction(100,'demo')
postTransaction(transaction_tobeposted)

# Check Balance
# checkBalance(newclient.publickey)












