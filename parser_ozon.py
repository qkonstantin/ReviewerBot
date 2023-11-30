import time

from bs4 import BeautifulSoup
from selenium import webdriver
import logging


class FeedbackParserOZN:
    def __init__(self, url):
        self.url = url
        self.html_content = None  # Добавим переменную для хранения HTML-кода

    def get_html(self):
        if self.html_content is not None:
            return self.html_content

        url = self.url
        if url == '':
            return "Не удалось получить ссылку на товар. Попробуйте еще раз."
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(1)
        final_url = driver.current_url
        driver.close()
        driver.quit()
        transformed_url = f'{final_url.split("?")[0]}reviews'
        logging.info(f"Получение HTML content из URL: {transformed_url}")
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        driver.get(transformed_url)
        time.sleep(3)
        self.html_content = driver.page_source  # Сохраняем HTML-контент
        driver.close()
        driver.quit()
        return self.html_content

    def get_reviews_from_html(self):
        html_content = self.get_html()
        if not html_content:
            return ["Не удалось получить html. Попробуйте еще раз."]
        soup = BeautifulSoup(html_content, 'html.parser')
        logging.info("Получение отзывов из HTML")
        all_reviews = []
        characteristics = soup.find_all('div', class_='vp7 p5w')

        for characteristic in characteristics:
            characteristic_elemets = characteristic.find_all('div', class_='p8v')
            for characteristic_elemet in characteristic_elemets:
                characteristic = characteristic_elemet.find('div', class_='pv8')
                if characteristic:
                    characteristic = characteristic.get_text(strip=True)
                else:
                    characteristic = 'Комментарий'

                text_element = characteristic_elemet.find('span', class_='v7p')
                if text_element:
                    text = text_element.get_text(strip=True)
                else:
                    text = 'none'
                all_reviews.append(f"{characteristic}: {text}")
        return all_reviews

    def get_item_name(self):
        html_content = self.get_html()
        if not html_content:
            return "Не удалось получить html. Попробуйте еще раз."

        logging.info("Извлечение наименования товара из HTML")
        soup = BeautifulSoup(html_content, 'html.parser')
        item_name = soup.find('div', class_='n21')
        print(item_name)

        if item_name:
            name = item_name.get_text(strip=True).split(',')[0]
            # Обрезаем наименование до 25 символов
            truncated_name = name[:30]
            return truncated_name
        else:
            return "Не удалось получить наименование товара. Попробуйте еще раз."

    def get_formatted_reviews(self):
        reviews_text = self.get_reviews_from_html()

        name = self.get_item_name()
        if not reviews_text or not name:
            return "Не удалось получить отредактированные отзывы. Попробуйте еще раз."
        logging.info("Редактирование отзывов")
        formatted_text = "Напиши основные плюсы и минусы товара {} исходя из отзывов:".format(name)
        for review in reviews_text:
            if len(formatted_text) + len(review) <= 4000:
                formatted_text += "\n" + review
            else:
                break
        return formatted_text
