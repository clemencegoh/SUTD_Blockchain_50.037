import spvClient, keyPair, transaction
import unittest
import json
import ecdsa
import codecs


class TestClientFunctions(unittest.TestCase):
    def test_create_tx(self):
        priv, pub = keyPair.GenerateKeyPair()
        client = spvClient.SPVClient(priv, pub)
        t = client.createTransaction(pub, 10, "test")

        self.assertTrue(t.validate(), "Client-made transaction must be valid")
        self.assertEqual(t.data["Amount"], 10, "Amount must not differ")


if __name__ == '__main__':
    unittest.main()