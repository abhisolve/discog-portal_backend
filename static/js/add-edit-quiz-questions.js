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
function appendQuestionRow(question){
    // function used to create a render
    // either new question or updated
    // to the HTML body
    let questionContainer = $("#questionContainer");
    questionContainer.append(`<div class="container shadow-lg bg-white rounded mb-5 p-5" data-question-id="${question.id}" id="question-container-${question.id}">
    <form data-question-id="${ question.id }" onsubmit="createUpdateQuizQuestion(event)" class="py-5">
      <div class="contaier-fluid">
        <div class="form-group">
          <label for="question-${question.id}">Question<span class="text-danger">*</span></label>
          <textarea class="form-control" name="question" id="question-${question.id}" required>${question.question}</textarea>
        </div>
        <div class="form-group">
          <label for="question-type-${question.id}">Question Type<span class="text-danger">*</span></label>
          <select class="form-control" name="question_type" id="question-type-${question.id}" required>
            <option disabled>Question Type</option>
            ${question.question_type == "SC" ? `<option value="SC" selected>Single Choice</option>`: `<option value="SC">Single Choice</option>`}
            ${ question.question_type == "MC"? `<option value="MC" selected>Multiple Choice</option>`:`<option value="MC">Multiple Choice</option>`}
          </select>
        </div>
        <div class="form-group">
          <button class="btn btn-sm btn-warning float-left" type="submit">Update Question</button>
          <button class="btn btn-sm btn-danger ml-2" type="button" data-question-id="${question.id}" onclick="deleteQuestion(event)">Delete Question</button>
          <button class="btn btn-sm btn-warning float-right" type="button" data-question-id="${question.id}" onclick="showOptionsContainer(event)">Show options</button>
        </div>
      </div>
    </form>
    <div class="container shadow-lg bg-white rounded mb-5 p-5" hidden id="option-container-${question.id}">
      <div id="main-option-container-${question.id}">
        </div>
      <div class="container text-center" id="add-option-container-${question.id}">
        <button class="btn btn-secondary btn-sm" data-question-id="${question.id}" onclick="addOption(event)">Add Option</button>
      </div>
    </div>
  </div>`)
  
}

function createUpdateQuizQuestion(event) {
    // function used to create or update the
    // question using XHR Request to API endpoint
    event.preventDefault();
    let requestData = new FormData(event.target)
    $.ajax({
        url: event.target.getAttribute('data-question-id', null) === null ? `/api/v1/generic/quiz-questions/` : `/api/v1/generic/quiz-questions/${event.target.getAttribute('data-question-id')}/`,
        type: event.target.getAttribute('data-question-id', null) === null ? `POST` : `PATCH`,
        headers: { 'X-CSRFToken': cookie },
        data: requestData,
        processData: false,
        contentType: false,
        success: function (data) {
            // hide the modal and reset the modal form
            $("#addQuestionModal").modal("hide");
            document.getElementById("createQuizQuestionFrom").reset();

            if(event.target.getAttribute("data-question-id") === null){
            // we will create a new question element and render it in desired
            //location in question container.
            try{
                document.getElementById("noQuestionExistContainer").remove();
            }
            catch(e){
                //do nothing
            }
            createNotification(type = 'success', message = 'Question Created');
            appendQuestionRow(question=data);
            // move focus on newly added element
            document.getElementById(`question-${data.id}`).focus();
            }
            else{
                // no need to render question. Just show update notifications.
                createNotification(type = 'success', message = 'Question Updated');
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
            createNotification(type = 'error', message = errorString)
        }
    });
}
function deleteQuestion(event){
    $.confirm({
        title: "Are You sure?",
        content: "This question will be deleted along with its options",
        buttons:{
            confirm: function(){
                $.ajax({
                    url: `/api/v1/generic/quiz-questions/${event.target.getAttribute('data-question-id')}/`,
                    type: "delete",
                    headers: { 'X-CSRFToken': cookie },
                    success: function (data) {
                        createNotification(type = 'success', message = 'Question Deleted');
                        document.getElementById(`question-container-${event.target.getAttribute("data-question-id")}`).remove();
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
                        createNotification(type = 'error', message = errorString)
                    }
                });
            },
            discard: function(){}
        }
    })
}
function createUpdateQuizOption(event) {
    // function used to create or update the
    // question option using XHR Request to API endpoint
    event.preventDefault();
    let requestData = new FormData(event.target)
    $.ajax({
        url: event.target.getAttribute('data-option-id', null) === null ? `/api/v1/generic/quiz-question-option/` : `/api/v1/generic/quiz-question-option/${event.target.getAttribute('data-option-id')}/`,
        type: event.target.getAttribute('data-option-id', null) === null ? `POST` : `PATCH`,
        headers: { 'X-CSRFToken': cookie },
        data: requestData,
        processData: false,
        contentType: false,
        success: function (data) {
            if(event.target.getAttribute("data-option-id") === null){
            createNotification(type = 'success', message = 'Option Created');
            event.target.setAttribute("data-option-id", data.id);
            // change the label of save button to update button
		event.target.querySelector("button[type='submit']").innerText = "Update";
		event.target.querySelector("button[type='button']").setAttribute("data-option-id", data.id);
		event.target.setAttribute("name", "savedForm");
            }
            else{
                createNotification(type = 'success', message = 'Option Updated');
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
            createNotification(type = 'error', message = errorString)
        }
    });
}

function deleteOption(event){
    // method used to delete the save and remove
    // the unsaved options
    let optionId = event.target.getAttribute("data-option-id")
    if(optionId === null){
        $.confirm({
            title: "Are You sure you want to delete this option?",
            content: "This Option has not been save to database.",
            buttons: {
                confirm : function(){
                    createNotification(type = 'success', message = 'Option Removed');
                    event.target.form.remove();
                },
                cancel: function(){

                }
            }
        })
    }
    else{
        $.confirm({
            title: "Are You sure you want to delete this option?",
            content: "This Option exists in database",
            buttons: {
                confirm : function(){
                    $.ajax({
                        url: `/api/v1/generic/quiz-question-option/${optionId}/`,
                        type: "delete",
                        headers: { 'X-CSRFToken': cookie },
                        success: function (data) {
                            createNotification(type = 'success', message = 'Option deleted');
                            event.target.form.remove();
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
                            createNotification(type = 'error', message = errorString)
                        }
                    })
                        
                },
                cancel: function(){

                }
            }
        })
    }
}

function showOptionsContainer(event){
    let optionsContainer = document.getElementById(`option-container-${event.target.getAttribute('data-question-id')}`);
    if(optionsContainer.hidden === true){
        //show the options container and change the event.target label
        // to hide option container
        event.target.innerText = "Hide Options";
        optionsContainer.hidden = false;
    }
    else{
        // hide the option container and changer the event.target label
        // to hide options
        event.target.innerText = "Show Options";
        optionsContainer.hidden = true;
    }
}

function addOption(event){
    // method used to render the add option form
    // in the desired location of the respective questions
    let questionId = event.target.getAttribute("data-question-id");
    $(`#main-option-container-${questionId}`).append(`<form data-question.id="${questionId}" onsubmit="createUpdateQuizOption(event)" class="shadow-lg bg-white rounded mb-5 p-5">
        <div class="form-group">
          <label>Option Content<span class="text-danger">*</span></label>
          <textarea class="form-control" required name="option_content"></textarea>
        </div>
        <div class="form-group">
          <label>Weightage<span class="text-danger">*</span></label>
            <input class="form-control" type="number" step="1" id="option-weightage-{{option.id}}" name="weightage" value="{{option.weightage}}">
        </div>
        <input type="text" name="question" value="${questionId}" hidden>
        <div class="form-group">
          <button class="btn btn-sm btn-warning float-left" type="submit">Save</button>
          <button class="btn btn-sm btn-danger float-right" type="button" onclick="deleteOption(event)">Delete Option</button>
        </div>
      </form>`)
}
