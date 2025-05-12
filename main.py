import time
# import json
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from model import Product
from db_connection import get_db_client


def setup_driver():
    """Set up the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")  # Uncomment to run in headless mode
    return webdriver.Chrome(options=options)


def scroll_to_bottom(driver):
    """Scroll to the bottom of the page incrementally."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        for i in range(0, last_height, 300):
            driver.execute_script(f"window.scrollTo(0, {i});")
            print(". ", end=" ")
            time.sleep(0.2)

        time.sleep(2)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the bottom of the page.")
            break
        last_height = new_height
    print("")


def extract_product_urls(driver):
    """Extract product details from the current page."""
    products = driver.find_elements(By.CSS_SELECTOR, ".product-card_product-card__a9BIh")
    print(f"Found {len(products)} products on this page.")
    urls = []
    
    for idx, product in enumerate(products):
        try:
            url = product.find_element(By.CSS_SELECTOR, "header a").get_attribute("href")
            urls.append(url)
            # image = product.find_element(By.CSS_SELECTOR, "img[data-testid='product-card-primary-image']").get_attribute("src")
            # name = product.find_element(By.CSS_SELECTOR, "p[data-testid='product-card-title']").text
            # price = product.find_element(By.CSS_SELECTOR, "div[data-testid='main-price'] span").text.replace("¥", "").replace(",", "").strip()

            # product_data = {
            #     "sl": idx + 1,
            #     "url": url,
            #     "image": image,
            #     "name": name,
            #     "price": price,
            # }
            # products_data.append(Product(**product_data).model_dump())
            # return products_data
        except Exception as e:
            print(f"Error processing product: {e}")
    return urls


def navigate_to_next_page(driver):
    """Navigate to the next page if the 'Next' button exists."""
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.pagination_prev-next-button__Ie7Iz[data-testid='pagination-next-button']"))
        )
        driver.execute_script("arguments[0].click();", next_button)
        print("Navigating to the next page...")
        time.sleep(3)  # Wait for the next page to load
        return True
    except Exception as e:
        print(f"No more pages to navigate or error occurred: {e}")
        return False


def get_all_categories(driver, url):
    """Get all category URLs from the navigation bar."""
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul[data-auto-id='main-menu']"))
    )
    categories = driver.find_elements(By.CSS_SELECTOR, "ul[data-auto-id='main-menu'] li a")
    return [category.get_attribute("href") for category in categories]


def get_sub_categories(driver, url):
    """Get all subcategory URLs from the given URL."""
    try:
        driver.get(url)
        print(f"Fetching subcategories from: {url}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "._wrapper_1xypm_81.grid-row"))
        )

        categories = driver.find_elements(By.CSS_SELECTOR, "._wrapper_1xypm_81.grid-row a")
        subcategory_urls = [categ.get_attribute("href") for categ in categories if categ.get_attribute("href")]
        print(f"Found {len(subcategory_urls)} subcategories.")
        return subcategory_urls

    except Exception as e:
        print(f"Error fetching subcategories: {e}")
        return []

async def scrape_product_detail(driver, url):
    """Scrape product details from the given URL."""
    driver.get(url)
    print(f"Scraping product details from: {url}")
    time.sleep(2)  # Wait for the page to load

    try:
        # Extract product name
        name = driver.find_element(By.CSS_SELECTOR, "h1[data-auto-id='product-title'] span font font").text

        # Extract price
        price_text = driver.find_element(By.CSS_SELECTOR, "div[data-testid='main-price'] span").text
        price = int(price_text.replace("¥", "").replace(",", "").strip())  # Convert price to integer

        # Extract image URL
        image = driver.find_element(By.CSS_SELECTOR, "img[data-auto-id='product-image']").get_attribute("src")

        # Extract rating (if available)
        try:
            rating = driver.find_element(By.CSS_SELECTOR, "button[data-auto-id='product-rating-review-count']").text
        except Exception:
            rating = "No rating available"

        # Extract color
        try:
            color = driver.find_element(By.CSS_SELECTOR, "div[data-auto-id='color-label']").text
        except Exception:
            color = "No color information"

        # Extract sizes
        try:
            size_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-auto-id='size-selector'] button span")
            sizes = [size.text for size in size_elements]
        except Exception:
            sizes = []

        # Construct product data dictionary
        product_data = {
            "name": name,
            "price": price,
            "image": image,
            "url": url,
            "rating": rating,
            "color": color,
            "sizes": sizes,
        }

        print(f"Product Data: {product_data}")

        # Store product data in the database
        client = get_db_client()
        db = client["adidas"]
        collection = db["products"]
        await collection.insert_one(product_data)

    except Exception as e:
        print(f"Error scraping product details: {e}")
        return None
        # product Product(**product_data).model_dump()

    except Exception as e:
        print(f"Error scraping product details: {e}")
        return None


async def scrape_product(driver, category_url):
    """Scrape all products from a single category."""
    driver.get(category_url)
    print(f"Scraping category: {category_url}")
    all_products = []

    while True:
        scroll_to_bottom(driver)
        products = extract_product_urls(driver)
        for product_url in products:
            # all_products.append(product_url)
            print(f"Product URL: {product_url}")
            scrape_product_detail(driver, product_url)


        if not navigate_to_next_page(driver):
            break

    return all_products


async def main():
    """Main function to scrape all categories."""
    driver = setup_driver()
    # categories = []

    # primary_categories = get_all_categories(driver, "https://www.adidas.jp/")

    # for prim_category in primary_categories:
    #     categories.extend(get_sub_categories(driver, prim_category))

    # for category_url in categories:
    #     await scrape_product(driver, category_url)
        
    await scrape_product_detail(driver, "https://www.adidas.jp/%E3%80%90%E3%82%B4%E3%83%AB%E3%83%95%E3%80%91%E3%82%A2%E3%83%87%E3%82%A3%E3%82%AF%E3%83%AD%E3%82%B9-%E3%83%8F%E3%82%A4/H03662.html")

    driver.quit()


if __name__ == "__main__":
    asyncio.run(main())