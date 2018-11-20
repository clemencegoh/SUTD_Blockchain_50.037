# Bitcoin NG - Microblocks

- Problem with conventional blockchains:
    - Each block is restricted by size
        - Size too large means that there is an increased prob of forks
        due to slow transfer of information
        - Too slow
        - Size too small leads to race problems and forks 
        - More forks leads to lower security
        
        
```python
#TODO: READ UP ON AND STUDY BYZATINE FAULT TOLERANCE (BFT)
```
- 2 new methods of blockchain implementation:
    - Bitcoin NG
        - Concept of "micro-blocks"
        - aim is to make the number of transactions per second increase
        - Thus, central "leader" is appointed, with rights to 
        append to the blockchain
        - Others will try to create their own Proof-of-Leadership Block
        - Prev leader gets 40% of subsequent chain, next gets 60%
            - This is to prevent forks happening since prev leader will
            be incentivised to add more to main chain and next leader will
            be incentivised to make the main chain longer.
            - Overall, both aims to lengthen the main chain instead of create
            a new one for profit.
    - Sharding
        - Database concept
        - Splitting work
        - Main "Final Committee" determines how much work is needed to be done
        and splits up the transactions
        - other sub-committees end up with a portion of the transactions, creating 
        mini-blocks, and sending them to final Committee
        - Final committee creates Final Block - appends to final blockchain
        - Requires max 30% malicious nodes within each committee
        - Makes use of BFT (Byzatine)
        
        
        
        