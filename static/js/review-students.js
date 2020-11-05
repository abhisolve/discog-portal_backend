$(document).ready(() => {
    let student_table = $("#student-detail-table")
    student_table.DataTable({
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
	    "url": '/api/v1/staff-to-student-relation-details/',
	    dataSrc: "",
	},
	"columnDefs": [
	    { "className": "dt-center", "targets": "_all" }
	],
	"columns": [
	    {
		"title": "Student ID",
		"data": "roll_number",
		"width": '20%',
	    },
	    {
		"title": "Student Name",
		"render": (data, type, row) => {
		    return `${row.user.first_name + ' ' + row.user.last_name}`
		},
		"width": '25%',
	    },
	    {
		"title": "Student Type",
		"data": "student_type",
		"width": '20%',
	    },
	    {
		"title": "In Review Modules",
		"data": "in_review_module_total",
		"width": '20%',
	    },
	    {
		"title": "View",
		"render": (data, type, row) => {
		    return `<a href="/review-modules/${row.user.id}/"><button type="button" style="background-color:#f9ca33" class= "btn btn-sm btn warning"><b>View</b></button></a>`
		},
		"width": '10%',
	    },
	    
	]
    })
})

