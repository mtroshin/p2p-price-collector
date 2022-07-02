
from selenium.webdriver import ChromeOptions, Chrome
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
import datetime
from app.config import host, user, password, db_name

from app.collector.huobi import HuobiPriceCollector
from app.collector.localbitcoins import LocalbitcoinsPriceCollector
import logging
import os

from selenium.webdriver import ChromeOptions, Remote, Chrome

def create_driver():
    command_executor = os.getenv("COMMAND_EXECUTOR")
    extensions = os.getenv("EXTENSIONS").split(";")
    options = ChromeOptions()
    options.add_argument("start-maximized")
    for ext in extensions:
        options.add_extension(ext)

    driver = Remote(command_executor=command_executor, options=options)
    return driver



if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, os.getenv("LOGGING_LEVEL", "info").upper()))
    
    ct = datetime.datetime.now()
    tss = ct.timestamp()

    driver = create_driver()
    try:
            collector = LocalbitcoinsPriceCollector(driver)
            orders = list(collector.collect())
            print(orders[0])
            connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
            )
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS bits (
                        ts INTEGER,
                        exchange VARCHAR(255),
                        min_amount INTEGER NOT NULL,
                        max_amount INTEGER NOT NULL,
                        price INTEGER NOT NULL,
                        currency VARCHAR(3),
                        bank VARCHAR(255),
                        seller_id VARCHAR);"""
                )
            j = 0
            for i in orders:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO bits VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (tss, 'local', orders[j][0], orders[j][1], orders[j][3], orders[j][2], orders[j][4], orders[j][5]))
                    j += 1
            j = 0
            i = 0
            collector = HuobiPriceCollector(driver)
            orders = list(collector.collect())
            for i in orders:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO bits VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (tss, 'huobi', orders[j][0], orders[j][1], orders[j][3], orders[j][2], orders[j][4], orders[j][5]))
                    j += 1

    

    finally:
        
        driver.close()
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")