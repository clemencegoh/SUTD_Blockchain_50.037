from KDCoin.helperFunctions import hashItem


# State is the current global state of the coin
# This is required due to implementation of addr:balance
class State:
    def __init__(self, _prev_state=None):
        self.prev_state = _prev_state
        self.data = {
            "Tx_global_list": [],
            "Balance": {},
            "Current_block": None,
            "Blockchain_length": 0
        }
        self.header = ""

        # prev state None should only happen in first block
        if self.prev_state is not None:
            self.data = self.prev_state.data
            self.header = self.prev_state.header

    def changeState(self, _transaction):
        sendr_addr = _transaction.data["Receiver"]
        recv_addr = _transaction.data["Receiver"]
        amount = _transaction.data["Amount"]

        if _transaction.data["Reward"]:
            # reward block, immediately award
            if recv_addr not in self.data:
                self.data["Balance"][recv_addr] = 0
            self.data["Balance"][recv_addr] += amount

        if sendr_addr not in self.data:
            return False

        # if less than amount
        if self.data[sendr_addr] < amount:
            return False

        self.completeTransaction(_transaction)
        return True

    def completeTransaction(self, _transaction):
        sendr_addr = _transaction.data["Receiver"]
        recv_addr = _transaction.data["Receiver"]
        amount = _transaction.data["Amount"]

        self.data["Balance"][sendr_addr] -= amount
        if recv_addr not in self.data:
            self.data["Balance"][recv_addr] = 0
        self.data["Balance"][recv_addr] += amount
        self.header = hashItem(self.header + hashItem(_transaction))

    # verify that this state was indeed created from prev_state and
    # transactions within the Block
    def verify(self, _prev_header, _tx_list):
        final_hash = _prev_header
        for tx in _tx_list:
            final_hash = hashItem(final_hash + hashItem(tx))

        return final_hash == self.header


if __name__ == '__main__':
    pass
