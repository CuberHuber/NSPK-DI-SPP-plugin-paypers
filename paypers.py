"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium.webdriver.common.by import By

from src.spp.types import SPP_document


class PAYPERS:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'paypers'
    HOST = "https://thepaypers.com/news/all"

    _content_document: list[SPP_document]

    def __init__(self, driver, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []
        self.driver = driver

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -

        date_begin = datetime(2019, 1, 1)
        self.driver.get(url=self.HOST)
        req = requests.get(self.HOST)
        if req.status_code == 200:
            req.encoding = "UTF-8"
            urls = []
            dates = []
            soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')
            amount = int(self.driver.find_element(By.ID, "ctl00_MainPlaceHolder_page11Nav").text)
            check = True
            try:
                for i in range(amount):
                    print("страница номер " + str(i))
                    try:
                        page = self.driver.page_source
                        soup = BeautifulSoup(page, 'html.parser')
                        link = soup.find("div", class_="topStories index_group")
                        for link1 in link.find_all("div", class_="index_group"):
                            j = link1.find("h3")
                            k = j.find("a")
                            if not (k.get('href') in urls):
                                urls.append(k.get('href'))
                                print(k.get('href'))
                            else:
                                check = False
                            dates.append(link1.find("span").text)
                    except Exception:
                        print(Exception)
                    print("ссылок всего собрано: " + str(len(urls)))
                    self.driver.execute_script('arguments[0].click()',
                                               self.driver.find_element(By.ID, "ctl00_MainPlaceHolder_nextLink"))
                    # print("кнопка нажата")
                    time.sleep(5)
            except not check:
                print("")


        else:
            self.logger.error('Ошибка обращения к источнику')
            raise RequestException('Источник недоступен')

        # Логирование найденного документа
        # self.logger.info(self._find_document_text_for_logger(document))

        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    @staticmethod
    def some_necessary_method():
        """
        Если для парсинга нужен какой-то метод, то его нужно писать в классе.

        Например: конвертация дат и времени, конвертация версий документов и т. д.
        :return:
        :rtype:
        """
        ...

    @staticmethod
    def nasty_download(driver, path: str, url: str) -> str:
        """
        Метод для "противных" источников. Для разных источника он может отличаться.
        Но основной его задачей является:
            доведение driver селениума до файла непосредственно.

            Например: пройти куки, ввод форм и т. п.

        Метод скачивает документ по пути, указанному в driver, и возвращает имя файла, который был сохранен
        :param driver: WebInstallDriver, должен быть с настроенным местом скачивания
        :_type driver: WebInstallDriver
        :param url:
        :_type url:
        :return:
        :rtype:
        """

        with driver:
            driver.set_page_load_timeout(40)
            driver.get(url=url)
            time.sleep(1)

            # ========================================
            # Тут должен находится блок кода, отвечающий за конкретный источник
            # -
            # ---
            # ========================================

            # Ожидание полной загрузки файла
            while not os.path.exists(path + '/' + url.split('/')[-1]):
                time.sleep(1)

            if os.path.isfile(path + '/' + url.split('/')[-1]):
                # filename
                return url.split('/')[-1]
            else:
                return ""
