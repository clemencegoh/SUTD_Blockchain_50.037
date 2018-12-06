// Need to add check if flightID dont exist

flightAPI = function(airlineID,flightID,date){
    const url = "https://api.flightstats.com/flex/flightstatus/rest/v2/json/flight/status/" + airlineID
              + "/" + flightID + "/arr/" + date +"?appId=ce0bfb9d&appKey=3e8b96e50e47533d6068a1fa42a2fdb6&utc=false"

    // var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    // var json = require('JSON');
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET",url,false)
    xhttp.setRequestHeader('Content-Type','application/json')
    xhttp.setRequestHeader('Allow-Control-Allow-Origin','*')
    xhttp.send();

    if (xhttp.status != 200){
      console.log('Not able to connect to API')
    };

    var response = xhttp.responseText;
    var json_response = JSON.parse(response);

    console.log('json_response: ', json_response)

    var flightstatuses = json_response['flightStatuses'];

    
    
    try{
    console.log('flight status:', flightstatuses)
    var checkcancelled = flightstatuses[0]['status'];
    var operational_times = flightstatuses[0]['operationalTimes'];
    var scheduledGateDeparture = new Date(operational_times['scheduledGateDeparture']['dateLocal']);
    var actualGateDeparture = new Date(operational_times['actualGateDeparture']['dateLocal']);
    // var testdate = new Date(operational_times['scheduledGateDeparture']['dateLocal']);
    var actualRunwayDeparture = operational_times['actualRunwayDeparture']['dateLocal'];
  }catch(error){
    return 'flight status unavailable';
  }
    
    var flightstatus = 0;
    var timediff = actualGateDeparture - scheduledGateDeparture;

    if (checkcancelled == "C"){
      flightstatus = "Cancelled"
      }
      // if >15 minutes, consider delayed
    else if (actualGateDeparture - scheduledGateDeparture >= 900000){
      flightstatus = "Delayed"
      }
    else{
      flightstatus = "On-Time"
      }
          
      return [flightstatus,actualRunwayDeparture];

};


console.log(flightAPI('SQ','306','2018/12/8'));
// console.log(flightAPI('SQ','391','2018/12/6'));
// console.log(flightAPI('SQ','529','2018/12/6'));
