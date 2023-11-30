import requests

# URL страницы с отзывами
url = 'https://feedbacks2.wb.ru/feedbacks/v1/14195922'

# Заголовки для имитации браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Отправка HTTP-запроса и получение содержимого страницы
response = requests.get(url, headers=headers)
data = response.json()

# извлечение текста отзывов
reviews_text = [review['text'] for review in data['feedbacks']]

print(reviews_text)