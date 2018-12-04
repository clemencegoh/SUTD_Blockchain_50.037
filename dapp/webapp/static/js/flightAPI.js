// Need to add check if flightID dont exist

flightAPI = function(airlineID,flightID,date){
    const url = "https://api.flightstats.com/flex/flightstatus/rest/v2/json/flight/status/" + airlineID
              + "/" + flightID + "/arr/" + date +"?appId=ce0bfb9d&appKey=3e8b96e50e47533d6068a1fa42a2fdb6&utc=false"

    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var json = require("json")
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET",url,false)
    xhttp.setRequestHeader('Content-Type','application/json')
    xhttp.responseType = "json";
    xhttp.send();


    var response = xhttp.responseText;
    var json_response = JSON.parse(response);
    var flightstatuses = json_response['flightStatuses'];
    var checkcancelled = flightstatuses[0]['status'];
    var operational_times = flightstatuses[0]['operationalTimes'];
    var scheduledGateDeparture = new Date(operational_times['scheduledGateDeparture']['dateLocal']);
    var actualGateDeparture = new Date(operational_times['actualGateDeparture']['dateLocal']);
    var testdate = new Date(operational_times['scheduledGateDeparture']['dateLocal']);
    var actualRunwayDeparture = operational_times['actualRunwayDeparture']['dateLocal'];
    
    
    var flightstatus = 0;

    // check flight status
    if (checkcancelled == "C"){
      flightstatus = "Cancelled"
      }
    else if (actualGateDeparture - scheduledGateDeparture > 0){
      flightstatus = "Delayed"
      }
    else{
      flightstatus = "On-Time"
      }
      
      return [flightstatus,actualRunwayDeparture];

};



console.log(flightAPI('SQ','979','2018/11/28'));