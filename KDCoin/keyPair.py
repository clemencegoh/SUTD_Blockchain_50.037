import ecdsa


# For purpose of creating a new user
def GenerateKeyPair():
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p)
    public_key = private_key.get_verifying_key()
    return private_key, public_key


# sk is private key, vk is public key
def generateSig(_message):
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p)
    vk = sk.get_verifying_key()
    sig = sk.sign(_message.encode('utf-8'))
    return sig, vk


def signWithPrivateKey(_message, sk):
    sig = sk.sign(_message.encode('utf-8'))
    return sig


def verifyExisting(_message, _public_key, _sig):
    return _public_key.verify(_sig, _message.encode('utf-8'))  # True


def generateVerifyKeyPairs():
    message = "Blockchain Technology"
    sig, vk = generateSig(message)
    # return vk.verify(sig, message.encode('utf-8'))
    return verifyExisting(message, vk, sig)


if __name__=='__main__':
    priv, pub = GenerateKeyPair()
    # print(pub.to_string().hex())
    # print(priv.to_string().hex())
    #
    # nextA = ecdsa.SigningKey.from_string(priv.to_string())
    # nextB = ecdsa.VerifyingKey.from_string(pub.to_string())
    #
    # print(nextA.to_string().hex())
    # print(nextB.to_string().hex())

    msg = "KDCoin"
    print(signWithPrivateKey(msg, priv))

