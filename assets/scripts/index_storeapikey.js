function storeAPIKey() {

    // Get the API Key from the input field
    var api_key = document.getElementById("apikey__store").value;

    // Set to local storage
    localStorage.setItem("apikey", api_key);

    // Reload the page
    location.reload();
}


function checkForApiKey() {
    var api_key = localStorage.getItem("apikey");
    if (api_key == null) {
        document.getElementById("apikey_card").style.display = "block";
        document.getElementById("dashboard").style.display = "none";
    }
    else {
        document.getElementById("apikey_card").style.display = "none";
        document.getElementById("dashboard").style.display = "block";
    }
}


function logOut() {
    localStorage.removeItem("apikey");
    document.getElementById("apikey_card").style.display = "block";
    document.getElementById("dashboard").style.display = "none";
    location.reload();
}

checkForApiKey();