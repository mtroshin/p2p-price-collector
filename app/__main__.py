import logging
import os

from selenium.webdriver import ChromeOptions, Remote

from app.collector.huobi import HuobiPriceCollector
from app.collector.localbitcoins import LocalbitcoinsPriceCollector


def create_driver():
    command_executor = os.getenv("COMMAND_EXECUTOR")
    extensions = os.getenv("EXTENSIONS").split(";")
    options = ChromeOptions()
    for ext in extensions:
        options.add_extension(ext)

    driver = Remote(command_executor=command_executor, options=options)
    return driver


if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, os.getenv("LOGGING_LEVEL", "info").upper()))

    driver = create_driver()
    try:
        collector = LocalbitcoinsPriceCollector(driver)
        for order in collector.collect():
            print('l', order)


        collector = HuobiPriceCollector(driver)
        for order in collector.collect():
            print('h', order)
    finally:
        driver.close()