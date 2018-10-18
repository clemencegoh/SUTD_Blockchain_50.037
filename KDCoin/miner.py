from keyPair import GenerateKeyPair
from KDCoin import blockChain, block, transaction, spvClient
from multiprocessing import Queue
import json
import ecdsa
import requests


# todo: Idea is for every miner to have its own flask app
# Miner's capabilities:
# - contains list of transactions
# - contains Blockchain
# - Ability to add blocks to the chain automatically
#   - Should automatically reward himself if he's the first to find
# - Ability to broadcast new block/ interrupt if broadcast received
# - Keeping track of balance is done either through UTXO or account balance
# - How to verify transaction?
class Miner:
    def __init__(self, _pub="", _priv=""):
        # create new miner with fields:
        # _pub and _priv are in hex, convert to object
        pub_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(_pub))
        priv_key = ecdsa.SigningKey.from_string(bytes.fromhex(_priv))

        self.client = spvClient.SPVClient(publickey=pub_key, privatekey=priv_key)  # client
        self.blockchain = None  # current valid blockchain
        self.wip_block = None  # to be built
        self.tx_pool = []  # tx_pool held by miner
        self.chains = {self.blockchain: 0}  # contains dict of chains in case of forks

    # todo: determine amount to give as reward for blockd
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

    def verifyTransaction(self):
        pass

    def sortChain(self, _block, _chain):
        current = _chain.current_block
        count = _chain.chain_length
        while current.prev_block is not None:
            if current.header == _block.prev_header:
                _block.prev_block = current  # set prev block for incoming
                self.chains[blockChain.Blockchain(_block, count)] = count  # create new blockchain
                return 1

            current = current.prev_block
            count -= 1
        return 0

    def handleBroadcastedBlock(self, _block):
        longest_chains = []
        longest_length = 0
        if len(self.chains) == 1:
            # just replace
            self.chains = {blockChain.Blockchain(_block): 1}

        # Find and add to chain
        for chain, _ in self.chains.items():
            if self.sortChain(_block, chain) == 1:
                break

    def mineBlock(self, _neighbours, _self_addr):
        # While there is no new block that is of a longer len than this miner's blockchain, keep mining till completed.
        interruptQueue = Queue(1)
        nonceQueue = Queue(1)
        yield interruptQueue

        # if this is ever invoked, it must be the first block
        # of the first miner
        if self.blockchain is None:
            # create new blockchain with empty data
            # balance = self.blockchain.current_block.state["Balance"]
            # todo: this is left here until implementation of finding block holds
            tx = transaction.Transaction(
                            _sender_public_key=self.client.publickey,
                            _receiver_public_key=self.client.publickey,
                            _amount=100,
                            _comment="Init Tx",
                            _reward=True,
                        )
            tx.sign(self.client.privatekey)
            firstBlock = block.Block(
                    _transaction_list=[tx],
                    _difficulty=1
                )

            p = firstBlock.build(_found=nonceQueue, _interrupt=interruptQueue)
            p.start()

            p.join()
            firstBlock.completeBlockWithNonce(_nonce=nonceQueue.get())

            self.blockchain = blockChain.Blockchain(_block=firstBlock)

        else:
            # validate the transactions
            temp_pool = []
            counter = 0
            while len(temp_pool) < 9:
                if self.tx_pool[counter].validate:
                    temp_pool.append(self.tx_pool[counter])
            newBlock = block.Block(
                    # choose first 10 transactions in tx_pool
                    _transaction_list=temp_pool.append(
                        self.createRewardTransaction(self.client.privatekey)),
                    _prev_header=self.blockchain.current_block.header,
                    _difficulty=1
                )

            p = newBlock.build(_found=nonceQueue, _interrupt=interruptQueue)
            p.start()

            p.join()
            newBlock.completeBlockWithNonce(_nonce=nonceQueue.get())
            self.blockchain.addBlock(_incoming_block=newBlock)

        to_broadcast = self.blockchain.current_block.getData()
        print("Trying to broadcast this data:\n", to_broadcast)

        self.broadcastBlock(to_broadcast, _neighbours, _self_addr)  # inform the rest that you have created a block first
        self.tx_pool = self.tx_pool[10:]  # truncate of the first 10 transactions from tx_pool
        self.handleBroadcastedBlock(self.blockchain.current_block)
        yield "Done Mining"

    # takes in the block data, and a list of neighbours to broadcast to
    def broadcastBlock(self, _block_data, _neighbours, _self_addr):
        # broadcasts blocks
        for neighbour in _neighbours:
            if neighbour != _self_addr:
                # broadcast
                # try:
                # successful
                print("sending block:", _block_data)
                print("to:", neighbour)
                requests.post(neighbour + "/newBlock", data=json.dumps({
                    "Block": _block_data
                }))

                # except:  # neighbour no longer present
                #     print(neighbour, "no longer present")





