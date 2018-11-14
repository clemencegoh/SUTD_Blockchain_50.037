Secret Phrase:
```
unit urge way age fish nephew humor mango umbrella text camp silk
```

Question 2
---
- Account Balance: 0.999838187
- Last Tx performed: Sept 17 2018
- Smart contracts created: yes.
- Stack looks like this:
```
contract Contract {
    function main() {
        memory[0x40:0x60] = 0x80;
        var var0 = msg.value;
    
        if (var0) { revert(memory[0x00:0x00]); }
    
        storage[0x00] = msg.sender | (storage[0x00] & ~0xffffffffffffffffffffffffffffffffffffffff);
        memory[0x00:0x013f] = code[0x60:0x019f];
        return memory[0x00:0x013f];
    }
}
```
- assign 0x80 to variable in memory
- let var0 be value of message
- If at any time the message value is not empty, execution will end
- Else save (sender | storage[0x00]) into storage[0x00]
- Last sender saved into storage[0x00]


---
Question 3
---
- By selecting multisignature wallet contract, it also allows
for multiple signatures on the transaction.

---
Question 4
---
```
pragma solidity ^0.4.0;

contract SimpleLottery{
    string[] people;  // in storage
    uint total = 0;
    
    function placeBet(uint x, person y) public {
        people.push(y);
        total = total + x
    }
    
    function random() private view returns (uint8) 
    {
     return uint8(uint256(keccak256(block.timestamp, block.difficulty))%251);
    }
    
    function chooseWinner() public {
        return people[random()%people.length]  // randomly pick from array
    }
}
```