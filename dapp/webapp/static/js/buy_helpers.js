function oneWayTrip(){
    console.log('One way trip selected');
    document.getElementById("payment_amount").innerHTML = "Payment Amount: 50 eth";
};

function twoWayTrip(){
    console.log('Two way trip selected');
    document.getElementById("payment_amount").innerHTML = "Payment Amount: 200 eth";

};

function checkFlight(_company, _flightID, _date){
    console.log('checking flight status for', _company, _flightID, _date);
    console.log(flightAPI(_company, _flightID, _date));
    const status = flightAPI(_company, _flightID, _date);
    var answer = "Flight Availability: ";
    if (status[0] === "On-Time"){
        answer += "Available";
    }else{
        answer += "Unavailable";
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
}

function testBuy(){
    restAPI('/buy', {dummy: true});
}


