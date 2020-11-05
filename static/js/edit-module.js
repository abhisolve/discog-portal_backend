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

function taskContentTypeChange(event) {
    // this method will be triggerd when the task content type
    // select box is changed
    if (event.target.value == "IMG") {
        document.getElementById("taskInputFieldFormGroup").hidden = false;
        document.getElementById("taskFile").setAttribute("accept", "image/*");
        document.getElementById("taskFile").required = true;
        document.getElementById("taskFile").disabled = false;
        document.getElementById("taskResponseType").disabled = false;

    }
    else if (event.target.value == "PDF") {
        document.getElementById("taskInputFieldFormGroup").hidden = false;
        document.getElementById("taskFile").setAttribute("accept", "application/pdf");
        document.getElementById("taskFile").required = true;
        document.getElementById("taskFile").disabled = false;
        document.getElementById("taskResponseType").disabled = false;
    }
    else if (event.target.value == "QUIZ") {
	document.getElementById("taskResponseType").value = 'QUIZ'
    }
    else if (event.target.value == "VIDEO") {
	document.getElementById("taskInputFieldFormGroup").hidden = false;
	document.getElementById("taskFile").setAttribute("accept", "video/mp4");
	document.getElementById("taskFile").required = true;
	document.getElementById("taskFile").disabled = false;
	document.getElementById("taskResponseType").disabled = false;
    }
    else {
        document.getElementById("taskInputFieldFormGroup").hidden = true;
        document.getElementById("taskFile").disabled = true;
        // if (event.target.value == "NONE") {
        //     document.getElementById("taskResponseType").value = 'NONE'
        //     document.getElementById("taskResponseType").disabled = true;

        // }
        // else {
        //     document.getElementById("taskResponseType").disabled = false;
        // }

    }
}
function openAddEditQuizQuestionPage(event) {
    // Method used to opne the add-edit-quiz-question-page
    // in new window and move focus from current window to it
    let addEditQuizQuestionWindow = window.open(url = `/content-manager/add-edit-quiz-questions/${event.target.getAttribute("data-task-id")}`)
    addEditQuizQuestionWindow.focus()
}
function showTaskModal(event) {
    // method used to add and update task
    // by rendring form inside the MOdal Popup

    function getTaskFileFields(taskData) {
        // closure to return the taskData file fileds based
        // on the logic.
        if (taskData.id == undefined) {
            return `<div class="form-group" hidden id="taskInputFieldFormGroup"><label for="taskFile">Task File<span class="text-danger">*</span></label><input type="file" class="form-control" id="taskFile" name="task_file" disabled></div>`
        }
        else if (taskData.id !== undefined) {
            if (taskData.content_type == 'IMG') {
                return `<div class="form-group"><label for="taskFile">Task File<span class="text-danger">*</span></label><input type="file" class="form-control" id="taskFile" name="task_file" accept="image/*,"/ >
            <a href="${taskData.task_file}" target="_blank">View previously added file</a></div>`
            }
            else if (taskData.content_type == 'PDF') {
                return `<div class="form-group"><label for="taskFile">Task File<span class="text-danger">*</span></label><input type="file" class="form-control" id="taskFile" name="task_file" accept="application/pdf"/ >
            <a href="${taskData.task_file}" target="_blank">View previously added file</a></div>`
            }
	    else if (taskData.content_type == 'VIDEO') {
		return `<div class="form-group"><label for="taskFile">Task File<span class="text-danger">*</span></label><input type="file" class="form-control" id="taskFile" name="task_file" accept="video/mp4"/ >
            <a href="${taskData.task_file}" target="_blank">View previously added file</a></div>`
	    }
            else {
                return `<div class="form-group" hidden id="taskInputFieldFormGroup"><label for="taskFile">Task File<span class="text-danger">*</span></label><input type="file" class="form-control" id="taskFile" name="task_file" disabled></div>`
            }
        }
    }

    function getResponseTypeSelect(taskData) {
        // closure used to find get the select box template
        // string for the task response
        if (taskData.id == undefined) {
            return `<select id="taskResponseType" name="response_type" class="form-control" required>
            <option value="NONE" id="optionNone">None</option>
            <option value="TXT" id="optionText">Text</option>
            <option value="FILE" id="optionFile">File</option>
            <option value="QUIZ" id="optionQuiz">Quiz</option> 
            </select>`
        }
        else {
            if (["QUIZ", "TXT", "PDF", "IMG", "VIDEO"].includes(taskData.content_type)) {
                return `<select id="taskResponseType" name="response_type" class="form-control" required>
                    ${taskData.response_type != 'NONE' ? `<option value="NONE" id="optionNone">None</option>` : `<option value="NONE" id="optionNone" selected>None</option>`}
                    ${taskData.response_type != 'QUIZ' ? `<option value="QUIZ" id="optionQuiz">Quiz</option>` : `<option value="QUIZ" id="optionQuiz" selected>Quiz</option>`}
            ${taskData.response_type != 'TXT' ? `<option value="TXT" id="optionText">Text</option>` : `<option value="TXT" id="optionText" selected>Text</option>`}
            ${taskData.response_type != 'FILE' ? `<option value="FILE" id="optionFile">File</option>` : `<option value="FILE" id="optionFile" selected>File</option>`}
                </select>`
		console.log("includes");

            }
            else {
                return `<select id="taskResponseType" name="response_type" class="form-control" required disabled>
                <option value="NONE" id="optionNone" selected>None</option>
                <option value="TXT" id="optionText">Text</option>
                <option value="FILE" id="optionFile">File</option>
                </select>`
		console.log(taskData.content_type)
		console.log("disabled");
            }
        }
    }
    function renderTaskModal(taskData) {
        // closure function to render the taskData modal
        // either will already existing task field values
        // or an enpty form to create task.
        let templateString = `${taskData.id !== undefined ? `<form data-id="${taskData.id}" data-lesson-id="${taskData.lesson}" onsubmit="createUpdateTask(event)">` : `<form data-lesson-id="${taskData.lesson}" onsubmit="createUpdateTask(event)">`}
        <div class="form-group">
            <label for="taskName">Task Name<span class="text-danger">*</span></label>
            ${taskData.task_name ? `<input type="text" name="task_name" class="form-control" id="taskName" placeholder="Task Name" value="${taskData.task_name}" required>` : `<input name="task_name" type="text" class="form-control" id="taskName" placeholder="Task Name" required>`}
          </div>
          <div class="form-group">
              <label for="taskContentType">Content Type<span class="text-danger">*</span></label>
              <select id="taskContentType" name="content_type" class="form-control" onchange="taskContentTypeChange(event)" required>
                ${taskData.content_type != 'TXT' ? `<option value="TXT">Text</option>` : `<option value="TXT" selected>Text</option>`}
                ${taskData.content_type != 'IMG' ? `<option value="IMG">Image</option>` : `<option value="IMG" selected>Image</option>`}
                ${taskData.content_type != 'PDF' ? `<option value="PDF">PDF</option>` : `<option value="PDF" selected>PDF</option>`}
                ${taskData.content_type != 'VIDEO' ? `<option value="VIDEO">Video</option>` : `<option value="VIDEO" selected>Video</option>`}
                ${taskData.content_type != 'QUIZ' ? `<option value="QUIZ">Quiz</option>` : `<option value="QUIZ" selected>Quiz</option>`}
              </select>
          </div>
          <div class="form-group">
            <label id ="response_type_label" for="taskResponseType">Response Type<span class="text-danger">*</span></label>
            ${getResponseTypeSelect(taskData)}
          </div>
          <div class="form-group">
            <label for="taskDescription">Task Description<span class="text-danger">*</span></label>
            ${taskData.task_description ? `<textarea class="w-100" rows="8" id="taskDescription" name="task_description" id="taskDescription">${taskData.task_description}</textarea>` : `<textarea class="w-100" rows="8" id="taskDescription" name="task_description" id="taskDescription" required></textarea>`}
          </div>
            ${getTaskFileFields(taskData)}
          <input type="text" name="lesson" value="${taskData.lesson}" hidden>
          
          ${taskData.id !== undefined && taskData.content_type == "QUIZ" ? `<button type="submit" id="taskSubmitButton" class="btn btn-warning">Submit</button><button type="button" class="btn btn-warning float-right" data-task-id="${taskData.id}" onclick="openAddEditQuizQuestionPage(event)" id="addEditQuestion">Add/Edit Questions</button>` : `<button type="submit" id="taskSubmitButton" class="btn btn-warning">Submit</button>`}
    </form>`
        document.getElementById("taskFormModalContent").innerHTML = templateString;
        $("#taskDescription").trumbowyg();
    }

    if (event.target.getAttribute('data-id') !== null) {
        // this means user have click on the
        // task name to in the accordian to view the task
        $.ajax({
            url: `/api/v1/generic/task/${event.target.getAttribute('data-id')}`,
            type: 'get',
            headers: { 'X-CSRFToken': cookie },
            accept: 'application/json',
            contentType: 'application/json; charset=ut-8',
            success: function (data) {
                $.confirm({
                    title: 'Alert',
                    content: 'Are you sure you want to edit this task ?',
                    buttons: {
                        confirm: function () {
                            renderTaskModal(data);
                            $("#addTaskFormModal").modal('show');
                        },
                        cancel: function () {
                            // do nothing
                        },
                    }
                });
            },
            error: function (request, status, error) {
                createNotificationOfAjaxError(request, error)
            }
        });
    }
    else {
        // this means user have clicked on add task button
        // in the Lesson accordian
        task = { 'lesson': event.target.getAttribute('data-lesson-id') }
        renderTaskModal(task)
        $("#addTaskFormModal").modal('show');
    }
}

function createUpdateTask(event) {
    // create or update task using API calls
    event.preventDefault();
    let requestData = new FormData(event.target)
    // logic to check if image field is updated or not
    if (event.target.getAttribute('data-id', null) !== null) {
        if (!document.getElementById('taskFile').value) {
            requestData.delete('task_file');
        }
    }
    $.ajax({
        url: event.target.getAttribute('data-id', null) === null ? `/api/v1/generic/task/` : `/api/v1/generic/task/${event.target.getAttribute('data-id')}/`,
        type: event.target.getAttribute('data-id', null) === null ? `POST` : `PATCH`,
        headers: { 'X-CSRFToken': cookie },
        data: requestData,
	beforeSend: function(){
	    document.getElementById('taskSubmitButton').innerHTML = `<span class="spinner-border spinner-border-sm"></span>Submiting`
	},
        processData: false,
        contentType: false,
        success: function (data) {
            if (event.target.getAttribute('data-id', null) === null) {
                // it means request is type POST
                createNotification('success', 'Task Created');
                // update the task in the lesson accordian task list
                $(`#taskContainer_${event.target.getAttribute('data-lesson-id')}`).append(`<li class="text-left">
                <a data-id="${data.id}" data-lesson-id="${data.lesson}" id="taskName_${data.id}"
                    href="javascript:;" onclick="showTaskModal(event)">${data.task_name}</a>
                <a class="float-right" onclick="showDeleteTaskModal(${data.id})" href="javascript:;"><i class="fa fa-times" aria-hidden="true"></i></a>
            </li>`)
            }
            else {
                // it means request is type PATCH
                createNotification('success', 'Task Updated');
                document.getElementById(`taskName_${event.target.getAttribute('data-id')}`).innerText = data.task_name;
            }
            if (data.content_type != "QUIZ") {
                $("#addTaskFormModal").modal('hide');
            }
            else{
		if(!document.getElementById("addEditQuestion")){
                    $(`<button type="button"  id="addEditQuestion" class="btn btn-warning float-right" data-task-id="${data.id}" onclick="openAddEditQuizQuestionPage(event)">Add/Edit Questions</button>`).insertAfter($("#taskSubmitButton"))
		}
		event.target.setAttribute('data-id', `${data.id}`)
            }
        },
        error: function (request, status, error) {
            createNotificationOfAjaxError(request, error)
        },
	complete: function () {
	    document.getElementById('taskSubmitButton').innerHTML = ``;
	    document.getElementById('taskSubmitButton').innerText = "Submit";
	}
    });
}

function createUpdateLesson(event) {
    // metod used to crete and update
    // lesson using API calls.
    event.preventDefault();
    let requestData = new FormData(event.target)
    $.ajax({
        url: event.target.getAttribute('data-id', null) === null ? `/api/v1/generic/module-lesson/` : `/api/v1/generic/module-lesson/${event.target.getAttribute('data-id')}/`,
        type: event.target.getAttribute('data-id', null) === null ? `POST` : `PATCH`,
        headers: { 'X-CSRFToken': cookie },
        data: requestData,
        processData: false,
        contentType: false,
        success: function (data) {
            if (event.target.getAttribute('data-id', null) === null) {
                // it means request is type POST
                createNotification('success', 'Lesson Created');
                $("#lessonAccordianContainer").append(`
                <div class="card mt-3">
                    <div class="card-header" id="heading_lesson_${data.id}">
                        <h5 class="mb-0">
                            <button class="btn btn-link float-left" data-toggle="collapse" data-target="#lesson_${data.id}"
                                aria-expanded=false aria-controls="collapseOne" id="lessonAccordian_${data.id}">
                                ${data.lesson_name}
                            </button>
<button class="btn btn-sm btn-warning float-right" data-delete-lesson-id="${data.id}" onclick="deleteLessonConfirm(event)">Delete</button>
                            <button class="btn btn-sm btn-warning float-right mr-1" id="viewLesson_${data.id}" data-id="${data.id}"
                                onclick="addEditLesson(event)">Edit</button>
                        </h5>
                    </div>
                    <div id="lesson_${data.id}" class="collapse show" aria-labelledby="heading_lesson_${data.id}"
                        data-parent="#accordion">
                        <div class="card-body">
                            <div class="container">
                                <!-- render the tasks list here-->
                                <ul class="list-styled" id="taskContainer_${data.id}">
                                </ul>
                            </div>
                            <div class="container text-center"><button class="btn btn-sm btn-warning"
                                    data-lesson-id="${data.id}" onclick="showTaskModal(event)">Add Task</button>
                            </div>
                        </div>
                    </div>
                </div>`)
            }
            else {
                // it means request is type PATCH
                createNotification('success', 'Lesson Updated');
                document.getElementById(`lessonAccordian_${event.target.getAttribute('data-id')}`).innerText = data.lesson_name;
            }
            $("#addLessonFormModal").modal('hide');
        },
        error: function (request, status, error) {
            createNotificationOfAjaxError(request, error)
        }
    });
}

function addEditLesson(event) {
    // function called when add lesson button is pressed
    // or a view lesson button is pressed

    function renderLessonModal(lessonData = null) {
        // closure function to render the lesson modal either with
        // empty form while creating the lesson or with update
        // form to update the lesson
        let templateString = `${lessonData === null ? `<form onsubmit="createUpdateLesson(event)">` : `<form onsubmit="createUpdateLesson(event)" data-id="${lessonData.id}" id="lesson_form_${lessonData.id}">`}
        <div class="form-group">
                <label for="LessonName">Lesson Name</label>
                ${lessonData === null ? `<input type="text" class="form-control" id="lessonName" name="lesson_name" placeholder="LessonName" required>` : `<input type="text" class="form-control" id="lessonName" name="lesson_name" placeholder="LessonName" value="${lessonData.lesson_name}" required>`}
                </div>
                <input type="text" value="${document.getElementById('moduleID').value}" id="moduleID" name="module" hidden>
                <div class="text-center">
                    <button type="submit" class="btn btn-warning btn-sm">${lessonData === null ? `Create` : `Update`}</button>
                </div>
        </form>`
        document.getElementById("lessonFormModalContent").innerHTML = templateString;
        $("#addLessonFormModal").modal('show');
    }

    // main function body begins here.
    if (event.target.getAttribute('data-id', null) !== null) {
        // view lesson button is pressed
        $.ajax({
            url: `/api/v1/generic/module-lesson/${event.target.getAttribute('data-id')}`,
            type: 'get',
            headers: { 'X-CSRFToken': cookie },
            accept: 'application/json',
            contentType: 'application/json; charset=ut-8',
            success: function (data) {
                $.confirm({
                    title: 'Alert',
                    content: 'Are you sure you want to edit this Lesson ?',
                    buttons: {
                        confirm: function () {
                            renderLessonModal(data);
                        },
                        cancel: function () {
                        },
                    }
                });
            },
            error: function (request, status, error) {
                createNotificationOfAjaxError(request, error)
            }
        });
    }
    else {
        // add lesson button is pressed
        renderLessonModal()
    }
}

function showImagePreview(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#imagePreview').attr('src', e.target.result);
            $("#imagePreview").attr("hidden", false);
        }

        reader.readAsDataURL(input.files[0]); // convert to base64 string
    }
}

$("#coverImageInputFileField").change(function () {
    showImagePreview(this);
});


function createNotificationOfAjaxError(request, error) {
    // function used to create notification on ajax errors
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

function submitEditModuleForm(event) {
    event.preventDefault();
    let requestData = new FormData(event.target);
    // logic to handle image reset to null on update.
    if (!document.getElementById('coverImageInputFileField').value) {
        requestData.delete('cover_image');
    }
    // Update API call
    $.ajax({
        url: `/api/v1/generic/module/${document.getElementById("moduleID").value}/`,
        type: 'PATCH',
        headers: { 'X-CSRFToken': cookie },
        contentType: false,
        processData: false,
        data: requestData,
        success: function (data) {
            createNotification(type = 'success', message = 'Module Updated')
        },
        error: function (request, status, error) {
            createNotificationOfAjaxError(request, error);
        }
    })
}

function createModuleCategory(event) {
    // function used to create the module
    // category on the go and assign it to the select2
    event.preventDefault();
    let requestData = new FormData(event.target);

    $.ajax({
        url: `/api/v1/generic/module-category/`,
        type: 'POST',
        headers: { 'X-CSRFToken': cookie },
        data: requestData,
        processData: false,
        contentType: false,
        success: function (data) {
            createNotification('success', 'Module Category Created');
            $("#createModuleCategoryModal").modal('hide');
            let newOption = new Option(data.category_type, data.id, false, true);
            $('#moduleCategory').append(newOption).trigger('change');
        },
        error: function (request, status, error) {
            createNotificationOfAjaxError(request, error)
        }
    });
}

const deleteTask = (taskId) => {
    $.ajax({
        url: `/api/v1/generic/task/${taskId}/`,
        type: 'delete',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: (res) => {
            $.alert({
                title: 'Success',
                content: 'Task has been deleted!'
            });
            $(`a[data-id=${taskId}]`).parent().remove();
        },
        error: (res) => {
        }
    });
}


const showDeleteTaskModal = (taskId) => {
    $.confirm({
        title: 'Confirm!',
        content: 'Are you sure you want to delete this task?',
        buttons: {
            confirm: function () {
                deleteTask(taskId);
            },
            cancel: function () {
                console.log("");
            },
        }
    });
}

function deleteLessonConfirm(event) {
    $.confirm({
        title: 'Confirm',
        content: 'Deleting a lesson would delete all tasks associated with it.',
        buttons: {
            confirm: function () {
                $.ajax({
                    url: `/api/v1/generic/module-lesson/${event.target.getAttribute('data-delete-lesson-id')}/`,
                    type: 'delete',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') },
                    success: function (data) {
                        $.alert({
                            title: 'Success',
                            content: 'Lesson has been deleted!'
                        });
                        $(`#heading_lesson_${event.target.getAttribute('data-delete-lesson-id')}`).parent().remove();
                    },
                    error: function (request, status, error) {
                        createNotificationOfAjaxError(request, error);
                    },
                });
            },
            cancel: function () {
            },
        }
    });
}


