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
var flight_status = json_response['flightStatuses'];
var checkcancelled = flight_status[0]['status'];
var operational_times = flight_status[0]['operationalTimes'];
var scheduledGateDeparture = operational_times['scheduledGateDeparture'];
var actualGateDeparture = operational_times['actualGateDeparture'];
// console.log(response);

if (checkcancelled == "C"){
  return "Cancelled";
  }
else if (actualGateDeparture - scheduledGateDeparture > 0){
  return "Delayed"
  }
else{
  return "On-Time"
  }
};



// console.log(flightAPI('SQ','979','2018/11/28'));