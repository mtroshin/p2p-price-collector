import typing as t

from time import sleep

import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.collector.base import Collector, Order


log = logging.getLogger(__name__)


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

        log.info("Video skipped")
        element = wait(self.__browser, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'price')))
        sleep(1)

        stay = 1

        orders = WebDriverWait(self.__browser, 10).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, 'info-wrapper'))
        )

        log.info("Orders loaded")

        stay = 1
        page = 1

        while (stay >= 0):

            """Поиск лимитов, цен и имен"""
            limits = self.__browser.find_elements(By.CLASS_NAME, 'limit')
            prices = self.__browser.find_elements(By.CLASS_NAME, 'price')
            names = self.__browser.find_elements(By.CLASS_NAME, 'font14')
            q = len(names) - 3
            del names[:-q]

            for i, (limit, price, name) in enumerate(zip(limits, prices, names)):
                log.info(f"Parsing pos {i}: limit={limit.get_attribute('innerHTML')}:{limit.text}, price={price.get_attribute('innerHTML')}:{price.text}, name={name.get_attribute('innerHTML')}:{name.text}")
                try:
                    groups = re.search(r'((\d\,?\.?)+)-((\d\,?\.?)+)', limit.text)
                    min_limit, max_limit = groups.group(1).replace(',', ''), groups.group(3).replace(',', '')

                    groups = re.search(r'((\d\,?\.?)+) (\w+)', price.text)
                    price_, currency = groups.group(1).replace(',', ''), groups.group(3)

                    yield Order(min_amount=float(min_limit), max_amount=float(max_limit), price=float(price_), currency=currency, seller_id=name.text)

                except Exception as e:
                    log.error(f"Error while parsing pos {i}: limit={limit.get_attribute('innerHTML')}:{limit.text}, price={price.get_attribute('innerHTML')}:{price.text}, name={name.get_attribute('innerHTML')}:{name.text}", exc_info=e)

            """Переключение страницы"""

            next_page = self.__browser.find_element(By.CLASS_NAME, 'ivu-page-next')
            element = wait(self.__browser, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, 'ivu-page-next')))
            next_page.click()
            page += 1

            log.info(f"Page {page} opened")

            if (check_exists_class(self.__browser, "ivu-page-disabled")):
                stay = stay - 1 
            
            sleep(5)

