# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShopAdidasItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    page_url = scrapy.Field()
    product_title = scrapy.Field()
    product_category = scrapy.Field()
    image_urls = scrapy.Field()
    product_price = scrapy.Field()
    available_sizes = scrapy.Field()
    breadcrumb_category = scrapy.Field()
    sense_of_size = scrapy.Field()
    coordinated_items = scrapy.Field()
