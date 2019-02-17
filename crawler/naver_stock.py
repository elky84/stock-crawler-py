import logging

from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import date, timedelta, datetime, timezone
from bs4 import BeautifulSoup
from .crawler import Crawler

from exception import SkipCrawler

logger = logging.getLogger("crawler")

class NaverStock(Crawler):

    def __init__(self, *, code=251270, page_max=20):
        Crawler.__init__(self)
        self.pageMax = page_max
        self.code = code

    def crawler(self):
        log = logger.getChild('NaverStock.crawler')
        for page in range(1, self.pageMax, 1):
            host = 'http://finance.naver.com/item/sise_day.nhn'
            query = 'code={}&page={}'.format(self.code, page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('crawler skip')
                raise SkipCrawler

            yield soup

    def do(self):
        log = logger.getChild('NaverStock.do')
        for soup in self.crawler():
            for ctx in soup.select('table tr'):
                if len(ctx.attrs) == 0:
                    continue

                td = ctx.findAll('td')
                obj = {'date': td[0].text,
                    'lastest': td[1].text,
                    'diff': td[2].text.replace("\n", "").replace("\t", ""),
                    'current': td[3].text,
                    'high': td[4].text,
                    'low': td[5].text,
                    'trade_count': td[6].text,
                    'type': self.type,
                    'code': self.code
                    }
                log.info(obj)
                self.insert_or_update(obj)