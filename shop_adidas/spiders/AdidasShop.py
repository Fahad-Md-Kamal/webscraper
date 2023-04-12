import time
from typing import Dict, Any

import scrapy
from scrapy.selector import Selector
from urllib.parse import urlparse


def should_abort_loading_image(request):
    if request.resource_type == 'image':
        return True
    return False


class AdidasShopSpider(scrapy.Spider):
    name = "adidasShop"
    allowed_domains = ["shop.adidas.jp"]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_loading_image
    }

    def start_requests(self):
        for i in range(1, 7):
            yield scrapy.Request(
                f"https://shop.adidas.jp/item/?gender=mens&category=wear&group=tops&page={i}",
                callback=self.get_products_numbers,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True
                ),
                errback=self.close_page)

    async def get_products_numbers(self, response, **kwargs):
        page = response.meta['playwright_page']
        pxl = 20
        while pxl < 300:
            await page.evaluate(f"window.scrollBy(0, {pxl})")
            time.sleep(0.15)
            pxl += 10
        html = await page.content()
        await page.close()
        selector = Selector(text=html)
        product_numbers = selector.css("a::attr(href)").re(r"/products/(\w+)/")
        for product in product_numbers:
            yield scrapy.Request(
                f"https://shop.adidas.jp/products/{product}/",
                callback=self.parse,
                cb_kwargs={"product_number": product},
                meta=dict(
                    playwright=True,
                    playwright_include_page=True
                ),
                errback=self.close_page)

    async def close_page(self, error):
        page = error.request.meta["playwright_page"]
        await page.close()

    def get_coordinating_items(self, response):
        list_data = []
        coordinated_items = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "css-aa7iv5", " " ))]')
        for item in coordinated_items:
            item_number = item.css(
                ".coordinate_item_tile.test-coordinate_item_tile::attr(data-articleid)").extract_first()
            if item_number:
                list_data.append({
                    f'img_url': f'https://shop.adidas.jp/{item.css(".coordinate_image_body::attr(src)").extract_first()}',
                    f'product_number': item_number,
                    f'price': item.css(".test-price-value::text").extract_first(),
                    f'product_name': item.css(".test-badge-label::text").extract_first(),
                    f'item_url': f"https://shop.adidas.jp/products/{item_number}/",
                })
        if list_data:
            return {"coordinated_items": list_data}
        return {}

    def get_product_information(self, response):
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

    def tale_of_size(self, response) -> dict:
        body_parts = response.css(".sizeChartTHeaderCell::text").extract()
        tags = response.css(".sizeChartTable:nth-child(2) tr:nth-child(1) span::text").extract()
        row_count = response.css(".sizeChartTable:nth-child(2) tr").extract()
        sizes = []
        for row_idx in range(len(row_count) + 1):
            if row_idx > 1:
                row_values = response.css(f".sizeChartTable:nth-child(2) tr:nth-child({row_idx}) span::text").extract()
                zipped_value = [f'{tag} - {val}' for tag, val in zip(tags, row_values)]
                sizes.append(zipped_value)

        result = [{part: ", ".join(size)} for part, size in zip(body_parts, sizes)]
        return {"tale_of_size": result}

    # def special_features_and_its_descriptions(self, response):
    #     return [
    #         {
    #             'function': special_function.css("").extract_first(),
    #             'description': special_function.css("").extract_first()
    #         }
    #         for special_function in response.css("").extract_first()
    #     ]

    @staticmethod
    def review_user_information(response):
        all_reviews = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "BVContentJaJp", " " ))]')

        reviews = [{
            "review_title": rev.css(".BVRRReviewTitle::text").extract_first(),
            'rating': rev.css("#BVRRRatingOverall_Review_Display .BVImgOrSprite::attr(title)").extract_first(),
            'date': rev.css(".BVRRReviewDate::text").extract_first(),
            "review_description": rev.css(".BVRRReviewTextContainer span::text").extract_first(),
            "reviewer_id": rev.css(".BVRRNickname::text").extract_first().strip(),
        } for rev in all_reviews]
        return {"rating": reviews} if reviews else {}

    @staticmethod
    def rating_and_reviews(response):
        rating = response.css(".BVRRRatingNumber::text").extract_first()
        if rating:
            number_of_reviews = response.css(".BVRRBuyAgainTotal::text").extract_first()
            recommended_rate = response.css(".BVRRBuyAgainPercentage .BVRRNumber::text").extract_first()
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
        return {}

    async def parse(self, response, **kwargs):
        page = response.meta['playwright_page']
        pxl = 20
        while pxl < 300:
            await page.evaluate(f"window.scrollBy(0, {pxl})")
            time.sleep(0.15)
            pxl += 10
        html = await page.content()
        await page.close()
        selector = Selector(text=html)
        yield {
            # **self.special_features_and_its_descriptions(selector), # No Example page found. That's why it was left.
            "product_url": response.url,
            "product_number": kwargs.get("product_number"),
            **self.get_coordinating_items(selector),
            **self.tale_of_size(selector),
            **self.rating_and_reviews(selector),
            **self.review_user_information(selector),
        }
