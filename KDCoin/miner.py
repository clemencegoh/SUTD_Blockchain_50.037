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
        # todo: SPV_client
        # _pub and _priv are in hex, convert to object
        pub_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(_pub))
        priv_key = ecdsa.SigningKey.from_string(bytes.fromhex(_priv))

        self.client = spvClient.SPVClient(publickey=pub_key, privatekey=priv_key)  # client
        self.blockchain = _blockchain  # current valid blockchain
        self.wip_block = None  # to be built
        self.tx_pool = []  # tx_pool held by miner

        mineBlock()


    def broadcastBlock(self, _type, _data):
        # broadcasts blocks
        pass

    # todo: determine amount to give as reward for block
    def createRewardTransaction(self, _private_key):
        reward = 100
        t = transaction.Transaction(
            _sender_public_key=self.address,
            _receiver_public_key=self.address,
            _amount=reward,
            _comment="Reward transaction",
            _private=_private_key,
            _reward=True
        )

        return t

    def verifyTransaction():
        pass

    def mineBlock()
        #While there is no new block that is of a longer len than this miner's blockchain, keep mining till completed.
        interruptQueue = Queue(1)
        nonceQueue = Queue(1)
        yield interruptQueue

        # if this is ever invoked, it must be the first block
        # of the first miner
        if self.blockchain is None:
            # create new blockchain with empty data
            # balance = self.blockchain.current_block.state["Balance"]
            # todo: this is left here until implementation of finding block holds
            firstBlock = block.Block(
                    _transaction_list=[
                        # initial empty transaction
                        transaction.Transaction(
                            _sender_public_key=self.client.publickey,
                            _receiver_public_key=self.client.publickey,
                            _amount=0,
                            _comment="Init Tx",
                            _private=self.client.privatekey,
                            _reward=True,
                        )
                    ],
                    _difficulty=1
                )

            p = firstBlock.build(_found=nonceQueue, _interrupt=interruptQueue)
            p.start()

            p.join()
            firstBlock.completeBlockWithNonce(_nonce=nonceQueue.get())

            self.blockchain = blockChain.Blockchain(_block=firstBlock)

        else:
            #validate the transactions
            temp_pool = []
            counter = 0
            while temp_pool.len() < 9:
                if tx_pool[counter].validate == True:
                    temp_pool.append(tx_pool[counter])
            newBlock = block.Block(
                    _transaction_list=
                        # choose first 10 transactions in tx_pool
                        self.tx_pool[:10].append(createRewardTransaction(self.client.privatekey)),
                    _prev_header=self.blockchain.current_block.header,
                    _difficulty=1
                )

            p = newBlock.build(_found=nonceQueue, _interrupt=interruptQueue)
            p.start()

            p.join()
            newBlock.completeBlockWithNonce(_nonce=nonceQueue.get())
            self.blockchain.addBlock(_incoming_block=newBlock)

        broadcastBlock(self.blockchain.current_block) #inform the rest that you have created a block first 
        #truncate of the first 10 transactions from tx_pool

    # takes in the block data, and a list of neighbours to broadcast to
    def broadcastBlock(self, _block_data, _neighbours, _self_addr):
        # broadcasts blocks
        for neighbour in _neighbours:
            if neighbour != _self_addr:
                # broadcast
                requests.post(neighbour + "/newBlock", {
                    "Block": _block_data
                })

    def createRewardTransaction(self, _private_key):
        reward = 100
        t = transaction.Transaction(
            _sender_public_key=self.client.publickey,
            _receiver_public_key=self.client.publickey,
            _amount=reward,
            _comment="Reward transaction",
            _private=_private_key,
            _reward=True
        )
        return t



