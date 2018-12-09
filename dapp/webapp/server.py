import json

from flask import Flask, render_template, request, redirect

# from web3.auto import w3
from solc import compile_source

app = Flask(__name__)
app.static_url_path = 'static/'

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

    def newContract(self, _contract_abi, _contract_address, _flight_ID, _flight_expiry):
        self.contract_abi.append(_contract_abi)
        self.contract_address.append(_contract_address)
        self.flight_ID.append(_flight_ID)
        self.claim_status.append(2)
        self.flight_expiry.append(_flight_expiry)

    def checkExistingFlight(self, _flight_ID):
        if _flight_ID in self.flight_ID:
            return True
        return False


# global mapping of user addresses to User class
user_db = {"Anon": User()}

# todo: remove this hardcoded data for testing purposes
user_db["Anon"].flight_ID = [["testFlight","123","testDate"], ["test2", "2", "date2"]]
user_db["Anon"].claim_status = [2, 2]
user_db["Anon"].flight_expiry = [0, 0]


# def createNewContract():
#     with open(contract_source_code_file, 'r') as file:
#         contract_source_code = file.read()
#
#     contract_compiled = compile_source(contract_source_code)
#     contract_interface = contract_compiled['<stdin>:FlightInsurance']
#     contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
#
#     w3.personal.unlockAccount(w3.eth.accounts[0], '')
#     tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0]})
#     # tx_hash = contract.constructor().transact({'from':w3.eth.accounts[0]})
#     # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
#
#     # Contract Object
#     insurance_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])
#     return insurance_contract, contract_interface


# Main page for interacting
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    global user_db
    user = request.cookies.get('userID')
    available_contracts = ""

    if user is None:
        # this is an anonymous user, either rogue or tester
        user = "Anon"

        # todo remove this, TESTING ONLY
        # user_db[user].newContract(0, 0, ["SQ", "979", "2018/11/28"], "2018/11/28")
        return render_template('test_template.html',
                           userID=user,
                           loyalty_points=user_db[user].loyalty_points,
                           active_contracts=available_contracts)

    if user not in user_db:
        # new person, add to db
        user_db[user] = User()
        return render_template('test_template.html',
                           userID=user,
                           loyalty_points=user_db[user].loyalty_points,
                           active_contracts=available_contracts)

    else:
        # construct contracts here
        user_obj = user_db[user]
        fid = user_obj.flight_ID
        cs = user_obj.claim_status
        for i in range(len(fid)):
            common_name = str(fid[i][0]) + str(fid[i][1])
            flight_name = common_name + "_fid"
            claim_name = common_name + "_cid"
            flight_status_name = common_name + "fsid"
            flight_details = ""

            for j in range(len(fid[i])):
                flight_details += fid[i][j]
                flight_details += " "

            claim_details = "Claim Status: "
            if cs[i] == 2:
                claim_details += "unclaimed"
            elif cs[i] == 1:
                claim_details += "delay claimed"
            else:
                claim_details += "fully claimed"

            available_contracts += render_template('current_contracts.html',
                                                   flight_refresh_id=flight_name,
                                                   flight_details_perm=flight_details,
                                                   flight_details=fid[i],
                                                   flight_refresh_status_id=flight_status_name,
                                                   claim_refresh_id=claim_name,
                                                   claim_details=claim_details)
            available_contracts += "\n"

    return render_template('test_template.html',
                           userID=user,
                           loyalty_points=user_db[user].loyalty_points,
                           active_contracts=available_contracts)


# Web Login
@app.route('/login', methods=['POST'])
def loginPage():
    # info passed from frontend, save cookie and sent to main
    print(request.form.get('test-login'))

    uid = request.form.get('test-login')
    redirect_to_index = redirect('/index')
    response = app.make_response(redirect_to_index)
    response.set_cookie('userID', value=uid)
    return response


# buy endpoint for creation of new contract
@app.route('/buy', methods=['POST'])
def buyPage():
    print('Received request...')

    # todo: check for multiple contracts of the same flight with the same account
    global user_db
    user = request.cookies.get('userID')
    if user is None:
        # user is not logged in
        return home()

    form_details = request.form
    # todo: parse form details and create contract
    print("Got form:", form_details)

    # todo: add flight details here
    # don't need this
    availability = form_details['flight_availability']

    # pass this into template
    flight_details_ID = form_details['flight_details'].split(',')
    trip_type_choice = form_details['trip_type_choice']
    trip_type_payment = form_details['trip_type_payment']
    selected_payment_method = form_details['selected_payment_method']

    # todo: Check if existing flight and create

    # determine how much loyalty to award
    if trip_type_choice == '1-way':
        reward_points = 5
    else:
        reward_points = 10
    user_db[user].loyalty_points += reward_points

    # check that it is eth
    if selected_payment_method == "Points":
        user_db[user].loyalty_points -= trip_type_payment
        trip_type_payment = 0

    # todo: uncomment this for the final draft
    # if not user_db[user].checkExistingFlight(flight_details_ID):
    #     # create new contract
    #     insurance_contract, contract_interface = createNewContract()
    #     user_db[user].newContract(
    #         _contract_abi=json.dumps(contract_interface['abi']),
    #         _contract_address=insurance_contract.address.lower(),
    #         _flight_ID=flight_details_ID,
    #         _flight_expiry=flight_details_ID[2],
    #     )
    #
    #     # topup with 200 Wei
    #     insurance_contract.functions.topUp().transact({'from': w3.eth.accounts[0], 'value': 200})
    #
    #     return render_template('confirm_buy.html',
    #                            contractAddress=insurance_contract.address.lower(),
    #                            contractABI=json.dumps(contract_interface['abi']),
    #                            payment=trip_type_payment
    #                            )
    print("Somehow was skipped")
    return home()


if __name__ == '__main__':
    app.run(port=5001)
