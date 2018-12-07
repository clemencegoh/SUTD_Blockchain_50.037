var new_contract_fields = {}

function oneWayTrip(){
    console.log('One way trip selected');

    // todo: conversion API here
    // SGD$20
    document.getElementById("payment_amount").innerHTML = "Payment Amount: 50 eth";

    // set choice
    new_contract_fields['trip_type_choice'] = "1-way";
    new_contract_fields['trip_type_payment'] = "20";
};

function twoWayTrip(){
    console.log('Two way trip selected');

    // SGD$30

    //todo: conversionAPI for SGD to eth
    document.getElementById("payment_amount").innerHTML = "Payment Amount: 200 eth";

    // set choice
    new_contract_fields['trip_type_choice'] = "2-way";
    new_contract_fields['trip_type_payment'] = "30";
};

function checkFlight(_company, _flightID, _date){
    console.log('checking flight status for', _company, _flightID, _date);
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

function testBuy(){
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


