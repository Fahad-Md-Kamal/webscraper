import scrapy
from chocolatescraper.items import ChocolateProduct
from chocolatescraper.itemloaders import ChocolateProductLoader


class ChocolatespiderSpider(scrapy.Spider):
    name = 'chocolatespider'
    allowed_domains = ['chocolate.co.uk']
    start_urls = ['https://www.chocolate.co.uk/collections/all']


    def parse(self, response):
        products = response.css("product-item")
        
        for product in products:
            price = product.css("span.price").get().replace(" price--highlight", "").replace('<span class="price">\n              <span class="visually-hidden">Sale price', "").replace("</span>", "").replace("\n", "")


            chocolate = ChocolateProductLoader(item=ChocolateProduct(), selector=product)
            chocolate.add_css('name', 'a.product-item-meta__title::text')
            chocolate.add_value('price', price) 
            chocolate.add_css('url', 'div.product-item-meta a::attr(href)')
            yield chocolate.load_item()

        next_page = response.css('[rel="next"] ::attr(href)').get()
        if next_page is not None:
            next_page_url = "https://www.chocolate.co.uk" + next_page
            yield response.follow(next_page_url, callback=self.parse)
