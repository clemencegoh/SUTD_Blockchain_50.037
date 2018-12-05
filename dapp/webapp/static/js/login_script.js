// load and connect to metamask immediately
window.onload = function(){
                if (typeof web3 !== 'undefined') {
                    web3 = new Web3(window.web3.currentProvider);
                    console.log('Connecting to the ropsten test network.');
                    web3.eth.defaultAccount = web3.eth.accounts[0];
                    if(!web3.eth.defaultAccount){
                        console.log('Log into metamask');
                        // _Connect(callback);
                    }else{
                        // Success
                        console.log('Web3 ETH Account: ${web3.eth.defaultAccount}');

                        // callback(false, web3.eth.defaultAccount);
                    }
                }
            };




