import os
from pathlib import Path
import scrapy


class NikeSpider(scrapy.Spider):
    name = "nike"
    allowed_domains = ["www.nike.com", "nike.com"]
    # Default to the Basketball category
    start_urls = [
        os.getenv("NIKE_CATEGORY_URL", "https://www.nike.com/w/basketball-3glsm"),
    ]

    custom_settings = {
        # Be a bit nicer
        "DOWNLOAD_DELAY": 0.5,
    }

    def start_requests(self):
        local_file = getattr(self, "local_file", None)
        if local_file:
            file_url = Path(local_file).expanduser().resolve().as_uri()
            yield scrapy.Request(file_url, callback=self.parse)
            return
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # Extract product cards
        for card in response.css('div.product-card[data-testid="product-card"]'):
            url = card.css('a.product-card__link-overlay::attr(href)').get()
            title = card.css('div.product-card__title::text').get()
            subtitle = card.css('div.product-card__subtitle::text').get()
            price_text = card.css('[data-testid="product-card__price"] [data-testid="product-price"]::text').get()
            if not price_text:
                price_text = card.css('.product-card__price .product-price.is--current-price::text').get()
            image_alt = card.css('img.product-card__hero-image::attr(alt)').get()
            position = card.attrib.get('data-product-position')

            if url and url.startswith('/'):
                url = response.urljoin(url)

            yield {
                "title": (title or '').strip() or None,
                "subtitle": (subtitle or '').strip() or None,
                "price": (price_text or '').strip() or None,
                "url": url,
                "image_alt": image_alt,
                "position": int(position) if position and position.isdigit() else position,
                "category_url": response.url,
                "source": "nike_basketball",
            }

        # If there is pagination, follow the next page link (Nike often uses infinite scroll; skip if absent)
        next_href = response.css('a[aria-label="Next Page"]::attr(href), a[rel="next"]::attr(href)').get()
        if next_href:
            yield response.follow(next_href, callback=self.parse)
