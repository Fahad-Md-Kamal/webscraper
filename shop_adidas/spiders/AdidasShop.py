import scrapy
from urllib.parse import urlparse


class AdidasShopSpider(scrapy.Spider):
    name = "adidasShop"
    allowed_domains = ["shop.adidas.jp"]

    def start_requests(self):
        yield scrapy.Request("https://shop.adidas.jp/products/HB9386/", callback=self.parse,
                             meta={"playwright": True,
                                   # "playwright_include_page": True,
                                   })

    @staticmethod
    def _get_url_base(response) -> str:
        page_url = response.url
        return f"{urlparse(page_url).scheme}://{urlparse(page_url).hostname}"

    def _get_coordinating_items(self, response):
        all_coordinating_items = response.css(".carouselListitem").extract()
        base_url = self._get_url_base(response)
        data = response.css(".test-badge-label::text").extract_first()
        price = response.css(".test-price-value::text").extract_first()
        img_url = response.css(".coordinate_image_body::attr(src)").extract_first("")
        product_number = response.css(".coordinate_item_tile::attr(data-articleid)").extract_first()

        return {"product_name": data,
                "product_price": int(price.replace(",", "")),
                "product_image_url": f"{base_url}{img_url}",
                "product_number": product_number,
                "product_url": f"https://shop.adidas.jp/products/{product_number}/"
                }

    def _get_product_information(self, response):
        breadcrumb = response.css(".breadcrumbList li.breadcrumbListItem:not(.back) a::text").extract()
        all_image_urls = response.css(".main_image.js-main_image.test-main_image::attr(src)").getall()
        return {
            "breadcrumb_category": '/'.join(breadcrumb),
            "page_url": response.url,
            "product_category": response.css(".test-categoryName::text").extract_first(),
            "product_name": response.css(".test-categoryName::text").extract_first(),
            "product_title": response.css(".test-itemTitle::text").extract_first(),
            "product_price": float(response.css(".test-price-value::text").extract_first().replace(',', '')),
            "available_sizes": response.css(".sizeSelectorListItemButton:not(.disable)::text").extract(),
            "sense_of_size": float(response.css(".sizeFitBar .bar span::attr(class)")
                                   .get().split(' ')[-1].replace("mod-marker_", '').replace("_", ".")),
            "image_urls": [f'{self._get_url_base(response)}{img_url}' for img_url in all_image_urls]
        }

    def parse(self, response):
        product_information = self._get_product_information(response)
        yield {**product_information
               # "coordinated_products": self._get_coordinating_items(response)
               }

        # page = response.meta["playwright_page"]
        # yield scrapy.Request(
        #     url="https://shop.adidas.jp/men/",
        #     callback=self.parse_headers,
        #     meta={"playwright": True, "playwright_page": page},
        # )
