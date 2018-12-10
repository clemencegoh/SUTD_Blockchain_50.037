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
};

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
};

function checkFlight(_company, _flightID, _date){
    console.log('checking flight status for', _company, _flightID, _date);
    // check if any fields are empty
    if (_company === 'undefined' || _flightID === 'undefined' || _date === 'undefined'){
        alert("Insufficient flight details");
    }

    console.log(flightAPI(_company, _flightID, _date));

    const status = flightAPI(_company, _flightID, _date);
    var answer = "Flight Availability: ";
    // maybe need to include check that is available but too far in the future
    // (No scheduledGateDeparture)
    var set_status = "unavailable";
    if (status[1] === "flight status unavailable"){
        if (status[0] === true){
            answer += "Available, further status will be updated";
            set_status = "Available";
        }else{
            answer += "Unavailable";
        }
    }else if (status[0] === true){
        answer+= "Available";
        set_status = "Available";
    }
    document.getElementById('flight_status').innerHTML = answer;

    // update form
    new_contract_fields['flight_details'] = [_company, _flightID, _date];
    new_contract_fields['flight_availability'] = set_status;
	
	var today = getDate();
	
	var date_selected = new_contract_fields['flight_details'][2];
	console.log(today);
	var t = today.split("/")
	var d = date_selected.split('/')
	for (i = 0; i<t.length;i++){
		if (t[i] < d[i]){
			alert("Please enter valid date");
		}
	}
	
};

function setPaymentOption(_method){
    console.log("Setting as", _method);

    document.getElementById("selected-option_display").innerHTML = "Selected Option: " + _method;

    new_contract_fields['selected_payment_method'] = _method;
};

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
};


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
    // todo: Check fields, alert if any unfilled or wrong
	var today = getDate();
	
	var date_selected = new_contract_fields['flight_details'][2];
	console.log(today);
	var t = today.split("/")
	var d = date_selected.split('/')
	for (i = 0; i<t.length;i++){
		if (t[i] < d[i]){
			alert("Please enter valid date");
			// todo: uncomment this
			// return;
		}
		
	}
	

    restAPI('/buy', new_contract_fields);
};

function checkAndRefresh(_flight_rid,
                         _flight_details,
                         _flight_refresh_status_id,
                         _claim_rid,
                         _claim_details){

    console.log("Received flight details:", _flight_details);
    console.log("Received claim status:", _claim_details);

    var flight_status = "Flight Status: ";
    response = flightAPI(_flight_details[0], _flight_details[1], _flight_details[2]);
    flight_status += response[1];

    document.getElementById(_flight_refresh_status_id).innerHTML = flight_status;

    document.getElementById(_claim_rid).innerHTML = _claim_details;
};


function web3login(){
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

	var account = web3.eth.accounts[0];
	var accountInterval = setInterval(function() {
	  if (web3.eth.accounts[0] !== account) {
		account = web3.eth.accounts[0];
		document.getElementById("address").innerHTML = account;
	  }
	}, 100);
	
	restAPI('/login', {'test-login': account}, 'POST');
}