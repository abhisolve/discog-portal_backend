// variable used to store the ID of the current parent which is either created using modal popup
// or for whom modal popup is opened
var currentParentId = null;
var currentParentUserData = new Object({ 'to_save': new Object(), 'to_update': new Object(), 'parent': null });
var dataTable = null;

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


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

jQuery.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function initSelect2() {
    $('#parentsSelect').select2({
        dropdownParent: $("#userAddFormModal"),
        containerCssClass: 'selectContainer',
        placeholder: 'Parent ID',
        tags: true,
        width: "resolve",
        ajax: {
            url: 'api/v1/staff-portal/user-account-dashboard-parent-select-two/',
            data: function (params) {
                var query = {
                    search: params.term,
                    type: 'public'
                }

                return query;
            }
        }
    });

    $('#parentsSelect').on('select2:select', function (e) {
        let data = e.params.data;
        if (data.childrens !== undefined) {
            currentParentId = data.id;
            renderParentDataToModal(data, null)

        }
    });
}

function addNewUser(event) {
    // method used to open the modalpopup for adding a new user
    document.getElementById("userFormModalContent").innerHTML = `<div class="container-fluid">
    <form id="addParentForm" data-saved="false" onsubmit="addParent(event)">
        <div class="form-row">
            <div class="form-group col-md-3">
            <label for="parentSelect">Parent Id <span style="color:red">*</span></label>
            <select id="parentsSelect" style="width: 100% !important" id="parentId" name="parent_id" required></select>
            </div>
            <div class="form-group col-md-3">
                <label for="firstName">First Name<span style="color:red">*</span></label>
                <input type="text" class="form-control" id="firstName" placeholder="First name" name="first_name" required>
            </div>
            <div class="form-group col-md-3">
                <label for="sirName">Surname</label>
                <input type="text" class="form-control" id="sirName" placeholder="Surname" name="last_name">
            </div>
            <div class="form-group col-md-3">
                <label for="email">Email<span style="color:red">*</span></label>
                <input type="email" class="form-control" id="email" placeholder="Email" name="email" required>
            </div>
        </div>
        <button type="submit" class="btn btn-warning" id="addUserFormSubmit"><b>Save Parent</b></button>
    </form>
    </div>
    <!-- studen add container begins here -->
    <div class="container-fluid mt-4" id="UserCreateUpdateContainer">
    <!-- Data here will be added using JS by using JS template strings -->
    </div>
    <!--- student add container ends here -->
    <div class="container-fluid">
    <div class="row" style="justify-content:center;">
        <button id="addUserRowButton" class="btn btn-warning" onclick="addUserRow(event)" hidden ><b>Add Child</b></button>
    </div>
    </div>`
    document.getElementById("combinedModalChangeRow").hidden = true;
    $("#userAddFormModal").modal("show")
    initSelect2();
}

function renderParentDataToModal(data, modal_trigger) {
    // to render the parent data in modal which is either received by
    // view button in table or select two field in the new user modal

    document.getElementById("userFormModalContent").innerHTML = `<div class="container-fluid">
    <form id="addParentForm" data-saved="true" data-parent-id="${data.id}" onsubmit="addParent(event)">
        <div class="form-row">
            <div class="form-group col-md-3">
            <label for="parentId">Parent Id<span style="color:red">*</span></label>
                <input type="text" class="form-control" id="parentId" placeholder="Parent Id" name="parent_id"  value=${data.parent_id} required>
            </div> 
            <div class="form-group col-md-3">
                <label for="firstName">First Name<span style="color:red">*</span></label>
                <input type="text" class="form-control" value="${data.first_name}" id="firstName" placeholder="First name" name="first_name" required>
            </div>
            <div class="form-group col-md-3">
                <label for="sirName">Surname</label>
                <input type="text" class="form-control" id="sirName" placeholder="Surname" name="last_name" value="${data.last_name}">
            </div>
            <div class="form-group col-md-3">
                <label for="email">Email<span style="color:red">*</span></label>
                <input type="email" class="form-control" id="email" placeholder="Email" name="email" required value="${data.email}">
            </div>
        </div>
        <button type="submit" data-parent-id="${data.id}" class="btn btn-warning" id="addUserFormSubmit" style="font-weight:bolder;">Update Parent</button>
    </form>
    </div>
    <!-- studen add container begins here -->
    <div class="container-fluid" id="UserCreateUpdateContainer">
    <!-- Data here will be added using JS by using JS template strings -->
    </div>
    <!--- student add container ends here -->
    <div class="container-fluid">
    <div class="row" style="justify-content:center">
        <button id="addUserRowButton" class="btn btn-warning" onclick="addUserRow(event)"><b>Add Child</b></button>
    </div>
    </div>`
    data.childrens.forEach((item, index) => {
        renderUserRow(item)
    })
    document.getElementById("combinedModalChangeRow").hidden = false;
    if (modal_trigger !== null) {
        $("#userAddFormModal").modal(modal_trigger)
    }
}

function viewParentModal(event) {
    // method used to view the modal
    // popup for a user's parent
    currentParentId = event.target.getAttribute('data-id');
    $.ajax({
        url: `/api/v1/staff-portal/user-account-dashboard/${currentParentId}/`,
        method: "get",
        cache: false,
	beforeSend: function(){
	    event.target.innerHTML=`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading`
	},
        contentType: "application/json; charset=utf-8",
        success: function (data) {
	    $.confirm({
		title: 'Alert',
		content: 'Are you sure you want to edit this User?',
		buttons: {
		    confirm: function() {
			renderParentDataToModal(data, modal_trigger = 'show');
		    },
		    cancel: function () {
		    },
		}
	    });
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
            createNotification(type = 'error', message = errorString)
        },
	complete: function(){
	    // show original UI of the edit button
	    event.target.innerHTML = ``;
	    event.target.innerText = "Edit";
	}
    })

}

function deleteParent(event) {
    $.confirm({
        title: 'Confirm',
        content: 'Deleting this parent will delete all associate childrens too?',
        buttons: {
            confirm: function () {
                $.ajax({
                    url: `/api/v1/generic/parents/${currentParentId}`,
                    method: "delete",
		    beforeSend: function(xhr, settings){
			event.target.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Deleting Parent`
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}
		    },
		    cache: false,
                    success: function (data) {
                        createNotification(type = 'success', message = 'Parent Deleted')
                        data_table.ajax.reload();
                        $("#userAddFormModal").modal("hide")
                        $("#userAddFormModal").modal("show")
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
                        createNotification(type = 'error', message = errorString)
                    },
		    complete: function(){
			event.target.innerHTML= ``;
			event.target.innerText = "Delete Parent";
		    }
                })
            },
            cancel: function () {
            }
        }
    });
}


function addParent(event) {
    event.preventDefault()
    let formData = new FormData(event.target)
    $.ajax({
        type: event.target.getAttribute('data-parent-id') === null ? 'POST' : 'PATCH',
        url: event.target.getAttribute('data-parent-id') === null ? '/api/v1/generic/parents/' : `/api/v1/generic/parents/${event.target.getAttribute('data-parent-id')}/`,
        cache: false,
        contentType: false,
        processData: false,
        data: formData,
        success: function (data) {
            if (event.target.getAttribute('data-parent-id') !== null) {
                createNotification(type = 'success', message = 'Parent Successfully updated')
            }
            else {
                createNotification(type = 'success', message = 'Parent Successfully created')
                
                document.getElementById("addUserFormSubmit").innerText = "Update Parent"
                // show the add user button
                document.getElementById("addUserRowButton").hidden = false;
            }
            event.target.setAttribute('data-parent-id', data.id)
            currentParentId = data.id;
            data_table.ajax.reload();
            
        },
        error: function (request, status, error) {
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

function addUserRow(event) {
    // the footer of modal popup contain two
    // button this method is used to show the footer
    // with that two buttons.
    renderUserRow(null)
    if (document.getElementById("combinedModalChangeRow").hidden) {
        // show the combined Modal change row with its content
        // This row contain "Delete User" and  "Confirm All Changes"
        // button.
        document.getElementById("combinedModalChangeRow").hidden = false;
    }
}

function deleteThisRow(event) {
    if (event.target.id == `deleteUser_${event.target.form.getAttribute('data-db-id')}`) {
        // This block will run if the user represented by the row
        // is already saved in the database
        $.confirm({
            title: 'Confirm',
            content: 'This User exists in the database, Are you sure you want to delete it?',
            buttons: {
                confirm: function () {
                    $.ajax({
                        url: `/api/v1/generic/users/${event.target.id.split('_')[1]}`,
                        method: "delete",
                        cache: false,
                        success: function (data) {
                            createNotification(type = 'success', message = 'User Deleted')
                            event.target.form.remove()
                            data_table.ajax.reload()
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
                            createNotification(type = 'error', message = errorString)
                        }
                    })
                },
                cancel: function () {
                }
            }
        });

    }
    else {
        event.target.form.remove()
    }
}

function renderUserRow(userData) {
    let id = Math.floor((Math.random() * 1000) + 1);
    let db_id = null;
    let email = "";
    let student_id = "";
    let first_name = "";
    let last_name = "";
    let student_type = "";

    if (userData !== null) {
        id = userData.id;
        db_id = id;
        email = userData.email;
        student_id = userData.student_id;
        first_name = userData.first_name;
        last_name = userData.last_name;
        student_type = userData.student_type ? userData.student_type : userData.roll_number;    
    }

    $("#UserCreateUpdateContainer").append(`<form onsubmit="createUser(event)" id="studentForm_${id}" data-db-id="${db_id}"><div class="form-row mt-4" data-db-id="${db_id}" >
        <div class="form-group col-md-2">
            <label for="studentId_${id}">Student Id<span style="color:red">*</span></label>
            <input type="text" class="form-control" id="studentId_${id}" placeholder="Student Id"
                name="student_id"  value="${student_id}"required>
        </div>
        <div class="form-group col-md-2">
            <label for="firstName_${id}">First Name<span style="color:red">*</span></label>
            <input type="text" class="form-control" id="firstName_${id}" placeholder="First name"
                name="first_name" value="${first_name}" required>
        </div>
        <div class="form-group col-md-2">
            <label for="sirName_${id}">Surname</label>
            <input type="text" class="form-control" id="lastName_${id}" placeholder="Surname"
                name="last_name" value="${last_name}">
        </div>
        <div class="form-group col-md-2">
            <label for="email_${id}">Email<span style="color:red">*</span></label>
            <input type="email" class="form-control" id="email_${id}" placeholder="Email" value="${email}" name="email" required>
        </div>
        <div class="form-group col-md-2">
            <label for="studentType_${id}">Student Type<span style="color:red">*</span></label>
            <input type="text" class="form-control" id="studentType_${id}" placeholder="Student Type" value="${student_type}" name="student_type" required>
        </div>
        <div class="form-group col-md-1">
            <label for="isActive_${id}">Active</label>
            <input type="checkbox" class="form-control" id="isActive_${id}"  name="is_active">
        </div>
        <div class="form-group col-md-1">
            <button type="button" class="btn btn-sm" id="deleteUser_${id}" data-db-id=${db_id} onclick="deleteThisRow(event)">X</button>
        </div>
    </div>
    </form>`)
    if (userData !== null) {
	if (userData.is_active == true) {
	    document.getElementById(`isActive_${id}`).checked = true;
	}
    }
}


function updateUsersInModalPopUp(data) {
    // once the data is sent to backend
    // related to changes in the users
    // in the modal popup, This method is used
    // to update the users.
    document.getElementById("UserCreateUpdateContainer").innerHTML = "";
    data.forEach((item, index) => {
        renderUserRow(item)
    })
}

function createUser(form) {
    // this method is used to add data to currentParentUserData
    // object. It validate the input fields and add data of the
    // users to that object
    console.log(`create user is called for form ${form}`)
    let studentId = form.id.split('_')[1]
    console.log("student ID is", studentId)
    if (form.reportValidity()) {
        // reportValidity check for validtion at
        // html level and raise HTML validation tooltips
        // if form in not valid w.r.t to HTML attribute 
        // (ie: required, input type validatation etc)
        // along with validation at html level it will alos return
        //  return True or False based upon that.
        // This block will run if the form is valid
        roll_number = document.getElementById(`studentId_${studentId}`).value;
        first_name = document.getElementById(`firstName_${studentId}`).value;
        last_name = document.getElementById(`lastName_${studentId}`).value;
        email = document.getElementById(`email_${studentId}`).value;
        student_type = document.getElementById(`studentType_${studentId}`).value;
        is_active = document.getElementById(`isActive_${studentId}`).checked;

        if (form.id != "studentForm_" + form.getAttribute("data-db-id")) {
            // This condition means user already exists in the database
            // in the backend.
            currentParentUserData['to_save'][`${studentId}`] = {
                'roll_number': roll_number,
                'first_name': first_name,
                "last_name": last_name,
                "email": email,
                "parent": currentParentId,
                "is_active": is_active,
                "student_type": student_type,
                "is_student": true
            }
            console.log(`current parent user data is ${currentParentUserData}`)
        }
        else {
            // this condition means user doesn't exists in the database
            currentParentUserData['to_update'][`${studentId}`] = {
                'id': studentId,
                'roll_number': roll_number,
                'first_name': first_name,
                "last_name": last_name,
                "email": email,
                "parent": currentParentId,
                "is_active": is_active,
                "student_type": student_type,
                "is_student": true,
            }
        }

    }
    else {
        // just to stop the flow
        // so the data is not sent to the backend.
        throw Error(`Form ID ${form.id} has validation errors`)
    }
}

function confirmChanges(event) {
    // method called on the confirm changes button click
    // This button exists in the footer of Modal popup.
    let formContainer = document.getElementById("UserCreateUpdateContainer").getElementsByTagName('form')
    for (form of formContainer) {
        createUser(form)
    }
    console.log("User Data is", currentParentUserData)
    // add parent to the currentParentUserData
    //  object as it is required by backend.
    currentParentUserData['parent'] = currentParentId
    $.ajax({
        url: "/api/v1/staff-portal/user-account-dashboard/",
        method: "POST",
	beforeSend: function(xhr, settings){
	    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
	    console.log("event.target is ", event.target)
	    event.target.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Confirming Changes`;
	},
        cache: false,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(currentParentUserData),
        success: function (data) {
            createNotification(type = 'success', message = 'User Information succesffuly updated')
            updateUsersInModalPopUp(data)
            currentParentUserData = new Object({ 'to_save': new Object(), 'to_update': new Object(), 'parent': null });
	    $("#userAddFormModal").modal("hide");
            data_table.ajax.reload();
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
            createNotification(type = 'error', message = errorString)
        },
        complete: function () {
            event.target.innerHTML = ``;
	    event.target.innerText = "Confirm Changes";
        }
    })
}



function search_table(event) {
    /*
        Method used to perform the search operations given on the LHS
        of the user-account-dashboard page
    */

    function reArrangeDataTableSearch(clearIDArray) {
        data_table.columns().search("").draw();
        for (let elementID of clearIDArray) {
            document.getElementById(elementID).value = ""
        }

    }
    if (event.target.id == "searchByParentId") {
        reArrangeDataTableSearch(['searchByParentName', 'searchByStudentId', 'searchByStudentName', "searchByStudentType"]);
        data_table.columns(0).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByParentName") {
        reArrangeDataTableSearch(['searchByParentId', 'searchByStudentId', 'searchByStudentName', "searchByStudentType"]);
        data_table.column(1).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStudentName") {
        reArrangeDataTableSearch(["searchByParentId", "searchByParentName", "searchByStudentId", "searchByStudentType"]);
        data_table.columns(4).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStudentId") {
        reArrangeDataTableSearch(["searchByParentId", "searchByParentName", "searchByStudentName", "searchByStudentType"]);
        data_table.columns(3).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStudentType") {
        reArrangeDataTableSearch(["searchByParentId", "searchByParentName", "searchByStudentName", "searchByStudentId"]);
        data_table.columns(5).search(event.target.value).draw();
    }
}

function renderTable() {
    let user_account_dashboard_table = $("#userAccountDashboardTable")
    data_table = user_account_dashboard_table.DataTable({
        "fnDrawCallback": function (oSettings) {
            if (oSettings.aoData.length <= oSettings._iDisplayLength) {
                $('.dataTables_paginate').hide();
            }
            else {
                $('.dataTables_paginate').show();
            }
        },
        "processing": true,
        "serverSide": false,
        "ajax": {
            "url": '/api/v1/staff-portal/user-account-dashboard',
            "dataSrc": ""
        },
        "columnDefs": [
            { "className": "dt-center", "targets": "_all" }
        ],
        "columns": [
            {
                "title": "Parent ID",
                "render": (data, type, row) => {
                    if (row.user.parent) {
                        return row.user.parent.parent_id
                    }
                    else {
                        return "N/A"
                    }
                }
            },
            {
                "title": "Parent Name",
                "render": (data, type, row) => {
                    if (row.user.parent && row.user.parent.first_name && row.user.parent.last_name) {
                        return `${row.user.parent.first_name} ${row.user.parent.last_name}`
                    }
                    else if (row.user.parent && row.user.parent.first_name) {
                        return row.user.parent.first_name
                    }
                    else {
                        return "N/A"
                    }
                }
            },
            {
                "title": "No.",
                "data": "sibling_number"
            },
            {
                "title": "Student ID",
                "render": (data, type, row) => {
                    return row.roll_number
                }
            },
            {
                "title": "Student Name",
                "render": (data, type, row) => {
                    if (row.user.first_name && row.user.last_name) {
                        return `${row.user.first_name} ${row.user.last_name}`
                    }
                    else if (row.user.first_name) {
                        return row.user.first_name
                    }
                    else {
                        return "N/A"
                    }

                }
            },
            {
                "title": "S_Type",
                "render": (data, type, row) => {
                    if (row.student_type) {
                        return row.student_type
                    }
                    else {
                        return 'N/A'
                    }
                }
            },
            {
                "title": "Act/Not Active",
                "render": (data, type, row) => {
                    if (row.user.is_active) {
                        return "Active"
                    }
                    else {
                        return "Not Active"
                    }
                }
            },
            {
                "title": "Edit",
                "render": (data, type, row) => {
                    return `<button class='btn btn-sm btn-warning' data-id="${row.user.parent.id}" onclick="viewParentModal(event)" style="cursor:pointer"><b data-id="${row.user.parent.id}">Edit</b></button>`
                }
            }
        ]
    })
}
$(document).ajaxStart( function(){
    // disable all button on ajax requests
    $('button').attr('disabled','disabled');
    
})
$(document).ajaxComplete( function(){
    // disable all button on ajax requests
    $('button').removeAttr('disabled');
    
})
$(document).ready(() => {
    console.log("document is ready")
    renderTable()
});
