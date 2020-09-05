""":mod:`crawler.database` ---  MongoDB Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from pymongo import MongoClient
from config import crawler_config

logger = logging.getLogger(__name__)


class MongoDB:

    def __init__(self, db: str):
        client = MongoClient('mongodb://%s:%s@%s' % (crawler_config.db_auth_user, crawler_config.db_auth_pass, crawler_config.db_config), serverSelectionTimeoutMS=3)
        self.collection = client[db]

    def query(self, collection: str):
        return self.collection[collection]

    def insert(self, collection: str, *, data: dict):
        return self.collection[collection].insert(data)

    def update(self, collection: str, *, document, data: dict):
        return self.collection[collection].update({'_id': document['_id']}, {'$set': data})
