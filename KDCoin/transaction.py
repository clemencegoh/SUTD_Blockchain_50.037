import json
from keyPair import GenerateKeyPair, signWithPrivateKey, verifyExisting
import ecdsa


# Transaction class
class Transaction:
    def __init__(self, _sender_public_key, _receiver_public_key, _amount, _comment, _reward=False, _signature=""):
        if type(_sender_public_key) is not str:
            _sender_public_key = _sender_public_key.to_string().hex()
        if type(_receiver_public_key) is not str:
            _receiver_public_key = _receiver_public_key.to_string().hex()

        self.version = 1.0
        self.data = {
            "Sender": _sender_public_key,
            "Receiver": _receiver_public_key,
            "Amount": _amount,
            "Comment": _comment,
            "Reward": _reward,
            "Signature": _signature,
        }

    @classmethod
    def new(cls, _from, _to, _amount, _comment, _private_key):
        # Instantiates object from passed values
        t = Transaction(_from, _to, _amount, _comment)

        # sign and return obj
        t.sign(_private_key)
        return t

    def to_json(self, _data=None):
        if _data is None:
            _data = self.data

        # Edit signature
        if type(_data["Signature"]) is not str:
            _data["Signature"] = _data["Signature"].hex()
        return json.dumps(_data)

    def from_json(self):
        # reverts Signature from created Transaction object
        self.data["Signature"] = bytes.fromhex(self.data["Signature"])
        return self.data

    def sign(self, _private_key):
        # Sign object with private key passed
        # sign data with private key
        sig = signWithPrivateKey(_message=json.dumps(self.data), sk=_private_key)

        # add signature to existing data
        self.data["Signature"] = sig.hex()
        return self.data, sig

    def getVKFromData(self):
        return ecdsa.VerifyingKey.from_string(bytes.fromhex(self.data["Sender"]))

    # only this is supposed to be touched once client inits using new or newReward
    def validate(self):
        # Validate transaction correctness.
        # Can be called within from_json()
        # remove signature
        sig = bytes.fromhex(self.data["Signature"])
        self.data["Signature"] = ""

        # verify data without signature in it
        vk = self.getVKFromData()
        result = verifyExisting(_message=self.to_json(self.data), _public_key=vk, _sig=sig)
        self.data["Signature"] = sig.hex()
        return result

    def __eq__(self, other):
        # Check whether transactions are the same
        return self.data == other.data

    def __str__(self):
        return self.to_json(self.data)

