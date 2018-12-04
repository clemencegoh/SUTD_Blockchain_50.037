# Introduction to Peercoin

Finding Coin Age:
- CA = unspent amt * number of blocks after
    - eg. 5 blocks after, left with 2 coins,
    coin age == 10
- Different mechanics: difficulty is dependent on 
Coin Age: new formula for difficulty = H(x) < Target * CA
    - This is to prove that we owe a larger "stake" since we're 
    older
    - This is also dependent on how much coin age we are willing
    to consume.
    
Comparison:

| Proof of stake | Proof of work | Hybrid |
| --- | --- | --- |
| Vote based on some stake. Richest will always win, same as company shares | | |
| The "nothing at stake" problem - rational miner will always try to create fork |
| In this example, with proof of stake, can vote on **ALL** branches |
| Problem: never sure you're in the correct branch |
| Solution: Checkpoints, all will continue on that branch | 
| However: Issue occurs when these checkpoints are different on diff chains |
| 51% miner can control chain forever |
| Stake centralization |
| No new powerful miner can emerge |
| Someone needs to give us stake |
