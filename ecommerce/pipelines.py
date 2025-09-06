# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from itemadapter import ItemAdapter
from pymongo import MongoClient


class MongoPipeline:
    def __init__(self, mongo_uri: str, mongo_db: str, default_collection: str | None = None):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.default_collection = default_collection
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        mongo_uri = os.getenv("MONGO_URI", crawler.settings.get("MONGO_URI", "mongodb://localhost:27017"))
        mongo_db = os.getenv("MONGO_DB", crawler.settings.get("MONGO_DB", "ecommerce"))
        default_collection = os.getenv("MONGO_COLLECTION", crawler.settings.get("MONGO_COLLECTION"))
        return cls(mongo_uri, mongo_db, default_collection)

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def _get_collection_name(self, spider):
        # Use explicit collection if provided, else spider name
        return self.default_collection or getattr(spider, "name", "items")


class EcommercePipeline:
    def process_item(self, item, spider):
        return item


class MongoStorePipeline(MongoPipeline):
    def process_item(self, item, spider):
        # Guard: pymongo Database does not support truthiness; compare to None
        if self.db is None or self.client is None:
            return item
        collection_name = self._get_collection_name(spider)
        collection = self.db[collection_name]
        doc = ItemAdapter(item).asdict()
        try:
            collection.insert_one(doc)
        except Exception as exc:
            spider.logger.error(f"Mongo insert failed for {collection_name}: {exc}")
        return item
