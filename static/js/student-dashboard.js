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

$(document).ready(() => {
    let cookie = getCookie('csrftoken');
    $.ajax({
	url:'/api/v1/student-portal/student-enrollments-data/',
	type:'get',
	headers: {'X-CSRFToken': cookie },
	success: function(data) {
	    $("#in-review-count").html(`<strong>${data.inreview_enrollments}</strong>`);
	    $("#on-time-count").html(`<strong>${data.ontime_submitted_enrollments}</strong>`);
	    $("#late-count").html(`<strong>${data.late_submitted_enrollments}</strong>`);
	    $("#completed-count").html(`<strong>${data.completed_enrollments}</strong>`)
	},
	error:function(request, status, error) {
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
});
