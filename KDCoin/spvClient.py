from KDCoin.transaction import Transaction
from KDCoin.keyPair import GenerateKeyPair

# Single Client
# Functionalities: i) Create Transactions, ii) Verify transactions validated

receiver_private_key, receiver_public_key = GenerateKeyPair()
print(type(receiver_public_key))

class SPVClient:

    def __init__(self):
        self.privatekey, self.publickey = GenerateKeyPair()

#Creates transaction and sign with private key
    def createTransaction(self, amount, comment):
        transaction_tobemade = Transaction(self.publickey, receiver_public_key,
                                                   amount, comment)
        transaction_tobemade.sign(self.privatekey)
        print (transaction_tobemade.data)

        return transaction_tobemade


# if __name__ == "__main__":
#     newclient = SPVClient()
#     newclient.createTransaction(150,'')