import scrapy
from scrapy_playwright.page import PageMethod
from medex_scraper.items import MedicineItem, MedicineItemLoader
import re
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime


class MedexSpider(scrapy.Spider):
    name = 'medex'
    allowed_domains = ['medex.com.bd']
    start_urls = ['https://medex.com.bd/brands?page=1']

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 3,
    }

    def start_requests(self):
        """Generate initial requests with Playwright configuration."""
        meta = {
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [
                PageMethod('wait_for_load_state', 'networkidle'),
                PageMethod('wait_for_selector', 'body'),  # Just wait for body to be ready
            ]
        }
        
        url = 'https://medex.com.bd/brands?page=1'
        yield scrapy.Request(
            url=url,
            meta=meta,
            callback=self.parse_listing,
            errback=self.handle_error
        )

    async def parse_listing(self, response):
        """Parse the brands listing page and extract medicine URLs"""
        page = response.meta["playwright_page"]
        
        try:
            # Extract medicine URLs from the listing using the correct selector
            medicine_links = response.css('a[href*="brand"]::attr(href)').getall()
            
            # Filter for actual brand detail pages (not just any link containing 'brand')
            medicine_links = [link for link in medicine_links if link and 'brands/' in link]
            
            self.logger.info(f"Found {len(medicine_links)} medicine links on page")
            
            # Process each medicine link
            for link in medicine_links:
                if link:
                    full_url = urljoin(response.url, link)
                    # Extract brand ID from URL
                    brand_id = self.extract_brand_id(full_url)
                    
                    yield scrapy.Request(
                        url=full_url,
                        callback=self.parse_medicine,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", ".page-heading-1-l", timeout=30000),
                                PageMethod("wait_for_load_state", "networkidle"),
                            ],
                            "brand_id": brand_id,
                        }
                    )
            
            # Check for next page and follow pagination
            next_page = None #response.css('a[rel="next"]::attr(href)').get()
            if next_page:
                next_url = urljoin(response.url, next_page)
                # Limit pagination for testing (remove this in production)
                current_page = self.get_page_number(response.url)
                if current_page < 5:  # Scrape only first 5 pages for testing
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse_listing,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_load_state", "networkidle"),
                                PageMethod("wait_for_selector", "body", timeout=10000),  # Wait for page to load
                                PageMethod("wait_for_timeout", 2000),  # Give extra time for dynamic content
                            ],
                        }
                    )
                else:
                    self.logger.info(f"Reached page limit: {current_page}")
            else:
                self.logger.info("No next page found - pagination complete")
        
        finally:
            await page.close()

    async def parse_medicine(self, response):
        """Parse individual medicine detail page"""
        page = response.meta["playwright_page"]
        
        try:
            loader = MedicineItemLoader(item=MedicineItem(), response=response)
            
            # Basic Information
            loader.add_css('name', '.page-heading-1-l.brand::text')
            loader.add_css('generic_name', 'a[href*="/generics/"]::text')
            loader.add_css('strength', 'div[title="Strength"]::text')
            loader.add_css('dosage_form', '.h1-subtitle::text')
            loader.add_css('manufacturer', 'a[href*="/companies/"]::text')
            
            # Pricing Information
            loader.add_css('unit_price', 'span:contains("Unit Price:") + span::text')
            loader.add_css('pack_price', '.pack-size-info::text')
            loader.add_css('strip_price', 'span:contains("Strip Price:") + span::text')
            
            # Medical Information - these are in collapsible sections
            self.extract_medical_info(loader, response)
            
            # URLs and Meta
            loader.add_value('url', response.url)
            loader.add_value('brand_id', response.meta.get('brand_id'))
            loader.add_value('scraped_at', datetime.now().isoformat())
            
            # Pack image URL
            pack_image = response.css('.mp-trigger::attr(href)').get()
            if pack_image:
                loader.add_value('pack_image_url', urljoin(response.url, pack_image))
            
            yield loader.load_item()
            
        except Exception as e:
            self.logger.error(f"Error parsing medicine page {response.url}: {e}")
        
        finally:
            await page.close()

    def extract_medical_info(self, loader, response):
        """Extract medical information from collapsible sections"""
        
        # Indications
        indications = response.css('#indications + .ac-body *::text').getall()
        if indications:
            loader.add_value('indications', ' '.join([text.strip() for text in indications if text.strip()]))
        
        # Composition
        composition = response.css('#composition + .ac-body *::text').getall()
        if composition:
            loader.add_value('composition', ' '.join([text.strip() for text in composition if text.strip()]))
        
        # Mode of Action
        mode_of_action = response.css('#mode_of_action + .ac-body *::text').getall()
        if mode_of_action:
            loader.add_value('mode_of_action', ' '.join([text.strip() for text in mode_of_action if text.strip()]))
        
        # Dosage
        dosage = response.css('div:contains("dosage") + div *::text, div:contains("Dosage") + div *::text').getall()
        if dosage:
            loader.add_value('dosage', ' '.join([text.strip() for text in dosage if text.strip()]))
        
        # Side Effects
        side_effects = response.css('#side_effects + .ac-body *::text').getall()
        if side_effects:
            loader.add_value('side_effects', ' '.join([text.strip() for text in side_effects if text.strip()]))
        
        # Contraindications
        contraindications = response.css('#contraindications + .ac-body *::text').getall()
        if contraindications:
            loader.add_value('contraindications', ' '.join([text.strip() for text in contraindications if text.strip()]))
        
        # Precautions
        precautions = response.css('#precautions + .ac-body *::text').getall()
        if precautions:
            loader.add_value('precautions', ' '.join([text.strip() for text in precautions if text.strip()]))
        
        # Interaction
        interaction = response.css('#interaction + .ac-body *::text').getall()
        if interaction:
            loader.add_value('interaction', ' '.join([text.strip() for text in interaction if text.strip()]))
        
        # Overdose Effects
        overdose = response.css('#overdose_effects + .ac-body *::text').getall()
        if overdose:
            loader.add_value('overdose_effects', ' '.join([text.strip() for text in overdose if text.strip()]))
        
        # Pregnancy Category
        pregnancy = response.css('#pregnancy_cat + .ac-body *::text').getall()
        if pregnancy:
            loader.add_value('pregnancy_category', ' '.join([text.strip() for text in pregnancy if text.strip()]))
        
        # Storage Conditions
        storage = response.css('#storage_conditions + .ac-body *::text').getall()
        if storage:
            loader.add_value('storage_conditions', ' '.join([text.strip() for text in storage if text.strip()]))
        
        # Drug Classes
        drug_classes = response.css('#drug_classes + .ac-body *::text').getall()
        if drug_classes:
            loader.add_value('drug_classes', ' '.join([text.strip() for text in drug_classes if text.strip()]))

    def extract_brand_id(self, url):
        """Extract brand ID from URL"""
        try:
            # URL format: https://medex.com.bd/brands/13717/3-bion-100-mg-tablet
            match = re.search(r'/brands/(\d+)/', url)
            if match:
                return match.group(1)
        except:
            pass
        return None

    def get_page_number(self, url):
        """Extract page number from URL"""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            page = query_params.get('page', ['1'])[0]
            return int(page)
        except:
            return 1
    
    def handle_error(self, failure):
        """Handle request failures"""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
