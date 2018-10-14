import ecdsa
from flask import Flask, request
import handlers, miner, keyPair, spvClient


app = Flask(__name__)


internal_storage = {
    "Public_key": "",  # hex, might want to eventually replace with SPVclient
    "Private_key": "",  # hex
    "Neighbour_nodes": [],  # array of website addresses to make requests to
    "Miner": miner.Miner(),  # Miner Object
}


@app.route('/')
def homePage():
    if internal_storage["Public_key"] is None:
        welcome = "Please log in:"
    else:
        welcome = "Welcome to KDCoin!<br>" \
               "Statistics:<br><br>" \
               "Currently logged in as: {}<br>" \
               "Neighbour nodes registered: {}<br>" \
               "".format(
            internal_storage["Public_key"],
            internal_storage["Neighbour_nodes"])

    loginPage = open("Mainpage.html").read()

    return welcome + loginPage


@app.route('/login', methods=['POST'])
def loginAPI():
    global internal_storage
    pub_hex = request.values.get("pub_key")
    pub_key = pub_hex #Might want to change it to a key object in the future
    internal_storage["Public_key"] = pub_key

    priv_hex = request.values.get("priv_key")
    priv_key = priv_hex #Might want to change it to a key object in the future
    internal_storage["Private_key"] = priv_key

    internal_storage["Miner"] = miner.Miner(internal_storage["Public_key"], pub_key, priv_key)

    # re-routes back to homepage
    return homePage()


@app.route('/new')
def newUser():
    global internal_storage
    priv, pub = keyPair.GenerateKeyPair()
    internal_storage["Private_key"] = priv.to_string().hex()
    internal_storage["Public_key"] = pub.to_string().hex()

    newUser = open("Newuser.html").read()

    info = "Public Key: {}<br>" \
    "Private Key: {}<br>" \
    "Please save these 2 (They are unrecoverable)".format(
        pub.to_string().hex(),
        priv.to_string().hex()
    )

    return info + newUser


@app.route('/blockchain')
def getCurrentBlockchain():
    # this API is here for other miners joining in to request the current blockchain
    return internal_storage["User"].blockchain


@app.route('/pay/<recv_addr>')
def payTo(recv_addr):
    # todo: handler to pay from sender to recv
    sender = internal_storage["Public_key"]
    recv = recv_addr

    pass


@app.route('/newTransaction')
def newTransaction():
    # todo: new transaction parsing
    pass

# todo: create more routes for miners and users of blockchain


if __name__ == '__main__':
    app.run(port=5000)
