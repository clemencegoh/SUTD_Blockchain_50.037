from keyPair import GenerateKeyPair
import blockChain, block, transaction, spvClient


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
        self.client = spvClient.SPVClient(_pub, _priv)  # client
        self.blockchain = _blockchain  # current valid blockchain
        self.wip_block = None  # to be built
        self.tx_pool = []  # tx_pool held by miner

        # if this is ever invoked, it must be the first block
        # of the first miner
        if self.blockchain is None:
            # create new blockchain with empty data
            # balance = self.blockchain.current_block.state["Balance"]

            self.blockchain = blockChain.Blockchain(
                block.Block(
                    _transaction_list=[
                        # initial empty transaction
                        transaction.Transaction(
                            _sender_public_key=self.client.pub_key,
                            _receiver_public_key=self.client.pub_key,
                            _amount=0,
                            _comment="Init Tx",
                            _private=self.client.priv_key,
                            _reward=False,
                        )
                    ]
                )
            )



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


if __name__ == '__main__':
    pass
