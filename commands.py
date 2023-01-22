import time
import uuid
import random

import click
import requests
from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from yarl import URL

import settings
from extensions import db
from products.models import Product
from transformers.models import Transformer


@click.command()
def collect_data():
    transformers = db.session.execute(db.select(Transformer)).scalars()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}

    driver = webdriver.Chrome(
        options=options,
        service=ChromeService(ChromeDriverManager().install()),
    )

    base_url = URL("https://www.avito.ru")
    region = "moskva_i_mo"
    # category = "tovary_dlya_detey_i_igrushki"

    for transformer in transformers:
        q = '+'.join(transformer.name.split())
        url = base_url / region % {'q': q}

        driver.get(str(url))

        products = driver.find_elements(By.XPATH, "//*[@data-marker='item']")

        logger.info(len(products))

        SCROLL_PAUSE_TIME = random.randint(0, 200) * 0.01

        # Get scroll height
        full_height = driver.execute_script("return document.body.scrollHeight")
        window_height = driver.execute_script("return window.innerHeight")

        logger.info(full_height)
        logger.info(window_height)

        while True:
            # Scroll down to bottom
            scroll_size = random.randint(100, 1000)
            driver.execute_script(f"window.scrollTo(0, window.scrollY + {scroll_size})")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return window.scrollY") + window_height

            logger.info(new_height)

            if new_height >= full_height:
                break

        element_present = expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "img"))
        WebDriverWait(driver, 50).until(element_present)

        for product in products:
            product_link = product.find_element(By.XPATH, ".//*[@data-marker='item-title']")
            price_tag = product.find_element(By.XPATH, ".//*[@itemprop='price']")

            try:
                product_image = product.find_element(By.XPATH, ".//*[@data-marker='item-photo']//img")
            except NoSuchElementException as e:
                logger.error(e)
                continue

            product_url = product_link.get_attribute("href")
            product_name = product_link.get_attribute("title")
            price = int(price_tag.get_attribute("content"))

            product_image_url = product_image.get_attribute("src")
            # product_image_content = requests.get(product_image_url).content
            # product_image_dir = settings.MEDIA_DIR
            # product_image_filename = f'{uuid.uuid4().hex}.jpg'

            # with open(f"{product_image_dir}/{product_image_filename}", 'wb') as f:
            #     f.write(product_image_content)

            try:
                new_product = Product(
                    name=product_name,
                    image_url=product_image_url,
                    url=product_url,
                    transformer=transformer.id,
                    price=price,
                )
                db.session.add(new_product)
                db.session.commit()
            except Exception as e:
                logger.debug(e)

    driver.close()
