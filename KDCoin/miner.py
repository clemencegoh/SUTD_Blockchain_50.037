from keyPair import GenerateKeyPair
import blockChain, block, transaction, spvClient
from multiprocessing import Queue
import ecdsa


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

        self.interruptQueue = Queue(1)
        self.nonceQueue = Queue(1)

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

            p = firstBlock.build(_found=self.nonceQueue, _interrupt=self.interruptQueue)
            p.start()

            p.join()
            firstBlock.completeBlockWithNonce(_nonce=self.nonceQueue.get())

            self.blockchain = blockChain.Blockchain(_block=firstBlock)

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


