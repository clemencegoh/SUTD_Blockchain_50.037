import ecdsa
from flask import Flask, request
import requests
import json
import time
import handlers, miner, keyPair, spvClient, block, blockChain, transaction
from multiprocessing import Queue


app = Flask(__name__)


internal_storage = {
    "Public_key": "",  # hex, might want to eventually replace with SPVclient
    "Private_key": "",  # hex
    "Neighbour_nodes": [],  # array of website addresses to make requests to
    "Miner": None,  # Miner Object
}

self_address = "http://localhost:8083"
trusted_server_addr = "http://localhost:8080"
interruptQueue = Queue(1)


def getNeighbours(_self_addr):
    global internal_storage
    req = requests.get(trusted_server_addr)
    miner_list = req.json()['miners_list']

    if self_address in miner_list:
        internal_storage["Neighbour_nodes"] = miner_list
        return True

    requests.post(trusted_server_addr + "/add", {
        "miner": self_address
    })
    print("Posted:", {
        "miner": self_address
    })

    req = requests.get(trusted_server_addr)
    miner_list = req.json()['miners_list']
    internal_storage["Neighbour_nodes"] = miner_list

    return False


def requestLatestBlockchain():
    req = requests.get(internal_storage["Neighbour_nodes"][0] + "/blockchain")
    print(req.json())
    return req.json()


def broadcastTx(_tx):
    for i in internal_storage["Neighbour_nodes"]:
        if i != self_address:
            # broadcast
            try:
                requests.post(i + "/newTx", {
                    "TX": _tx.data
                })
            except:
                print(i, "no longer present")
                del i


def createTxWithBroadcast(_recv_pub, _amount, _comment=""):
    tx = internal_storage["Miner"].client.\
        createTransaction(_recv_pub, _amount, _comment)
    broadcastTx(tx)
    internal_storage["Miner"].tx_pool.append(tx)

    # debug:
    print("Complete")
    print(internal_storage["Miner"].tx_pool)


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
        create_block = block.Block( #Is this still needed since in miner class when it init, block is created.
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
        generator = internal_storage["Miner"].mineBlock(
            _neighbours=internal_storage["Neighbour_nodes"],
            _self_addr=self_address
        )
        interruptQueue = next(generator)
        next(generator)

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
    generator = internal_storage["Miner"].mineBlock(
        _neighbours=internal_storage["Neighbour_nodes"],
        _self_addr=self_address
    )
    next(generator)
    next(generator)

    return info + newUser


@app.route('/blockchain')
def getCurrentBlockchain():
    # this API is here for other miners joining in to request the current blockchain
    return internal_storage["User"].blockchain


@app.route('/pay', methods=["GET", "POST"])
def payTo():
    if request.method == "GET":
        current_user_status = \
            "Currently logged in as: {} \n\n<br>".format(
                internal_storage["Public_key"]
            )
        payment_page = open('Payment.html').read()
        return current_user_status + payment_page
    if request.method == "POST":
        pub_key = request.values.get("pub_key")
        amount = request.values.get("amount")
        comment = request.values.get("comment")

        # execute payment method
        createTxWithBroadcast(pub_key, amount, comment)
        return "Transaction Complete"

    return "Invalid method"


# receive new Tx from broadcast
@app.route('/newTx', methods=["POST"])
def newTx():
    tx = request.get_json()["TX"]
    print(tx)
    t = transaction.Transaction(
        _sender_public_key=tx["Sender"],
        _receiver_public_key=tx["Receiver"],
        _amount=tx["Amount"],
        _comment=tx["Comment"],
    )
    t.data["Signature"] = tx["Signature"]

    if t in internal_storage["Miner"].tx_pool:
        # don't do anything
        return ""
    else:
        # add to pool
        internal_storage["Miner"].tx_pool.append(t)

        # broadcast to the rest
        broadcastTx(t)
        return "Transaction received"


# receive new Block from broadcast
@app.route('/newBlock', methods=["POST"])
def newBlock():
    global interruptQueue
    # this is returning None
    recv_block = request.__dict__
    print(recv_block)
    rb = recv_block["Block"]
    # create block from data
    b = block.Block(_transaction_list=rb["tx_list"],
                    _prev_header=rb["prev_header"],
                    _prev_block=rb["prev_block"],
                    _difficulty=rb["difficulty"],
                    _current_header=rb["current_header"],
                    _nonce=rb["nonce"],
                    _state=rb["state"])
    # validate
    if b.validate():
        # interrupt and add block
        interruptQueue.put(1)
        current_chain = internal_storage["Miner"].blockchain
        current_chain.addBlock(
            _prev_block=current_chain.current_block,
            _incoming_block=b
        )

    return ""


@app.route('/mine')
def mineAPI():
    global internal_storage

    if internal_storage["Public_key"] == "":
        return homePage()
    else:
        return miningPage()


@app.route('/mining')
def miningPage():
    global internal_storage, interruptQueue
    # mining = "Currently Mining ...!<br>" \
    #         "Statistics:<br><br>" \
    #         "Currently logged in as: {}<br>" \
    #         "Neighbour nodes registered: {}<br>" \
    #         "".format(
    #     internal_storage["Public_key"],
    #     internal_storage["Neighbour_nodes"])
    # miningPage = open("Mining.html").read()
    while True:
        if len(internal_storage["Miner"].tx_pool) >= 1:
            generator = internal_storage["Miner"].mineBlock(
                _neighbours=internal_storage["Neighbour_nodes"],
                _self_addr=self_address
            )
            interruptQueue = next(generator)
            print(next(generator))
        time.sleep(1)

    # return mining + miningPage


@app.route('/state')
def getState():
    state = internal_storage["Miner"].blockchain.current_block.state
    pool = []
    for tx in state["Tx_pool"]:
        pool.append(tx.to_json())

    return "Balance: " + json.dumps(state["Balance"]) + "<br>" \
           + "Pool" + str(pool) + "<br>" \
           + "Length" + str(state["Blockchain_length"])


@app.route('/update')
def updateNeighbours():
    getNeighbours(self_address)
    return homePage()


if __name__ == '__main__':
    machine_IP = ""
    if machine_IP == "":
        machine_IP = "localhost"
    app.run(host=machine_IP, port=8083)
