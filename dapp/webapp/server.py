import json

from flask import Flask, render_template, request, redirect

# from web3.auto import w3
from solc import compile_source

app = Flask(__name__)
app.static_url_path='static/'

contract_source_code = None
contract_source_code_file = 'contract.sol'


class User:
    """
    Class User to store all data related to each user wallet
    :param _contract_abi: string: First contract's ABI
    :param _contract_address: string: First contract's address
    :param _flight_ID: string: flight ID
    :param _flight_expiry: string: flight departure time

    Claim_status will store the status of the claim: 0,1,2
    0 indicates fully claimed - nothing left
    1 indicates partial claim for delay
    2 indicates not claimed - full amount left
    """
    def __init__(self):
        self.contract_abi = []
        self.contract_address = []
        self.loyalty_points = 0
        self.flight_ID = []
        self.claim_status = []
        self.flight_expiry = []

    def newContract(self, _contract_abi, _contract_address, _flight_ID, _flight_expiry, _points_gained):
        self.contract_abi.append(_contract_abi)
        self.contract_address.append(_contract_address)
        self.loyalty_points += _points_gained
        self.flight_ID.append(_flight_ID)
        self.claim_status.append(2)
        self.flight_expiry.append(_flight_expiry)


# global mapping of user addresses to User class
user_db = {"Anon": User()}


# def createNewContract():
#     with open(contract_source_code_file, 'r') as file:
#         contract_source_code = file.read()
#
#     contract_compiled = compile_source(contract_source_code)
#     contract_interface = contract_compiled['<stdin>:FlightInsurance']
#     FlightInsurance = w3.eth.contract(abi=contract_interface['abi'],
#                               bytecode=contract_interface['bin'])
#
#     w3.personal.unlockAccount(w3.eth.accounts[0], '')
#     tx_hash = FlightInsurance.constructor().transact({'from':w3.eth.accounts[0]})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#
#     # Contract Object
#     insurance_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])
#     return insurance_contract, contract_interface


# Web Login
@app.route('/login', methods=['POST', 'GET'])
def loginPage():
    if request.method == 'GET':
        # fresh login, ask for metamask
        return render_template('login_template.html')
    if request.method == 'POST':
        # info passed from frontend, save cookie and sent to main
        # todo: parse info here
        print(request.form.get('test-login'))

        uid = request.form.get('test-login')
        redirect_to_index = redirect('/index')
        response = app.make_response(redirect_to_index)
        response.set_cookie('userID', value=uid)
        return response


# buy endpoint for creation of new contract
@app.route('/buy', methods=['POST'])
def buyPage():
    print('A dummy has clicked!')
    return home()


# Main page for interacting
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    global user_db
    user = request.cookies.get('userID')

    if user is not None and user not in user_db:
        # new person, add to db
        user_db[user] = User()

        # todo: remove debug
        print("New user added to db:", user)

    else:
        # this is an anonymous user, either rogue or tester
        user = "Anon"

    return render_template('test_template.html',
                           userID=user,
                           loyalty_points=user_db[user].loyalty_points)

    # insurance_contract, contract_interface = createNewContract()

    # add to db
    # user_db[user] = User(
    #     _contract_abi=json.dumps(contract_interface['abi']),
    #     _contract_address=insurance_contract.address.lower()
    # )

    # current_user = user_db[user]
    # return render_template('template.html',
    #                        contractAddress=current_user.contract_address,
    #                        contractABI=current_user.contract_abi)


if __name__ == '__main__':
    app.run(port=5001)
