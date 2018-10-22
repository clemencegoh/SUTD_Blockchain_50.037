import requests
import ecdsa
import unittest
import re
import time
import json
from multiprocessing import Process
from KDCoin import transaction, miner, spvClient


def extractBalanceFromState(_response_text):
    pattern = re.compile('Balance: (.*)<br>Pool')
    balance = pattern.match(_response_text).group(1)

    # extract data:
    data = json.loads(balance)
    return data


def startMining(_session, _addr):
    return _session.get(_addr)


def extractPubFromText(_text):
    pattern = re.compile('Public Key: (.*)<br>Private Key:')
    pub = pattern.match(_text).group(1)

    return pub


def giveMinerMoney(_session, _addr):
    return _session.post(
        _addr + "/pay?pub_key=random&amount=0&comment=getMoney")


def checkCurrentBalance(_session, _addr):
    response = _session.get(_addr+"/state")
    current_balance = extractBalanceFromState(response.text)
    return current_balance


def startMiners(_number):
    for i in range(_number):
        # define variables
        miner_address = "http://localhost:808{}".format(2 + i)

        # create new miner
        miner = requests.session()
        miner.get(miner_address)
        pub = extractPubFromText(
            miner.get(miner_address + "/new").text
        )

        # allow up to 4 seconds to finish
        time.sleep(2)

        current_balance = checkCurrentBalance(miner, miner_address)

        yield miner_address, pub, miner, current_balance


# normal tests require block difficulty to be set at 4
# these tests have to be run after starting servers
class FullTests(unittest.TestCase):
    # This test requires block difficulty to be set at 4 instead of 5
    def test_one_miner_one_client(self):
        # start 1 miner
        generator = startMiners(1)
        miner1_address, miner1_pub, miner1, balance = next(generator)

        self.assertEqual(balance[miner1_pub], 0, "Current balance for all should be 0")

        # start 1 client
        client_addr = "http://localhost:8081"
        client1 = requests.session()
        client1.get(client_addr)
        client1_pub = extractPubFromText(
            client1.get(client_addr+"/new").text
        )

        # start mining
        p = Process(target=startMining,
                    args=(miner1, miner1_address + "/mine"))
        p.daemon = True
        p.start()

        # give miner moneys
        giveMinerMoney(miner1, miner1_address)
        time.sleep(20)

        miner1_balance = checkCurrentBalance(miner1, miner1_address)
        self.assertEqual(miner1_balance[miner1_pub], 100, "Miner1 should have 100 by now")

        # create transaction
        print("Creating transactions...")
        persons = [client1_pub]
        amount = [100]
        comment = ["Give all moneys"]
        for i in range(len(persons)):
            miner1.post(
                miner1_address +
                "/pay?pub_key={}&amount={}&comment={}".format(
                    persons[i], amount[i], comment[i]
                ))

        # most time taken here for miner to find block
        time.sleep(30)

        res = client1.get(client_addr+"/clientCheckBalance")
        self.assertEqual(res.text, '100', "Client should have 100")

    # This test requires block difficulty to be set at 4 instead of 5
    def test_two_miners_one_client(self):
        # start 2 miners
        generator = startMiners(2)
        miner1_address, miner1_pub, miner1, balance = next(generator)
        miner2_address, miner2_pub, miner2, miner2_balance = next(generator)

        self.assertEqual(balance[miner1_pub], 0, "Current balance for all should be 0")
        self.assertEqual(miner2_balance[miner2_pub], 0,
                         "Current balance for all should be 0")

        # start 1 client
        client_addr = "http://localhost:8081"
        client1 = requests.session()
        client1.get(client_addr)
        client1_pub = extractPubFromText(
            client1.get(client_addr + "/new").text
        )

        # update miners
        miner1.get(miner1_address+"/update")
        miner2.get(miner2_address+"/update")

        # start mining
        p = Process(target=startMining,
                    args=(miner1, miner1_address + "/mine"))
        p.daemon = True

        p2 = Process(target=startMining,
                     args=(miner2, miner2_address + "/mine"))
        p2.daemon = True

        p.start()
        p2.start()

        # give miner moneys
        giveMinerMoney(miner1, miner1_address)
        time.sleep(10)
        giveMinerMoney(miner2, miner2_address)
        time.sleep(20)

        miner1_balance = checkCurrentBalance(miner1, miner1_address)[miner1_pub]
        miner2_balance = checkCurrentBalance(miner2, miner2_address)[miner2_pub]
        total = miner1_balance + miner2_balance
        print("Balance for:\nMiner1: {}\nMiner2: {}".format(
            miner1_balance, miner2_balance
        ))
        self.assertEqual(total, 200, "total 200 should have been generated")

        # create transaction
        print("Creating transactions...")
        persons = [client1_pub]
        amount = [100]
        comment = ["Give all moneys"]
        for i in range(len(persons)):
            miner1.post(
                miner1_address +
                "/pay?pub_key={}&amount={}&comment={}".format(
                    persons[i], amount[i], comment[i]
                ))

        print("Sleeping...")
        # most time taken here for miner to find block
        time.sleep(20)

        res = client1.get(client_addr + "/clientCheckBalance")
        self.assertEqual(res.text, '100', "Client should have 100")

        client1.post(client_addr +
                     "/createTransaction?pub_key={}&amount={}&comment={}".
                     format("random_other_client", 10, "test payment"))

        # wait for miners
        time.sleep(20)
        client_amount = client1.get(client_addr+"/clientCheckBalance").text
        self.assertEqual(client_amount, 90, "Client should have 90 by now")


    # requires 2 miners, 1 set at difficulty 3, 1 set at difficulty 5
    def test_selfish_mining(self):
        pass

    # again, requires 2 miners at different difficulty
    # miner spends money, forks from previous block to create new
    def test_double_spending(self):
        pass


if __name__ == '__main__':
    unittest.main()
