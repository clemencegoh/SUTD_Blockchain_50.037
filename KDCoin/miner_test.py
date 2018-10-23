import unittest
import miner, minerApp, transaction, block, blockChain
from multiprocessing import Queue


def createTxFromDict(tx):
    return transaction.Transaction(
        tx["Sender"],
        tx["Receiver"],
        tx["Amount"],
        tx["Comment"],
        tx["Reward"],
        tx["Signature"],
    )


def createBlockFromDict(tx_list, block_data):
    return block.Block(
        _transaction_list=tx_list,
        _current_header=block_data['Header'],
        _nonce=block_data["Nonce"],
        _prev_header=block_data['Prev_header'],
        _timestamp=block_data["Timestamp"],
        _merkle_header=block_data["Merkle_header"],
        _difficulty=block_data["Difficulty"],
        _state=block_data["State"]
    )


def createMiner():
    m = miner.Miner()
    priv, pub = m.createNewAccount()

    return m, priv, pub


class TestMiner(unittest.TestCase):
    def test_simple_create(self):
        m, priv, pub = createMiner()

        self.assertIsNotNone(m.client)
        self.assertEqual(priv,
                         m.client.privatekey,
                         "Priv key object must be the same")
        self.assertEqual(pub,
                         m.client.publickey,
                         "Public key object must be the same")

    def test_create_first_block(self):
        m, priv, pub = createMiner()
        self.assertIsNone(m.blockchain, "At this point, it should be none")
        generator = m.mineBlock()  # mine first, create reward
        interrupt = next(generator)
        block_data = next(generator)

        # create a block from data
        tx_list = []
        for tx in block_data['Tx_list']:
            tx_list.append(createTxFromDict(tx))

        b = createBlockFromDict(tx_list, block_data)

        self.assertEqual(m.blockchain.chain_length, 1, "chain length should be 1")
        self.assertEqual(b.getData(), block_data, "Block data do not match")
        self.assertEqual(len(b.tx_list), 1, "Single reward only")
        print(m.blockchain.current_block.state)

    def test_multiple_blocks(self):
        m, priv, pub = createMiner()
        self.assertIsNone(m.blockchain, "At this point, it should be none")
        generator = m.mineBlock()  # mine first, create reward
        interrupt = next(generator)
        block_data = next(generator)

        # create a block from data
        tx_list = []
        for tx in block_data['Tx_list']:
            tx_list.append(createTxFromDict(tx))

        b = createBlockFromDict(tx_list, block_data)

        self.assertEqual(m.blockchain.chain_length, 1, "chain length should be 1")
        self.assertEqual(b.getData(), block_data, "Block data do not match")
        self.assertEqual(len(b.tx_list), 1, "Single reward only")
        print(m.blockchain.current_block.state)

        r_tx = m.client.createTransaction(
            receiver_public_key="random",
            amount=10,
            comment="tx2")
        m.tx_pool.append(r_tx.data)

        generator = m.mineBlock()
        interrupt = next(generator)
        block_data = next(generator)

        tx_list = []
        for tx in block_data['Tx_list']:
            tx_list.append(createTxFromDict(tx))

        b = createBlockFromDict(tx_list, block_data)
        self.assertEqual(m.blockchain.chain_length, 2, "Chain length did not increase")
        self.assertEqual(m.blockchain.current_block.getData(), b.getData())

        print(m.blockchain.current_block.state)

    def test_build_with_interrupt(self):
        m, priv, pub = createMiner()
        self.assertIsNone(m.blockchain, "At this point, it should be none")
        generator = m.mineBlock()  # mine first, create reward
        interrupt = next(generator)
        block_data = next(generator)

        # create a block from data
        tx_list = []
        for tx in block_data['Tx_list']:
            tx_list.append(createTxFromDict(tx))

        b = createBlockFromDict(tx_list, block_data)

        self.assertEqual(m.blockchain.chain_length, 1, "chain length should be 1")
        self.assertEqual(b.getData(), block_data, "Block data do not match")
        self.assertEqual(len(b.tx_list), 1, "Single reward only")
        print("Initial state:", m.blockchain.current_block.state)

        # build block
        prev_header = m.blockchain.current_block.header
        t2 = transaction.Transaction(
            _sender_public_key=pub,
            _receiver_public_key=pub,
            _amount=20,
            _comment="T2",
            _reward=True,
        )
        t2.sign(priv)

        b2 = block.Block(
            _transaction_list=[t2],
            _prev_header=prev_header,
            _prev_block=m.blockchain.current_block,
        )
        q1 = Queue()
        q2 = Queue()
        p = b2.build(q1, q2)
        p.start()
        p.join()
        b2.completeBlockWithNonce(q1.get())  # completed block
        b2.executeChange()

        print("Block 2 state:", b2.state)

        r_tx = m.client.createTransaction(
            receiver_public_key="random",
            amount=10,
            comment="tx2")
        m.tx_pool.append(r_tx.data)

        generator = m.mineBlock()
        try:
            interrupt = next(generator)
            interrupt.put(1)
            block_data = next(generator)
            self.fail("Should not reach here")
        except StopIteration:
            print("This should happen")
            m.handleBroadcastedBlock(b2)

        tx_list = []
        for tx in block_data['Tx_list']:
            tx_list.append(createTxFromDict(tx))

        b = createBlockFromDict(tx_list, block_data)
        print(m.blockchain.chain_length)
        self.assertEqual(m.blockchain.chain_length, 2, "Chain length did not increase")
        self.assertNotEqual(m.blockchain.current_block.getData(),
                            b.getData(),
                            "b should not have been added")
        self.assertEqual(m.blockchain.current_block.getData(),
                         b2.getData(),
                         "b2 should have been added")

        print(m.blockchain.current_block.state)
        print("This will be broadcasted:", m.blockchain.current_block.getData())


if __name__ == '__main__':
    unittest.main()
