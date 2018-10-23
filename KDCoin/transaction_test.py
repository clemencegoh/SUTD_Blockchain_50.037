import unittest
import transaction, keyPair
import json


class TestTransaction(unittest.TestCase):
    def test_Simple(self):
        # generate sender
        sender_private_key, sender_public_key = keyPair.GenerateKeyPair()

        # generate recv
        receiver_private_key, receiver_public_key = keyPair.GenerateKeyPair()

        # amount
        amount = 10000
        comment = "testRun"

        # create transaction
        t = transaction.Transaction(sender_public_key, receiver_public_key, amount, comment)
        t.sign(sender_private_key)

        # validate is ok
        self.assertTrue(t.validate())

        # change to json
        json_form = t.to_json()

        # assume received
        recv_json = json.loads(json_form)

        # create transaction
        new_t = transaction.Transaction(
            _sender_public_key=recv_json["Sender"],
            _receiver_public_key=recv_json["Receiver"],
            _amount=recv_json["Amount"],
            _comment=recv_json["Comment"],
            _reward=recv_json["Reward"],
            _signature=recv_json["Signature"]
        )

        # change the signatures back
        t.from_json()
        new_t.from_json()
        self.assertEqual(new_t.data, t.data, "both do not give the same data")


if __name__ == '__main__':
    unittest.main()
