import unittest
from multiprocessing import Queue
from KDCoin.blockChain import Blockchain
from KDCoin.block import Block
from KDCoin.keyPair import GenerateKeyPair
from KDCoin.transaction import Transaction


class TestBlockchain(unittest.TestCase):
    def test_SimpleE2E(self):
        # create parties
        sender_priv, sender_pub = GenerateKeyPair()
        recv_priv, recv_pub = GenerateKeyPair()
        difficulty = 1

        # init with 20 coins each
        tx0 = Transaction(
            sender_pub,
            sender_pub,
            20,
            "First transaction",
            sender_priv,
            True
        )
        tx1 = Transaction(
            recv_pub,
            recv_pub,
            10,
            "First transaction",
            recv_priv,
            True
        )
        tx2 = Transaction(
            sender_pub,
            recv_pub,
            10,
            "Sending money",
            sender_priv
        )
        tx3 = Transaction(
            recv_pub,
            sender_pub,
            5,
            "Return Transaction",
            recv_priv
        )

        tx_list = [tx0, tx1, tx2, tx3]

        # create block from tx_list
        # this should be the longest step
        b = Block(tx_list, _difficulty=difficulty)
        q = Queue(1)
        interrupt = Queue(1)

        process = b.build(q, interrupt)
        process.start()

        # wait for block to finish building
        process.join()

        # finish building block
        b.completeBlockWithNonce(q.get())

        # NEW BLOCK
        bc = Blockchain(b)

        prev_block = b
        for i in range(3):
            b1 = Block(_transaction_list=tx_list,
                       _prev_block=prev_block,
                       _prev_header=prev_block.header)

            process = b1.build(q, interrupt)
            process.start()

            process.join()

            b1.completeBlockWithNonce(q.get())

            bc.addBlock(_incoming_block=b1, _prev_block=prev_block)

            prev_block = b1

        # verify
        res = bc.validate()

        self.assertEqual(
            bc.checkChainLength(bc.current_block),
            4,
            "Chain length is not 4"
        )

        self.assertTrue(res, "Validation is not True")


if __name__ == "__main__":
    unittest.main()
