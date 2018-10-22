import unittest
import requests
import time
import re
import json
from multiprocessing import Process
from KDCoin import transaction, keyPair


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


class TestMinerApp(unittest.TestCase):

    def test_single_miner_with_payment(self):
        generator = startMiners(1)
        miner1_address, miner1_pub, miner1, current_balance = next(generator)

        # verify initial balance is correct
        for k, v in current_balance.items():
            self.assertEqual(v, 0, "Balance should be 0")

        p = Process(target=startMining,
                    args=(miner1, miner1_address+"/mine"))
        p.daemon = True
        p.start()

        time.sleep(1)

        giveMinerMoney(miner1, miner1_address)
        time.sleep(2)

        # create transaction
        miner1.post(miner1_address + "/pay?pub_key=random&amount=10&comment=first")

        time.sleep(5)
        res = miner1.get(miner1_address+"/state")
        current_balance = extractBalanceFromState(res.text)

        self.assertEqual(current_balance[miner1_pub], 190, "Miner 1 should have 190 left")
        self.assertEqual(current_balance["random"], 10, "random should have been given 10")

        print("Test 1 current balance:", current_balance)

    def test_single_miner_multiple_payments(self):
        generator = startMiners(1)
        miner1_address, miner1_pub, miner1, current_balance = next(generator)

        # verify initial balance is correct
        for k, v in current_balance.items():
            self.assertEqual(v, 0, "Balance should be 0")

        print("mining...")
        p = Process(target=startMining,
                    args=(miner1, miner1_address + "/mine"))
        p.daemon = True
        p.start()

        time.sleep(1)

        giveMinerMoney(miner1, miner1_address)
        time.sleep(3)

        # create transaction
        print("Creating transactions...")
        persons = ["random1", "random2", "random3"]
        amount = [10, 10, 10]
        comment = ["First", "Second", "Last"]
        for i in range(3):
            miner1.post(
                miner1_address +
                "/pay?pub_key={}&amount={}&comment={}".format(
                    persons[i], amount[i], comment[i]
                ))

        time.sleep(5)
        res = miner1.get(miner1_address + "/state")
        current_balance = extractBalanceFromState(res.text)

        self.assertEqual(current_balance["random1"], 10, "random1 should have been given 10")
        self.assertEqual(current_balance["random2"], 10, "random2 should have been given 10")
        self.assertEqual(current_balance["random3"], 10, "random3 should have been given 10")

        print(current_balance)

    def test_double_miners_resolve(self):
        generator = startMiners(2)
        miner1_address, miner1_pub, miner1, current_balance = next(generator)
        miner2_address, miner2_pub, miner2, m2_current = next(generator)

        self.assertEqual(current_balance[miner1_pub], 0, "Current balance for all should be 0")
        self.assertEqual(m2_current[miner2_pub], 0, "Current balance for 2 should also be 0")

        # update both miners
        miner1.get(miner1_address + "/update")
        miner2.get(miner2_address + "/update")

        giveMinerMoney(miner1, miner1_address)
        time.sleep(5)

        giveMinerMoney(miner2, miner2_address)
        time.sleep(5)

        # both should have their state updated
        print(checkCurrentBalance(miner1, miner1_address))
        print(checkCurrentBalance(miner2, miner2_address))


if __name__ == '__main__':
    unittest.main()