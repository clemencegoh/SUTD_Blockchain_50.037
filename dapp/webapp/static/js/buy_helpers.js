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


