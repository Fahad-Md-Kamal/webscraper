import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


def clean_text(text):
    """Clean text by stripping whitespace and removing empty strings"""
    if text:
        return text.strip()
    return ""


def clean_price(text):
    """Extract and clean price information"""
    if text:
        text = text.strip()
        # Remove currency symbol and extract numeric value
        import re
        price_match = re.search(r'৳\s*([\d,]+\.?\d*)', text)
        if price_match:
            return price_match.group(1).replace(',', '')
    return ""


class MedicineItem(scrapy.Item):
    # Basic Information
    name = scrapy.Field()
    generic_name = scrapy.Field()
    strength = scrapy.Field()
    dosage_form = scrapy.Field()
    manufacturer = scrapy.Field()
    
    # Pricing Information
    unit_price = scrapy.Field()
    pack_price = scrapy.Field()
    pack_info = scrapy.Field()
    strip_price = scrapy.Field()
    
    # Medical Information
    indications = scrapy.Field()
    composition = scrapy.Field()
    mode_of_action = scrapy.Field()
    dosage = scrapy.Field()
    side_effects = scrapy.Field()
    contraindications = scrapy.Field()
    precautions = scrapy.Field()
    interaction = scrapy.Field()
    overdose_effects = scrapy.Field()
    pregnancy_category = scrapy.Field()
    storage_conditions = scrapy.Field()
    drug_classes = scrapy.Field()
    
    # URLs and Meta
    url = scrapy.Field()
    brand_id = scrapy.Field()
    pack_image_url = scrapy.Field()
    
    # Scraped metadata
    scraped_at = scrapy.Field()


class MedicineItemLoader(ItemLoader):
    default_item_class = MedicineItem
    default_input_processor = MapCompose(clean_text)
    default_output_processor = TakeFirst()
    
    # Custom processors for specific fields
    unit_price_in = MapCompose(clean_text, clean_price)
    pack_price_in = MapCompose(clean_text, clean_price)
    strip_price_in = MapCompose(clean_text, clean_price)
    
    # Join multiple values for text fields
    indications_out = Join('\n')
    composition_out = Join('\n')
    mode_of_action_out = Join('\n')
    dosage_out = Join('\n')
    side_effects_out = Join('\n')
    contraindications_out = Join('\n')
    precautions_out = Join('\n')
    interaction_out = Join('\n')
    overdose_effects_out = Join('\n')
    storage_conditions_out = Join('\n')
