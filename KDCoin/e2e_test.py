import requests
import ecdsa
import unittest
import re
import time
import json
from multiprocessing import Process
import transaction, miner, spvClient


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


def startHackers(_number):
    for i in range(_number):
        # define variables
        hacker_address = "http://localhost:809{}".format(i)

        # create new miner
        hacker = requests.session()
        hacker.get(hacker_address)
        pub = extractPubFromText(
            hacker.get(hacker_address + "/new").text
        )

        # allow up to 4 seconds to finish
        time.sleep(2)

        current_balance = checkCurrentBalance(hacker, hacker_address)

        yield hacker_address, pub, hacker, current_balance


def startAttackers(_number):
    for i in range(_number):
        # define variables
        attacker_address = "http://localhost:807{}".format(i)

        # create new miner
        attacker = requests.session()
        attacker.get(attacker_address)
        pub = extractPubFromText(
            attacker.get(attacker_address + "/new").text
        )

        # allow up to 4 seconds to finish
        time.sleep(2)

        current_balance = checkCurrentBalance(attacker, attacker_address)

        yield attacker_address, pub, attacker, current_balance


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

    # requires 1 miner (difficulty 4) and 1 hacker (difficulty 2)
    def test_selfish_mining(self):
        generator = startMiners(1)
        miner1_address, miner1_pub, miner1, current_balance = next(generator)

        g2 = startHackers(1)
        hacker_address, hacker_pub, hacker, h_current = next(g2)

        self.assertEqual(current_balance[miner1_pub], 0, "Current balance for all should be 0")
        self.assertEqual(h_current[hacker_pub], 0, "Current balance for 2 should also be 0")

        # update both miners
        miner1.get(miner1_address + "/update")
        hacker.get(hacker_address + "/update")

        p = Process(target=startMining,
                    args=(miner1, miner1_address + "/mine"))
        p.daemon = True

        p2 = Process(target=startMining,
                     args=(hacker, hacker_address + "/mine"))
        p2.daemon = True

        p.start()
        p2.start()

        giveMinerMoney(miner1, miner1_address)
        time.sleep(5)

        # most likely the hacker will finish everything quickly
        giveMinerMoney(hacker, hacker_address)
        time.sleep(5)

        # both should have their state updated
        try:
            miner1_balance = checkCurrentBalance(miner1, miner1_address)[miner1_pub]
            print("Miner is in!")
            hacker_balance = checkCurrentBalance(hacker, hacker_address)[hacker_pub]
            print("Hacker is in!")

            print("Miner1:", miner1_balance)
            print("Hacker:", hacker_balance)
            total = miner1_balance + hacker_balance
            print("Total:", total)
            print("Miner1:", checkCurrentBalance(miner1, miner1_address))
            print("Hacker:", checkCurrentBalance(hacker, hacker_address))
        except KeyError:
            print("Most likely 1 has everything")

        # create 4 transactions on hacker
        # create transaction
        print("Creating transactions...")
        persons = ["random1", "random2", "random3", "random4"]
        amount = [10, 10, 10, 10]
        comment = ["First", "Second", "Third", "Last"]
        for i in range(len(persons)):
            hacker.post(
                hacker_address +
                "/pay?pub_key={}&amount={}&comment={}".format(
                    persons[i], amount[i], comment[i]
                ))
            time.sleep(2)

        time.sleep(60)

        res = hacker.get(hacker_address + "/state")
        res2 = miner1.get(miner1_address+"/state")
        hacker_state = extractBalanceFromState(res.text)
        miner_state = extractBalanceFromState(res2.text)

        print("miner state:", miner_state)
        print("hacker state:", hacker_state)

        self.assertEqual(hacker_state["random1"], 10, "random1 should have been given 10")
        self.assertEqual(hacker_state["random2"], 10, "random2 should have been given 10")
        self.assertEqual(hacker_state["random3"], 10, "random3 should have been given 10")
        self.assertEqual(hacker_state["random4"], 10, "random4 should have 10")
        self.assertEqual(miner_state, hacker_state, "They should resolve to the same")

    # again, requires 1 miner, 1 attacker
    # attacker spends money, forks from previous block to spend same amount
    def test_double_spending(self):
        # same steps as above
        generator = startMiners(1)
        miner1_address, miner1_pub, miner1, current_balance = next(generator)

        g2 = startAttackers(1)
        attacker_address, attacker_pub, attacker, a_current = next(g2)

        # update both miners
        miner1.get(miner1_address + "/update")
        attacker.get(attacker_address + "/update")

        p = Process(target=startMining,
                    args=(miner1, miner1_address + "/mine"))
        p.daemon = True

        p2 = Process(target=startMining,
                     args=(attacker, attacker_address + "/mine"))
        p2.daemon = True

        p.start()
        p2.start()

        giveMinerMoney(attacker, attacker_address)
        giveMinerMoney(miner1, miner1_address)

        # both should have their state updated
        try:
            miner1_balance = checkCurrentBalance(miner1, miner1_address)[miner1_pub]
            print("Miner is in!")
            hacker_balance = checkCurrentBalance(attacker, attacker_address)[attacker_pub]
            print("Hacker is in!")

            print("Miner1:", miner1_balance)
            print("Hacker:", hacker_balance)
            total = miner1_balance + hacker_balance
            print("Total:", total)
            print("Miner1:", checkCurrentBalance(miner1, miner1_address))
            print("Hacker:", checkCurrentBalance(attacker, attacker_address))
        except KeyError:
            print("Most likely 1 has everything")

        # create transaction for attacker
        print("Creating transactions...")
        attacker.post(
            attacker_address +
            "/pay?pub_key={}&amount={}&comment={}".format(
                "merchant1", 50, "Pay to merch 1"
            ))

        time.sleep(10)

        # create 4 transactions on miner
        persons = ["random1", "random2", "random3", "random4"]
        amount = [10, 10, 10, 10]
        comment = ["First", "Second", "Third", "Last"]
        for i in range(len(persons)):
            miner1.post(
                miner1_address +
                "/pay?pub_key={}&amount={}&comment={}".format(
                    persons[i], amount[i], comment[i]
                ))
            time.sleep(5)
            print("Transaction for {} sent".format(persons[i]))

        print("Done with transactions! Sleeping...")
        time.sleep(20)

        res = attacker.get(attacker_address + "/state")
        res2 = miner1.get(miner1_address + "/state")
        attacker_state = extractBalanceFromState(res.text)
        miner_state = extractBalanceFromState(res2.text)

        print("miner state:", miner_state)
        print("attacker state:", attacker_state)

        self.assertEqual(attacker_state["random1"], 10, "random1 should have been given 10")
        self.assertEqual(attacker_state["random2"], 10, "random2 should have been given 10")
        self.assertEqual(attacker_state["random3"], 10, "random3 should have been given 10")
        self.assertEqual(attacker_state["random4"], 10, "random4 should have 10")
        self.assertEqual(attacker_state["merchant1"], 50, "Merchant1 should have received 50")
        if miner_state != attacker_state:
            print("Attacker state != Miner state")
            print("Moving on...")

        print("Starting attack...")
        # Different here, pay to merch 2 instead
        requests.post(attacker_address+"/attack",
                      json={
                          "TX": {
                              "Receiver": "merchant2",
                              "Amount": 50,
                              "Comment": "Pay to merch 2"
                          }
                      })

        # check state
        res = attacker.get(attacker_address + "/state")
        res2 = miner1.get(miner1_address + "/state")
        attacker_state = extractBalanceFromState(res.text)
        miner_state = extractBalanceFromState(res2.text)
        self.assertEqual(attacker_state["random1"], 10, "random1 should have been given 10")
        self.assertEqual(attacker_state["random2"], 10, "random2 should have been given 10")
        self.assertEqual(attacker_state["random3"], 10, "random3 should have been given 10")
        self.assertEqual(attacker_state["random4"], 10, "random4 should have 10")
        self.assertEqual(miner_state, attacker_state, "They should resolve to the same")
        # self.assertEqual(attacker_state["merchant2"], 50, "Merchant2 should have received 50")
        for key, value in attacker_state.items():
            if key == "merchant1":
                self.fail("Merchant1 should no longer be in this state")


if __name__ == '__main__':
    unittest.main()
