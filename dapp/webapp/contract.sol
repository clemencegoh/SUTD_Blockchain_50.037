pragma solidity ^0.4.24;

contract FlightInsurance {

	address public myAddress;
    address public client;
    uint public amountState;
	string private flightID;

    constructor() public payable {
        myAddress = msg.sender;  // address is the owner of the server
		amountState = 2;  // state of claim, should be 2 if unclaimed, 1 if partially claimed, 0 if fully claimed
	}

	// This is called when client checks on contract
	function claim(uint _full_amount, uint _part_amount, uint _code, bool end) public {
		/*
		* Code 0: claim cancelled amount
		* Code 1: claim delayed amount
		* Code 2: normal
		*/
		
		if (end){
			// flight has landed or past the date
			killContract();
			return;
		}
		
		if (_code != 2){
			if (_code == 0){
				if (amountState == 2){
					// full claim
					client.transfer(_full_amount);
					killContract();
					return;
				}
				else if (amountState == 1){
					// claim the rest
					client.transfer(_full_amount - _part_amount);
					killContract();
					return;
				}else{
					// amount state should never be 0, error catch
					killContract();
					return;
				}
			} else if (_code == 1){
				if (amountState == 2){
					// partial claim
					client.transfer(_part_amount);
					return;
				}else if (amountState == 1) {
					// already claimed, do nothing
					return;
				}else{
					// do nothing - this should not happen
					return;
				}
			}
		}
	}

	function setFlight(string _flightID) public {
		flightID = _flightID;
	}

	function getFlight() view public returns(string){
		return(flightID);
	}

	function () payable public {
	}

    // call this to set contract owner, sender.Value taken as amount being paid
	function setOwner() payable public returns(bool success){
        client = msg.sender;
        return true;
	}

	function topUp() payable public returns(bool success){
	    return true;
	}

	function killContract() public {
	    // Returns leftover to main
	    selfdestruct(myAddress);
	}

	function viewBalance() view public returns(uint256){
	    return address(this).balance;
	}

}
