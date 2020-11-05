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

var addAssignment = function(moduleid){
    let url = window.location.href;
    let url_array = url.split('/')
    let stu_id = url_array[url_array.length-2];
    let cookie = getCookie('csrftoken');
    let date_due = new Date();
    $.ajax({
	url: '/api/v1/generic/enrollment/',
	type: 'post',
	data: { module: moduleid, student: stu_id, enrollment_method: 'MANUAL', enrollment_status: 'NOT-STARTED', date_set:  moment().format()},
	headers: { 'X-CSRFToken': cookie },
	success: (e) => {
	    location.reload();
	    createNotification('success', 'Assignment Added Successfully!')
	}, error(request, status, error) {
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

var updateAssignment = function () {
    let id = localStorage.getItem("assignment-id");
    let d_due = $("#date-due").val();
    let cookie = getCookie('csrftoken');

    $.ajax({
	url: `/api/v1/generic/enrollment/${id}/`,
	type: 'patch',
	data: { date_due: d_due },
	headers: { 'X-CSRFToken': cookie },
	success: (e) => {
	    $('#editModal').modal('toggle');
	    data_table.ajax.reload();
	    createNotification('success', 'Assignment Updated Successfully!')
	},  error(request, status, error) {
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

var deleteAssignment = function (AssignmentId) {
	let cookie = getCookie('csrftoken');
	$.ajax({
		url: '/api/v1/generic/enrollment/' + AssignmentId,
		type: 'delete',
		headers: { 'X-CSRFToken': cookie },
		success: (e) => {
		    location.reload();
		    createNotification('success', 'Assignment Deleted Successfully!')
		},  error(request, status, error) {
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

$(document).ready(() => {
	let url = window.location.href;
	let url_array = url.split('/')
	let stu_id = url_array[url_array.length - 2];
	let assignments_table = $("#specific-assignments-dashboard-table")
	data_table = assignments_table.DataTable({
		"fnDrawCallback": function(oSettings) {
            if (oSettings.aoData.length <= oSettings._iDisplayLength) {
                $('.dataTables_paginate').hide();
            }
            else{
                $('.dataTables_paginate').show();
            }
        },
		"processing": true,
		"serverSide": false,
		"ajax": {
			"url": `/api/v1/assignment-table/?userID=${stu_id}`,
			dataSrc: "",
		},
		"columns": [
			{
				"title": "Module ID",
				"data": "module.id",
				"width": "13%",
			},
			{
				"title": "Title",
				"data": "module.title",

			},
			{
				"title": "Status",
				"data": "enrollment_status",
				"width": '18%',
			},
			{
				"title": "Enroll Type",
				"data": "enrollment_method",
				"width": '20%',

			},
			{
				"title": "D.Set",
			    "render": (data, type, row) => {
				if (row.date_set != null) {
				    let formattedDate = new Date(row.date_set);
				    let month = formattedDate.getMonth() + 1;
				    return `${row.date_set}`
				}
				else {
				    return `Not Set Yet`
				}
			    }
			},
			{
				"title": "D.Started",
				"data": "date_to_start",
				"render": (data, type, row) => {
					if (row.date_to_start != null) {
					    let formattedDate = new Date(row.date_to_start);
					    let month = formattedDate.getMonth() + 1;
					    return `${row.date_to_start}`
					}
					else {
					    return `Not started Yet`
					}
				}
			},
			{
				"title": "D.Due",
				"render": (data, type, row) => {
					if (row.date_due != null) {
					    let formattedDate = new Date(row.date_due);
					    let month = formattedDate.getMonth() + 1;
					    return `${row.date_due}`
					}
					else {
						return `Not Set`
					}
				},
				"width": '10%',
			},
			{
				"title": "D.Completed",
				"render": (data, type, row) => {
					if (row.date_completed != null) {
					    let formattedDate = new Date(row.date_completed);
					    let month = formattedDate.getMonth() + 1;
					    return `${row.date_completed}`
					}
					else {
						return `Not completed Yet`
					}
				},
				"width": '15%',
			},
			{
				"title": "Tasks",
				"render": (data, type, row) => {
					if (row.total_tasks != null) {
						return `${row.tasks_completed + '/' + row.total_tasks}`
					}
					else {
						return `NA`
					}

				},
				"width": "5%",
			},
			{
				"title": "Edit",
				"render": (data, type, row) => {
					return `<a style="cursor: pointer;"><button type="button" data-toggle="modal" data-target="#editModal" onclick="localStorage.setItem('assignment-id', ${row.id})" style="background-color:#f9ca33" class= "btn btn-sm btn warning"><b>Edit</b></button></a>`
				}
			},
			{
				"title": "Delete",
				"render": (data, type, row) => {
					return `<a style="cursor: pointer;" onclick="deleteAssignment(${row.id})" style="color: #037afb; cursor: pointer;">Delete</a>`
				}
			},
		]
	})
})
