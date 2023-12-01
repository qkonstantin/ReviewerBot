import time

from bs4 import BeautifulSoup
from selenium import webdriver
import logging


def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)


def quit_driver(driver):
    driver.quit()


def get_transformed_url(url):
    transformed_url = f'{url.split("?")[0]}reviews'
    logging.info(f"Редактирование и открытие отредактированной ссылки: {transformed_url}")
    return transformed_url


class FeedbackParserOZN:
    def __init__(self, url):
        self.url = url
        self.html_content = None  # Добавим переменную для хранения HTML-кода

    def get_html(self):
        if self.html_content is not None:
            return self.html_content

        if not self.url:
            logging.info("Не удалось получить ссылку на товар.")
            return None

        driver_one = create_driver()
        driver_two = None
        try:
            logging.info(f"Получение HTML-контента из URL")
            # Создаем второй драйвер только если ссылка короткая
            if 'ozon.ru/t/' in self.url:
                driver_one.get(self.url)
                long_url = driver_one.current_url
                transformed_url = get_transformed_url(long_url)

                driver_two = create_driver()
                driver_two.get(transformed_url)
                time.sleep(0.1)
                self.html_content = driver_two.page_source
            else:
                transformed_url = get_transformed_url(self.url)
                driver_one.get(transformed_url)
                time.sleep(0.1)
                self.html_content = driver_one.page_source

        finally:
            quit_driver(driver_one)
            if driver_two:
                quit_driver(driver_two)

        return self.html_content

    def get_reviews_from_html(self):
        html_content = self.get_html()
        if not html_content:
            logging.info('Не удалось получить html.')
            return None
        soup = BeautifulSoup(html_content, 'html.parser')
        logging.info("Получение отзывов из HTML")
        all_reviews = []
        characteristics = soup.find_all('div', class_='v3o wo1')

        for characteristic in characteristics:
            characteristic_elemets = characteristic.find_all('div', class_='vo4')
            for characteristic_elemet in characteristic_elemets:
                characteristic = characteristic_elemet.find('div', class_='o4v')
                if characteristic:
                    characteristic = characteristic.get_text(strip=True)
                else:
                    characteristic = 'Комментарий'

                text_element = characteristic_elemet.find('span', class_='ov4')
                if text_element:
                    text = text_element.get_text(strip=True)
                else:
                    text = 'none'
                all_reviews.append(f"{characteristic}: {text}")
        return all_reviews

    def get_item_name(self):
        html_content = self.get_html()
        if not html_content:
            logging.info('Не удалось получить html.')
            return None

        logging.info("Извлечение наименования товара из HTML")
        soup = BeautifulSoup(html_content, 'html.parser')
        item_name = soup.find('a', class_='ln7')

        if item_name:
            name = item_name.get_text(strip=True).split(',')[0]
            # Обрезаем наименование до 60 символов
            truncated_name = name[:60]
            return truncated_name
        else:
            logging.info("Не удалось получить наименование товара.")
            return None

    def get_formatted_reviews(self):
        reviews_text = self.get_reviews_from_html()

        name = self.get_item_name()
        if not reviews_text or not name:
            logging.info('Не удалось получить отредактированные отзывы')
            return None
        logging.info("Редактирование отзывов")
        formatted_text = ("Предоставь ответ в текстовом формате без звёздочек и прочего. Напиши основные плюсы и "
                          "минусы товара {} исходя из отзывов:").format(
            name)
        for review in reviews_text:
            if len(formatted_text) + len(review) <= 4000:
                formatted_text += "\n" + review
            else:
                break
        return formatted_text
