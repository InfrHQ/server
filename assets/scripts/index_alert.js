function showAlert(text, error = true, location = "alert__user") {
	alert = document.getElementById(location);
	alert.innerHTML = text;
	if (error) {
		alert.classList.add("alert-danger");
	} else {
		alert.classList.add("alert-success");
	}
	alert.style.display = "block";
}

function hideAlert(location = "alert__user") {
	alert = document.getElementById(location);
	alert.style.display = "none";
}

function setAlert(text, error = true, location = "alert__user") {
	showAlert(text, error, location);
	setTimeout(function () {
		hideAlert(location);
	}, 5000);
}
