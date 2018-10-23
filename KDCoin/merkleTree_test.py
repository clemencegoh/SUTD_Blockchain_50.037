import unittest
import json
import time
from helperFunctions import generateRandomString
from merkleNode import MerkleNode
from merkleTree import MerkleTree, verify_proof


class TestMerkle(unittest.TestCase):
    def test_createAndVerify(self):
        randomDict = {}
        sender = generateRandomString(12)
        randomDict[sender] = 1

        n = MerkleNode("Leaf", json.dumps({"Sender": sender}))
        m = MerkleTree(n)

        verify_numbers = [0, 1, 2, 6, 21, 30, 102]
        to_verify = [n]

        for i in range(100):
            while sender in randomDict:
                sender = generateRandomString(12)

            randomDict[sender] = 1
            n1 = MerkleNode("Leaf", json.dumps({"Sender": sender}))
            m.add(n1)

            # add to verify
            if i in verify_numbers:
                to_verify.append(n1)

        print("-------------- REPORT ------------------")

        print("size of tree:", m.count_elements())
        print("total transactions:", len(m.leaf_nodes))

        # this should be true
        for i in to_verify:
            self.assertTrue(verify_proof(i, m.get_proof(i), m.root))

        # this should be false
        self.assertFalse(
            verify_proof(n,
                         m.get_proof(n) + [(MerkleNode("", json.dumps({"Sender": "attacker"})), 0)],
                         m.root)
        )

        print("------------ REPORT END ----------------")


if __name__=='__main__':
    unittest.main()
