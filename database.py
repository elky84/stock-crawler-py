""":mod:`crawler.database` ---  MongoDB Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from pymongo import MongoClient
from config import crawler_config

logger = logging.getLogger(__name__)


class MongoDB:

    def __init__(self, db: str):
        db_config = crawler_config.db_config
        client = MongoClient(host=db_config['url'],
                             serverSelectionTimeoutMS=3)
        self.collection = client[db]

    def query(self, collection: str):
        return self.collection[collection]

    def insert(self, collection: str, *, data: dict):
        return self.collection[collection].insert(data)

    def update(self, collection: str, *, document, data: dict):
        return self.collection[collection].update({'_id': document['_id']}, {'$set': data})
