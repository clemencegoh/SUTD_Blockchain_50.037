import requests
import json
from KDCoin.keyPair import GenerateKeyPair
from flask import Flask, request

from KDCoin.spvClient import SPVClient


app = Flask(__name__)

miners_list = []
user = None
miner_server = 'http://127.0.0.1:8080'

internal_storage = {
    "Public_key": "",  # hex, might want to eventually replace with SPVclient
    "Private_key": "",  # hex
    "Neighbour_nodes": [],  # array of website addresses to make requests to
    # "SPV_Client": SPVClient(),  # Miner Object
}

@app.route('/')
def homepage():
    if internal_storage["Public_key"] =="":
        welcome = "Please log in:"
        loginPage = open("SPVAppLogin.html").read()
        return welcome + loginPage

    else:
        welcome = "Welcome to KDCoin!<br>" \
                  "Statistics:<br><br>" \
                  "Currently logged in as: {}<br>" \
                  "Neighbour nodes registered: {}<br>" \
                  "".format(
            internal_storage["Public_key"],
            internal_storage["Neighbour_nodes"])
        successfulloginpage = open("SPVAppSuccessfulLogin.html").read()
        return welcome + successfulloginpage

@app.route('/new')
def newUser():
    global internal_storage
    priv, pub = GenerateKeyPair()
    internal_storage["Private_key"] = priv.to_string().hex()
    internal_storage["Public_key"] = pub.to_string().hex()

    newUser = open("SPVNewuser.html").read()

    info = "Public Key: {}<br>" \
           "Private Key: {}<br>" \
           "Please save these 2 (They are unrecoverable)".format(
        pub.to_string().hex(),
        priv.to_string().hex()
    )
    global user
    user = SPVClient(priv,pub)

    return info + newUser

#No Verification of Login done here
@app.route('/login', methods = ['POST'])
def login():
    print('Got into here')
    # temporary
    pub = request.values.get("pub_key")
    priv = request.values.get("priv_key")
    global user
    user = SPVClient(privatekey=priv, publickey=pub)

    #Straight redirect to createTransaction page
    createTransactionPage = open("SPVAppCreateTransaction.html").read()
    return createTransactionPage


# When Transaction created, Broadcast to all miners done here
@app.route('/createTransaction', methods=['GET','POST'])
def createTransaction():
    if user is None:
        return "Please login"

<<<<<<< HEAD
    if (request.method == 'GET'):
        createTransactionPage = open("SPVAppCreateTransaction.html").read()
        return createTransactionPage

    elif(request.method == 'POST'):
        Receiver_PublicKey = request.values.get('Receiver_PublicKey')
        Amount = request.values.get("Amount")
        Comment = request.values.get("Comment")

    #From previous version (No user front end)
    # if request.headers['Content-Type'] == 'application/json':
    #     #Receive data regarding transaction
    #     json_received = request.json
    #     transaction_data = json.loads(json_received)
    #     print(transaction_data)
=======
    if request.headers['Content-Type'] == 'application/json':
        #Receive data regarding transaction
        json_received = request.json()
        transaction_data = json.loads(json_received)
        print(transaction_data)
>>>>>>> 05c343effb78ecb93ed517e28b3831adc6db0503

        transaction = user.createTransaction(
                        receiver_public_key=Receiver_PublicKey,
                        amount=Amount,
                        comment=Comment
                        )

        miners_list = user.getMiners(miner_server)

        # broadcast to all known miners
        for miner in miners_list:
<<<<<<< HEAD
             # execute post request to broadcast transaction
            broadcast_endpoint = miner + "/newTransaction"
=======
            # execute post request to broadcast transaction
            broadcast_endpoint = miner + "/newTx"
>>>>>>> 05c343effb78ecb93ed517e28b3831adc6db0503
            requests.post(
                url=broadcast_endpoint,
                data=json.dumps({
                    "TX": transaction.data
                })
            )
<<<<<<< HEAD
        info = "Transaction Successfully sent to Miners <br>"
        createTransactionPage = open("SPVAppCreateTransaction.html").read()
        return info + createTransactionPage

    #
    # else:
    #     return 'wrong format of transaction sent'
=======
    else:
        return 'wrong format of transaction sent'
>>>>>>> 05c343effb78ecb93ed517e28b3831adc6db0503


# Check with any miner on acc balance (Based on public key received)
@app.route('/clientCheckBalance', methods=['GET'])
def clientCheckBalance():
    balance = user.checkBalance(miners_list[0])
    clientCheckBalancePage = open("SPVAppCheckBalance.html").read()
    balanceinfo = "<p>" +  balance + "</p>"

    return clientCheckBalancePage + balanceinfo


if __name__ == '__main__':
    app.run(port=8081)

