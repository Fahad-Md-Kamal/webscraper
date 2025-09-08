import json
import logging
from datetime import datetime
from pathlib import Path
from scrapy.exceptions import DropItem
from sqlalchemy.exc import IntegrityError
from .models import Medicine, db_manager


class MedexScraperPipeline:
    """Pipeline for processing scraped medicine data"""
    
    def process_item(self, item, spider):
        """Process each scraped item"""
        
        # Clean and validate data
        self.clean_item_data(item)
        
        # Log the processed item
        spider.logger.info(f"Processed item: {item.get('name', 'Unknown')}")
        
        return item
    
    def clean_item_data(self, item):
        """Clean and normalize item data"""
        
        # Clean text fields by removing extra whitespace
        text_fields = [
            'name', 'generic_name', 'strength', 'dosage_form', 'manufacturer',
            'indications', 'composition', 'mode_of_action', 'dosage',
            'side_effects', 'contraindications', 'precautions', 'interaction',
            'overdose_effects', 'pregnancy_category', 'storage_conditions',
            'drug_classes'
        ]
        
        for field in text_fields:
            if field in item and item[field]:
                # Clean multiple spaces and newlines
                cleaned_text = ' '.join(item[field].split())
                item[field] = cleaned_text
        
        # Clean price fields - ensure they're numeric
        price_fields = ['unit_price', 'pack_price', 'strip_price']
        for field in price_fields:
            if field in item and item[field]:
                try:
                    # Remove any non-numeric characters except decimal point
                    import re
                    cleaned_price = re.sub(r'[^\d.]', '', str(item[field]))
                    if cleaned_price:
                        item[field] = float(cleaned_price)
                    else:
                        item[field] = None
                except (ValueError, TypeError):
                    item[field] = None


class JsonExportPipeline:
    """Pipeline for exporting data to JSON files"""
    
    def open_spider(self, spider):
        """Initialize the pipeline when spider opens"""
        self.items = []
        self.start_time = datetime.now()
        
        # Create output directory
        self.output_dir = Path('scraped_data')
        self.output_dir.mkdir(exist_ok=True)
        
        spider.logger.info(f"Started scraping at {self.start_time}")
    
    def close_spider(self, spider):
        """Save all items to JSON when spider closes"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Create filename with timestamp
        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f'medicines_{timestamp}.json'
        
        # Prepare metadata
        metadata = {
            'scraping_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'total_items': len(self.items),
                'spider_name': spider.name,
            },
            'data': self.items
        }
        
        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        spider.logger.info(f"Saved {len(self.items)} items to {filename}")
        spider.logger.info(f"Scraping completed in {duration}")
        
        # Also create a simple CSV summary
        self.create_csv_summary(timestamp)
    
    def process_item(self, item, spider):
        """Add item to the collection"""
        self.items.append(dict(item))
        return item
    
    def create_csv_summary(self, timestamp):
        """Create a CSV summary of basic medicine info"""
        try:
            import csv
            
            csv_filename = self.output_dir / f'medicines_summary_{timestamp}.csv'
            
            if not self.items:
                return
            
            # Define CSV columns
            csv_columns = [
                'name', 'generic_name', 'strength', 'dosage_form', 
                'manufacturer', 'unit_price', 'brand_id', 'url'
            ]
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                
                for item in self.items:
                    # Create a row with only the specified columns
                    row = {col: item.get(col, '') for col in csv_columns}
                    writer.writerow(row)
            
            logging.info(f"Created CSV summary: {csv_filename}")
            
        except Exception as e:
            logging.error(f"Error creating CSV summary: {e}")


class DuplicateFilterPipeline:
    """Pipeline to filter out duplicate items based on brand_id"""
    
    def __init__(self):
        self.seen_ids = set()
    
    def process_item(self, item, spider):
        """Filter out duplicate items"""
        url = item.get('url')
        
        if url in self.seen_ids:
            spider.logger.warning(f"Duplicate item found: {item.get('name')} (Url: {url})")
            raise DropItem(f"Duplicate item: {url}")
        else:
            self.seen_ids.add(url)
            return item


class PostgreSQLPipeline:
    """Pipeline to save items to PostgreSQL database"""
    
    def open_spider(self, spider):
        """Initialize database connection when spider opens"""
        # Test database connection (tables should be managed by Alembic)
        if db_manager.test_connection():
            spider.logger.info("✅ PostgreSQL pipeline initialized successfully")
        else:
            spider.logger.error("❌ Failed to connect to PostgreSQL database")
            raise Exception("Database connection failed - ensure Alembic migrations are applied")
    
    def close_spider(self, spider):
        """Clean up when spider closes"""
        spider.logger.info("PostgreSQL pipeline closed")
    
    def process_item(self, item, spider):
        """Process and save item to database"""
        # Create database session
        session = db_manager.get_session()
        
        try:
            # Check if medicine already exists by brand_id or name
            existing_medicine = session.query(Medicine).filter(
                (Medicine.brand_id == item.get('brand_id')) |
                (Medicine.name == item.get('name'))
            ).first()
            
            if existing_medicine:
                # Update existing record
                for field, value in item.items():
                    if value and hasattr(existing_medicine, field):
                        setattr(existing_medicine, field, value)
                
                spider.logger.info(f"Updated medicine: {item.get('name')}")
            else:
                # Create new medicine record
                medicine = Medicine(
                    brand_id=item.get('brand_id'),
                    name=item.get('name'),
                    generic_name=item.get('generic_name'),
                    strength=item.get('strength'),
                    dosage_form=item.get('dosage_form'),
                    manufacturer=item.get('manufacturer'),
                    unit_price=self._safe_float(item.get('unit_price')),
                    pack_price=self._safe_float(item.get('pack_price')),
                    strip_price=self._safe_float(item.get('strip_price')),
                    pack_info=item.get('pack_info'),
                    indications=item.get('indications'),
                    composition=item.get('composition'),
                    mode_of_action=item.get('mode_of_action'),
                    dosage=item.get('dosage'),
                    side_effects=item.get('side_effects'),
                    contraindications=item.get('contraindications'),
                    precautions=item.get('precautions'),
                    interaction=item.get('interaction'),
                    overdose_effects=item.get('overdose_effects'),
                    pregnancy_category=item.get('pregnancy_category'),
                    storage_conditions=item.get('storage_conditions'),
                    drug_classes=item.get('drug_classes'),
                    url=item.get('url'),
                    pack_image_url=item.get('pack_image_url')
                )
                
                session.add(medicine)
                spider.logger.info(f"Added new medicine: {item.get('name')}")
            
            # Commit the transaction
            session.commit()
            
        except IntegrityError as e:
            session.rollback()
            spider.logger.warning(f"Integrity error for {item.get('name')}: {e}")
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error saving {item.get('name')}: {e}")
        finally:
            session.close()
        
        return item
    
    def _safe_float(self, value):
        """Safely convert string to float"""
        if not value:
            return None
        try:
            # Remove any non-numeric characters except decimal point
            import re
            clean_value = re.sub(r'[^\d.]', '', str(value))
            return float(clean_value) if clean_value else None
        except (ValueError, TypeError):
            return None
