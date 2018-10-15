import requests
import unittest


# these tests have to be run after starting servers
class FullTests(unittest.TestCase):
    def test_register(self):
        trustedSession = requests.session()
        neighbourArray = trustedSession.get("http://localhost:8080").json()["miners_list"]
        self.assertEqual(neighbourArray, [], "list should be empty at first")

        miner1 = requests.session()
        miner1.get("http://localhost:8082/new")

        miner2 = requests.session()
        miner2.get("http://localhost:8083/new")

        neighbourArray = trustedSession.get("http://localhost:8080").json()["miners_list"]
        self.assertNotEqual(neighbourArray, [], "list should not be empty now")
        print(neighbourArray)


if __name__ == '__main__':
    unittest.main()
