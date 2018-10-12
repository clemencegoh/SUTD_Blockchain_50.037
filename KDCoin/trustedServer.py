from flask import Flask, request
import json
from KDCoin.transaction import Transaction

app = Flask(__name__)

miners_list = []


@app.route('/')
def setupServer():
    return str(miners_list)


@app.route('/add/<miner>')
def addNewMiner(miner):
    global miners_list
    if miner not in miners_list:
        miners_list.append(miner)
    return setupServer()

#When Transaction created, Broadcast to all miners done here
@app.route('/createTransaction', methods = ['POST'])
def createTransaction():

    if request.headers['Content-Type'] == 'application/json':
        #Receive data regarding transaction
        json_received = request.json
        transaction_data = json.loads(json_received)

        #Now redundant because cannot recreate transaction object
        sender_publickey = transaction_data['Sender']
        receiver_publickey = transaction_data['Receiver']
        amount = transaction_data['Amount']
        comment = transaction_data['Comment']


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

        #Check with any miner, request for blockchain state
        blockchain_state = miners_list[0].blockchain.state
        clientbalance = blockchain_state[publickey_tobechecked]

        print ('client balance retrieved = ' + str(clientbalance))
        return clientbalance

    else:
        return 'wrong format of transaction sent'


if __name__ == '__main__':
    app.run(port=8080)
