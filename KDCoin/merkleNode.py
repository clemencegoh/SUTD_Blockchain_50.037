import json
from helperFunctions import hashItem


############
# MerkleNode
# This is a node containing the type and the transaction, in hex
# Also contains pointers to other nodes
############
class MerkleNode:
    def __init__(self, _type, _transaction):
        self.data = {
            "Type": _type,
            "Transaction": hashItem(_transaction)
        }
        self.parent = None
        self.children = [None, None]

    def findPartner(self):
        if self.parent is None:
            return None
        if self.parent.children[0] is not self:
            return self.parent.children[0], 0
        if self.parent.children[1] is not self:
            return self.parent.children[1], 1
        return None

    def setParent(self, _node):
        self.parent = _node

    def setChild(self, _position, _node):
        self.children[_position] = _node

    def hasChildren(self):
        if self.children[0] is None and self.children[1] is None:
            return False
        return True

    def hasParent(self):
        if self.parent is None:
            return False
        return True

    def __str__(self):
        return json.dumps(self.data)