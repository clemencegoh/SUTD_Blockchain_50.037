<<<<<<< HEAD
# from keyPair import GenerateKeyPair, signWithPrivatekey
import keyPair

priv , pub = keyPair.GenerateKeyPair()
message = 'a'
signedmessage = keyPair.signWithPrivateKey(message, priv)

import pdb;pdb.set_trace()
print (signedmessage)
=======
import json
import requests


# tx_pool = [1,2,3,4,5,6,7,8,9,10]
# new_pool= tx_pool[:5].append(6)
# print (new_pool)
#
#
# items = {"Hello":
#              {"Name": "Clemence",
#               "Age": [{
#                   "Able": True
#               }, {
#                   "Weird": True
#               }
#               ]
#               }
#          }
#
# j_items = json.dumps(items)
#
# print(j_items)

requests.post("http://localhost:8070/attack",
                      data=json.dumps({
                          "TX": {
                              "Receiver": "merchant2",
                              "Amount": 50,
                              "Comment": "Pay to merch 2"
                          }
                      }))
>>>>>>> 9074dfb343a3b3131b7dfc4f1a8bbec78b07eb26
