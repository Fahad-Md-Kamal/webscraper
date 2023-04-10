import time

import scrapy
from scrapy.selector import Selector
from urllib.parse import urlparse
from scrapy_playwright.page import PageMethod


class AdidasShopSpider(scrapy.Spider):
    name = "adidasShop"
    allowed_domains = ["shop.adidas.jp"]

    def start_requests(self):
        yield scrapy.Request("https://shop.adidas.jp/products/HB9386/", callback=self.parse,
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 # playwright_page_methods=[
                                     # PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                                     # PageMethod('wait_for_selector', 'table'),
                                 # ]
                             ),
                             errback=self.close_page
                             )

    async def close_page(self, error):
        page = error.request.meta["playwright_page"]
        await page.close()

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

        return {
            "product_name": data,
            "product_price": int(price.replace(",", "")),
            "product_image_url": f"{base_url}{img_url}",
            "product_number": product_number,
            "product_url": f"https://shop.adidas.jp/products/{product_number}/"
        }

    def _get_product_information(self, response):
        breadcrumb = response.css(".breadcrumbList li.breadcrumbListItem:not(.back) a::text").extract()
        all_image_urls = response.css(".main_image.js-main_image.test-main_image::attr(src)").getall()
        return {
            "breadcrumb_category": ' / '.join(breadcrumb),
            "page_url": response.url,
            "product_category": response.css(".test-categoryName::text").extract_first(),
            "product_name": response.css(".test-categoryName::text").extract_first(),
            "product_title": response.css(".test-itemTitle::text").extract_first(),
            "product_price": float(response.css(".test-price-value::text").extract_first().replace(',', '')),
            "available_sizes": response.css(".sizeSelectorListItemButton:not(.disable)::text").extract(),
            "sense_of_size": float(response.css(".sizeFitBar .bar span::attr(class)")
                                   .get().split(' ')[-1].replace("mod-marker_", '').replace("_", ".")),
            "image_urls": [f'{self._get_url_base(response)}{img_url}' for img_url in all_image_urls],
            "title_of_description": response.css(".inner h4::text").extract_first(),
            "general_description": response.css(".test-commentItem-mainText::text").extract_first(),
            "general_description_itemization": response.css(".articleFeaturesItem::text").extract(),
        }

    @staticmethod
    def tale_of_size(response) -> dict:
        body_parts = response.css(".sizeChartTHeaderCell::text").extract()
        tags = response.css(".sizeChartTable:nth-child(2) tr:nth-child(1) span::text").extract()
        row_count = response.css(".sizeChartTable:nth-child(2) tr").extract()
        sizes = []
        for row_idx in range(len(row_count)+1):
            if row_idx > 1:
                row_values = response.css(f".sizeChartTable:nth-child(2) tr:nth-child({row_idx}) span::text").extract()
                zipped_value = [f'{tag} - {val}' for tag, val in zip(tags, row_values)]
                sizes.append(zipped_value)

        result = [f'{part} :: {" | ".join(size)}' for part, size in zip(body_parts, sizes)]
        return {"tale_of_size": result}

    @staticmethod
    def special_features_and_its_descriptions(response):
        return [
            {
                'function': special_function.css("").extract_first(),
                'description': special_function.css("").extract_first()
            }
            for special_function in response.css("").extract_first()
        ]

    @staticmethod
    def review_user_information(response):
        date = response.css("").extract_first()
        rating = response.css(".BVRRRatingNumber::text").extract_first()
        review_title = response.css("").extract_first()
        review_description = response.css("").extract_first()
        reviewer_id = response.css("").extract_first()
        return {
            "rating": rating
        }

    @staticmethod
    def rating_and_reviews(response):
        rating = response.css(".BVRRRatingNumber::text").extract_first().replace('\n', '')
        number_of_reviews = response.css(".BVRRBuyAgainTotal::text").extract_first().replace('\n', '')
        recommended_rate = response.css(".BVRRBuyAgainPercentage .BVRRNumber::text").extract_first().replace('\n', '')
        sense_of_fitting_and_its_rating = {response.css(".BVRRRatingHeaderFit::text").extract_first().replace('\n', ''): response.css(".BVImgOrSprite::attr(title)").extract_first()}
        appropriation_of_length_and_its_rating = {response.css(".BVRRRatingHeaderLength::text").extract_first().replace('\n', ''): response.css(".BVRRRatingLength .BVImgOrSprite::attr(title)").extract_first()}
        quality_of_material_and_its_rating = {response.css(".BVRRRatingHeaderQuality::text").extract_first().replace('\n', ''): response.css(".BVRRRatingQuality .BVImgOrSprite::attr(title)").extract_first()}
        comfort_and_its_rating = {response.css(".BVRRRatingHeaderComfort::text").extract_first().replace('\n', ''): response.css(".BVRRRatingComfort .BVImgOrSprite::attr(title)").extract_first()}
        return {
            "rating": rating,
            "number_of_reviews": number_of_reviews,
            "recommended_rate": recommended_rate,
            "sense_of_fitting_and_its_rating": sense_of_fitting_and_its_rating,
            "appropriation_of_length_and_its_rating": appropriation_of_length_and_its_rating,
            "quality_of_material_and_its_rating": quality_of_material_and_its_rating,
            "comfort_and_its_rating": comfort_and_its_rating
        }

    async def parse(self, response, **kwargs):
        page = response.meta['playwright_page']
        pxl = 20
        while pxl < 500:
            await page.evaluate(f"window.scrollBy(0, {pxl})")
            time.sleep(0.15)
            pxl += 10
        await page.wait_for_selector('table')
        html = await page.content()
        await page.close()
        selector = Selector(text=html)
        # yield self.tale_of_size(sel)
        yield self.rating_and_reviews(selector)
