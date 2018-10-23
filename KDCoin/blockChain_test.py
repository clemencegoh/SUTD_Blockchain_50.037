import unittest
import time
from multiprocessing import Manager
from KDCoin import transaction, block, blockChain, keyPair


manager = Manager()


def createInitialBlockchain():
    priv, pub = keyPair.GenerateKeyPair()
    t = transaction.Transaction(
        _sender_public_key=pub,
        _receiver_public_key=pub,
        _amount=100,
        _comment="Reward",
        _reward=True
    )
    t.sign(priv)

    b = block.Block([t])
    q_find = manager.Queue()
    q2 = manager.Queue()

    p = b.build(q_find, q2)
    p.start()
    p.join()
    nonce = q_find.get()
    print("Nonce1:", nonce)
    b.completeBlockWithNonce(nonce)
    b.executeChange()

    bc = blockChain.Blockchain(_block=b)
    return priv, pub, b, bc


def createSecondBlock(priv, pub, b):
    q5 = manager.Queue()
    q6 = manager.Queue()

    t2 = transaction.Transaction(
        _sender_public_key=pub,
        _receiver_public_key="Random",
        _amount=10,
        _comment="giving",
    )
    t2.sign(priv)

    t3 = transaction.Transaction(
        _sender_public_key=pub,
        _receiver_public_key=pub,
        _amount=100,
        _comment="Reward for mining",
        _reward=True
    )
    t3.sign(priv)

    b2 = block.Block(
        _transaction_list=[t2, t3],
        _prev_block=b,
        _prev_header=b.header,
        _state=b.state,
    )
    p2 = b2.build(q5, q6)
    p2.start()
    p2.join()

    nonce2 = q5.get()
    print("Nonce2:", nonce2)
    b2.completeBlockWithNonce(nonce2)
    b2.executeChange()

    return b2


def createThirdBlock(priv, pub, b):
    q3 = manager.Queue()
    q4 = manager.Queue()

    t2 = transaction.Transaction(
        _sender_public_key=pub,
        _receiver_public_key="Random",
        _amount=100,
        _comment="giving",
        _reward=True
    )
    t2.sign(priv)

    t3 = transaction.Transaction(
        _sender_public_key=pub,
        _receiver_public_key=pub,
        _amount=100,
        _comment="Reward for mining",
        _reward=True
    )
    t3.sign(priv)

    b2 = block.Block(
        _transaction_list=[t2, t3],
        _prev_block=b,
        _prev_header=b.header,
        _state=b.state,
    )
    p2 = b2.build(q3, q4)
    p2.start()
    p2.join()

    nonce2 = q3.get()
    b2.completeBlockWithNonce(nonce2)
    b2.executeChange()

    return b2


class TestBlockchain(unittest.TestCase):
    def test_create_blockchain_add_block(self):
        priv, pub, b, bc = createInitialBlockchain()

        self.assertTrue(bc.current_block.validate(), "Block cannot be validated")
        self.assertEqual(bc.current_block, b, "Blocks are not the same")
        self.assertEqual(bc.chain_length, 1, "Chain length is supposed to be 1")

        b2 = createSecondBlock(priv, pub, b)
        print("b2 stats:")
        print(b2.header)
        print(b2.state)
        print(b2.nonce)
        bc.addBlock(b2, b.header)

        self.assertEqual(bc.current_block, b2, "Current block is not at b2")
        self.assertTrue(bc.current_block.validate(), "Block 2 cannot be validated")

    def test_resolve_fork(self):
        priv, pub, b, bc = createInitialBlockchain()

        b2 = createSecondBlock(priv, pub, b)
        print("B2:", b2.state)
        bc.addBlock(b2, b.header)

        b3 = createThirdBlock(priv, pub, b2)
        bc.addBlock(b3, b2.header)

        b4_fork = createSecondBlock(priv, pub, b2)
        bc.addBlock(b4_fork, b2.header)

        self.assertTrue(b.validate(), "Validate block 1")
        self.assertTrue(b2.validate(), "Validate block 2")
        self.assertTrue(b3.validate(), "Validate block 3")
        self.assertTrue(b4_fork.validate(), "Validate block 4")
        self.assertEqual(bc.chain_length, 3, "Chain length must be 3")
        self.assertEqual(len(bc.block_heads), 2, "There must be 2 forks")

    def test_add_to_start(self):
        priv, pub, b, bc = createInitialBlockchain()

        b2 = createSecondBlock(priv, pub, b)
        print("B2:", b2.state)
        bc.addBlock(b2, b.header)

        b3 = createThirdBlock(priv, pub, b2)
        bc.addBlock(b3, b2.header)

        # at this point chain length should be 4
        b4 = createSecondBlock(priv, pub, b3)
        bc.addBlock(b4, b3.header)

        # add back to start
        b2_alternate = createThirdBlock(priv, pub, b)
        bc.addBlock(b2_alternate, b.header)

        self.assertTrue(b.validate(), "Validate block 1")
        self.assertTrue(b2.validate(), "Validate block 2")
        self.assertTrue(b3.validate(), "Validate block 3")
        self.assertTrue(b4.validate(), "Validate block 4")
        self.assertTrue(b2_alternate.validate(), "Validate alternate block 2")
        self.assertEqual(bc.chain_length, 4, "Chain length must be 4")
        self.assertEqual(len(bc.block_heads), 2, "There must be 2 forks")


if __name__ == "__main__":
    unittest.main()
