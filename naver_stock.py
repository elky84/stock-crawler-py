import logging

from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import date, timedelta, datetime, timezone
from bs4 import BeautifulSoup

logger = logging.getLogger("crawler")

class SkipCrawler(ValueError):
    pass

class NaverStock():

    def __init__(self, *, code=251270, threshold=15, page_max=20):
        self.threshold = threshold
        self.pageMax = page_max
        self.code = code


    def crawling(self, url, encoding='cp949'):
        log = logger.getChild('BaseSite.crawling')
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
                    }
                log.info(obj)
