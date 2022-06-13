from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from app.collector.huobi import HuobiPriceCollector


if __name__ == '__main__':
    options = ChromeOptions()
    options.binary_location='/Users/mtroshin/Private Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    driver = Chrome(ChromeDriverManager().install(), options=options)

    try:
        collector = HuobiPriceCollector(driver)
        for order in collector.collect():
            print(order)
    finally:
        driver.close()
