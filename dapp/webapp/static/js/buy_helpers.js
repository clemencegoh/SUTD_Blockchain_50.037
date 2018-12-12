var new_contract_fields = {}

function oneWayTrip(){
    console.log('One way trip selected');

    // SGD$20
    amount = exchangerateAPI("SGD", 20);
    amount_payable_text = "Payment Amount: " + amount + " eth/100 points"

	// Convert to Wei
	wei = amount * 1000000000000000000

    document.getElementById("payment_amount").innerHTML = amount_payable_text;

    // set choice
    new_contract_fields['trip_type_choice'] = "1-way";
    new_contract_fields['trip_type_payment'] = wei;
}

function twoWayTrip(){
    console.log('Two way trip selected');

    // SGD$30
    amount = exchangerateAPI("SGD", 30);
	
	// Convert to Wei
	wei = amount * 1000000000000000000
	
    amount_payable_text = "Payment Amount: " + amount + " eth/150 points"
    document.getElementById("payment_amount").innerHTML = amount_payable_text;

    // set choice
    new_contract_fields['trip_type_choice'] = "2-way";
    new_contract_fields['trip_type_payment'] = wei;
}

function checkFlight(_company, _flightID, _date){
    console.log('checking flight status for', _company, _flightID, _date);
    // check if any fields are empty
    if (_company === 'undefined' || _flightID === 'undefined' || _date === 'undefined'){
        alert("Insufficient flight details");
    }

    var date_selected = new_contract_fields['flight_details'][2];
	
	console.log(date_selected);

	var input_split = date_selected.split("/")
	var input_year = input_split[0];
	var input_month = input_split[1];
	var input_day = input_split[2];

    var today = new Date();
    var day = today.getDate();
    var month = today.getMonth() + 1;
    var year = today.getFullYear();

    //check if flight date has passed
    if (input_year <= year){
    	if (input_month <= month){
    		if (input_day <= day){

    			console.log(flightAPI(_company, _flightID, _date));

			    var curr_status = flightAPI(_company, _flightID, _date);
			    var answer = "Flight Availability: ";
			    // maybe need to include check that is available but too far in the future
			    // (No scheduledGateDeparture)
			    var set_status = "unavailable";
			    if (curr_status[1] === "flight status unavailable"){
			        if (curr_status[0] === true){
			            answer += "Available, further status will be updated";
			            set_status = "Available";
			        }else{
			            answer += "Unavailable";
			        }
			    }else if (curr_status[0] === true){
			        answer+= "Available";
			        set_status = "Available";
			    }
			    document.getElementById('flight_status').innerHTML = answer;

			    // update form
			    new_contract_fields['flight_details'] = [_company, _flightID, _date];
			    new_contract_fields['flight_availability'] = set_status;
	
				// 	var today = getDate();
	
				// var date_selected = new_contract_fields['flight_details'][2];
				// console.log(today);
				// var t = today.split("/")
				// var d = date_selected.split('/')
				// for (i = 0; i<t.length;i++){
				// 	if (t[i] < d[i]){
				// 		alert("Please enter valid date");
				// 	}
				// }
    		}
    	}
    }

    
	
}

function setPaymentOption(_method){
    console.log("Setting as", _method);

    document.getElementById("selected-option_display").innerHTML = "Selected Option: " + _method;

    new_contract_fields['selected_payment_method'] = _method;
}

// params here must be a json
function restAPI(path, params, method){
    method = method || "post"; // Set method to post by default if not specified.

    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}


function getDate(){
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!
	var yyyy = today.getFullYear();

	if(dd<10) {
		dd = '0'+dd
	} 

	if(mm<10) {
		mm = '0'+mm
	} 

	today = yyyy + '/' + mm + '/' + dd;
	return today;
}


function testBuy(){
    // check correct Date before letting them buy
	var today = getDate();
	
	var date_selected = new_contract_fields['flight_details'][2];
	console.log(today);
	var t = today.split("/")
	var d = date_selected.split('/')
	for (i = 0; i<t.length;i++){
		if (t[i] < d[i]){
			alert("Please enter valid date");
			return;
		}
		
	}
	

    restAPI('/buy', new_contract_fields);
}

function checkAndRefresh(_flight_rid,
                         _flight_details,
                         _flight_refresh_status_id,
                         _claim_rid,
                         _claim_details,
						 _contract_address,
						 _contract_abi){

    console.log("Received flight details:", _flight_details);
    console.log("Received claim status:", _claim_details);

	checkLogin();
	
	console.log("Checking...");

    var flight_status = "Flight Status: ";
    response = flightAPI(_flight_details[0], _flight_details[1], _flight_details[2]);
    flight_status += response[1];

    document.getElementById(_flight_refresh_status_id).innerHTML = flight_status;

    document.getElementById(_claim_rid).innerHTML = _claim_details;
	
	// execute checks:
	// check time - update end bool
	var _end = true;
	var today = getDate();
	
	var date_selected = _flight_details[2];
	
	var t = today.split("/");
	var d = date_selected.split('/');
	
	for (i = 0; i<t.length;i++){
		if (t[i] < d[i]){
			end = false;
		}
	};
	
	// check flight status - update claim
	var _code = 2;
	if (response[1] == "On-Time"){
		_code = 2;
	}
	else if (response[1] == "Delayed"){
		_code = 1;
	}
	else if (response[1] == "Cancelled"){
		_code = 0;
	}
	
	// update full amount and part amount
	// SGD 5000
	var _full_amt = exchangerateAPI("SGD",5000);
	_full_amt = _full_amt * 1000000000000000000;
	
	// SGD 200
	var _part_amt = exchangerateAPI("SGD", 200);
	_part_amt = _part_amt * 1000000000000000000;
	
	var sc_address = _contract_address;
	var contractABI = web3.eth.contract(JSON.parse(_contract_abi));
	var contractInstance = contractABI.at(sc_address);
	
	
	contractInstance.claim(_full_amt, _part_amt, _code, _end, function(err, res){
		console.log("Error in refreshing claim:");
		console.log(err);
		console.log(res);
	});
	
};

function checkLogin(){
	// Load WEB3
	// Check wether it's already injected by something else (like Metamask or Parity Chrome plugin)
	if(typeof web3 !== 'undefined') {
		web3 = new Web3(web3.currentProvider);  

	// Or connect to a node
	} else {
		web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
	}

	// Check the connection
	if(!web3.isConnected()) {
		console.error("Not connected");
	}
}


function web3login(){
	checkLogin();

	var account = web3.eth.accounts[0];
	var accountInterval = setInterval(function() {
	  if (web3.eth.accounts[0] !== account) {
		account = web3.eth.accounts[0];
		document.getElementById("address").innerHTML = account;
	  }
	}, 100);
	
	restAPI('/login', {'test-login': account}, 'POST');
}