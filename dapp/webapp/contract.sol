pragma solidity ^0.4.24;

contract FlightInsurance {

	address public myAddress = 0x63F8Ca14261a495fEEE473B1636e29087D7Cbe8f;
    address public client;
    uint public amountState;
	uint public expiryTime;
	string private flightID;

    constructor() public payable {
        client = msg.sender;
		amountState = 2;  // state of claim, should be 2 if unclaimed, 1 if partially claimed, 0 if fully claimed
	}

	function claim(uint _full_amount, uint _part_amount, uint _code) public {
		/*
		* Code 1: claim cancelled amount
		* Code 2: claim delay amount
		*/
		if(_code == 1){
			if(amountState == 2){
				// give part amount
				amountState = 1;
				client.transfer(_part_amount);
			}
		}
		else if(_code == 2){
			if (amountState == 2){
				// give full amount
				amountState = 0;
				client.transfer(_full_amount);
			} else if (amountState == 1){
				// give remaining
				amountState = 0;
				client.transfer(_full_amount - _part_amount);
			}
		}

	}


	function setFlight(uint _expiryTime, string _flightID) public {
		expiryTime = _expiryTime;
		flightID = _flightID;
	}

	function getFlight() view public returns(string){
		return(flightID);
	}

	function checkStatus(uint _timenow) view public returns(bool){
		if (_timenow >= expiryTime){
			return(true);
		}
		return(false);
	}

	function () payable public {
	}

	function setOwner() payable public returns(bool success){
        client = msg.sender;
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
