# from keyPair import GenerateKeyPair, signWithPrivatekey
import keyPair

priv , pub = keyPair.GenerateKeyPair()
message = 'a'
signedmessage = keyPair.signWithPrivateKey(message, priv)

import pdb;pdb.set_trace()
print (signedmessage)