from KDCoin import blockChain, block, transaction, spvClient, keyPair
from multiprocessing import Queue
import json
import ecdsa
import requests
import time


# todo: Idea is for every miner to have its own flask app
# Miner's capabilities:
# - contains list of transactions
# - contains Blockchain
# - Ability to add blocks to the chain automatically
#   - Should automatically reward himself if he's the first to find
# - Ability to broadcast new block/ interrupt if broadcast received
# - Keeping track of balance is done either through UTXO or account balance
# - How to verify transaction?
class Hacker:
    def __init__(self, _pub="", _priv="", _blockchain=None):
        # create new miner with fields:
        # _pub and _priv are in hex, convert to object

        self.client = None

        if _pub != "" and _priv != "":
            pub_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(_pub))
            priv_key = ecdsa.SigningKey.from_string(bytes.fromhex(_priv))

            self.client = spvClient.SPVClient(publickey=pub_key, privatekey=priv_key)  # client

        self.blockchain = _blockchain  # current valid blockchain
        self.tx_pool = []  # tx_pool held by miner, in json

    def createNewAccount(self):
        priv, pub = keyPair.GenerateKeyPair()
        self.client = spvClient.SPVClient(privatekey=priv, publickey=pub)
        return priv, pub

    def createRewardTransaction(self, _private_key):
        reward = 100
        t = transaction.Transaction(
            _sender_public_key=self.client.publickey,
            _receiver_public_key=self.client.publickey,
            _amount=reward,
            _comment="Reward transaction",
            _reward=True
        )
        t.sign(_private_key)

        return t

    # call this on interrupt
    def handleBroadcastedBlock(self, _block):
        if _block.validate():  # valid block
            # create if None
            if self.blockchain is None:
                self.blockchain = blockChain.Blockchain(_block)
            else:
                self.blockchain.addBlock(_block, _block.prev_header)
            # use other person's tx pool
            self.tx_pool = _block.state["Tx_pool"]
            return True
        return False

    def mineBlock(self):
        print("Mining...")
        time.sleep(1)
        # wait till tx_pool is not empty
        if self.blockchain is not None:
            while not self.tx_pool:
                time.sleep(1)

        # While there is no new block that is of a longer len than this miner's blockchain, keep mining till completed.
        interruptQueue = Queue(1)
        nonceQueue = Queue(1)
        yield interruptQueue

        # if this is ever invoked, it must be the first block
        # of the first miner
        if self.blockchain is None:
            tx = transaction.Transaction(
                _sender_public_key=self.client.publickey,
                _receiver_public_key=self.client.publickey,
                _comment="Hello world",
                _amount=0,
                _reward=True
            )
            tx.sign(self.client.privatekey)

            first_block = block.Block(
                    _transaction_list=[tx],
                    _difficulty=1,
            )

            p = first_block.build(_found=nonceQueue, _interrupt=interruptQueue)
            p.start()
            p.join()
            nonce_found = nonceQueue.get()
            if nonce_found == "":
                print("interrupted!")
                return

            first_block.completeBlockWithNonce(_nonce=nonce_found)
            first_block.tx_list = [tx.data]
            first_block.executeChange()

            self.blockchain = blockChain.Blockchain(_block=first_block)

        else:
            # validate the transactions
            temp_pool = []

            print("Getting from tx_pool...-->", self.tx_pool)
            print("Current:", self.blockchain.current_block.state)

            while len(self.tx_pool) > 0 and len(temp_pool) <= 10:
                item = self.tx_pool.pop(0)

                # create transaction
                t = transaction.Transaction(
                    item["Sender"],
                    item["Receiver"],
                    item["Amount"],
                    item["Comment"],
                    item["Reward"],
                    item["Signature"]
                )
                temp_pool.append(t)

            temp_pool.append(
                self.createRewardTransaction(self.client.privatekey))

            print("----> TEMP POOL:", temp_pool)
            newBlock = block.Block(
                    _transaction_list=temp_pool,
                    _prev_header=self.blockchain.current_block.header,
                    _prev_block=self.blockchain.current_block,
                    _difficulty=2,
                )

            p = newBlock.build(_found=nonceQueue, _interrupt=interruptQueue)
            p.start()
            p.join()

            nonce_found = nonceQueue.get()
            if nonce_found == "":
                return   # stop here
            newBlock.completeBlockWithNonce(_nonce=nonce_found)
            newBlock.executeChange()
            print("newBlock--->", newBlock.state, newBlock.tx_list)

            self.blockchain.addBlock(
                _incoming_block=newBlock,
                _prev_block_header=newBlock.prev_header
            )

        to_broadcast = self.blockchain.current_block.getData()

        yield to_broadcast

    # takes in the block data, and a list of neighbours to broadcast to
    def broadcastBlock(self, _block_data, _neighbours, _self_addr):
        # broadcasts blocks
        for neighbour in _neighbours:
            if neighbour != _self_addr:
                # broadcast
                try:
                    print("sending block:", _block_data)
                    print("to:", neighbour)
                    requests.post(neighbour + "/newBlock", data=json.dumps({
                        "Block": _block_data
                    }))

                except:  # neighbour no longer present
                    print(neighbour, "no longer present")

    def getAllBlockStates(self):
        state_dict = {}
        count=1
        for block, _ in self.blockchain.block_heads.items():
            state_dict[str(count)] = block.getData()
            count += 1

        return json.dumps(state_dict)




