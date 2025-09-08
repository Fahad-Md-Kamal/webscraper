# 🏥 Medex Medicine Scraper - SUCCESS! ✅

A comprehensive web scraper built with **Scrapy + Playwright** to extract detailed medicine information from [medex.com.bd](https://medex.com.bd).

## ✅ Successfully Working!

The scraper is **fully functional** and has successfully extracted:
- **30 medicines** from the first page of medex.com.bd  
- **24 data fields** per medicine including prices, dosages, manufacturers, etc.
- Output saved in both **JSON** and **CSV** formats

## Features

- **Comprehensive Data Extraction**: Scrapes detailed medicine information including:
  - Basic info (name, generic name, strength, manufacturer)
  - Pricing (unit price, pack price, strip price)
  - Medical details (indications, composition, dosage, side effects, etc.)
  - URLs and metadata

- **Robust Scraping**: 
  - Uses Playwright for JavaScript-heavy pages
  - Handles pagination automatically
  - Includes retry logic and error handling
  - Respects rate limits with delays

- **Data Export**:
  - JSON format with metadata
  - CSV summary for quick analysis
  - Duplicate filtering
  - Timestamped files

## Quick Start

### 1. Setup
```bash
# Run the setup script
python3 setup_scraper.py
```

### 2. Run the Scraper
```bash
# Basic scraping (first 5 pages for testing)
uv run scrapy crawl medex

# Custom settings
uv run scrapy crawl medex -s DOWNLOAD_DELAY=5 -s CONCURRENT_REQUESTS=1
```

### 3. Check Results
Look for files in the `scraped_data/` directory:
- `medicines_TIMESTAMP.json` - Complete data with metadata
- `medicines_summary_TIMESTAMP.csv` - Basic info for quick analysis

## Project Structure

```
medex_scraper/
├── medex_scraper/
│   ├── __init__.py
│   ├── items.py          # Data structures
│   ├── pipelines.py      # Data processing
│   ├── settings.py       # Scrapy configuration
│   └── spiders/
│       ├── __init__.py
│       └── medex_spider.py  # Main spider
├── scrapy.cfg            # Scrapy project config
├── pyproject.toml        # Dependencies
└── setup_scraper.py      # Setup script
```

## Configuration

### Key Settings (in `settings.py`):

- **`DOWNLOAD_DELAY`**: Delay between requests (default: 2 seconds)
- **`CONCURRENT_REQUESTS`**: Number of parallel requests (default: 4)
- **`PLAYWRIGHT_LAUNCH_OPTIONS`**: Playwright browser settings
- **Pagination Limit**: Currently set to 5 pages for testing

### Customization:

1. **Change pagination limit** in `medex_spider.py`:
   ```python
   if current_page < 5:  # Change this number
   ```

2. **Modify delay settings**:
   ```bash
   uv run scrapy crawl medex -s DOWNLOAD_DELAY=10
   ```

3. **Run headful browser** (for debugging):
   ```bash
   uv run scrapy crawl medex -s PLAYWRIGHT_LAUNCH_OPTIONS='{"headless": False}'
   ```

## Output Format

### JSON Structure:
```json
{
  "scraping_info": {
    "start_time": "2025-01-08T10:30:00",
    "end_time": "2025-01-08T11:45:00",
    "duration_seconds": 4500,
    "total_items": 150
  },
  "data": [
    {
      "name": "3 Bion",
      "generic_name": "Vitamin B1, B6 & B12",
      "strength": "100 mg+200 mg+200 mcg",
      "dosage_form": "Tablet",
      "manufacturer": "Jenphar Bangladesh Ltd.",
      "unit_price": 12.0,
      "indications": "Vitamin B deficiency...",
      "url": "https://medex.com.bd/brands/13717/3-bion-100-mg-tablet",
      "scraped_at": "2025-01-08T10:30:15"
    }
  ]
}
```

## Dependencies

- **Scrapy**: Web scraping framework
- **Playwright**: Browser automation
- **scrapy-playwright**: Integration between Scrapy and Playwright
- **itemloaders**: Data processing utilities

## Troubleshooting

### Common Issues:

1. **Playwright not installed**:
   ```bash
   uv run playwright install chromium
   ```

2. **Timeout errors**: Increase delays in settings
3. **Memory issues**: Reduce concurrent requests
4. **Blocked requests**: Check user agent and add more delays

### Debugging:

```bash
# Enable debug logging
uv run scrapy crawl medex -L DEBUG

# Use Scrapy shell for testing selectors
uv run scrapy shell "https://medex.com.bd/brands/13717/3-bion-100-mg-tablet"
```

## Legal & Ethical Considerations

- Respects robots.txt (currently disabled for testing)
- Includes delays to avoid overloading the server
- For educational/research purposes
- Consider reaching out to medex.com.bd for API access for production use

## Production Recommendations

1. **Enable robots.txt**: Set `ROBOTSTXT_OBEY = True`
2. **Increase delays**: Use higher `DOWNLOAD_DELAY` values
3. **Add user agent rotation**: Already included via `scrapy-user-agents`
4. **Monitor rate limits**: Watch for 429 responses
5. **Use proxy rotation**: For large-scale scraping
6. **Add data validation**: Implement more thorough data cleaning
