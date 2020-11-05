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

function showImagePreview(input){
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

function submitCreateModuleForm(event) {
    event.preventDefault();
    let requestData = new FormData(event.target);
    $.ajax({
        url: '/api/v1/generic/module/',
        type: 'post', 
        headers: { 'X-CSRFToken': cookie },
        contentType: false,
        processData: false,
        data: requestData,
        success: function (data) {
            window.location.assign(`/content-manager/edit-module/${data.id}`)
        },
        error: function (request, status, error) {
            createNotificationOfAjaxError(request, error);
        }
    })
}

function createModuleCategory(event) {
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
