from locale import currency
import typing as t
from time import sleep
import re



from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as wait
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

        element = wait(self.__browser, 10).until(ec.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/div/div/span/i')))

        """Скрытие видео"""
        if(check_exists_by_xpath(self.__browser, '/html/body/div[4]/div[2]/div/div/span/i')):
            button = self.__browser.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/span/i')
            button.click()
        element = wait(self.__browser, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'price')))
        sleep(1)

        stay = 1

        fist = 0

        while (stay >= 0):

            """ Считывание страницы"""
            get_source = self.__browser.page_source


            """Поиск лимитов, цен и имен"""
            limits = self.__browser.find_elements(By.CLASS_NAME, 'limit')
            prices = self.__browser.find_elements(By.CLASS_NAME, 'price')
            names = self.__browser.find_elements(By.CLASS_NAME, 'font14')
            q = len(names) - 3
            del names[:-q]

            for limit, price, name in zip(limits, prices, names):
                groups = re.search(r'((\d\,?\.?)+)-((\d\,?\.?)+)', limit.text)
                min_limit, max_limit = groups.group(1).replace(',', ''), groups.group(3).replace(',', '')

                groups = re.search(r'((\d\,?\.?)+) (\w+)', price.text)
                price_, currency = groups.group(1).replace(',', ''), groups.group(3)

                yield Order(min_amount=float(min_limit), max_amount=float(max_limit), price=float(price_), currency=currency, seller_id=name.text)

            """Переключение страницы"""

            next_page = self.__browser.find_element(By.CLASS_NAME, 'ivu-page-next')
            element = wait(self.__browser, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, 'ivu-page-next')))
            next_page.click()
            

  
            if (check_exists_class(self.__browser, "ivu-page-disabled")):
                stay = stay - 1 
            
            sleep(5)

