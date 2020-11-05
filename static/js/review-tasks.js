function sendFeedback() {
    let url = window.location.href;
    let url_array = url.split('/')
    let enroll_id = url_array[url_array.length - 2];
    let feedback_text = $('#feedback-text').val();
    let cookie = getCookie('csrftoken');
    let fileName = $("#upload-review-file").get(0).files[0];
    let data = new FormData();
    let status = $("#enrollment-status").val();
    data.append('enrollment_status', status);
    data.append('enrollment', enroll_id);
    data.append('comment', feedback_text);
    if(fileName !== undefined){
	data.append('feedback_file', fileName);
    } 
    $.ajax({
	url: '/api/v1/generic/enrollment-feedback/',
	type: 'post',
	enctype: 'multipart/form-data',
	contentType: false,
	processData: false,
	headers: { 'X-CSRFToken': cookie },
	data: data,
	success: (e) => {
	    $('#feedbackModal').modal('toggle');
	    createNotification('success', 'Feedback Added Succesfully');
	    data_table.ajax.reload();
	    window.location.replace('/review-students');
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

function getResponse(taskID) {
    let url_array = window.location.href.split('/');
    let enrollmentID = url_array[url_array.length - 2];
    let cookie = getCookie('csrftoken');
    $.ajax({
	url: `/api/v1/enrollment-feedback-page-datatable/?enrollmentID=${enrollmentID}&taskID=${taskID}`,
	type: "get",
	headers: { 'X-CSRFToken': cookie },
	success: function (data) {
	    $('#response-result').html(`${data[0].task_response_text}`);
	    $('#getResponseModal').modal('show');
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
	    createNotification('error', message = errorString)
	}
    })

}

function getQuizResponse(ID) {
    let cookie = getCookie('csrftoken');
    $("#quiz-response-result").empty();
    $.ajax({
	url: `/api/v1/quiz-response/?taskprogressID=${ID}`,
	type: "get",
	headers: {'X-CSRFToken': cookie},
	success: function (data) {
	    let i;
	    let j;
	    let k;
	    let l;
	    for(i = 0; i < data.length; i++){
		let htmltemplate = `
			<section>
			<h5>Question: ${data[i].question.question}</h5>
                        <section class="ml-3 mt-4" id="question-choices-${i}">
                        </section>
                        <section id="question-correct-answers-${i}">
                        <label><p>Correct Answer:</p></label>
                        </section>
                        <section id="question-answers-${i}">
                        <label><p>Answer given by Student:</p></label>
                        </section>
			</section> `  
		$("#quiz-response-result").append(htmltemplate);
		for(j = 0; j < data[i].choices.length; j++){	
		    $("#question-choices-"+i).append(`<label for="option-${j}"><p id="option-${j}">${j+1}: ${data[i].choices[j].option_content}</p></label></br>`);
		}
		for(k=0; k < data[i].answer.length; k++) {
		    $("#question-answers-"+i).append(`<label class="mr-2" for="answer-${k}"><p id="answer-${k}"><b>${data[i].answer[k].option_content}</b></p></label>`);
		}
		for(l=0; l < data[i].correct_answer.length; l++) {
		    $("#question-correct-answers-"+i).append(`<label class="mr-2" for="correct-answer-${l}"><p id="correct-answer-${l}"><b>${data[i].correct_answer[l].option_content}</b></p></label>`);
		}
	    }
	    $('#getQuizResponseModal').modal('show');
	
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
	    createNotification('error', message = errorString)
	}
    })
    
}

function taskReject() {
    taskprogressID = localStorage.getItem('TaskprogressID')
    console.log(taskprogressID);
    let cookie = getCookie('csrftoken');
    feedback = $('#reject-feedback').val();
    console.log(feedback)
    if (feedback.length != 0) {
	$.ajax({
	    url: `/api/v1/reject-task/${taskprogressID}/`,
	    type: 'patch',
	    data: {'feedback': feedback},
	    headers: {'X-CSRFToken': cookie},
	    success: function (data) {
		createNotification('success', 'Task has been rejected.');
		data_table.ajax.reload();
		$('#reject-feedback').val('');
		$('#taskrejectModal').modal('hide');
	    },
	    error: function (request, status, error) {
		let errorString = `<h5>${error}</h5>`
		if (request.responseJSON) {
		    for (key in request.responseJSON) {
			if (key !== undefined) {
			    errorString += `<small>${key}:${request.responseJSON[key]}</small>`
			}
		    }
		}
		createNotification('error', message = errorString)
	    }
	})
    }
    else {
	createNotification('error', message = 'Comment Field is mandatory.')
    }
}

$(document).ready(() => {
    let url = window.location.href;
    let url_array = url.split('/')
    let enroll_id = url_array[url_array.length - 2];

    let review_tasks_table = $("#inreview-tasks-table")
    data_table = review_tasks_table.DataTable({
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
	    "url": `/api/v1/enrollment-feedback-page-datatable/?enrollID=${enroll_id}`,
	    dataSrc: "",
	},
	"columns": [
	    {
		"title": "Task ID",
		"data": "task.id",
		"width": "12%",
	    },
	    {
		"title": "Task Name",
		"data": "task.task_name",
		"width": '15%'
	    },
	    {
		"title": "D.Started",
		"render": (data, type, row) => {
		    if (row.date_started != null) {
			return `${row.date_started}`
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
			return `${row.date_completed}`
		    }
		    else {
			return `Not completed Yet`
		    }
		},
		"width": '18%'
	    },
	    {
		"title": "Duration (hh:mm:ss)",
		"render": (data, type, row) => {
		    return `${row.duration}`
		},
		"width": '15%'
	    },
	    {
		'title': 'Student Response',
		'render': (data, type, row) => {
		    if(row.task.response_type == "TXT"){
			return `<button id="feedback-button" type="button" class="btn btn-sm btn-warning" onclick="getResponse(${row.task.id})" style= "background-color:#ffca12"><b>View</b></button>`
		    } else if(row.task.response_type == "FILE"){
			return `<a href="${row.task_response_file}" download><button id="feedback-button" type="button" class="btn btn-sm btn warning" style= "background-color:#ffca12"><b>Download</b></button></a>`
		    } else if(row.task.response_type == "QUIZ"){
			return `<button id="feedback-button" type="button" class="btn btn-sm btn-warning" onclick="getQuizResponse(${row.id})" style= "background-color:#ffca12"><b>View</b></button>`
		    }
		},
		"width": '15%'
	    },
	    {
		'title': 'Reject Task',
		'render': (data, type, row) => {
		    if (row.rejected_count == 0) {
			return `<button type="button" class="btn btn-sm btn-warning" data-toggle="modal" data-target="#taskrejectModal" onclick="localStorage.setItem('TaskprogressID', ${row.id});" style="background-color:#ffca12"><b>Reject</b></button>`
		    } else {
			return `<b>Rejected<b>`
		    }
		},
		"width":'13%'
	    }
	]
    })    
});
