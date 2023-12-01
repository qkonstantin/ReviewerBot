import requests
import regex
from useragent import UserAgentGenerator

class FeedbackParserWB:
    def __init__(self, url):
        self.url = url

    def get_item_id(self):
        pattern = regex.compile(r'catalog/(\d+)/detail')
        match = pattern.search(self.url)
        if match:
            item_id = match.group(1)
            return item_id
        else:
            print("Не удалось найти id товара")

    def get_item_root(self):
        item_id = self.get_item_id()
        url = f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1180979&spp=29&nm={item_id}'
        user_agent = UserAgentGenerator().get_random_user_agent()
        response = requests.get(url, headers=user_agent)
        data = response.json()
        root = data["data"]["products"][0]["root"]
        return root

    def get_item_name(self):
        item_id = self.get_item_id()
        url = f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1180979&spp=29&nm={item_id}'
        user_agent = UserAgentGenerator().get_random_user_agent()
        response = requests.get(url, headers=user_agent)
        data = response.json()
        name = data["data"]["products"][0]["name"]
        return name

    def get_item_feedbacks(self):
        root = self.get_item_root()
        user_agent_2 = UserAgentGenerator().get_random_user_agent()
        url = f'https://feedbacks1.wb.ru/feedbacks/v1/{root}'
        response = requests.get(url, headers=user_agent_2)
        data = response.json()
        if 'feedbacks' in data and data['feedbacks'] is not None:
            if any('text' in review for review in data['feedbacks']):
                reviews_text = [review['text'] for review in data['feedbacks']]
                return reviews_text
            else:
                print('Ошибка: ключ "text" отсутствует во всех словарях.')
        else:
            url = f'https://feedbacks2.wb.ru/feedbacks/v1/{root}'
            response = requests.get(url, headers=user_agent_2)
            data = response.json()
            reviews_text = [review['text'] for review in data['feedbacks']]
            return reviews_text

    def get_formatted_feedbacks(self):
        reviews_text = self.get_item_feedbacks()
        name = self.get_item_name()
        formatted_text = ("Предоставь ответ в текстовом формате, без выделений и прочего."
                          "Напиши основные плюсы и минусы товара {} исходя из отзывов:").format(name)
        for review in reviews_text:
            if len(formatted_text) + len(review) <= 4000:
                formatted_text += "\n" + review
            else:
                break
        return formatted_text