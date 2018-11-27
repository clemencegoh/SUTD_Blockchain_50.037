// solium-disable linebreak-style
pragma solidity ^0.4.24;


contract Insurance {
    
    // hashmap of person to claim
    mapping (address => uint8) person;
    
    // Constructor
    constructor () public {
        
    }

    function addPerson(address _person) public {
        // simple add to map
        person[_person] = 200;
    }

    function getMap(address _person) internal view returns (uint8){
        return person[_person];
    }

    function destroy(address a) public {
        selfdestruct(a);
    }

}