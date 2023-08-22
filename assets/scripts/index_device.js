var deviceData = [];

// Fetch the devices and display them
async function getDevices() {
    var api_key = localStorage.getItem("apikey");
    if (!api_key) {
        return
    }

    try {
        let resp = await fetch("/v1/device/query", {
            method: "GET",
            headers: {
                "Infr-API-Key": api_key
            }
        });

        if (resp.ok) {
            let data_full = await resp.json();
            let data = data_full?.devices;
            deviceData = data;
            let tbody = document.getElementById('devices_tbody');
            tbody.innerHTML = '';

            data.forEach(device => {
                let row = `<tr>
                    <td>${device.name}</td>
                    <td>${device.description}</td>
                    <td>${device.device_type}</td>
                    <td>${device.status}</td>
                    <td>
                        <button class="btn btn-sm btn-primary m-1" onclick="updateDevice('${device.id}')">Edit</button>
                        <!-- Additional action buttons can be added here -->
                    </td>
                </tr>`;
                tbody.innerHTML += row;
            });
        } else {
            let data = await resp.json();
            setAlert(data?.message, true, "alert__device");
        }
    } catch (e) {
        setAlert(e, true, "alert__device");
    }
}

// Create a new Device
async function createDevice() {
    var api_key = localStorage.getItem("apikey");
    try {
        let name = document.getElementById("device__name").value;
        let description = document.getElementById("device__description").value;
        let device_type = document.getElementById("device__type").value;

        let resp = await fetch("/v1/device/create", {
            method: "POST",
            headers: {
                "Infr-API-Key": api_key,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                description: description,
                device_type: device_type
            })
        });

        if (resp.ok) {
            setAlert("Device added successfully.", false, "alert__device");
            getDevices();
        } else {
            let data = await resp.json();
            setAlert(data?.message, true, "alert__device");
        }
    } catch (e) {
        setAlert(e, true, "alert__device");
    }
}

async function submitDeviceUpdate() {
    var api_key = localStorage.getItem("apikey");

    let id = document.getElementById("selected_device_id").value;
    let name = document.getElementById("update_device__name").value;
    let description = document.getElementById("update_device__description").value;
    let device_type = document.getElementById("update_device__type").value;

    try {
        let resp = await fetch("/v1/device/update", {
            method: "POST",
            headers: {
                "Infr-API-Key": api_key,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: id,
                name: name,
                description: description,
                device_type: device_type
            })
        });

        if (resp.ok) {
            setAlert("Device updated successfully.", false, "alert__device");
            getDevices();  // Assuming a function to refresh the list
            let modal = bootstrap.Modal.getInstance(document.getElementById('updateDeviceModal'));
            modal.hide();
        } else {
            let data = await resp.json();
            setAlert(data?.message, true, "alert__device");
        }
    } catch (e) {
        setAlert(e, true, "alert__device");
    }
}

function showDeviceUpdateModal(device) {
    document.getElementById("selected_device_id").value = device.id;
    document.getElementById("update_device__name").value = device.name;
    document.getElementById("update_device__description").value = device.description;
    document.getElementById("update_device__type").value = device.device_type;

    // Show the modal
    let modal = new bootstrap.Modal(document.getElementById('updateDeviceModal'));
    modal.show();
}


async function updateDevice(id) {
    let device = deviceData.find(d => d.id === id);
    if (!device) {
        return
    }
    showDeviceUpdateModal(device);
}

    
// On page load or on some trigger, fetch the devices
getDevices();
