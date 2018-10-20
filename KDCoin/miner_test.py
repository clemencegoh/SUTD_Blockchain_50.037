import unittest
from KDCoin import miner, minerApp, transaction, block, blockChain


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


if __name__ == '__main__':
    unittest.main()
