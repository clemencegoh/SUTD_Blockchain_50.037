import ecdsa
from flask import Flask, request
import requests
import json
import time
from KDCoin import handlers, miner, keyPair, spvClient, block, blockChain, transaction
from multiprocessing import Queue


app = Flask(__name__)


internal_storage = {
    "Public_key": "",  # hex, might want to eventually replace with SPVclient
    "Private_key": "",  # hex
    "Neighbour_nodes": [],  # array of website addresses to make requests to
    "Miner": None,  # Miner Object
}

self_address = "http://localhost:8090"
trusted_server_addr = "http://localhost:8080"
interruptQueue = Queue(1)


def createBlockFromDict(tx_list, block_data):
    return block.Block(
        _transaction_list=tx_list,
        _current_header=block_data['Header'],
        _nonce=block_data["Nonce"],
        _prev_header=block_data['Prev_header'],
        _timestamp=block_data["Timestamp"],
        _merkle_header=block_data["Merkle_header"],
        _difficulty=block_data["Difficulty"],
        _state=block_data["State"]
    )


def createTxFromDict(tx):
    return transaction.Transaction(
        tx["Sender"],
        tx["Receiver"],
        tx["Amount"],
        tx["Comment"],
        tx["Reward"],
        tx["Signature"],
    )


def getNeighbours(_self_addr):
    global internal_storage
    try:
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

    except:
        return False


# not expected to use this
def requestLatestBlock():
    req = requests.get(internal_storage["Neighbour_nodes"][0] + "/block")
    return req.json()


def broadcastTx(_tx):
    global internal_storage
    for i in internal_storage["Neighbour_nodes"]:
        if i != self_address:
            internal_storage["Miner"].client.broadcastTransaction(
                _tx=_tx,
                _address=i + "/newTx",
            )


def createTxWithBroadcast(_recv_pub, _amount, _comment=""):
    tx = internal_storage["Miner"].client.createTransaction(
        _recv_pub, _amount, _comment)
    print("CREATING TX...", tx.data)
    broadcastTx(tx.data)
    internal_storage["Miner"].tx_pool.append(tx.data)

    # debug:
    print("Complete")


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
    global internal_storage, interruptQueue
    pub_hex = request.values.get("pub_key")
    pub_key = pub_hex
    internal_storage["Public_key"] = pub_key

    priv_hex = request.values.get("priv_key")
    priv_key = priv_hex
    internal_storage["Private_key"] = priv_key

    if getNeighbours(self_address):
        # not the first one
        # request latest block as json
        current_block = requestLatestBlock()

        data = json.loads(current_block)
        tx_list = []
        for tx in data['Tx_list']:
            tx_list.append(createTxFromDict(tx))
        # build block
        b = createBlockFromDict(tx_list, data)

        # update state
        bc = blockChain.Blockchain(_block=b)
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
        generator = internal_storage["Miner"].mineBlock()
        try:
            interruptQueue = next(generator)
            block_data = next(generator)
            internal_storage["Miner"].broadcastBlock(
                _block_data=block_data,
                _neighbours=internal_storage["Neighbour_nodes"],
                _self_addr=self_address,
            )
        except StopIteration:
            print("MinerApp Interrupted")

    # re-routes back to homepage
    return homePage()


@app.route('/new')
def newUser():
    global internal_storage, interruptQueue
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

    internal_storage["Miner"] = miner.Miner(_pub=pub_key, _priv=priv_key)

    # announce yourself
    getNeighbours(self_address)
    generator = internal_storage["Miner"].mineBlock()

    try:
        interruptQueue = next(generator)
        block_data = next(generator)
        internal_storage["Miner"].broadcastBlock(
            _block_data=block_data,
            _neighbours=internal_storage["Neighbour_nodes"],
            _self_addr=self_address,
        )
    except StopIteration:
        print("MinerApp New Interrupted")

    return info + newUser


@app.route('/block')
def getCurrentBlock():
    # this API is here for other miners joining in to request the current blockchain
    data = internal_storage["Miner"].blockchain.current_block.getData()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


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
    tx = request.get_json(force=True)["TX"]
    print("Getting:", tx)

    if tx in internal_storage["Miner"].tx_pool:
        # don't do anything
        return ""
    else:
        # add to pool
        internal_storage["Miner"].tx_pool.append(tx)

        # broadcast to the rest
        # broadcastTx(tx)
        return "Transaction received"


# receive new Block from broadcast
@app.route('/newBlock', methods=["POST"])
def newBlock():
    global interruptQueue, internal_storage
    recv_block = request.get_json(force=True)
    print("New block posted to me:", recv_block)
    rb = recv_block["Block"]
    data = rb
    tx_list = []
    for tx in data['Tx_list']:
        tx_list.append(createTxFromDict(tx))
    # create block from data
    b = createBlockFromDict(
        tx_list=tx_list,
        block_data=rb)

    # validate
    if b.validate():

        if internal_storage["Miner"] is None:
            # ignore until done
            return ""

        # interrupt and add block
        interruptQueue.put(1)
        m = internal_storage["Miner"]
        m.handleBroadcastedBlock(b)

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
    while True:
        if len(internal_storage["Miner"].tx_pool) >= 1:
            generator = internal_storage["Miner"].mineBlock()
            try:
                interruptQueue = next(generator)
                # this should be getData() from block obj
                block_data = next(generator)
                block_data["State"]["Tx_pool"] = internal_storage["Miner"].tx_pool
                internal_storage["Miner"].broadcastBlock(
                    _block_data=block_data,
                    _neighbours=internal_storage["Neighbour_nodes"],
                    _self_addr=self_address,
                )
            except StopIteration:
                print("Mining interrupted, MinerApp")
        time.sleep(1)
        print("Continuing to mine...")


@app.route('/state')
def getState():
    state = internal_storage["Miner"].blockchain.current_block.state
    pool = []
    for tx in state["Tx_pool"]:
        pool.append(json.dumps(tx))

    return "Balance: " + json.dumps(state["Balance"]) + "<br>" \
           + "Pool: " + str(pool) + "<br>" \
           + "minerpool: " + str(internal_storage["Miner"].tx_pool)


@app.route('/update')
def updateNeighbours():
    getNeighbours(self_address)
    return homePage()


@app.route('/allStates')
def getAllStates():
    global internal_storage
    return internal_storage["Miner"].getAllBlockStates()


if __name__ == '__main__':
    machine_IP = ""
    if machine_IP == "":
        machine_IP = "localhost"
    app.run(host=machine_IP, port=8090)
