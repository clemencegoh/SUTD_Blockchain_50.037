function QRAPI(qrfile){
	
	// console.log(typeof qrfile.files[0]);
	var fd = new FormData();

	fd.append('file',qrfile.files[0]);

	var xhr = new XMLHttpRequest();
//   	//maybe should set false
  	xhr.open('POST', 'http://api.qrserver.com/v1/read-qr-code/', false); 

	xhr.send(fd);
   var response = xhr.responseText;
   var json_response = JSON.parse(response);
   // console.log(response);
   // console.log(json_response[0]);
   var detail = json_response[0]['symbol'][0];
   var flight = detail['data'];
   // console.log('under here is detail');
   // console.log(typeof detail);
   // console.log(flight);
   // Split into airline ID and flight number in a LIST
	// var regexStr = flight.match(/[a-z]+|[^a-z]+/gi);
	// var airlineID = regexStr[0];
	// var flightnumber = regexStr[1];
   var split = flight.split(" ");
   var airlineID = split[0]
   var flightnumber = split[1]
   var flightdate = split[2]
	console.log(airlineID);
	console.log(flightnumber);
   console.log(flightdate);
   document.getElementById('_flight_company').value = airlineID;
   document.getElementById('_flight_number').value = flightnumber;
   document.getElementById('_flight_date').value = flightdate;

   
   
   // return (airlineID,flightnumber);
} 

