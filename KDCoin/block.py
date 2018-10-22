import time
import json
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
    def __init__(self, _transaction_list, _prev_header="", _prev_block=None,
                 _difficulty=3, _current_header="", _nonce="", _state=None,
                 _timestamp=str(time.time()), _merkle_header=""):
        # to create
        self.header = _current_header
        self.nonce = _nonce

        # variables included in hash
        self.prev_header = _prev_header  # hash of previous header
        self.timestamp = _timestamp  # timestamp of block
        self.merkle_header = _merkle_header

        # pointers
        self.merkle_tree = None
        self.prev_block = _prev_block

        # static variables
        # transactions used in this block
        # self.tx_list is in json
        self.tx_list = []
        self.txs = []

        # catching wrong inits
        if _state is None:
            if _prev_block is None:
                self.state = {
                    "Balance": {},
                    "Tx_pool": [],
                }
            else:
                self.state = _prev_block.state
        else:
            self.state = _state

        self.difficulty = _difficulty
        # _transaction_list is a transaction object []
        self.filterTxFromPool(_transaction_list)

    def executeChange(self):
        while self.txs:
            tx = self.txs.pop(0)
            self.changeState(tx)

    # filter and verify transaction from the tx_list given
    def filterTxFromPool(self, _transaction_list=[]):
        tx_list = []
        if not _transaction_list:
            print("HIGHLIGHTING ERROR HERE, EMPTY TX LIST")
            return ""
        while _transaction_list:
            tx = _transaction_list.pop(0)
            # invalid transactions will be lost here
            if tx.validate():
                tx_list.append(tx)
            else:
                print("lost:\n", tx)

        for tx in tx_list:
            self.tx_list.append(tx.data)
        print("After filtering:", self.tx_list)
        self.txs = tx_list

        # build merkle tree from transaction list
        self.merkle_tree = createTreeFromTx(tx_list)
        self.merkle_header = self.merkle_tree.root.data["Transaction"]

    # changes state based off transaction
    def changeState(self, _tx):
        sendr_addr = _tx.data["Sender"]
        amount = int(_tx.data["Amount"])

        balance = self.state["Balance"]

        if _tx.data["Reward"]:
            # reward block, immediately award
            self.completeTransaction(_tx, True)

        # cannot send from someone non-existent if not reward
        if sendr_addr not in balance:
            print("WARNING: {} NOT FOUND".format(sendr_addr))
            balance[sendr_addr] = 0
            return False

        # if less than amount
        if balance[sendr_addr] < amount:
            return False

        self.completeTransaction(_tx)
        return True

    # completes transaction, assumes everything is correct
    def completeTransaction(self, _transaction, _reward=False):
        sendr_addr = _transaction.data["Sender"]
        recv_addr = _transaction.data["Receiver"]
        amount = int(_transaction.data["Amount"])

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
                            + self.merkle_header \
                            + self.nonce
        minimum_pow = simpleLOD(self.difficulty)
        # verify proof of work is more than minimum requirement
        # this requires digest <= minimum proof of work
        return minimum_pow >= int(getDigest(validating_string.encode()), 16)

    # Call build after initialising with all the params
    # This should take up the longest time
    # This must be called manually
    def build(self, _found, _interrupt):

        print("Prev header:", self.prev_header)

        first_half = self.prev_header \
                     + str(self.timestamp) \
                     + self.merkle_header

        return Process(target=findPreimage,
                       args=(simpleLOD(self.difficulty), first_half, _found, _interrupt))

    def completeBlockWithNonce(self, _nonce):
        self.nonce = _nonce
        self.header = self.prev_header \
                     + str(self.timestamp) \
                     + self.merkle_header \
                     + self.nonce

    def checkIfTransactionInBlock(self, _transaction):
        return _transaction in self.merkle_tree.leaf_nodes

    def setPrevBlock(self, _block):
        self.prev_block = _block
        self.prev_header = _block.header

    def getData(self):
        final_list = []
        final_pool = []
        for tx_data in self.tx_list:
            final_list.append(tx_data)
        for tx_data in self.state["Tx_pool"]:
            final_pool.append(tx_data)

        final_state = {
            "Balance": self.state["Balance"],
            "Tx_pool": final_pool,
        }

        return {
            "Header": self.header,
            "Nonce": self.nonce,
            "Prev_header": self.prev_header,
            "Timestamp": self.timestamp,
            "Merkle_header": self.merkle_header,
            "Tx_list": final_list,
            "State": final_state,
            "Difficulty": self.difficulty,
        }

