import unittest
import ecdsa
from KDCoin import keyPair


class TestKeyPair(unittest.TestCase):
    def test_conversion(self):
        priv, pub = keyPair.GenerateKeyPair()
        pubHex = pub.to_string().hex()
        privHex = priv.to_string().hex()
        print(pubHex)
        print(privHex)

        nextA = ecdsa.SigningKey.from_string(bytes.fromhex(privHex))
        nextB = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubHex))

        print(nextA.to_string().hex())
        print(nextB.to_string().hex())

        msg = "KDCoin"
        print(keyPair.signWithPrivateKey(msg, priv))


if __name__ == "__main__":
    unittest.main()
