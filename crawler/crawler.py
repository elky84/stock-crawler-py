""":mod:`crawler.worker.base` ---  Crawler Base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import date, timedelta, datetime, timezone

from bs4 import BeautifulSoup

from config import crawler_config
from database import MongoDB

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self):
        if crawler_config.debug:
            self.db = MongoDB('test_stock_crawler')
        else:
            self.db = MongoDB('stock_crawler')

        self.url = ""

    @property
    def type(self):
        return self.__class__.__name__

    def insert_or_update(self, data):
        log = logger.getChild( self.type + '.insert_or_update')
        log.setLevel(logging.INFO)

        log.debug('insert data: {}'.format(data))
        collection = 'stock'

        document = self.db.query(collection).find_one({'type': data['type'], 'date': data['date'], 'code': data['code']})
        if document is None:
            self.db.insert(collection, data=data)
            log.debug('insert data: {}'.format(data))
                

    def crawling(self, url, encoding='cp949'):
        log = logger.getChild(self.type + 'crawling')
        request = Request(url, headers={
            'User-Agent':
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) '
                'Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'})
        try:
            handle = urlopen(request)
        except URLError:
            log.error('may be, url host changed: {}'.format(url))
            return None
        data = handle.read()
        soup = BeautifulSoup(data.decode(encoding, 'ignore'), "html.parser", from_encoding="utf-8")

        return soup