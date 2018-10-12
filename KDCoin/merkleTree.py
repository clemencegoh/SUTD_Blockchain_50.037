from helperFunctions import hashItem
from merkleNode import MerkleNode


def createNewNode(_merging_node, _incoming_node):
    new_transaction = hashItem(_merging_node.data["Transaction"] + _incoming_node.data["Transaction"])

    n = MerkleNode("", new_transaction)
    n.setChild(0, _merging_node)
    n.setChild(1, _incoming_node)
    _merging_node.setParent(n)
    _incoming_node.setParent(n)

    return n


def buildTree(_merging_nodes, _incoming_node):
    if len(_merging_nodes) == 1:  # reached end
        merging_node = _merging_nodes.pop()
        return createNewNode(merging_node, _incoming_node)

    merging_node = _merging_nodes.pop()
    n = createNewNode(merging_node, _incoming_node)
    return buildTree(_merging_nodes, n)


def leftChildren(_node):
    if _node.children[0] is None:
        return 1
    return leftChildren(_node.children[0]) + 1


def rightChildren(_node):
    if _node.children[1] is None:
        return 1
    return rightChildren(_node.children[1]) + 1


def isBalanced(_node):
    number_left = leftChildren(_node)
    number_right = rightChildren(_node)

    if number_left == number_right:
        return True
    return False


def findBalanced(_node):
    if _node is None:
        return []
    balanced_node = _node
    merge_list = []
    while not isBalanced(balanced_node):
        merge_list.append(balanced_node.children[0])
        balanced_node = balanced_node.children[1]
    merge_list.append(balanced_node)
    return merge_list


def tree_size(root, count=0):
    if root is None:
        return count

    return tree_size(root.children[0], tree_size(root.children[1], count + 1))


######################
# Merkle Tree
# Linked list styled implementation
######################
class MerkleTree:
    def __init__(self, _node):
        self.root = _node
        self.leaf_nodes = [_node]

    def add(self, _node):
        # Add hashed entries to tree
        self.leaf_nodes.append(_node)
        self.build()

    # build can only be carried out after the Merkle tree has 2 or more elements
    def build(self):
        leaf_size = len(self.leaf_nodes)
        last_node = self.leaf_nodes[leaf_size - 2]
        incoming_node = self.leaf_nodes[leaf_size - 1]

        if leaf_size == 2:  # handle 1 only
            self.root = buildTree([last_node], incoming_node)
        else:
            # root should never be none
            merge_list = findBalanced(self.root)
            # print("merge_list", merge_list)
            self.root = buildTree(merge_list, incoming_node)

    def get_proof(self, _node):
        # Get membership proof for entry
        proof = []
        current_node = _node
        # print("partner node", _node.findPartner())
        while current_node.hasParent():
            partner, pos = current_node.findPartner()
            if partner is None:
                # Sound warning, this should not happen
                print("WARNING: ERROR ENCOUNTERED AT {}".format(current_node.data))
            proof.append(current_node.findPartner())
            current_node = current_node.parent
        return proof

    def get_root(self):
        # Return the current root
        return self.root

    def set_root(self):
        current_node = self.leaf_nodes[0]
        while current_node.parent is not None:
            current_node = current_node.parent
        self.root = current_node

    def count_elements(self):
        return tree_size(self.root)


# proof here returned as a tuple of partner node + position of partner node
def verify_proof(entry, proof, root):
    # Verifies proof for entry and given root. Returns boolean.
    # Entry must be a node
    # proof must be a list of Nodes
    # root to be compared (if entry + proof == root, return True)
    current_entry = entry
    for nodes in proof:
        # debug
        # print("FOR {}\nPROOF {}\nPOSITION {}".format(current_entry, nodes[0], nodes[1]))
        if nodes[1] == 1:
            # right child
            current_entry = MerkleNode("", hashItem(current_entry.data["Transaction"] + nodes[0].data["Transaction"]))
        else:
            current_entry = MerkleNode("", hashItem(nodes[0].data["Transaction"] + current_entry.data["Transaction"]))

    if current_entry.data["Transaction"] == root.data["Transaction"]:
        return True
    # print("expected: {}\nfound: {}".format(root.data["Transaction"], current_entry.data["Transaction"]))
    return False
