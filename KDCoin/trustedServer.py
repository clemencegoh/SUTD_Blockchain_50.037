from flask import Flask
import json

app = Flask(__name__)

miners_list = []

# runs on http://127.0.0.1:8080/
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
