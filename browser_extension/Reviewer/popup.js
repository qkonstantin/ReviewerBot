document.getElementById('sendLinkButton').addEventListener('click', function() {
  // Блокируем кнопку
  var button = document.getElementById('sendLinkButton');
  button.disabled = true;

  // Получаем текущую ссылку
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var url = tabs[0].url;

    // Проверяем, поддерживается ли ссылка
    var regex = /^(https?:\/\/)?(www\.)?(wildberries\.ru|ozon\.ru)/;
    if (!regex.test(url)) {
      // Выводим ошибку, если ссылка не поддерживается
      var status = document.getElementById('status');
      status.innerText = 'Поддерживается только wildberries и ozon';
      status.style.backgroundColor = 'red';

      var result = document.getElementById('result');
      result.style.display = 'none'; // Скрываем результат

      // Разблокируем кнопку
      button.disabled = false;
      return;
    }

    // Обновляем надпись и стиль статуса
    var status = document.getElementById('status');
    status.innerText = 'Запрос обрабатывается';
    status.style.backgroundColor = 'orange';

    // Отправляем ссылку на сервер
    fetch('http://localhost:5000/send_link', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({url: url})
    })
    .then(response => response.json())
    .then(data => {
      // Вставляем текст в элемент с id "result"
      var result = document.getElementById('result');
      result.innerText = data.text;
      result.style.display = 'block'; // Отобразить элемент

      // Разблокируем кнопку
      button.disabled = false;

      // Обновляем надпись и стиль статуса
      status.innerText = 'Нажмите на кнопку выше, чтобы получить отзывы';
      status.style.backgroundColor = 'green';
    })
    .catch(error => {
      console.error(error);

      // Разблокируем кнопку в случае ошибки
      button.disabled = false;

      // Обновляем надпись и стиль статуса в случае ошибки
      status.innerText = 'Ошибка';
      status.style.backgroundColor = 'red';
    });
  });
});
