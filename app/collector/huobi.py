from locale import currency
import typing as t
from time import sleep
import re

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from app.collector.base import Collector, Order


def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def check_exists_class(browser, classs):
    try:
        browser.find_element(By.CLASS_NAME, classs)
    except NoSuchElementException:
        return False
    return True


class HuobiPriceCollector(Collector):
    def __init__(self, browser) -> None:
        self.__browser = browser

    def collect(self) -> t.Iterable[Order]:
        self.__browser.get("https://c2c.huobi.com/en-us/trade/buy-btc/")

        sleep(7)


        """Скрытие видео"""
        if(check_exists_by_xpath(self.__browser, '/html/body/div[4]/div[2]/div/div/span/i')):
            button = self.__browser.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/span/i')
            button.click()

        sleep(5)

        stay = 1
        more = 1
        fist = 0

        while (stay >= 0):

            """ Считывание страницы"""
            get_source = self.__browser.page_source
            soup = BeautifulSoup(get_source, 'lxml')

            """Поиск лимитов, цен и имен"""
            limits = soup.findAll('div', class_='limit')
            prices = soup.findAll('div', class_='width210 price font-green average mr-40')
            names = soup.findAll('h3', class_='font14')

            for limit, price, name in zip(limits, prices, names):
                groups = re.search(r'((\d\,?\.?)+)-((\d\,?\.?)+)', limit.text)
                min_limit, max_limit = groups.group(1).replace(',', ''), groups.group(3).replace(',', '')

                groups = re.search(r'((\d\,?\.?)+) (\w+)', price.text)
                price_, currency = groups.group(1).replace(',', ''), groups.group(3)

                yield Order(min_amount=float(min_limit), max_amount=float(max_limit), price=float(price_), currency=currency, seller_id=name.text)

            """Переключение страницы"""

            if (check_exists_class(self.__browser, "ivu-page-disabled")):
                stay = stay - 1
                more = more - 1
                fist = 1

            if ((check_exists_by_xpath(self.__browser, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[8]'))):
                next_page = self.__browser.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[8]')
                next_page.click()

            if (not check_exists_class(self.__browser, "ivu-page-disabled") or more >= 0):   
                if((check_exists_by_xpath(self.__browser, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[7]')) and (not check_exists_by_xpath(self.__browser, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[8]'))):
                    next_page = self.__browser.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[7]')
                    next_page.click()

            if ((check_exists_by_xpath(self.__browser, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[6]')) and (not check_exists_by_xpath(self.__browser, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[7]'))):
                next_page = self.__browser.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[3]/div[2]/div[4]/div/ul/li[6]')
                next_page.click()
            
            if (fist):
                more = more - 1
            
            sleep(5)

