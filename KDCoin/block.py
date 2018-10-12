import time
from KDCoin.merkleNode import MerkleNode
from KDCoin.merkleTree import MerkleTree
from KDCoin.helperFunctions import simpleLOD
from KDCoin.preImage import getDigest, findPreimage
from KDCoin.transaction import Transaction
from KDCoin.keyPair import GenerateKeyPair
from KDCoin.globalState import State
from multiprocessing import Process, Queue


def createTreeFromTx(_transaction_list):

    node = MerkleNode("Leaf", _transaction_list[0])
    tree = MerkleTree(node)

    for i in range(len(_transaction_list)-1):  # start from 1
        tree.add(
            MerkleNode("Leaf", _transaction_list[i+1])
        )

    return tree


##########################
# Assembling a Block:
# Block should be able to be created by specifying a list of transactions
# Only leave _prev and _root empty for genisys block creation
##########################
class Block:
    def __init__(self, _transaction_list, _prev_header=None, _prev_block=None):
        self.prev_header = _prev_header  # hash of previous header
        self.timestamp = str(time.time())  # timestamp of block
        self.merkle_tree = None
        self.tx_list = _transaction_list

        self.prev_block = _prev_block
        self.state = State()
        self.nonce = "default_nonce"
        self.header = "genisys"

        if _prev_header is not None:
            self.nonce = None  # random number needed to generate PoW
            self.prev_header = None  # header has to be created after nonce is found
            # init state from prev
            self.state = State(_prev_block.state)

        tx_list = []
        for tx in _transaction_list:
            # invalid transactions will be lost here

            if self.state.changeState(tx):
                print ('appended')
                tx_list.append(tx)
        print (tx_list)
        # build merkle tree from transaction list
        self.merkle_tree = createTreeFromTx(tx_list)

    # This should be called by miners as the block comes in
    # Validate checks that the nonce is proper
    def validate(self, _LOD):
        validating_string = self.prev_header \
                            + self.timestamp \
                            + self.merkle_tree.root.data["Transaction"] \
                            + self.nonce
        minimum_pow = simpleLOD(_LOD)

        # verify proof of work is more than minimum requirement
        # this requires digest <= minimum proof of work
        return minimum_pow >= int(getDigest(validating_string.encode()), 16)

    # Call build after initialising with all the params
    # This should take up the longest time
    # This must be called manually
    # todo: have a way to interrupt
    def build(self, _LOD, _book):
        first_half = self.prev_header \
                     + str(self.timestamp) \
                     + self.merkle_tree.root.data["Transaction"]

        return Process(target=findPreimage, args=(simpleLOD(_LOD), first_half, _book))

    def setNonce(self, _nonce):
        self.nonce = _nonce
        self.header = self.prev_header \
                     + str(self.timestamp) \
                     + self.merkle_tree.root.data["Transaction"] \
                     + self.nonce

    def setPrevBlock(self, _block):
        self.prev_block = _block

    def checkTransactionInBlock(self, _transaction):
        return _transaction in self.merkle_tree.leaf_nodes


# Test with proper transactions in block
if __name__ == '__main__':
    sender_private_key, sender_public_key = GenerateKeyPair()

    receiver_private_key, receiver_public_key = GenerateKeyPair()

    amount = 10000
    comment = "testRun"
    tx_list = [
        Transaction(sender_public_key, receiver_public_key, amount, comment),
        Transaction(sender_public_key, receiver_public_key, amount, "new one"),
    ]
    b = Block(tx_list)

    channel = Queue(1)  # max size = 1

    level_of_difficulty = 3

    p = b.build(level_of_difficulty, channel)

    p.start()
    p.join()

    nonce_found = channel.get()  # nonce string from process

    # setNonce must be called once a result is found
    b.setNonce(nonce_found)

    # debug messages
    print("Nonce found:", nonce_found)
    print("Current header:", b.header)
    print("Verifying block...", b.validate(level_of_difficulty))
#
