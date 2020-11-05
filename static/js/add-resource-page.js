function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
	var cookies = document.cookie.split(';');
	for (var i = 0; i < cookies.length; i++) {
	    var cookie = cookies[i].trim();
	    // Does this cookie string begin with the name we want?
	    if (cookie.substring(0, name.length + 1) === (name + '=')) {
		cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		break;
	    }
	}
    }
    return cookieValue;
}

let cookie = getCookie('csrftoken');

function AddResource(event) {
    event.preventDefault();
    let data = new FormData(event.target);
    console.log(data);
    $.ajax({
	url: '/api/v1/generic/resources/',
	type: 'post',
	headers: {'X-CSRFToken': cookie },
	data: data,
	beforeSend: function(data) {
	    document.getElementById('resourceSubmitButton').innerHTML = `<span class="spinner-border spinner-border-sm"></span> Submitting`
	},
	processData: false,
	contentType: false,
	success: function(data) {
	    createNotification('success', 'Resource has been added.');
	    window.setTimeout(function () {
		location.reload(true);
	    }, 3000);
	},
	error: function(request, status, error) {
	    let errorString = `<h5>${error}</h5>`
	    if (request.responseJSON) {
		for (key in request.responseJSON) {
		    if (key !== undefined) {
			errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
		    }
		}
	    }
	    createNotification('error', message = errorString)
	},
	complete: function() {
	    document.getElementById('resourceSubmitButton').innerHTML = ``
	    document.getElementById('resourceSubmitButton').innerText = "Submit";
	}
    })
}
