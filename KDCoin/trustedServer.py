from flask import Flask, request
import json
from KDCoin.transaction import Transaction

app = Flask(__name__)

miners_list = []


@app.route('/')
def setupServer():
    return str(miners_list)


@app.route('/add/<miner>')
def addNewMiner(miner):
    global miners_list
    if miner not in miners_list:
        miners_list.append(miner)
    return setupServer()

@app.route('/updateSPVMinerList')
def updateMinerList():
    json_miners_list = json.dumps({'miners_list' : miners_list})
    return json_miners_list



if __name__ == '__main__':
    app.run(port=8080)
