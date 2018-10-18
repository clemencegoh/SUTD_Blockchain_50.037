from KDCoin import spvClient, keyPair, transaction
import unittest
import json
import ecdsa
import codecs


class TestClientFunctions(unittest.TestCase):
    def test_create_tx(self):
        priv, pub = keyPair.GenerateKeyPair()
        client = spvClient.SPVClient(priv, pub)
        t = client.createTransaction(receiver_public_key=pub,
                                 amount=10,
                                 comment="Hi")
        t.data["Signature"] = t.data["Signature"].hex()
        tx = json.dumps(t.data)

        print(tx)

        # convert back
        tx = json.loads(tx)

        recv_tx = transaction.Transaction(
        _sender_public_key=tx["Sender"],
        _receiver_public_key=tx["Receiver"],
        _amount=tx["Amount"],
        _comment=tx["Comment"],
        _signature=tx["Signature"]
        )

        pub = recv_tx.data["Sender"]
        pub = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(pub)
        )

        sig = recv_tx.data["Signature"]

        sig = bytes.fromhex(sig)
        recv_tx.data["Signature"] = ""

        self.assertTrue(
            keyPair.verifyExisting(recv_tx.to_json(),
                                   pub,
                                   sig),
            "This must be true")


if __name__ == '__main__':
    unittest.main()