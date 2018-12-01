pragma solidity ^0.4.24;

contract Lottery {
	
    address private client;
    uint private number;
	uint amount;

    constructor() public {
        client = msg.sender;
		amount = 0;
    }
	
	function addAmount(uint _number) public {
		amount += _number;
	}
	
	function getAmount() view public returns(uint) {
		return(amount);
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
