import datetime
import logging
import os
import time

import psycopg2

from selenium.webdriver import ChromeOptions, Remote

from app.collector.huobi import HuobiPriceCollector
from app.collector.localbitcoins import LocalbitcoinsPriceCollector


log = logging.getLogger(__name__)


def create_driver():
    command_executor = os.getenv("COMMAND_EXECUTOR")
    extensions = os.getenv("EXTENSIONS").split(";")
    options = ChromeOptions()
    options.add_argument("start-maximized")
    for ext in extensions:
        options.add_extension(ext)

    driver = Remote(command_executor=command_executor, options=options)
    return driver


def create_db_conn():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE", "postgres")
    port = int(os.getenv("DB_PORT", "5432"))

    if not host or not user or not password:
        raise ValueError("DB_HOST, DB_USER, DB_PASSWORD are required for start")

    connection = None
    for i in range(5):
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
            )
        except psycopg2.OperationalError as e:
            connection = None
            time_to_sleep_before_retry = 2 ** (i + 1)
            log.error("Error connecting to DB, try #%d, sleeping %d seconds", i + 1, time_to_sleep_before_retry, exc_info=e)
            time.sleep(time_to_sleep_before_retry)

    if not connection:
        raise RuntimeError("Could not connect to database")

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

if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, os.getenv("LOGGING_LEVEL", "info").upper()))
    
    t = datetime.datetime.now().timestamp()

    driver = create_driver()
    db_conn = create_db_conn()
    try:
            collector = LocalbitcoinsPriceCollector(driver)
            orders = list(collector.collect())

            with db_conn.cursor() as cursor:
                for order in orders:
                    cursor.execute(
                        "INSERT INTO bits VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (t, 'local', order.min_amount, order.max_amount, order.price, order.currency, order.bank, order.seller_id)
                    )

            collector = HuobiPriceCollector(driver)
            orders = list(collector.collect())

            with db_conn.cursor() as cursor:
                for order in orders:
                    cursor.execute(
                        "INSERT INTO bits VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (t, 'huobi', order.min_amount, order.max_amount, order.price, order.currency, order.bank, order.seller_id)
                    )

    finally:        
        driver.close()
        db_conn.close()
