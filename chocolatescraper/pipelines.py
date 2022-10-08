# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem 
import mysql.connector
import psycopg2
from pymongo import MongoClient


class ChocolatescraperPipeline:
    def process_item(self, item, spider):
        return item


class PriceToUSDPipeline:
    gdpToUsdRate = 1.3

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('price'):
            floatPrice = float(adapter['price'])
            adapter['price'] = floatPrice * self.gdpToUsdRate
            return item
        else:
            raise DropItem("Missing price in {item}")


class DuplicatePipeline:

    def __init__(self):
        self.name_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter['name'] in self.name_seen:
            raise DropItem("Duplicate Item found: {item!r}")
        else:
            self.name_seen.add(adapter['name'])
            return item

class SavingToMysqlPipeline(object):
    """
    MySQL DB

    Args:
        object (_type_): _description_
    """
    def __init__(self):
        self.create_connection()

    
    def create_connection(self):
        self.connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'mevr1k1234',
            database = 'scrapy_db',
            port = '3306'
        )
        self.curr = self.connection.cursor()

        self.curr.execute("""CREATE TABLE IF NOT EXISTS chocolate_products 
        (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            name VARCHAR(255),
            price FLOAT,
            url VARCHAR(255)
        )
        """)
    
    def process_item(self, item, spider):
        self.store_db(item)
        return item
    
    def store_db(self, item):
        self.curr.execute("""INSERT INTO chocolate_products (name, price, url) values (%s, %s, %s)""", (
            item["name"], 
            item["price"], 
            item["url"]
        ))
        self.connection.commit()


class SavingToPostgresPipeline(object):
    """
    POSTGRES DB

    Args:
        object (_type_): _description_
    """
    def __init__(self):
        self.create_connection()

    
    def create_connection(self):
        self.connection = psycopg2.connect(
            host = 'localhost',
            user = 'postgres',
            password = 'postgres',
            database = 'scrapy_db',
            port = '5432'
        )
        self.curr = self.connection.cursor()

        self.curr.execute("""CREATE TABLE IF NOT EXISTS chocolate_products 
        (
            id serial PRIMARY KEY, 
            name VARCHAR(255),
            price FLOAT,
            url VARCHAR(255)
        )
        """)
    
    def process_item(self, item, spider):
        self.store_db(item)
        return item
    
    def store_db(self, item):
        self.curr.execute("""INSERT INTO chocolate_products (name, price, url) values (%s, %s, %s)""", (
            item["name"], 
            item["price"], 
            item["url"]
        ))
        self.connection.commit()


class SavingToMongoDbPipeline(object):
    """
    MONGO DB

    Args:
        object (_type_): _description_
    """

    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['mongo_db']
    
    def process_item(self, item, spider):
        self.db['chocolate_products'].insert_one(dict(item))
        return item
    