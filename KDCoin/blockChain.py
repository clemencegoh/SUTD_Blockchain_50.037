import ecdsa


# Blockchain contains the current block
class Blockchain:
    def __init__(self, _block):
        # verify that block has a nonce, required
        if _block.nonce is None or _block.header is None:
            raise ValueError("Block must be properly initiated")

        # current leading block to be worked on
        self.current_block = _block

        # hashmap of all leading blocks in case of forking
        self.block_heads = {_block: 1}

    # checkChainLength meant to be used to check the chain's length
    # starts from current block and keeps counting backwards
    def checkChainLength(self, _block):
        current_block = _block
        count = 1

        while current_block.prev_block is not None:
            count += 1
            current_block = current_block.prev_block

        return count

    def validate(self):
        # check root is not None
        if self.current_block is None:
            return False

        # validates current block, should be called when broadcasted by miner
        return self.current_block.validate()

    # adds a new block
    # has option to add a new block to a certain block along the chain
    def addBlock(self, _incoming_block, _prev_block=None):
        # default sets the prev block as the head of the chain
        if _prev_block is None:
            _prev_block = self.current_block

        # set current block
        _incoming_block.setPrevBlock(self.current_block)
        self.current_block = _incoming_block

        # replace prev entry with incoming block
        del self.block_heads[_prev_block]
        self.block_heads[_incoming_block] = 1

    # In case of forking, choose current block to work on based on longest chain
    def resolve(self):
        # resolves longest chain
        new_head_block = None
        longest_chain = 0

        for key, _ in self.block_heads.items():
            chain_length = self.checkChainLength(key)
            if longest_chain <= chain_length:
                new_head_block = key
                longest_chain = chain_length

        self.current_block = new_head_block


# if __name__ == '__main__':
#     sender_private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p)
#     sender_public_key = sender_private_key.get_verifying_key()
#
#     receiver_private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p)
#     receiver_public_key = receiver_private_key.get_verifying_key()
#
#     amount = 10000
#     comment = "testRun"
#
#
#     bc = Blockchain()
#     bc.addTransaction(sender_public_key, receiver_public_key, 200, "TestAmount")
#     print(bc.current_block.root)

