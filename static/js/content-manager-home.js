const deleteModule = (moduleId) => {
    let cookie = getCookie('csrftoken');
    $.ajax({
        url: `/api/v1/module-delete/${moduleId}/`,
        type: 'delete',
        headers: { 'X-CSRFToken': cookie },
        success: (e) => {
            createNotification('success', 'Module has been deleted.');
	    location.reload();
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


const copyModule = (obj, id) => {
    let cookie = getCookie('csrftoken');
    $.ajax({
        url: `/api/v1/copy-module/${id}/`,
        type: 'post',
        headers: {'X-CSRFToken': cookie},
        success: (e) => {
            createNotification('success', 'Module copy has been created you can edit it now!');
            let edit_button = $($(obj).parent().children()[0])
            edit_button.attr('href', `content-manager/edit-module/${e.id}`)
            edit_button.toggleClass('btn btn-outline-danger')
        },
        error: (e) => {
            createNotification('error', 'Something went wrong please try again later.')
        }
    })
}

$(document).ready(() => {
    let module_table = $("#show-module-table")
    module_table.DataTable({
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
            "url": '/api/v1/content-manager-page',
            dataSrc: "",
        },
        "columnDefs": [
            { "className": "dt-center", "targets": "_all" }
        ],
        "columns": [
            {
                "title": "Module ID",
                "data": "id",
            },
            {
                "title": "Module Title",
                "data": "title",
            },
            {
                "title": "Short Title",
                "render": (data, type, row) => {
                    return row.short_title
                }
            },
            {
                "title": "Status",
                "data": "status"
            },
            {
                "title": "Category",
                "render": (data, type, row) => {
                    if(row.module_category){
                        return row.module_category.category_type
                    }
                    else{
                        return "NA"
                    }
                }
            },
            {
                "title": "Enrolled",
                "data": "enrolled_student_count"
            },
            {
                "title": "Date Created",
                "render": (data, type, row) => {
                    let formattedDate = new Date(row.created_at);
		    let month = formattedDate.getMonth() + 1
                    return `${row.created_at}`
                }
            },
            {
                "title": "Date Updated",
                "render": (data, type, row) => {
                    let formattedDate = new Date(row.updated_at);
		    let month = formattedDate.getMonth() + 1
                    return `${row.updated_at}`
                }
            },
            {
                "title": "Edit",
                "render": (data, type, row) => {
                    return `<a href="/content-manager/edit-module/${row.id}" class="edit"><button type="button" class="btn btn-sm btn-warning"><b>Edit</b></button></a>
                    <a href="/content-manager"><button type="button" onclick="copyModule(this, ${row.id})" class="btn btn-sm btn-warning"><b>Copy</b></button></a>`
                }
            },
            {
                "title": "Delete",
                "render": (data, type, row) => {
                    return `<a onclick="deleteModule(${row.id})" style="color: #037afb; cursor: pointer;" class=btn btn-sm btn-warning>Delete</a>`
                }
            }
        ]
    })
});
