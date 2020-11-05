function search_table(event) {
    if (event.target.id == "searchByStudentId") {
	data_table.column(0).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStudentName") {
	data_table.column(1).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByStudentType") {
	data_table.column(2).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByCurrentAssignment") {
	data_table.column(4).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByPreviousAssignment") {
	data_table.columns(5,6,7).search(event.target.value).draw();
    }
    else if (event.target.id == "searchByNextAssignment") {
	data_table.columns(3).search(event.target.value).draw();
    }
    
}

$(document).ready(() => {
	let assignments_table = $("#assignments-dashboard-table")
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
			"url": '/api/v1/custom-student-details/',
			dataSrc: "",
		},
		"columnDefs": [
			{ "className": "dt-center", "targets": "_all" }
		],
		"columns": [
		    {
			"title": "Student ID",
			"data": "roll_number",
		    },
		    {
			"title": "Student Name",
			"render": (data, type, row) => {
			    if(row.user.last_name != null && row.user.first_name != null){
				return `${row.user.first_name + ' ' + row.user.last_name}`
			    }else if(row.user.last_name == null){
				return `${row.user.first_name}`
			    }else{
				return `NA`
			    }
			}
		    },
		    {
			"title": "Student Type",
			"data": "student_type"
		    },
		    {
			"title": "Next Module",
			"render": (data, type, row) => {
			    if(row.next_module[0] != null){
				return `${row.next_module}`
			    }else{
				return 'NA'
			    }	
			}
		    },
		    {
			"title": "Current",
			"render": (data, type, row) => {
			    if(row.current_module[0] != null){
				return `${row.current_module}`
			    }else{
				return 'NA'
			    }
			}
		    },
		    {
			"title": "Previous 1",
			"render": (data, type, row) => {
			    if(row.previous_modules[0] != null){
				return `${row.previous_modules[0]}`
			    }else{
				return 'NA'
			    }
			}
		    },
		    {
			"title": "Previous 2",
			"render": (data, type, row) => {
			    if(row.previous_modules[1] != null){
				return `${row.previous_modules[1]}`
			    }else{
				return 'NA'
			    }
			}
		    },
		    {
			"title": "Previous 3",
			"render": (data, type, row) => {
			    if(row.previous_modules[2] != null){
				return `${row.previous_modules[2]}`
			    }else{
				return 'NA'
			    }
			}
		    },
		    {
			"title": "View",
			"render": (data, type, row) => {
			    return `<a href="/specific-assignments-dashboard/${row.user.id}/"><button type="button" style="background-color:#f9ca33" class="btn btn-sm btn warning"><b>View</b></button></a>`
			}
		    }
		    
		]
	})
})

	                           
