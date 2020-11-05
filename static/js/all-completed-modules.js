function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
	var cookies = document.cookie.split(';');
	for (var i = 0; i < cookies.length; i++) {
	    var cookie = cookies[i].trim();
	    if (cookie.substring(0, name.length + 1) === (name + '=')) {
		cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		break;
	    }
	}
    }
    return cookieValue;
}

function ModuleFeedback(Moduleid, Studentid) {
    console.log(Moduleid);
    console.log(Studentid)
    let cookie = getCookie('csrftoken');
    $.ajax({
	url: `/api/v1/student-portal/completed-enrollment-feedback/?moduleID=${Moduleid}&studentID=${Studentid}`,
	method: "get",
	headers: { 'X-CSRFToken': cookie },
	success: function (data) {
	    console.log(data);
	    $(`#comment-${Moduleid}`).html(`${data[0].comment}`)
	},
	error: function(request, status, error) {
	    console.log(request.text)
	    let errorString = `<h5>${error}</h5>`
	    if (request.responseJSON) {
		for (key in request.responseJSON) {
		    if (key !== undefined) {
			errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
		    }
		}
	    }
	    createNotification('error', message = errorString)
	}
    })

}

