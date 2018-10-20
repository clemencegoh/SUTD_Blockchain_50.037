import unittest
from KDCoin import block, transaction, keyPair
from multiprocessing import Queue


class TestBlockMethods(unittest.TestCase):
    def test_create_block(self):
        priv, pub = keyPair.GenerateKeyPair()
        t = transaction.Transaction(
            _sender_public_key=pub,
            _receiver_public_key=pub,
            _amount=100,
            _comment="Test Reward",
            _reward=True
        )
        t.sign(priv)

        t2 = transaction.Transaction(
            _sender_public_key=pub,
            _receiver_public_key="random",
            _amount=10,
            _comment="First Payment"
        )
        t2.sign(priv)

        # create Block with single tx
        b = block.Block([t, t2])

        found_q = Queue(1)
        q2 = Queue(1)

        p = b.build(found_q, q2)
        p.start()
        p.join()
        nonce = found_q.get()
        b.completeBlockWithNonce(nonce)

        self.assertEqual(b.nonce, nonce, "Nonce does not match")
        self.assertIsNotNone(b.merkle_tree, "Merkle tree cannot be none")
        self.assertNotEqual(b.tx_list, [], "tx_list should contain tx in block")
        print("tx_list:", b.tx_list)
        print("state:", b.state)

        self.assertEqual(b.state["Tx_pool"], [], "TX pool should be empty")
        self.assertEqual(b.state["Balance"],
                         {pub.to_string().hex(): 90,
                          'random': 10}, "Balance is not properly shown")
        self.assertTrue(b.validate(), "Block cannot be validated")


if __name__ == '__main__':
    unittest.main()