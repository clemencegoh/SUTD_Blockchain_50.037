import ecdsa


# Blockchain contains the current block
class Blockchain:
    def __init__(self, _block, _length=1):
        # verify that block has a nonce, required
        if _block.nonce is None or _block.header is None:
            raise ValueError("Block must be properly initiated")

        # current leading block to be worked on
        self.current_block = _block
        self.chain_length = _length
        self.block_heads = {_block: _length}

    # checkChainLength meant to be used to check the chain's length
    # starts from current block and keeps counting backwards
    def checkChainLength(self, _block):
        current_block = _block
        count = 1

        while current_block.prev_block is not None:
            count += 1
            current_block = current_block.prev_block

        self.chain_length = count

        return count

    def validate(self):
        # check root is not None
        if self.current_block is None:
            return False

        # validates current block, should be called when broadcasted by miner
        return self.current_block.validate()

    # WARNING: This should be called as a decoration.
    # Blocks should be initialised with prev block in mind already
    def addBlock(self, _incoming_block, _prev_block_header):
        # adds block to chain
        for k, _ in self.block_heads.items():
            while k is not None:
                count = self.block_heads[k]
                if k.header == _prev_block_header:
                    _incoming_block.setPrevBlock(k)
                    self.block_heads[_incoming_block] = count + 1
                    return self.resolve()
                else:
                    count -= 1
                    k = k.prev_block

        return "Not found"

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
        self.chain_length = longest_chain



