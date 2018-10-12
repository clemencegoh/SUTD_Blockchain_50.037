import requests
import json
from flask import Flask, request


app = Flask(__name__)

miners_list = []

#When Transaction created, Broadcast to all miners done here
@app.route('/createTransaction', methods = ['POST'])
def createTransaction():

    if request.headers['Content-Type'] == 'application/json':
        #Receive data regarding transaction
        json_received = request.json
        transaction_data = json.loads(json_received)
        print(transaction_data)

        #Now redundant because cannot recreate transaction object
        sender_publickey = transaction_data['Sender']
        receiver_publickey = transaction_data['Receiver']
        amount = transaction_data['Amount']
        comment = transaction_data['Comment']

        #Update Miners list before appending
        json_miners_list = json.loads(updateMinerList())
        miners_list = json_miners_list('json_miners_list')

        #Here is broadcasting
        #Note that DICT is being appended to miners' tx_list
        for miner in miners_list:
            miner.tx_list.append(transaction_data)

        return 'succesfully broadcasted transaction'

    else:
        return 'wrong format of transaction sent'

#Check with any miner on acc balance (Based on public key received)
@app.route('/clientCheckBalance', methods = ['GET'])
def clientCheckBalance():

    if request.headers['Content-Type'] == 'application/json':
        json_received = request.json
        publickey_data = json.loads(json_received)
        publickey_tobechecked = publickey_data['publickey_tobechecked']

        #Update Miners list before checking with it
        updateMinerList()

        #Check with any miner, request for blockchain state
        blockchain_state = miners_list[0].blockchain.state
        clientbalance = blockchain_state[publickey_tobechecked]

        print ('client balance retrieved = ' + str(clientbalance))
        return clientbalance

    else:
        return 'wrong format of transaction sent'


def updateMinerList():
    miners_list = requests.get('http://127.0.0.1:8080/updateSPVMinerList')
    return miners_list








if __name__ == '__main__':
    app.run(port=8081)
    print(updateMinerList())
