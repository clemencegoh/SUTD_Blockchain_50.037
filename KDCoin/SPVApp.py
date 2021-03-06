import requests
import json
from flask import Flask, request
import spvClient,keyPair


app = Flask(__name__)

miners_list = []
user = None
miner_server = 'http://localhost:8080'


@app.route('/')
def homepage():
    return "This is the homepage of SPV Clients"

@app.route('/new')
def createNew():
    global user, miners_list
    priv, pub = keyPair.GenerateKeyPair()
    user = spvClient.SPVClient(privatekey=priv,
                               publickey=pub)
    miners_list = user.getMiners(miner_server)
    return "Public Key: {}<br>Private Key: {}".format(
        pub.to_string().hex(),
        priv.to_string().hex()
    )


# todo: create endpoint which provides frontend for creation of transaction
@app.route('/login/<pub>/<priv>')
def login(pub, priv):
    # temporary
    global user
    user = spvClient.SPVClient(privatekey=priv, publickey=pub)
    miners_list = user.getMiners(miner_server)
    return homepage()


# When Transaction created, Broadcast to all miners done here
@app.route('/createTransaction', methods=['POST'])
def createTransaction():
    global miners_list
    if user is None:
        return "Please login"

    # Receive data regarding transaction
    pub_key = request.values.get("pub_key")
    amount = request.values.get("amount")
    comment = request.values.get("comment")

    transaction = user.createTransaction(
                    receiver_public_key=pub_key,
                    amount=amount,
                    comment=comment
                    )

    miners_list = user.getMiners(miner_server)

    print("Will broadcast:", transaction.data)

    # broadcast to all known miners
    for miner in miners_list:
        # execute post request to broadcast transaction
        broadcast_endpoint = miner + "/newTx"
        requests.post(
            url=broadcast_endpoint,
            data=json.dumps({
                "TX": transaction.data
            })
        )
    return ""


# Check with any miner on acc balance (Based on public key received)
@app.route('/clientCheckBalance', methods=['GET'])
def clientCheckBalance():
    return user.checkBalance(miners_list[0])


if __name__ == '__main__':
    app.run(port=8081)

