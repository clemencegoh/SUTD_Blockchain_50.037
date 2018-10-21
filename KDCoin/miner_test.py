import unittest
from KDCoin import miner, minerApp, transaction, block, blockChain



class TestMiner(unittest.TestCase):
    def test_simple_create(self):
        m = miner.Miner()