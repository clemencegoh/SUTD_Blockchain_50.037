import unittest
import ecdsa
from KDCoin import keyPair


class TestKeyPair(unittest.TestCase):
    def test_conversion(self):
        priv, pub = keyPair.GenerateKeyPair()
        print(pub.to_string().hex())
        print(priv.to_string().hex())

        nextA = ecdsa.SigningKey.from_string(priv.to_string())
        nextB = ecdsa.VerifyingKey.from_string(pub.to_string())

        print(nextA.to_string().hex())
        print(nextB.to_string().hex())

        msg = "KDCoin"
        print(keyPair.signWithPrivateKey(msg, priv))


if __name__ == "__main__":
    unittest.main()
