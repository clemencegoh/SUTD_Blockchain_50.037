from keyPair import GenerateKeyPair
import blockChain, block, transaction, spvClient
from multiprocessing import Queue
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
    def __init__(self, _blockchain=None, _pub="", _priv=""):
        # create new miner with fields:
        # _pub and _priv are in hex, convert to object
        pub_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(_pub))
        priv_key = ecdsa.SigningKey.from_string(bytes.fromhex(_priv))

        self.client = spvClient.SPVClient(publickey=pub_key, privatekey=priv_key)  # client
        self.blockchain = _blockchain  # current valid blockchain
        self.wip_block = None  # to be built
        self.tx_pool = []  # tx_pool held by miner

    # todo: determine amount to give as reward for block
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

        self.broadcastBlock(self.blockchain.current_block.__dict__, _neighbours, _self_addr)  # inform the rest that you have created a block first
        self.tx_pool = self.tx_pool[10:]  # truncate of the first 10 transactions from tx_pool
        yield "Done Mining"

    # takes in the block data, and a list of neighbours to broadcast to
    def broadcastBlock(self, _block_data, _neighbours, _self_addr):
        # broadcasts blocks
        for neighbour in _neighbours:
            if neighbour != _self_addr:
                # broadcast
                try:
                    requests.post(neighbour + "/newBlock", data={
                        "Block": _block_data
                    })
                except:  # neighbour no longer present
                    print(neighbour, "no longer present")





