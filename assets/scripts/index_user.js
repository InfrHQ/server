
async function getUser() {
    var api_key = localStorage.getItem("apikey");
    if (!api_key) {
        return
    }
    try {
        let resp = await fetch("/v1/user/query/apikey", {
            method: "GET",
            headers: {
                "Infr-API-Key": api_key
            }
        });

        if (resp.ok) {
            let data = await resp.json();
            document.getElementById("user__name__hi").innerHTML = `Hey, ${data?.user?.name} 👋`;
            document.getElementById("user__name").value = data?.user?.name;
            document.getElementById("user__email").value = data?.user?.email_id;
            document.getElementById("user__description").value = data?.user?.description;
        } else {
            let data = await resp.json();
            setAlert(data?.message, true);
        }

    } catch (e) {
        setAlert(e, true);
    }
}


async function updateUser() {

    var apikey = localStorage.getItem("apikey");

    // Set btn to loading
    btn = document.getElementById("save__user");
    btn.innerHTML = "Loading...";
    btn.disabled = true;

    try {

        let user__name = document.getElementById("user__name").value;
        let user__description = document.getElementById("user__description").value;

        let resp = await fetch("/v1/user/update", {
            method: "POST",
            headers: {
                "Infr-API-Key": apikey,
                "Content-Type":"application/json"
            },
            body: JSON.stringify({
                name: user__name,
                description: user__description
                })
            });

        if (resp.ok) {
            setAlert("User updated successfully.", false);
        } else {
            let data = await resp.json();
            setAlert(data?.message, true);
        }
    } catch (e) {
        setAlert(e, true);
    }
    // Set btn to normal
    btn.innerHTML = "Save";
    btn.disabled = false;
}

// Get user on page load
getUser();