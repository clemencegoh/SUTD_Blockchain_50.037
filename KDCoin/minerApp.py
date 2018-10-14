import ecdsa
from flask import Flask, request
from KDCoin import handlers, miner, keyPair, spvClient, blockChain, block
import requests


app = Flask(__name__)


internal_storage = {
    "Public_key": "",  # hex, might want to eventually replace with SPVclient
    "Private_key": "",  # hex
    "Neighbour_nodes": [],  # array of website addresses to make requests to
    "Miner": None,  # Miner Object
}

self_address = "http://localhost:8082"
trusted_server_addr = "http://localhost:8080"


def getNeighbours(_self_addr):
    global internal_storage
    req = requests.get(trusted_server_addr)
    miner_list = req.json()['miners_list']
    if miner_list:
        internal_storage["Neighbour_nodes"] = miner_list
        return True

    requests.post(trusted_server_addr + "/add", {
        "miner": self_address
    })

    return False


def requestLatestBlockchain():
    req = requests.get(internal_storage["Neighbour_nodes"][0] + "/blockchain")
    print(req.json())
    return req.json()


@app.route('/')
def homePage():
    if internal_storage["Public_key"] == "":
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

    if getNeighbours(self_address):
        # not the first one
        # request latest block
        current_blockchain = requestLatestBlockchain()
        current_block = current_blockchain['current_block']

        # update state
        create_block = block.Block(
            _transaction_list=current_block['tx_list'],
            _prev_header=current_block['prev_header'],
            _prev_block=None,
            _current_header=current_block['current_header'],
            _nonce=current_block['nonce'],
            _difficulty=current_block['difficulty'],
        )
        bc = blockChain.Blockchain(_block=create_block)
        internal_storage["Miner"] = miner.Miner(
            _blockchain=bc,
            _pub=pub_key,
            _priv=priv_key
        )

    else:
        # create first block
        internal_storage["Miner"] = miner.Miner(_blockchain=None,
                                                _pub=pub_key,
                                                _priv=priv_key)

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

    pub_key = internal_storage["Public_key"]
    priv_key = internal_storage["Private_key"]

    internal_storage["Miner"] = miner.Miner(_blockchain=None, _pub=pub_key, _priv=priv_key)

    # announce yourself
    getNeighbours(self_address)

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
    app.run(port=8082)