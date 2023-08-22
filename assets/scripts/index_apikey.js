
var apiKeyData = [];
// Fetch the API keys and display them
async function getAPIKeys() {

    var api_key = localStorage.getItem("apikey");
    if (!api_key) {
        return
    }

    try {
        let resp = await fetch("/v1/apikey/query", {
            method: "GET",
            headers: {
                "Infr-API-Key": api_key
            }
        });

        if (resp.ok) {
            let data_full = await resp.json();
            let data = data_full?.api_keys;
            apiKeyData = data; // Key data is stored in a global variable for use in the update function
            let tbody = document.getElementById('api_keys_tbody');
            tbody.innerHTML = '';  // Clear existing rows

            data.forEach(key => {
                let row = `<tr>
                    <td>${key.name}</td>
                    <td>${key.description}</td>
                    <td>${key.access_level.join(', ')}</td>
                    <td>${key.status}</td>
                    <td>
                        <button class="btn btn-sm btn-primary m-1" onclick="updateAPIKey('${key.id}')">Edit</button>
                        <button class="btn btn-sm btn-primary m-1" onclick="copyAPIKey('${key.id}')">Copy</button>
                        <!-- You can also add more buttons for actions like "Deactivate", "Delete", etc. -->
                    </td>
                </tr>`;
                tbody.innerHTML += row;
            });
        } else {
            let data = await resp.json();
            setAlert(data?.message, true, "alert__api");
        }
    } catch (e) {
        setAlert(e, true, "alert__api");
    }
}

// Create a new API key
async function createAPIKey() {
    var api_key = localStorage.getItem("apikey");
    try {
        let name = document.getElementById("api__name").value;
        let description = document.getElementById("api__description").value;
        let access_level = Array.from(document.getElementById("api__access_level").selectedOptions).map(option => option.value);

        let resp = await fetch("/v1/apikey/create", {
            method: "POST",
            headers: {
                "Infr-API-Key": api_key,  // Replace this with the actual API key
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                description: description,
                access_level: access_level
            })
        });

        if (resp.ok) {
            setAlert("API key created successfully.", false, "alert__api");
            getAPIKeys();  // Refresh the list
        } else {
            let data = await resp.json();
            setAlert(data?.message, true, "alert__api");
        }
    } catch (e) {
        setAlert(e, true, "alert__api");
    }
}



function showUpdateModal(apiKey) {
    document.getElementById("selected_api_key_id").value = apiKey.id;
    document.getElementById("update_api__name").value = apiKey.name;
    document.getElementById("update_api__description").value = apiKey.description;

    // Clear previous selections
    let select = document.getElementById('update_api__access_level');
    for(let i = 0; i < select.length; i++) {
        select[i].selected = apiKey.access_level.includes(select[i].value);
    }

    document.getElementById("update_api__status").value = apiKey.status;

    // Show the modal
    let modal = new bootstrap.Modal(document.getElementById('updateAPIKeyModal'));
    modal.show();
}

async function submitAPIKeyUpdate() {

    var api_key = localStorage.getItem("apikey");

    let id = document.getElementById("selected_api_key_id").value;
    let name = document.getElementById("update_api__name").value;
    let description = document.getElementById("update_api__description").value;
    let access_level = Array.from(document.getElementById("update_api__access_level").selectedOptions).map(option => option.value);
    let status = document.getElementById("update_api__status").value;

    
    try {
        let resp = await fetch("/v1/apikey/update", {
            method: "POST",
            headers: {
                "Infr-API-Key": api_key,  
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: id,
                name: name,
                description: description,
                access_level: access_level,
                status: status
            })
        });

        if (resp.ok) {
            setAlert("API key updated successfully.", false, "alert__api");
            getAPIKeys();  // Refresh the list
            let modal = bootstrap.Modal.getInstance(document.getElementById('updateAPIKeyModal'));
            modal.hide();
        } else {
            let data = await resp.json();
            setAlert(data?.message, true, "alert__api");
        }
    } catch (e) {
        setAlert(e, true, "alert__api");
    }
}

// Update the updateAPIKey function
function updateAPIKey(keyID) {
    let apiKey = apiKeyData.find(key => key.id == keyID);
    showUpdateModal(apiKey);
}

function copyAPIKey(keyID) {
    let apiKey = apiKeyData.find(key => key.id == keyID);
    navigator.clipboard.writeText(apiKey.key);
    setAlert("API key copied to clipboard.", false, "alert__api");
}

// Get API keys on apikey update in local storage
getAPIKeys();

