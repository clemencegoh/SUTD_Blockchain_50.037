import json

from flask import Flask, render_template, request, redirect

from web3.auto import w3
from solc import compile_source

app = Flask(__name__)

contract_source_code = None
contract_source_code_file = 'contract.sol'


# global mapping of user addresses to User class
user_db = {}


class User:
    def __init__(self, _contract_abi, _contract_address):
        self.contract_abi = _contract_abi
        self.contract_address = _contract_address
        self.loyalty_points = 0


def createNewContract():
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
    return insurance_contract, contract_interface


# Web Login
@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def loginPage():
    if request.method == 'GET':
        # fresh login, ask for metamask
        return render_template('login_template.html')
    if request.method == 'POST':
        # info passed from frontend, save cookie and sent to main
        # todo: parse info here
        uid = ''
        redirect_to_index = redirect('/index')
        response = app.make_response(redirect_to_index)
        response.set_cookie('userID', value=uid)
        return response


# Main page for interacting
@app.route('/index', methods=['GET'])
def hello():
    global user_db
    try:
        user = request.cookies.get('userID')
        if user not in user_db:
            # new person, create new contract
            insurance_contract, contract_interface = createNewContract()

            # add to db
            user_db[user] = User(
                _contract_abi=json.dumps(contract_interface['abi']),
                _contract_address=insurance_contract.address.lower()
            )

        current_user = user_db[user]
        return render_template('template.html',
                               contractAddress=current_user.contract_address,
                               contractABI=current_user.contract_abi)
    except:
        return loginPage()



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
