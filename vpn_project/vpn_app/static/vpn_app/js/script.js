function sendForm(formId, method) {
    form = document.getElementById(formId)
    const formData = new FormData(form);
    const csrfToken = formData.get('csrfmiddlewaretoken');

    fetch(form.action, {
        method: method,
        headers: {
            'X-CSRFToken': csrfToken, // Добавляем CSRF-токен в заголовки
        },
        body: formData,
    })
    .then(response => {
        console.log(response)
        // Проверяем, был ли ответ успешным (статус 2xx)
        if (!response.ok) {
            // Если нет, пытаемся прочитать JSON с ошибкой или просто выбрасываем ошибку
            return response.json().then(errorData => {
                const errorMessage = errorData.message || 'Произошла ошибка на сервере.';
                const errorElement = errorData.element;
                const errorProcess = errorData.process;

                const resultDiv = document.getElementById(`${errorElement}-message`);
                if (resultDiv) {
                    resultDiv.innerHTML = `<p class='message-${errorProcess}'>${errorMessage}</p>`;
                }

                if (errorElement == 'None') {
                    throw new Error(errorMessage); // Выбрасываем ошибку, чтобы она попала в .catch

                }
            }).catch(error => {
                const err_url = 'https://dvpn.yuniversia.eu/error';

                // window.location.href = `${err_url}?status=${response.status}&message=${error.message}`;
            });
        }
        return response.json(); // Если OK, парсим как JSON
    })
    .then(data => {

        if (data.message) {
        const msg = data.message
        } else {
        const msg = data.statusText;
        }

        const element = data.element;
        const process = data.process;
        const reloadPage = data.reload;
        const redirectUrl = data.redirect_url; // Получаем URL для перенаправления

        console.log(redirectUrl)

        // Если есть URL для перенаправления, переходим по нему
        if (redirectUrl) {
            window.location.href = redirectUrl;
            return; // Прекращаем выполнение, так как страница будет перезагружена/перенаправлена
        }

        // Если нет перенаправления, но нужно перезагрузить страницу
        if (reloadPage === true) {
            location.reload();
            return; // Прекращаем выполнение
        }

        // В противном случае, выводим сообщение на текущей странице
        const div = `<p class='message-${process}'>${msg}</p>`;
        const result = document.getElementById(`${element}-message`);
        
        result.innerHTML = '';
        result.innerHTML = div;
    })
    .catch(error => {
        console.error('Ошибка при отправке формы:', error);
        // Здесь можно показать общее сообщение об ошибке, если оно не было обработано выше
        const loginMessageDiv = document.getElementById('login-message'); // Предполагаем, что у вас есть такой div для ошибок логина
        if (loginMessageDiv) {
            loginMessageDiv.innerHTML = `<p class='message-error'>${error.message || 'Произошла непредвиденная ошибка.'}</p>`;
        }
    });
}

function generateLink(formId, method, container){
    form = document.getElementById(formId)
    const formData = new FormData(form);
    const csrfToken = formData.get('csrfmiddlewaretoken');

    fetch(form.action, {
        method: method,
        headers: {
            'X-CSRFToken': csrfToken, // Добавляем CSRF-токен в заголовки
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        const link = data.link;

        document.getElementById(`${container}-link`).value = `${link}`;
        document.getElementById(`${container}-container`).style.display = 'block';
    });

    
}