import time

import scrapy
from scrapy.selector import Selector


def should_abort_loading_image(request):
    return request.resource_type == 'image'


class AdidasShopSpider(scrapy.Spider):
    name = "adidasShop"
    allowed_domains = ["shop.adidas.jp"]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_loading_image
    }

    def start_requests(self):
        for i in range(1, 10): # This takes all the products for the first page. To increase limit increase the range from 2 to n+1
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
        coordinating_items_dict = {}
        coordinated_items = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "css-aa7iv5", " " ))]')

        for idx, item in enumerate(coordinated_items):
            item_number = item.css(".coordinate_item_tile.test-coordinate_item_tile::attr(data-articleid)").extract_first()
            if item_number:
                coordinating_items_dict |= {
                    f'coordinating_item_{idx}_img_url': f'https://shop.adidas.jp/{item.css(".coordinate_image_body::attr(src)").extract_first()}',
                    f'coordinating_item_{idx}_product_number': item_number,
                    f'coordinating_item_{idx}_price': item.css(".test-price-value::text").extract_first(),
                    f'coordinating_item_{idx}_product_name': item.css(".test-badge-label::text").extract_first(),
                    f'coordinating_item_{idx}_item_url': f"https://shop.adidas.jp/products/{item_number}/",
                }
        return coordinating_items_dict

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
        result = {}
        body_parts = response.css(".sizeChartTHeaderCell::text").extract()
        tags = response.css(".sizeChartTable:nth-child(2) tr:nth-child(1) span::text").extract()
        row_count = response.css(".sizeChartTable:nth-child(2) tr").extract()
        sizes = []
        for row_idx in range(len(row_count) + 1):
            if row_idx > 1:
                sizes.append(response.css(f".sizeChartTable:nth-child(2) tr:nth-child({row_idx}) span::text").extract())

        part_tag = []
        for prt in body_parts:
            tmp_list = [f'{prt} - {tg}' for tg in tags]
            part_tag.append(tmp_list)

        for i in range(len(part_tag)):
            result.update(dict(zip(part_tag[i], sizes[i])))

        return result

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

        result = {}
        for idx, rev in enumerate(all_reviews): 
            result.update({
                f"review_{idx}_title": rev.css(".BVRRReviewTitle::text").extract_first(),
                f"review_{idx}_rating": rev.css("#BVRRRatingOverall_Review_Display .BVImgOrSprite::attr(title)").extract_first(),
                f"review_{idx}_date": rev.css(".BVRRReviewDate::text").extract_first(),
                f"review_{idx}_description": rev.css(".BVRRReviewTextContainer span::text").extract_first(),
                f"review_{idx}_reviewer_id": rev.css(".BVRRNickname::text").extract_first().strip(),
            })
        return result

    @staticmethod
    def rating_and_reviews(response):
        if rating := response.css(".BVRRRatingNumber::text").extract_first():
            return {
                "rating": rating,
                "number_of_reviews": response.css(".BVRRBuyAgainTotal::text").extract_first(),
                "recommended_rate": response.css(".BVRRBuyAgainPercentage .BVRRNumber::text").extract_first(),
                response.css(".BVRRRatingHeaderFit::text").extract_first().replace('\n', ''): response.css(".BVImgOrSprite::attr(title)").extract_first(),
                response.css(".BVRRRatingHeaderLength::text").extract_first().replace('\n', ''): response.css(".BVRRRatingLength .BVImgOrSprite::attr(title)").extract_first(),
                response.css(".BVRRRatingHeaderQuality::text").extract_first().replace('\n', ''): response.css(".BVRRRatingQuality .BVImgOrSprite::attr(title)").extract_first(),
                response.css(".BVRRRatingHeaderComfort::text").extract_first().replace('\n', ''): response.css(".BVRRRatingComfort .BVImgOrSprite::attr(title)").extract_first()
            }
        return {}

    async def parse(self, response, **kwargs):
        page = response.meta['playwright_page']
        pxl = 20
        while pxl < 300:
            await page.evaluate(f"window.scrollBy(0, {pxl})")
            time.sleep(0.15)
            pxl += 10
        # await page.wait_for_selector('table') ## Even with this sometimes table is missed to load. Therefore, slow scroll configured. 
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
