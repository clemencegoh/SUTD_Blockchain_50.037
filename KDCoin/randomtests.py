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
