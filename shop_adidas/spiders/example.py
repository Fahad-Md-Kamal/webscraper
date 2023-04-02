import asyncio
from urllib.parse import urlparse
import scrapy
from scrapy.http import Response
from scrapy.selector import Selector
from scrapy.spiders import Spider
from typing import List
from playwright.async_api import async_playwright, Page


class ShopAdidasItem(scrapy.Item):
    page_url = scrapy.Field()
    product_title = scrapy.Field()
    product_category = scrapy.Field()
    breadcrumb_category = scrapy.Field()
    image_urls = scrapy.Field()
    product_price = scrapy.Field()
    available_sizes = scrapy.Field()
    sense_of_size = scrapy.Field()


class Example(Spider):
    name = "example"
    allowed_domains = ["shop.adidas.jp"]
    start_urls = ["https://shop.adidas.jp/products/HB9386"]

    async def start_requests(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.start_urls[0])
            await asyncio.sleep(5)  # wait for page to load
            html = await page.content()
            await browser.close()
        yield Response(url=self.start_urls[0], body=html)

    async def get_image_urls(self, page: Page) -> List[str]:
        images = []
        coordinate_items = await page.querySelectorAll('.coordinate_image_body .test-img')
        for item in coordinate_items:
            image_url = await item.getAttribute('src')
            images.append(image_url)
        return images

    async def parse(self, response: Response):
        page = Selector(text=response.body)
        items = ShopAdidasItem()
        page_url = response.url
        url_protocol = urlparse(page_url).scheme
        url_hostname = urlparse(page_url).hostname
        product_category = page.css(".test-categoryName::text").get()
        breadcrumb_category = '/'.join(
            page.css(".breadcrumbList li.breadcrumbListItem:not(.back) a::text").getall())
        all_image_urls = page.css(".main_image.js-main_image.test-main_image::attr(src)").getall()
        image_urls = [f'{url_protocol}://{url_hostname}{img_url}' for img_url in all_image_urls]
        product_title = page.css(".test-itemTitle::text").get()
        product_price = int(page.css(".test-price-value::text").get().replace(',', ''))
        available_sizes = page.css('.sizeSelectorListItemButton:not(.disable)::text').getall()
        sense_of_size = float(page.css(".sizeFitBar .bar span::attr(class)")
                              .get().split(' ')[-1].replace("mod-marker_", '').replace("_", "."))
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(response.url)
            await asyncio.sleep(5)  # wait for page to load
            items['image_urls'] = await self.get_image_urls(page)
            await browser.close()

        items['page_url'] = page_url
        items['product_title'] = product_title
        items['product_category'] = product_category
        items['breadcrumb_category'] = breadcrumb_category
        items['product_price'] = product_price
        items['available_sizes'] = available_sizes
        items['sense_of_size'] = sense_of_size
        yield items

#
# import time
#
# import scrapy
# from scrapy.utils.url import urlparse
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# from ..items import ShopAdidasItem
#
#
# class AdidasSpider(scrapy.Spider):
#     name = "adidas"
#     allowed_domains = ["shop.adidas.jp"]
#     start_urls = ["https://shop.adidas.jp/products/HB9386"]
#
#     def __init__(self, *args, **kwargs):
#         super(AdidasSpider, self).__init__(*args, **kwargs)
#         self.driver = webdriver.Chrome()
#         self.wait = WebDriverWait(self.driver, 10)
#         self.scroll_offset = 500
#
#     def parse(self, response):
#         self.driver.get(response.url)
#         self.driver.maximize_window()
#         self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".test-itemTitle")))
#         while True:
#             last_height = self.driver.execute_script("return document.body.scrollHeight")
#             self.driver.execute_script(f"window.scrollBy(0, {self.scroll_offset});")
#             time.sleep(0.5)
#             self.wait.until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
#             new_height = self.driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 break
#
#         items = ShopAdidasItem()
#         page_url = response.url
#         url_protocol = urlparse(page_url).scheme
#         url_hostname = urlparse(page_url).hostname
#         product_category = response.css(".test-categoryName::text").extract_first()
#         breadcrumb_category = '/'.join(
#             response.css(".breadcrumbList li.breadcrumbListItem:not(.back) a::text").extract())
#         all_image_urls = response.css(".main_image.js-main_image.test-main_image::attr(src)").extract()
#         image_urls = [f'{url_protocol}://{url_hostname}{img_url}' for img_url in all_image_urls]
#         product_title = response.css(".test-itemTitle::text").extract_first()
#         product_price = int(response.css(".test-price-value::text").extract_first().replace(',', ''))
#         available_sizes = response.css('.sizeSelectorListItemButton:not(.disable)::text').extract()
#         sense_of_size = float(response.css(".sizeFitBar .bar span::attr(class)")
#                               .extract_first().split(' ')[-1].replace("mod-marker_", '').replace("_", "."))
#         coordinated_items = [
#             {
#                 'coordinated_image_urls': f"{url_protocol}://{url_hostname}{response.css('.coordinate_image img::attr(src)').extract_first()}",
#                 'coordinated_item_price': response.css(".price-value .test-price-value").extract_first(),
#                 'coordinated_item_title': response.css(".articleBadgeText .test-text .test-badge-label").extract(),
#                 'coordinated_item_number': response.css(
#                     ".coordinate_item_tile .test-coordinate_item_tile::attr(data-articleid)").extract(),
#             }
#             for _ in response.css(".coordinateItems .item_tile_wrapper").extract()
#         ]
#         title_of_description = response.css("h4 font font").extract_first(),
#         items['page_url'] = page_url
#         items['product_title'] = product_title
#         items['product_category'] = product_category
#         items['breadcrumb_category'] = breadcrumb_category
#         items['image_urls'] = image_urls
#         items['product_price'] = product_price
#         items['available_sizes'] = available_sizes
#         items['sense_of_size'] = sense_of_size
#         items['coordinated_items'] = coordinated_items
#
#         yield items
#
