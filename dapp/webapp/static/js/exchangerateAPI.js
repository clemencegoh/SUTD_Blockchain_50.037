// Need to add check if invalid currency id
function exchangerateAPI(currencyID,amount){

    const url = "https://rest.coinapi.io/v1/exchangerate/ETH/" + currencyID

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET",url,false);
    xhttp.setRequestHeader('X-CoinAPI-Key','AABB3709-1E0A-488C-B324-B84C21FB004D');
    xhttp.send();

    // Action to be performed when the document is read;
    // var response = xhttp.responseJSON;
    // console.log(response)
    var response = xhttp.responseText;
    var json_response = JSON.parse(response)
    var rate = json_response['rate']
    var currencytoeth = 1/rate
    var eth = currencytoeth * amount
    return eth;
}

// console.log(exchangerateAPI("USD",200));
