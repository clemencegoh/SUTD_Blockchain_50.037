import json

from flask import Flask, render_template, request

from web3.auto import w3
from solc import compile_source

app = Flask(__name__)

contract_source_code = None
contract_source_code_file = 'contract.sol'


# global mapping of users to

with open(contract_source_code_file, 'r') as file:
    contract_source_code = file.read()

contract_compiled = compile_source(contract_source_code)
contract_interface = contract_compiled['<stdin>:FlightInsurance']
FlightInsurance = w3.eth.contract(abi=contract_interface['abi'],
                          bytecode=contract_interface['bin'])

w3.personal.unlockAccount(w3.eth.accounts[0], '')
tx_hash = FlightInsurance.constructor().transact({'from':w3.eth.accounts[0]})
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Contract Object
insurance_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])

# Web Login
@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def loginPage():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass


# Main page for interacting
@app.route('/index', methods=['GET'])
def hello():
    return render_template('template.html',
                           contractAddress = insurance_contract.address.lower(),
                           contractABI = json.dumps(contract_interface['abi']))


# FlightAPI
@app.route('/flightAPI', methods=['GET'])
def flightAPI():
    pass


# currency convert API
@app.route('/convertCurrencyAPI', methods=['POST'])
def convertCurrencyAPI():
    pass


if __name__ == '__main__':
    app.run()
