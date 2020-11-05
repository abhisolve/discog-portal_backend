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

function ChangeResourceFile(event) {
    event.preventDefault();
    //let cookie = getCookie('csrftoken');
    let id = localStorage.getItem('resourceID');
    let data = new FormData(event.target);
    $.ajax({
	url:`/api/v1/generic/resources/${id}/`,
	type:'patch',
	headers: {'X-CSRFToken': cookie },
	data: data,
	beforeSend: function(){
	    document.getElementById('changeFileButton').innerHTML = `<span class="spinner-border spinner-border-sm"></span> Changing`
	},
	processData: false,
	contentType: false,
	success: function (data) {
	    createNotification(type= 'success', message = 'Resource File Updated successfully.');
	    data_table.ajax.reload();
	    $('#change-file-modal').modal('toggle');
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
	    createNotification(type = 'error', message = errorString)
	},
	complete: function(){
	    document.getElementById('changeFileButton').innerHTML = ``
	    document.getElementById('changeFileButton').innerHTML = `<b>Change</b>`;
	}
    })
}

function deleteResource(resourceID) {
    //let cookie = getCookie('csrftoken');
    $.ajax({
	url: `/api/v1/generic/resources/${resourceID}/`,
	type:'delete',
	headers: {'X-CSRFToken': cookie },
	success: function(data) {
	    createNotification(type = 'success', message = 'Resource has been deleted successfully');
	    data_table.ajax.reload();
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
	    createNotification(type = 'error', message = errorString)
	}
    })
}

function unassignStudents(studentID, resourceID) {
    console.log(studentID);
    console.log(resourceID);
    $.ajax({
	url:`/api/v1/un-assign-students/${resourceID}/`,
	type: 'patch',
	headers: {'X-CSRFToken': cookie},
	data: {student: studentID},
	success: function (data) {
	    createNotification(type= 'success', message = 'Resource has been Un-Assigned.');
	    unassign_table.ajax.reload();
	    data_table.ajax.reload();
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
	    createNotification(type = 'error', message = errorString)
	}
    })
}

function assignStudents(studentID, resourceID) {
    console.log(studentID);
    console.log(resourceID);
    $.ajax({
	url:`/api/v1/assign-students/${resourceID}/`,
	type: 'patch',
	headers: {'X-CSRFToken': cookie},
	data: {student: studentID},
	success: function (data) {
	    createNotification(type= 'success', message = 'Resource has been Assigned.');
	    assign_table.ajax.reload();
	    data_table.ajax.reload();
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
	    createNotification(type = 'error', message = errorString)
	}
    })
}

function showUnassignStudents(resourceID) {
    let unassign_students_datatable = $("#students-table")
    unassign_table = unassign_students_datatable.DataTable({
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
	"destroy": true,
	"searching": true,
	"paging": true,
	"ajax": {
	    "url": `/api/v1/student-detail-by-resource/?resourceID=${resourceID}`,
	    dataSrc: "",
	},
	"columns": [
	    {
		"title": "Student ID",
		"data": "roll_number",
	    },
	    {
		"title": "Student Name",
		"render": (data, type, row) => {
		    return `${row.user.first_name} ${row.user.last_name}`
		},
	    },
	    {
		"title": "Student Type",
		"render": (data, type, row) => {
		    return `${row.student_type}`
		},
	    },
	    {
		"title": "Active",
		"render": (data, type, row) => {
		    if (row.user.is_active == true)
		    {
			return `YES`
		    }
		    else if (row.user.is_active == false)  {
			return `NO`
		    }
		},
	    },
	    {
		"title": "Current Module",
		"render": (data, type, row) => {
		    if (row.current_module[0] != null){
			return `${row.current_module}`
		    }
		    else {
			return `NA`
		    }
		},
	    },
	    {
		"title": "Total Resources",
		"data": "total_resource",
	    },
	    {
		"title": "Un-Assign",
		"render": (data, type, row) => {
		    return `<button type="button" onclick="unassignStudents(${row.user.id}, ${resourceID})" style="background-color:#f9ca33;" class="btn btn-sm btn warning ml-2"><b>Un-Assign</b></button>`
		},
	    }
	]
    })
    $('#view-student-modal').modal('toggle');
}

function showAssignStudents(resourceID) {
    let assign = true;
    let assign_students_datatable = $("#students-table")
    assign_table = assign_students_datatable.DataTable({
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
	"destroy": true,
	"searching": true,
	"paging": true,
	"ajax": {
	    "url": `/api/v1/student-detail-by-resource/?resourceID=${resourceID}&assign=${assign}`,
	    dataSrc: "",
	},
	"columns": [
	    {
		"title": "Student ID",
		"data": "roll_number",
	    },
	    {
		"title": "Student Name",
		"render": (data, type, row) => {
		    return `${row.user.first_name} ${row.user.last_name}`
		},
	    },
	    {
		"title": "Student Type",
		"render": (data, type, row) => {
		    return `${row.student_type}`
		},
	    },
	    {
		"title": "Active",
		"render": (data, type, row) => {
		    if (row.user.is_active == true)
		    {
			return `YES`
		    }
		    else if (row.user.is_active == false)  {
			return `NO`
		    }
		},
	    },
	    {
		"title": "Current Module",
		"render": (data, type, row) => {
		    if (row.current_module[0] != null){
			return `${row.current_module}`
		    }
		    else {
			return `NA`
		    }
		},
	    },
	    {
		"title": "Total Resources",
		"data": "total_resource",
	    },
	    {
		"title": "Assign",
		"render": (data, type, row) => {
		    return `<button type="button" onclick="assignStudents(${row.user.id}, ${resourceID})" style="background-color:#f9ca33;" class="btn btn-sm btn warning ml-2"><b>Assign</b></button>`
		},
	    }
	]
    })
    $('#view-student-modal').modal('toggle');
}
	    
$(document).ready(() => {
    let all_resources_datatable = $("#all-resources-table")
    data_table = all_resources_datatable.DataTable({
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
	    "url": 'api/v1/resource-manager-page',
	    dataSrc: "",
	},
	"columns": [
	    {
		"title": "Title",
		"data": "resource_title",
		"width": "10%",
	    },
	    {
		"title": "Short Ttile",
		"render": (data, type, row) => {
		    if (row.resource_short_title != null)
		    {
			return `${row.resource_short_title}`
		    }
		    else {
			return `NA`
		    }
		},
		"width": "8%",
	    },
	    {
		"title": "Suggested Student Type",
		"data": "suggested_student_type",
	    },
	    {
	    	"title": "Description",
	    	"render": (data, type, row) => {
	    	    return `${row.resource_description}`
		},
		"width": '14%',
	    },
	    {
		"title": "Date Modified",
		"render": (data, type, row) => {
		    return `${row.updated}`
		},
		"width": '10%',
	    },
	    {
		"title": "No. of Students",
		"render": (data, type, row) => {
		    return `${row.users_count} nos.`
		},
		"width": '11%',
	    },
	    {
		"title": "Change File",
		"render": (data, type, row) => {
		    return `<button type="button" data-toggle="modal" onclick="localStorage.setItem('resourceID', ${row.id})" data-target="#change-file-modal" style="background-color:#f9ca33" class="btn btn-sm btn warning"><b>Change File</b></button>`
		},
		"width":'9%',
	    },
	    {
		"title": "Assign Resource",
		"render": (data, type, row) => {
		    return `<button type="button"  onclick="showAssignStudents(${row.id})" style="background-color:#f9ca33;" class= "btn btn-sm btn warning ml-2"><b>Assign</b></button>`
		},
		"width": '12%',
	    },
	    {
		"title": "Un-Assign Resource",
		"render": (data, type, row) => {
		    return `<button type="button"  onclick="showUnassignStudents(${row.id})" style="background-color:#f9ca33;" class= "btn btn-sm btn warning ml-2"><b>Un-Assign</b></button>`
		},
		"width": '13%',
	    },
	    {
		"title": "Edit || Delete",
		"render": (data, type, row) => {
		    return `<a href="/edit-resource/${row.id}/"><button type="button" style="background-color:#f9ca33" class="btn btn-sm btn warning"><b>Edit</b></button></a> || <a style="cursor: pointer; color: #037afb; " onclick="deleteResource(${row.id})">Delete</a>`
		},
		"width":'12%',
	    }
	]
    })
});
