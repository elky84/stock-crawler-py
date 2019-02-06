import logging
import logging.config

from datetime import datetime, timedelta
from naver_stock import NaverStock
from config import config

logger = logging.getLogger('crawler')
logging.config.dictConfig(config.logging_formatter)

if __name__ == '__main__':
    log = logger.getChild('main')
    oldtime = datetime.now()
    log.info('crawler start')
    crawler = NaverStock(code=251270, threshold=0, page_max=10)
    crawler.do()
