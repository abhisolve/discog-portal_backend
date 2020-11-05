const createNotification = (type, message) => {
    new Noty({
        type: type,
        layout: 'topRight',
        theme: 'nest',
        text: message,
        timeout: '4000',
        progressBar: true,
        closeWith: ['click'],
        killer: true,
    }).show();
} 