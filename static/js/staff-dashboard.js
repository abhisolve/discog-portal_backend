// variable used to store the ID of the current parent which is either created using modal popup
// or for whom modal popup is opened
var currentUserId = null;
var currentUserData = new Object({ 'to_save': new Object(), 'to_update': new Object(), 'parent': null });
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

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function randomPassword(length) {
    var chars = "abcdefghijklmnopqrstuvwxyz!@#$%^&*()-+<>ABCDEFGHIJKLMNOP1234567890";
    var pass = "";
    for (var x = 0; x < length; x++) {
        var i = Math.floor(Math.random() * chars.length);
        pass += chars.charAt(i);
    }
    return pass;
}

function renderModuleCategoryRow(categoryData, assignedModules = null) {
    // fuction used to render the row of module category and inside
    // it it will render the cols of modules in a row of 6 cols.

    function verifyChecked(assignedModules, moduleId) {
        // closure return true or false if assigned module contain the
        // moduleId in it.
        console.log(assignedModules, moduleId)
        if (assignedModules !== null) {
            if (assignedModules.includes(moduleId)) { console.log("checked", moduleId); return true; }
            else { return false }
        }
        else {
            return false;
        }
    }
    function createModuleCol(modul, assignedModules){
        // closure to return each row column representing each 
        // module checkbox in the staff dashboard Modal.

        let current_row = `<div class="col-md-2">
                <div class="input-group">
                <label for="module_${modul.id}" class="main">${modul.title}
                ${verifyChecked(assignedModules, modul.id) ? `<input class="form-control" type="checkbox" data-module-id="${modul.id}" id="module_${modul.id}" checked/>`:
                `<input class="form-control" type="checkbox" data-module-id="${modul.id}" id="module_${modul.id}"/>`}
                <span class="geekmark"></span>
                </label>
                </div>
                </div>`
                return current_row;
    }

    function renderModulesOfModuleCategory(modules, assignedModules) {
        //cloure to render the Module inside the module
        // category section in the main function.
        let returnTemplate = $(`<div></div>`);
        let currentRow = $(`<div class="row"></div>`);
        let loop_counter = 1;

        for (modul of modules) {
            // logic to render 6 modules in
            // each row of module category
            if (loop_counter <= 6) {
                currentRow.append(createModuleCol(modul, assignedModules));
            }
            else {
                if (loop_counter == 7) {
                    loop_counter = 1;
                    returnTemplate.append(currentRow);
                    currentRow = $(`<div class="row"></div>`);
                }
                currentRow.append(createModuleCol(modul, assignedModules));
            }
            loop_counter += 1;
        }
        returnTemplate.append(currentRow);
        return returnTemplate.html();
    }

    // main function body begins here
    if (categoryData.length != 0) {
        for (category of categoryData) {
            $("#moduleSelectionContainer").append(`<div class="container-fluid" id="module_category_${category.id}">
            <h5 class="mt-2 mb-4">${category.category_type}:</h5>
            ${renderModulesOfModuleCategory(category.modules, assignedModules)}         
        </div>`)
        }
    }
    else {
        $("#moduleSelectionContainer").append(`<p style="text-align:center">No Module Category exists in the Database</p>`)
    }
}
function updateTheRenderedModalFormWithUserData(userData = null) {
    // This method is only called when you have staff details
    // when we have staff details after click view button on table
    // or by creating a new Staff details using modal popup.
    if (userData !== null) {
        document.getElementById("moduleLoader").hidden = true;
        document.getElementById("staffIdInput").value = userData.staff_id;
        document.getElementById("firstName").value = userData.user_data.first_name;
        document.getElementById("sirName").value = userData.user_data.last_name;
        document.getElementById("email").value = userData.user_data.email;
        document.getElementById("role").value = userData.staff_role;
        document.getElementById("addUserForm").setAttribute('data-id', userData.id)
        renderModuleCategoryRow(categoryData = userData.module_categories, assignedModules = userData.assigned_modules);
        $("<input />").attr("type", "hidden").attr("name", "user").attr('id', 'userId').attr("value", userData.user_data.id).appendTo($("#addUserForm"));
        document.getElementById("modalChangeRow").hidden = false;
        document.getElementById("deleteUserButton").hidden = false;
        document.getElementById("deleteUserButton").setAttribute('data-user-id', userData.user_data.id)
    }
    else {
        // call the API for available Modules that can be assigned
        // to this staff user.
        $.ajax({
            url: `api/v1/staff-portal/staff-dashboard-module-category/`,
            method: "get",
            cache: false,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                document.getElementById("moduleLoader").hidden = true;
                renderModuleCategoryRow(categoryData = data, assignedModules = null);
                document.getElementById("modalChangeRow").hidden = false;
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
    }
}

function renderUserToModal(userData = null) {
    // method used to open the modalpopup for adding a new user
    document.getElementById("userFormModalContent").innerHTML = `<div class="container-fluid">
    <form id="addUserForm" onsubmit="addUser(event)">
        <div class="form-row">
            <div class="form-group col-md-2">
            <label for="staffIdInput">Staff Id<span style="color:red">*</span></label>
            <input type="text" class="form-control" id="staffIdInput" name="staff_id"  placeholder="staff ID" required>
            </div>
            <div class="form-group col-md-2">
                <label for="firstName">First Name<span style="color:red">*</span></label>
                <input type="text" class="form-control" id="firstName" placeholder="First name" name="first_name" required>
            </div>
            <div class="form-group col-md-2">
                <label for="sirName">Surname</label>
                <input type="text" class="form-control" id="sirName" placeholder="Surname" name="last_name">
            </div>
            <div class="form-group col-md-2">
                <label for="email">Email<span style="color:red">*</span></label>
                <input type="email" class="form-control" id="email" placeholder="Email" name="email" required>
            </div>
            <div class="form-group col-md-2">
                <label for="role">Role<span style="color:red">*</span></label>
                <select class="form-control" id="role" placeholder="Role" name="role" required>
                <option value="" disabled selected>Select a Role</option>
                <option value="MAN">Manager</option>
                <option value="MOD">Moderator</option>
                <option value="CC">Content Creator</option>
                </select>
            </div>
        </div>
    
    <!-- studen add container begins here -->
    <div class="container-fluid mt-4 p-2" id="moduleSelectionContainer" style="background-color:#80808040">
    <div class="container-fluid">
    <div class="row">
    <h5> Access To:</h5>
    </div>
    <div class="loader" id="moduleLoader"></div>
    <!-- Data here will be appended using JS by using JS template strings -->
    </div>
    </div>
    <div class="row mt-4" id="modalChangeRow" hidden>
                    <div class="col-md-6"><button type="button" class="btn btn-secondary btn-md" id="deleteUserButton" onclick="deleteUser(event)" style="float:left" hidden>Delete User</button>
                    </div>
                    <div class="col-md-6"><button class="btn btn-md btn-warning" type="submit" style="float:right;">Confirm Changes</button></div>
                </div>
                </form>
                </div>`
    updateTheRenderedModalFormWithUserData(userData)
    $("#userAddFormModal").modal("show")
}

function viewStaffModal(event) {
    // method used to view the modal
    // popup for a user's staff details
    console.log(event.target)
    currentUserId = event.target.getAttribute('data-id');
    $.ajax({
        url: `/api/v1/staff-portal/staff-dashboard-staff-details/${event.target.getAttribute('data-id')}/`,
        method: "get",
        cache: false,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
	    $.confirm({
		title: 'Alert',
		content: 'Are you sure you qnt to edit this Staff detail?',
		buttons: {
		    confirm: function() {
			renderUserToModal(userData = data);
		    },
		    cancel: function() {
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
        }
    })

}

function deleteUser(event) {
    console.log("event target for delete is", event.target)
    console.log("event target user-id attribute is", event.target.getAttribute('data-user-id'))
    $.confirm({
        title: 'Confirm',
        content: 'Deleting this user will delete the staff role and premissions associated with it?',
        buttons: {
            confirm: function () {
                $.ajax({
                    url: `/api/v1/generic/users/${event.target.getAttribute('data-user-id')}/`,
                    method: "delete",
                    cache: false,
                    success: function (data) {
                        createNotification(type = 'success', message = 'User Deleted')
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
                    }
                })
            },
            cancel: function () {
            }
        }
    });
}


function addUser(event) {
    // This method is called when user is new user
    // is added using "confirm changes", button in modal popup
    // the submit event is fired by the form in the Modal Popup

    event.preventDefault()
    let requestData = {
        'is_teacher': true,
        'staff_id': $("#staffIdInput").val(),
        'first_name': $('#firstName').val(),
        'last_name': $("#sirName").val(),
        'email': $("#email").val(),
        'staff_role': $("#role").val(),
        'assigned_modules': [],
    }
    if (event.target.getAttribute('data-id') !== null) {
        // it means the user already exists in the database
        // and we need to update data. In such case we need to supply
        // staff details model ID and user ID for updating the associate
        // user data
        requestData['user'] = $("#userId").val()
        requestData['id'] = event.target.getAttribute('data-id')
    }
    else{
        requestData['password'] = randomPassword(10);
    }

    $("#moduleSelectionContainer").find(':checkbox').each((index, element) => {
        if (element.checked) {
            requestData.assigned_modules.push(element.getAttribute('data-module-id'))
        }
    });
    console.log("Request data is ", requestData)
    $.ajax({
        type: event.target.getAttribute('data-id') === null ? 'POST' : 'PATCH',
        url: event.target.getAttribute('data-id') === null ? '/api/v1/staff-portal/staff-dashboard-staff-details/' : `/api/v1/staff-portal/staff-dashboard-staff-details/${event.target.getAttribute('data-id')}/`,
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(requestData),
        success: function (data) {
            if (event.target.getAttribute('data-id') !== null) {
                createNotification(type = 'success', message = 'Staff Successfully updated')
            }
            else {
                createNotification(type = 'success', message = 'Staff Successfully created');
                renderUserToModal(data);
            }
            event.target.setAttribute('data-id', data.id);
            currentUserId = data.id;
            data_table.ajax.reload();
	    $("#userAddFormModal").modal('hide');
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
    if (event.target.id == "searchByStaffId") {
        reArrangeDataTableSearch(['searchByStaffName', 'searchByAccessTotal', 'searchByStaffRole']);
        data_table.columns(0).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStaffName") {
        reArrangeDataTableSearch(['searchByStaffId', 'searchByAccessTotal', 'searchByStaffRole']);
        data_table.column(1).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStaffRole") {
        reArrangeDataTableSearch(["searchByStaffId", "searchByStaffName", "searchByAccessTotal"]);
        data_table.columns(2).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByAccessTotal") {
        reArrangeDataTableSearch(["searchByStaffId", "searchByStaffName", "searchByStaffRole",]);
        data_table.columns(3).search(event.target.value).draw();
    }
}

function renderTable() {
    let staff_account_dashboard_table = $("#staffAccountDashboardTable")
    data_table = staff_account_dashboard_table.DataTable({
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
            "url": '/api/v1/staff-portal/staff-dashboard-datatable',
            "dataSrc": ""
        },
        "columnDefs": [
            { "className": "dt-center", "targets": "_all" }
        ],
        "columns": [
            {
                "title": "Staff ID",
                "data": "staff_id"
            },
            {
                "title": "Staff Name",
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
                "title": "Staff Role",
                "data": "staff_role"
            },
            {
                "title": "Access Total",
                "render": (data, type, row) => {
                    if (row.user.access_total) {
                        return row.user.access_total
                    }
                    else {
                        return 'NA'
                    }
                }
            },
            {
                "title": "Edit",
                "render": (data, type, row) => {
                    return `<button class='btn btn-sm btn-warning' data-id="${row.id}" onclick="viewStaffModal(event)" style="cursor:pointer"><b data-id="${row.id}">Edit</b></button>`
                }
            }
        ]
    })
}


$(document).ready(() => {
    console.log("document is ready")
    renderTable()
});
