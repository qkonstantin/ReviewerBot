from flask import Flask, request, jsonify
from flask_cors import CORS
from gpt import GPT
from parser_wb import FeedbackParserWB
from parser_ozon import FeedbackParserOZN

app = Flask(__name__)
CORS(app)  # Разрешает запросы с других доменов
@app.route('/send_link', methods=['POST'])
def send_link():
    text = ""
    data = request.get_json()
    url = data['url']
    print(url)

    if url.split('/')[2] == 'www.ozon.ru' or url.split('/')[2] == 'ozon.ru':
        extractor = FeedbackParserOZN(url)
        text = extractor.get_formatted_reviews_html()
    elif url.split('/')[2] == 'www.wildberries.ru':
        extractor = FeedbackParserWB(url)
        text = extractor.get_formatted_feedbacks_html()

    # Обрабатываем текст с помощью GPT
    question_str = text
    gpt_instance = GPT(question_str)
    answer = gpt_instance.ask_gpt()

    # Возвращаем текст в расширение
    return jsonify({'text': answer})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
