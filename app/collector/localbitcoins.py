import datetime as dt
import logging
import re
import typing as t

from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from app.collector.base import Collector, Order


log = logging.getLogger(__name__)


class LocalbitcoinsPriceCollector(Collector):
    def __init__(self, browser) -> None:
        self.__browser = browser

    def collect(self) -> t.Iterable[Order]:
        self.__browser.get("https://localbitcoins.com/ru/buy-bitcoins-online/rub/")
        get_source = self.__browser.page_source
        page = ""
        soup = BeautifulSoup(get_source, 'lxml')
        pages = soup.find('div', class_='pull-right')
    
        x = 48
        
        while (pages.text[x] != '\n'):
            page = page + pages.text[x]
            x = x + 1
    
        total = 1 + (int(page)//50)

        current_page = 1
        while(current_page <= total):
            self.__browser.get("https://localbitcoins.com/ru/buy-bitcoins-online/rub/?page=" + str(current_page))

            log.info(f"Page {current_page} loaded")

            current_page = current_page + 1
            sleep(7)
            """Считывание страницы"""
            get_source = self.__browser.page_source
            soup = BeautifulSoup(get_source, 'lxml')
            limits = soup.findAll('td', class_='column-limit')
            prices = soup.findAll('td', class_='column-price')
            names = soup.findAll('td', class_='column-user')
            """Заброс лимитов, цен и имен в массивы"""
            i = 0
            banks = []
            while i < len(names):
                banks.append((self.__browser.find_element((By.XPATH, '/html/body/div[4]/table/tbody/tr[' + str(i + 2) + ']/td[2]'))).text)
                i += 1
            i = 0

            for limit, price, name, bank in zip(limits, prices, names, banks):
                groups = re.search(r'((\d\,?\.?)+) (\w+)', price.text)
                price_, currency_ = groups.group(1).replace(',', ''), groups.group(3)

                groups = re.search(r'((\d\,?\.?)+) - ((\d\,?\.?)+)', limit.text)
                min_limit, max_limit = groups.group(1).replace(',', ''), groups.group(3).replace(',', '')

                seller_id = name.text.replace('\n', '')

                yield Order(min_amount=float(min_limit), max_amount=float(max_limit), currency=currency_, price=float(price_), seller_id=seller_id, bank = bank.text)
