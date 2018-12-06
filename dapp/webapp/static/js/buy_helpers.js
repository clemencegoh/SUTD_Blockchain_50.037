function oneWayTrip(){
    console.log('One way trip selected');


    // SGD$20
    document.getElementById("payment_amount").innerHTML = "Payment Amount: 50 eth";
};

function twoWayTrip(){
    console.log('Two way trip selected');

    // SGD$30

    //todo: conversionAPI for SGD to eth
    document.getElementById("payment_amount").innerHTML = "Payment Amount: 200 eth";

};

function checkFlight(_company, _flightID, _date){
    console.log('checking flight status for', _company, _flightID, _date);
    console.log(flightAPI(_company, _flightID, _date));
    const status = flightAPI(_company, _flightID, _date);
    var answer = "Flight Availability: ";
    // maybe need to include check that is available but too far in the future
    // (No scheduledGateDeparture)
    if (status[1] === "flight status unavailable"){
        if (status[0] === true){
            answer += "Available, further status will be updated";
        }else{
            answer += "Unavailable";
        }
    }else if (status[0] === true){
        answer+= "Available";
    }
    document.getElementById('flight_status').innerHTML = answer;
};

function setPaymentOption(_method){
    console.log("Setting as", _method);

    document.getElementById("selected-option_display").innerHTML = "Selected Option: " + _method;
    document.getElementById("payment-method_selected").innerHTML = _method;
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
    restAPI('/buy', {dummy: true});
};

function checkAndRefresh(_flight_rid,
                         _flight_details,
                         _flight_refresh_status_id,
                         _claim_rid,
                         _claim_details){
    // todo: change this to call actual API

    console.log("Received flight details:", _flight_details);
    console.log("Received claim status:", _claim_details);

    var flight_status = "Flight Status: "
    flight_status += flightAPI(_flight_details[0], _flight_details[1], _flight_details[2])[0];


    //placeholder for flight status
    document.getElementById(_flight_refresh_status_id).innerHTML = flight_status;

    document.getElementById(_claim_rid).innerHTML = _claim_details;
};


