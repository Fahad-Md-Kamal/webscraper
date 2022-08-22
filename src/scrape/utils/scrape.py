import math
from threading import Thread
from bs4 import BeautifulSoup
from requests_html import HTMLSession


from ..models import ScrapeData

BASE_URL = "https://www.ebay.com/b/Desktops-All-In-One-Computers/171957/bn_1643067?rt=nc&_dmd=1"


def get_page_content(link):
    request_url = link
    session = HTMLSession()
    resp = session.get(request_url)
    soup = BeautifulSoup(resp.html.html, "lxml")
    return soup


def get_products_details(resp):
    scraped_item = 0
    content_list = resp.find_all('li', attrs={'class': "s-item s-item--large"})
    for content in content_list:
        try:
            title = content.find_all('h3', attrs={'class': 's-item__title'})[0].getText()
            price = content.find_all('span', attrs={'class': 's-item__price'})[0].getText().replace('$', '').replace(',', '')
            price_splitted = price.split('to')
            if len(price_splitted) > 1:
                price = price_splitted[0]
            image = content.find_all('img')[0]['src']
            product_link = content.find_all('a')[0]['href']
            product_uid = product_link.split('/', maxsplit=5)[-1].split('?')[0]
            product_details = {
                'product_uid': product_uid,
                "title": title,
                "price": float(price),
                "image_src": image,
                "product_link": product_link
            }
            if not ScrapeData.objects.filter(product_uid=product_uid).exists():
                ScrapeData.objects.create(**product_details)
                scraped_item +=1

        except Exception as e:
            print(str(e))
    return scraped_item

def get_total_pages():
    total_page_count = 0
    try:
        html_content = get_page_content(BASE_URL)
        content_list = html_content.find_all('h2', attrs={'class': "srp-controls__count-heading"})[0].getText().split(' ')[0].replace(',', '')
        total_page_count = math.ceil(int(content_list)/48)
    except Exception as e:
        print(str(e))
    return total_page_count

def get_product_data(page_count):
    page_number = 1
    total_items = 0
    while page_number < page_count:
        start_page = f"{BASE_URL}&_pgn={page_number}"
        html_content = get_page_content(start_page)
        total_items += get_products_details(html_content)
        page_number += 1
    return total_items

def start_scrape():
    """
    Start Thread for scraping for better user experience
    """
    page_count = get_total_pages()
    thread_obj = Thread(target=get_product_data, args=(page_count,))
    thread_obj.start()
    return page_count

