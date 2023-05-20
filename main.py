from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
from time import sleep
from config import ConfigDataLoader


class ParseVacansiesLink:
    """
    Класс парсит ссылки вакансий по заданным ключевым словам и сохраняем их в файл
    """

    INSTANCE = None

    def __new__(cls):
        """
        Singleton pattern
        """
        if not cls.INSTANCE:
            cls.INSTANCE = object.__new__(cls)
        return cls.INSTANCE

    def __init__(self, keys: tuple =('flask', 'python')):
        self.URL: str = "https://hh.ru/search/vacancy?no_magic=true&L_save_area=true&text=&excluded_text=&professional_role=96&professional_role=114&professional_role=160&area=16&salary=&currency_code=RUR&experience=doesNotMatter&order_by=publication_time&search_period=30&items_on_page=50&page={}"
        self.START_PAGE: int = 0
        self.COUNT_PAGE: int | None = None
        self.KEYS_WORDS: tuple = keys
        self.user_agent = ConfigDataLoader.UA
        self.vacansies_link_list: list = []

        self.options = webdriver.ChromeOptions()
        self.options.add_argument(r'--user-data-dir=userData')
        self.options.add_argument(self.user_agent)


    def __call__(self):

        with webdriver.Chrome(options=self.options) as driver:
            driver.set_window_size(1850, 1000)

            driver.get(self.URL.format(0))
            # проскролить в низ страницы
            driver.execute_script("window.scrollTo(0, 14000)")
            # узнать количество страниц по номеру предпослелней кнопки пагинации
            paginate_block = driver.find_element(By.CLASS_NAME, 'pager')
            self.COUNT_PAGE = int(paginate_block.find_elements(By.CLASS_NAME, 'bloko-button')[-2].text) # количество страниц

            self.__get_link_in_all_page(driver=driver)
            self.__save_link_in_json_file(self.vacansies_link_list)
            driver.close()


    
    def __get_link_in_all_page(self, driver: webdriver.Chrome):

        while self.START_PAGE <= self.COUNT_PAGE:
            driver.get(self.URL.format(self.START_PAGE))
            driver.execute_script("window.scrollTo(0, 14000)")
            # собрать все вакансии со страницы
            vacansies = driver.find_elements(By.CLASS_NAME, 'serp-item')
            for vacanci in vacansies:
                # получить заголовок вакансии
                title = vacanci.find_element(By.TAG_NAME, 'h3')

                for word in title.text.split():
                    # если слово из заголовка есть в массиве ключей то добавить вакансию в список-вакансий
                    # и выйти из цикла для перехода к следующей вакансии
                    if word.lower() in self.KEYS_WORDS:
                        link_vacanci = title.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        self.vacansies_link_list.append(link_vacanci)
                        break
            # увеличивваем счетчик
            self.START_PAGE += 1
            sleep(10)

    def __save_link_in_json_file(self, vac_list):
        """
        Сохранение вакансий в json file
        """
        dict_vac = {i: vac for i, vac in enumerate(vac_list)}
        with open('vacansies.json', 'w', encoding='utf-8') as file:
            json.dump(list(dict_vac), file, ensure_ascii=False, indent=4)

def parce():
    """
    Запускает парсинг ссылок
    """
    parce = ParseVacansiesLink()
    parce()

class MallingResumeForVaccancies(ParseVacansiesLink):
    """

    """

    def __init__(self):
        self.URL = 'https://hh.ru/'
        self.user_agent = ConfigDataLoader.UA

        with open('resume.txt', encoding='utf-8') as file:
            self.resume_text = file.read()
        with open('vacansies.json', encoding='utf-8') as file:
            self.links: list[dict] = json.load(file)


        self.options = Options()
        self.options.add_argument(r'--user-data-dir=userData')
        self.options.add_argument(self.user_agent)
        self.options.add_argument("--referer=https://hh.ru/")

    
    def _process_authentification_in_site(self, driver: webdriver.Chrome):
            """
            Метод выполняет аутиндефикацию на сайте
            Необходим 1 раз, в дальнейшем данные запомнит каталог userData который вы передали в опции драйвера
            """
            driver.get(self.URL)
            # регистрация
            button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="HH-React-Root"]/div/div[2]/div[1]/div/div/div/div[5]/a')))
            button.click()
            # вставить в поле входа емеил
            input_p = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, 'login')))
            driver.execute_script("arguments[0].value='ilyabulatau@gmail.com';", input_p)
            # кликнуть на кнопку ввода емейла
            button2 = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.TAG_NAME, 'button')))
            button2.click()
            sleep(120)


    def __call__(self):
        """
        При первом запуске скрипта в начале этого метода(после менеджера контекста with) следует прописать метод _process_authentification_in_site
        и передать в не обьект драйвера
        А так же пройти аутендификацию нужно будет в ручную для этого стоит слип на 120 сек что бы успеть чекнуть смс на емейле
        После этого данные аутендификации попадут в папку определенную в найстройках user-data в опциях драйвера 
        И в дальнейшем вход будет происходить в качестве авторизованного юзера
        """

        with webdriver.Chrome(options=self.options) as driver:
            driver.set_window_size(1850, 1000)

            for urls in self.links:
                # проходимся по найденым вакансиям
                for url in urls.values():
                    driver.get(url)

                    # находим и кликамем оставить отклик
                    button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Откликнуться')))
                    button.click()
                    # находим и кликаем добавить сопроводительное
                    button_text = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="RESPONSE_MODAL_FORM_ID"]/div/div/div[3]/button')))
                    button_text.click()
                    # вставляем сопроводительное
                    send_text = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.TAG_NAME, 'textarea')))
                    driver.execute_script(f"arguments[0].value='{self.resume_text}';", send_text)
                    # отправлем отклик
                    responce_send = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[14]/div/div[2]/div[5]/button[2]')))
                    responce_send.click()
                    # что бы не наглеть подождем
                    sleep(20)
                    print(url)
                    
            driver.close()

def mailling():
    """
    Начать рассылку резюме
    """
    maillong = MallingResumeForVaccancies()
    maillong()

if __name__ == "__main__":
    mailling()
