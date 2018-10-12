import time
from merkleNode import MerkleNode
from merkleTree import MerkleTree
from helperFunctions import simpleLOD
from preImage import getDigest, findPreimage
from transaction import Transaction
from keyPair import GenerateKeyPair
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
# Only leave _prev empty for genisys block creation
##########################
class Block:
    def __init__(self, _transaction_list, _prev_header="", _prev_block=None, _difficulty=3):
        # to create
        self.header = ""
        self.nonce = ""

        # variables included in hash
        self.prev_header = _prev_header  # hash of previous header
        self.timestamp = str(time.time())  # timestamp of block
        self.merkle_root = None

        # pointers
        self.merkle_tree = None
        self.prev_block = _prev_block

        # static variables
        self.tx_list = _transaction_list  # transactions verified within this block
        self.state = {
            "Balance": {},
            "Tx_pool": [],
            "Blockchain_length": 0
        }
        self.difficulty = _difficulty

        if _prev_header is not None:
            self.nonce = None  # random number needed to generate PoW
            self.prev_header = _prev_header  # header has to be created after nonce is found

        if _prev_block is not None:
            # init state from prev
            self.state["Balance"] = _prev_block.state["Balance"]
            self.state["Blockchain_length"] = _prev_block.state["Blockchain_length"]

        self.filterTxFromPool(_transaction_list)

    # filter and verify transaction from the tx_list given
    def filterTxFromPool(self, _transaction_list):
        tx_list = []
        for tx in _transaction_list:
            # invalid transactions will be lost here
<<<<<<< HEAD

            if self.state.changeState(tx):
                print ('appended')
=======
            if self.changeState(tx):
>>>>>>> master
                tx_list.append(tx)
        print (tx_list)
        # build merkle tree from transaction list
        self.merkle_tree = createTreeFromTx(tx_list)
        self.merkle_root = self.merkle_tree.root

    # changes state based off transaction
    def changeState(self, _tx):
        sendr_addr = _tx.data["Receiver"]
        amount = _tx.data["Amount"]

        balance = self.state["Balance"]

        if _tx.data["Reward"]:
            # reward block, immediately award
            self.completeTransaction(_tx, True)

        # cannot send from someone non-existent if not reward
        if sendr_addr not in balance:
            return False

        # if less than amount
        if balance[sendr_addr] < amount:
            return False

        self.completeTransaction(_tx)
        return True

    # completes transaction, assumes everything is correct
    def completeTransaction(self, _transaction, _reward=False):
        sendr_addr = _transaction.data["Receiver"]
        recv_addr = _transaction.data["Receiver"]
        amount = _transaction.data["Amount"]

        balance = self.state["Balance"]

        if not _reward:
            balance[sendr_addr] -= amount

        if recv_addr not in balance:
            balance[recv_addr] = 0
        balance[recv_addr] += amount

    # This should be called by miners as the block comes in
    # Validate checks that the nonce is proper
    def validate(self):
        validating_string = self.prev_header \
                            + self.timestamp \
                            + self.merkle_root.data["Transaction"] \
                            + self.nonce
        minimum_pow = simpleLOD(self.difficulty)

        # verify proof of work is more than minimum requirement
        # this requires digest <= minimum proof of work
        return minimum_pow >= int(getDigest(validating_string.encode()), 16)

    # Call build after initialising with all the params
    # This should take up the longest time
    # This must be called manually
    def build(self, _found, _interrupt):

        first_half = self.prev_header \
                     + str(self.timestamp) \
                     + self.merkle_root.data["Transaction"]

        return Process(target=findPreimage,
                       args=(simpleLOD(self.difficulty), first_half, _found, _interrupt))

    def completeBlockWithNonce(self, _nonce):
        self.nonce = _nonce
        self.header = self.prev_header \
                     + str(self.timestamp) \
                     + self.merkle_root.data["Transaction"] \
                     + self.nonce

    def checkIfTransactionInBlock(self, _transaction):
        return _transaction in self.merkle_tree.leaf_nodes

    def setPrevBlock(self, _block):
        self.prev_block = _block

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
