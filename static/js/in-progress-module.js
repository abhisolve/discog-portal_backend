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

function beginThisEnrollment(event) {
    // method used to create the
    // begin the enrollment by sending the
    // date_to_start to the the backend for the
    // in-progress enrollment
    $.ajax({
	url: `/api/v1/generic/enrollment/${document.getElementById("enrollmentId").getAttribute('data-id', null)}/`,
	method: "PATCH",
	cache: false,
	contentType: "application/json; charset=utf-8",
	data: JSON.stringify({ 'date_to_start': moment().format() }),
	success: function (data) {
	    $.confirm({
		title: "Good job!",
		content: "Your Enrollment begin now. Press Okay button to move to first task of the enrollment",
		buttons: {
		    Okay : function(){
			window.location.reload();
		    }
		}
	    });
	},
	error: function (request, status, error) {
	    console.log(request.text)
	    let errorString = `<h5>${error}</h5>`
	    if (request.responseJSON) {
		for (key in request.responseJSON) {
		    if (key !== undefined) {
			errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
		    }
		}
	    }
	    swal({
		title: "Error",
		text: errorString,
		icon: "error",
	    });
	    // createNotification(type = 'error', message = errorString)
	},
    })
}

function startTask(event) {
    // method used to start the task
    // by creating an TaskProgressStatus
    // model instance at backend
    event.target.disabled = true;
    let requestData = {
	'task': event.target.getAttribute('data-task-id', null),
	'enrollment': document.getElementById("enrollmentId").getAttribute('data-id', null)
    }
    $.ajax({
	url: `/api/v1/generic/task-progress-status/`,
	method: "POST",
	cache: false,
	contentType: "application/json; charset=utf-8",
	data: JSON.stringify(requestData),
	success: function (data) {
	    for(let element of document.getElementsByName("resourceContainer")){
		element.hidden = false;
	    }
	    $.confirm({
		title: 'Well Done',
		content: 'Your Task has been started, Go through the task description and when you think you are done. Click the Mark as complete button.',
		buttons: {
		    Okay: function () {
			if(document.getElementById("taskType").value != 'QUIZ' && document.getElementById("taskType").value != 'VIDEO'){
			    // only show mark as complete button if the task type is not
			    // QUIZ. Just to convert the start task button to Mark As Complete Button
			    event.target.setAttribute('id', "markAsCompleteButton")
			    event.target.setAttribute('class', "btn btn-sm btn-danger float-right")
			    event.target.setAttribute('onclick', "completeTask(event)")
			    event.target.setAttribute('data-task-progress-status-id', data.id)
			    event.target.setAttribute('data-task-response-type', document.getElementById("taskResponseType").value)
			    event.target.innerText = "Mark as Complete"
			}
			else if(document.getElementById("taskType").value == 'VIDEO'){
			    window.location.reload();
			}
			else{
			    // Remove start task button
			    event.target.remove();
			    $("body").append(`<input type="text" id="quizTaskProgressStatusId" value="${data.id}">`)
			}
		    }
		}
	    });

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
	    $.alert({
		title: "Error",
		content: errorString,
	    });

	},
	complete: function(){
	    event.target.disabled = false;
	}
    })
}

function updateTaskProgressStatus(event, requestData) {
    // method used to update the task progress
    // status of the current task if it is started
    $.ajax({
	url: `/api/v1/generic/task-progress-status/${event.target.getAttribute('data-task-progress-status-id', null)}/`,
	method: "PATCH",
	processData: false,
	contentType: false,
	data: requestData,
	success: function (data) {
	    $.confirm({
		title: 'Well Done',
		content: 'Your task is marked as completed. click the button below to automically move to next task.',
		buttons: {
		    "Redo": function () {
			document.getElementById('markAsCompleteButton').disabled = false;
		    },
		    "Move to Next Task": function () {
			window.location.reload();
		    },
		}
	    });
	},
	error: function (request, status, error) {
	    console.log(request.text)
	    let errorString = `<h5>${error}</h5>`
	    if (request.responseJSON) {
		for (key in request.responseJSON) {
		    if (key !== undefined) {
			errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
		    }
		}
	    }
	    $.alert({
		title: "Error",
		content: errorString,
	    });
	    event.target.disabled = false;
	},
    })
}

function submitTaskResponse(event) {
    // method used to create the FormData
    // object with respective data as per
    // task_response type and call updateTaskProgressStatus
    // function with this data
    event.preventDefault();
    let requestData = new FormData()
    let responseType = event.target.getAttribute("data-response-type", null);
    
    if (responseType == 'TXT') {
	requestData.append('task_response_text', $("#responseInput").val());
	requestData.append('date_completed', moment().format());
    }
    else if (responseType == "IMG" || responseType == "FILE") {
	requestData.append("task_response_file", $("#responseInputFile").get(0).files[0]);
	requestData.append('date_completed', moment().format());
    }
    else {
	requestData.append('date_completed', moment().format());
    }
    updateTaskProgressStatus(event,requestData)
}

function completeTask(event) {
    // method used to start the task
    // by creating an TaskProgressStatus
    // model instance at backend
    event.target.disabled = true;
    let responseType = event.target.getAttribute('data-task-response-type', null);
    let task_progress_id = event.target.getAttribute('data-task-progress-status-id', null);
    let confirmation_content = ``;
    let confirmationButtons = {

    }
    let confirmBoxTitle = 'Task Response';

    $.ajax({
	url:`/api/v1/generic/task-progress-status/${task_progress_id}`,
	type: 'get',
	success: function (data) {
	    if (data.task_response_text != null){
		document.getElementById('responseInput').innerText = `${data.task_response_text}`;
	    }
	},
	error: function (request, status, error) {
	    console.log(request.text)
	    let errorString = `<h5>${error}</h5>`
	    if (request.responseJSON) {
		for (key in request.responseJSON) {
		    if (key !== undefined) {
			errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
		    }
		}
	    }
	    $.alert({
		title: "Error",
		content: errorString,
	    });
	},
    })
    
    if (responseType == 'TXT') {
	confirmation_content = `<div class="container">
		<h6>Please provide the response of this task as metiond in the description of the Task</h6>
		<form onsubmit="submitTaskResponse(event)" data-response-type="${responseType}"
		data-task-progress-status-id="${event.target.getAttribute('data-task-progress-status-id', null)}">
		<textarea class="form-control" rows="10" id="responseInput" required></textarea>
		<button class="btn btn-sm btn-success m-2" type="submit">Submit Response</button>
		</form>
		</div>`;
	confirmationButtons['Cancel'] = function () {
	    // Only canel button is required as submit button is
	    // in the form itself
	    event.target.disabled = false;
	}
    }
    else if (responseType == "IMG") {
	confirmation_content = `<div class="container">
		<h3>Please provide the response of this task as metiond in the description of the Task</h3>'
		<form onsubmit="submitTaskResponse(event)" data-response-type="${responseType}"
		data-task-progress-status-id="${event.target.getAttribute('data-task-progress-status-id', null)}">
		<input name="task_response_file" class="form-control" type="file" id="responseInputFile" accept="image/*" required/>
		<button class="btn btn-sm btn-success m-2" type="submit">Submit Response</button>
		</form>
		</div>`
	confirmationButtons['Cancel'] = function () {
	    // Only canel button is required as submit button is
	    // in the form itself
	    event.target.disabled = false;
	}
    }
    else if (responseType == "FILE") {
	confirmation_content = `<div class="container">
		<h3>Please provide the response of this task as metiond in the description of the Task'</h3>
		<form onsubmit="submitTaskResponse(event)" data-response-type="${responseType}"
		data-task-progress-status-id="${event.target.getAttribute('data-task-progress-status-id', null)}">
		<input class="form-control" type="file" id="responseInputFile" required name="task_response_file" />
		<button class="btn btn-sm btn-success m-2" type="submit">Submit Response</button>
		</form>
		</div>`
	confirmationButtons['Cancel'] = function () {
	    // Only canel button is required as submit button is
	    // in the form itself
	    event.target.disabled = false;
	}
    }
    else {
	confirmation_content = `Are you sure. You want to mark this Task as Completed?`;
	confirmationButtons['Yes'] = function () {
	    submitTaskResponse(event);
	}
	confirmationButtons['No'] = function () {
	    event.target.disabled = false;
	}
	confirmBoxTitle = "Alert";
    }

    $.confirm({
	title: confirmBoxTitle,
	content: confirmation_content,
	buttons: confirmationButtons

    })
}

function answerCheck(AnswerData) {
    let response = JSON.stringify(AnswerData.options)
    let question = AnswerData.question
    $.ajax({
	url:'/api/v1/check-answer/',
	method: 'get',
	data: {question:question, options:response},
	success: function (data) {
	    $.confirm({
		title: '<b>Remark</b>',
		content: data.remark,
		buttons: {
		    "Ok": function () {
			// check if any form is available if not
			// refresh tha page in order to move to next page
			let undoneQuestions = document.getElementsByName("quizQuestionForm")
			if(undoneQuestions.length == 0){
			    // no question available
			    // refresh the page
			    let requestData = new FormData()
			    requestData.append('date_completed', moment().format())
			    $.ajax({
				url: `/api/v1/generic/task-progress-status/${document.getElementById('quizTaskProgressStatusId', null).value}/`,
				method: "PATCH",
				processData: false,
				contentType: false,
				data: requestData,
				success: function (data) {
				    $.confirm({
					title: 'Well Done',
					content: 'Your Quiz task is completed. click the button below to view answers.',
					buttons: {
					     "Show Quiz Answers": function () {
						$.ajax({
						    url: `/api/v1/quiz-response/?taskprogressID=${document.getElementById('quizTaskProgressStatusId', null).value}`,
						    method: 'get',
						    success: function (data) {
							let i;
							let l;
							for(i=0; i < data.length; i++){
							    let htmltemplate =
								`<section id="correct-answers">
								<h5>Question: ${data[i].question.question}</h5>                                                                        
								<section id="question-correct-answers-${i}">                                                                                                 
								<label><p>Correct Answer:</p></label>                                                                                  
								</section>`
							    $("#answers").append(htmltemplate);
							    
							    for(l=0; l < data[i].correct_answer.length; l++) {
								$("#question-correct-answers-"+i).append(
								    `<label class="mr-2" for="correct-answer-${l}"><p id="correct-answer-${l}"><b>${data[i].correct_answer[l].option_content}</b></p></label>`);
							    }
							    
							}
							$("#show-quiz-answers").modal('show');
						    }
						});
					     }
					}
				    });
				},
			    });
			}
		    }
		}
	    });
	},
	error: function (request, status, error) {
	    console.log(request.text)
	    let errorString = `<h5>${error}</h5>`
	    if (request.responseJSON) {
		for (key in request.responseJSON) {
		    if (key !== undefined) {
			errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
		    }
		}
	    }
	    $.alert({
		title: "Error",
		content: errorString,
	    });
	},
    })
}

function submitQuizAnswer(event){
    // method used to submit the quiz question
    // response to the backen using API
    // and remove the form after the response is submited
    event.preventDefault();
    let requestData = new FormData(event.target)
    let optionsSelected = requestData.getAll('options').length
    var requestDataObject = {};
    requestData.forEach((value, key) => {requestDataObject[key] = value});
    requestDataObject['options'] = requestData.getAll('options');
    requestDataObject['question'] = event.target.getAttribute('data-question-id', null)
    requestDataObject['task_progress_status'] = document.getElementById("quizTaskProgressStatusId").value
    // Validataion logic
    if(optionsSelected == 0){
	// raise warning and
	// do nothing
	$.alert({
	    title: "Invalid Response",
	    content: "You need to select at least one option"

	});
    }
    else{
	// Ask the user if he/she is sure about
	// his submission
	$.confirm({
	    title: "Are you Sure with your response",
	    content: "Press yes if you verify your response.",
	    buttons: {
		"yes": function(){
		    // do an ajax request and remove the question from here
		    // after user has inputed the data
		    $.ajax({
			url: `api/v1/generic/quiz-answers/`,
			method: "POST",
			contentType: "application/json; charset=utf-8",
			accept: "application/json",
			data: JSON.stringify(requestDataObject),
			success: function (data) {
			    document.getElementById(`question-container-${data.question}`).remove();
			    answerCheck(data);
			},
			error: function (request, status, error) {
			    console.log(request.text)
			    let errorString = `<h5>${error}</h5>`
			    if (request.responseJSON) {
				for (key in request.responseJSON) {
				    if (key !== undefined) {
					errorString += `<small>${key}:${request.responseJSON[key]}</small><br/>`
				    }
				}
			    }
			    $.alert({
				title: "Error",
				content: errorString,
			    });
			    event.target.disabled = false;
			},
		    })
		},
		"No": function(){
		    // do nothing.
		    // the alert box will closed
		    // and no submission will take place
		}
	    }
	});
    }
}
