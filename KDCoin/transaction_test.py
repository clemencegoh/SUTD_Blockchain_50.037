import unittest
from KDCoin import transaction, keyPair


class TestTransaction(unittest.TestCase):
    def test_Simple(self):
        # variables
        sender_private_key, sender_public_key = keyPair.GenerateKeyPair()

        receiver_private_key, receiver_public_key = keyPair.GenerateKeyPair()

        amount = 10000
        comment = "testRun"

        t = transaction.Transaction(sender_public_key, receiver_public_key, amount, comment, sender_private_key)
        # print(t.data)
        self.assertTrue(t.validate())


if __name__ == '__main__':
    unittest.main()
