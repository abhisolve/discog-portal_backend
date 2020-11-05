function sendPasswordResetLink(event){
    event.preventDefault();
    let submitButton = document.getElementById("submitButton");
    let goBackToLoginButton = document.getElementById("goBackLoginButton");
    let cookie = getCookie('csrftoken');
    const email = $("#email").val();

    $.ajax({
        url: '/api/v1/send-reset-password-link',
        type: 'post',
        headers: {'X-CSRFToken': cookie},
	beforeSend: function(){
	    // disable subbmit button and show loading
	    submitButton.disabled = true;
	    submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Sending Email...`;
	    // hide to back to login untill request is completed
	    goBackToLoginButton.hidden = true;
	},
        data: {'email': email},
        success:function(data){
            createNotification('success', '<b>Success</b><p>A reset password Instructions mail has been scheduled for delivery to your Email Id, You will receive it within next 10 mintutes.</p>')
	    resetPasswordForm.reset();
	    // show go back to login button
	    goBackToLoginButton.hidden=false;
        },
        error: function(request, status, error){
	    let errorString = ``;
            for (key in request.responseJSON) {
		if (key !== undefined) {
		    errorString += `<b>${key}</b><p>${request.responseJSON[key]}</small></p>`
		}
	    }
	    createNotification('error', message = errorString)
        },
	complete: function(){
	    // stop loading and bring
	    // the button to its origin form
	    submitButton.disabled = false;
	    submitButton.innerHTML = `<b>Reset Password</b>`;
	}
    });
}
