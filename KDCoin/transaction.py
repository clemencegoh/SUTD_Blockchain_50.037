import json
from KDCoin.keyPair import GenerateKeyPair, signWithPrivateKey, verifyExisting
import ecdsa


# variables
# sender_private_key, sender_public_key = GenerateKeyPair()
#
# receiver_private_key, receiver_public_key = GenerateKeyPair()
#
# amount = 10000
# comment = "testRun"


# Transaction class
class Transaction:
    def __init__(self, _sender_public_key, _receiver_public_key, _amount, _comment, _private, _reward=False):
        self.version = 1.0
        self.data = {
            "Sender": _sender_public_key.to_string().hex(),
            "Receiver": _receiver_public_key.to_string().hex(),
            "Amount": _amount,
            "Comment": _comment,
            "Reward": _reward,
            "Signature": ""
        }
        self.sign(_private)

    @classmethod
    def new(cls, _from, _to, _amount, _comment, _private_key):
        # Instantiates object from passed values
        t = Transaction(_from, _to, _amount, _comment)

        # sign and return obj
        t.sign(_private_key)
        return t

    def to_json(self, _data):
        # Edit signature
        if type(self.data["Signature"]) is not str:
            self.data["Signature"] = self.data["Signature"].hex()
        return json.dumps(_data)

    @classmethod
    def from_json(cls, _data):
        # Instantiates/Deserializes object from JSON string
        hex_data = json.loads(_data)
        hex_data["Signature"] = bytes.fromhex(hex_data["Signature"])

    def sign(self, _private_key):
        # Sign object with private key passed
        # sign data with private key
        sig = signWithPrivateKey(_message=json.dumps(self.data), sk=_private_key)

        # add signature to existing data
        self.data["Signature"] = sig
        return self.data, sig

    def getVKFromData(self, _person):
        return ecdsa.VerifyingKey.from_string(bytes.fromhex(self.data[_person]))

    # only this is supposed to be touched once client inits using new or newReward
    def validate(self):
        # Validate transaction correctness.
        # Can be called within from_json()
        # remove signature
        sig = bytes.fromhex(self.data["Signature"])
        self.data["Signature"] = ""

        # verify data without signature in it
        vk = self.getVKFromData("Sender")
        result = verifyExisting(_message=self.to_json(self.data), _public_key=vk, _sig=sig)
        self.data["Signature"] = sig
        return result

    def __eq__(self, other):
        # Check whether transactions are the same
        return self.data == other.data

    def __str__(self):
        return self.to_json(self.data)


# if __name__=="__main__":
#     t = Transaction.new(sender_public_key, receiver_public_key, amount, comment, sender_private_key)
#     # print(t.data)
#     print(t.validate())
