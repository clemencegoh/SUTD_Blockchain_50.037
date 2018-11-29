pragma solidity ^0.4.24;

contract FlightInsurance {
    address public client;  // this is the client's address
	address private company;  // this is the address to pay to
    uint private max_value;
    uint private expiry_time;
    string public flightID;
	bool private paid;  // this is the bool to ensure client knows he has paid
		
	
	constructor() public{
		client = msg.sender;  // person paying
	}
	
	function buy(uint _amount) payable returns(bool success){
		paid = true;
		client = msg.sender;
		return(true);
	}
	
	function confirmPurchase() public returns(bool){
		if msg.sender == client:{
			return(paid);
		}
	}
	
	
    function claim(string status, uint8 timeNow, string _flightID){
		
    }

    function payout(string status, uint8 timeNow, string _flightID){

    }


}

contract Lottery {

    address private owner;
    uint private number;


    constructor() public {
        owner = msg.sender;
    }

    function setNumber(uint _number) public {
        number = _number;
    }

    function getNumber() view public returns(uint) {
        return(number);
    }

    function getOwner() view public returns(address){
        return(owner);
    }

}