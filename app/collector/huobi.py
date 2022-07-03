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
        self.__browser.execute_script("window.open()")
        sleep(3)
        self.__browser.switch_to.window(self.__browser.window_handles[0])
	
        element = wait(self.__browser, 100).until(ec.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/div/div/span/i')))
	
        """Скрытие видео"""
        if(check_exists_by_xpath(self.__browser, '/html/body/div[4]/div[2]/div/div/span/i')):
            button = self.__browser.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div/span/i')
            button.click()

        log.info("Video skipped")
        element = wait(self.__browser, 100).until(ec.presence_of_element_located((By.CLASS_NAME, 'price')))
        sleep(1)
        bitki = self.__browser.find_elements(By.CLASS_NAME, 'font16')
        bitok = bitki[4]
        bitok.click()
        sleep(1)
        bitok = bitki[5]
        bitok.click()
        sleep(1)
        stay = 1

        orders = WebDriverWait(self.__browser, 10).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, 'info-wrapper'))
        )

        log.info("Orders loaded")
	
        stay = 1
        page = 1
        sdvig = 1
        n = 0
        m = 0
        j = 2
        i = 0
        q = 0      
        payment_c = []        

        while (stay >= 0):
            self.__browser.execute_script("document.body.style.zoom='50%'")
            self.__browser.execute_script("window.scrollTo(0, 0);")
            """Поиск лимитов, цен и имен"""
            limits = self.__browser.find_elements(By.CLASS_NAME, 'limit')
            prices = self.__browser.find_elements(By.CLASS_NAME, 'price')
            names = self.__browser.find_elements(By.CLASS_NAME, 'font14')
            payments = self.__browser.find_elements(By.CLASS_NAME, 'width190')
            payment = self.__browser.find_elements(By.CLASS_NAME, 'payment-block')
            q = len(names) - 3
            del names[:-q]
            q = 1	
            while (j <= ((len(prices) - 1) * 2) + 2):
                for a in payments[j].text:
                    if (payments[j].text[i] == '\n'):
                    	q = q + 1
                    i = i + 1
                j = j + 2
                i = 0
                payment_c.append(q)
                q = 1
            fif = len(names)
            while m < fif:
                while n < (payment_c[m] - 1):
                    limits.insert(m + sdvig, limits[m + sdvig - 1])
                    prices.insert(m + sdvig, prices[m + sdvig - 1])
                    names.insert(m + sdvig, names[m + sdvig - 1])
                    n = n + 1
                    sdvig = sdvig + 1
                n = 0
                m += 1
            payment_c = []
            m = 0
            sdvig = 1
            j = 2


            for i, (limit, price, name, bank) in enumerate(zip(limits, prices, names, payment)):
                log.info(f"Parsing pos {i}: limit={limit.get_attribute('innerHTML')}:{limit.text}, price={price.get_attribute('innerHTML')}:{price.text}, name={name.get_attribute('innerHTML')}:{name.text}")
                try:
                    groups = re.search(r'((\d\,?\.?)+)-((\d\,?\.?)+)', limit.text)
                    min_limit, max_limit = groups.group(1).replace(',', ''), groups.group(3).replace(',', '')

                    groups = re.search(r'((\d\,?\.?)+) (\w+)', price.text)
                    price_, currency = groups.group(1).replace(',', ''), groups.group(3)

                    yield Order(min_amount=float(min_limit), max_amount=float(max_limit), price=float(price_), currency=currency, seller_id=name.text, bank = bank.text)

                except Exception as e:
                    log.error(f"Error while parsing pos {i}: limit={limit.get_attribute('innerHTML')}:{limit.text}, price={price.get_attribute('innerHTML')}:{price.text}, name={name.get_attribute('innerHTML')}:{name.text}", exc_info=e)

            """Переключение страницы"""
            self.__browser.execute_script("document.body.style.zoom='100%'")
            next_page = self.__browser.find_element(By.CLASS_NAME, 'ivu-page-next').click()

            page += 1
            log.info(f"Page {page} opened")

            if (check_exists_class(self.__browser, "ivu-page-disabled")):
                stay = stay - 1 
            i = 0      
            sleep(3)

