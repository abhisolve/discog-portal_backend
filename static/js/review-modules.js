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
    let url = window.location.href;
    let url_array = url.split('/')
    let stu_id = url_array[url_array.length - 2];
    let review_modules_table = $("#inreview-modules-table")
    data_table = review_modules_table.DataTable({
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
	    "url": `/api/v1/in-review-modules-table/?userID=${stu_id}`,
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
		"width": '15%'
	    },
	    {
		"title": "Short Title",
		"data": "module.short_title",
		"width": '15%'
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
		"width": '13%'
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
		"width": '18%'
	    },
	    {
		'title': 'Feedback',
		'render': (data, type, row) => {
		    return `<a href="/enrollment-feedback/${row.id}/"><button id="feedback-button" type="button" class="btn btn-sm btn warning" onclick="localStorage.setItem('module_id', ${row.module.id});" style= "background-color:#ffca12"><b>View</b></button></a>`
		},
		"width": '10%'
	    }
	]
    })
})
