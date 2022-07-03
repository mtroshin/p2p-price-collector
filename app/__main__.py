import datetime
import logging
from multiprocessing.sharedctypes import Value
import os



from selenium.webdriver import ChromeOptions, Remote

from app.collector.huobi import HuobiPriceCollector
from app.collector.localbitcoins import LocalbitcoinsPriceCollector


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

    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
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
