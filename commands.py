import uuid

import click
import requests
from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
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
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(
        options=options,
        service=ChromeService(ChromeDriverManager().install()),
    )

    base_url = URL("https://www.avito.ru")
    region = "moskva_i_mo"
    category = "tovary_dlya_detey_i_igrushki"

    for transformer in transformers:
        q = '+'.join(transformer.name.split())
        url = base_url / region / category % {'cd': '1', 'q': q}

        driver.get(str(url))

        products = driver.find_elements(By.XPATH, "//*[@data-marker='item']")

        for product in products:
            product_link = product.find_element(By.XPATH, ".//*[@data-marker='item-title']")

            try:
                product_image = product.find_element(By.XPATH, ".//*[@data-marker='item-photo']//img")
            except NoSuchElementException:
                continue

            product_url = product_link.get_attribute("href")
            product_name = product_link.get_attribute("title")

            product_image_url = product_image.get_attribute("src")
            product_image_content = requests.get(product_image_url).content
            product_image_dir = settings.MEDIA_DIR
            product_image_filename = f'{uuid.uuid4().hex}.jpg'

            with open(f"{product_image_dir}/{product_image_filename}", 'wb') as f:
                f.write(product_image_content)

            try:
                new_product = Product(
                    name=product_name,
                    image=product_image_filename,
                    url=product_url,
                    transformer=transformer.id,
                )
                db.session.add(new_product)
                db.session.commit()
            except Exception as e:
                logger.debug(e)

    driver.close()
