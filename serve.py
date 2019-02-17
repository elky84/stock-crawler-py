""":mod:`crawler.serve` ---  Crawler thread context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import logging.config
import random
import threading

from datetime import datetime, timedelta

from queue import Queue

from config import crawler_config
from exception import SkipCrawler, TerminatedCrawler

from crawler.naver_stock import NaverStock

from pymongo.errors import ServerSelectionTimeoutError
from time import sleep

import sys
import os

logger = logging.getLogger('crawler')
logging.config.dictConfig(crawler_config.logging_formatter)


class Crawler(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.is_stop = False
        self.queue = queue

    def run(self):
        l = logger.getChild('Crawler.run')
        site = self.queue.get()
        
        while True:
            try:
                site.do()
            except ServerSelectionTimeoutError:
                self.is_stop = True
            except SkipCrawler:
                l.info('crawler skip')
            except Exception as e: 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                l.error(e)
                l.error(exc_type, fname, exc_tb.tb_lineno)

            sleep(int(crawler_config.crawler_interval['sec']))

        self.queue.task_done()

def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

def crawler(*, queue: Queue):
    l = logger.getChild('Crawler.crawler')
    l.info(crawler_config.crawling_targets)

    sites = []
    for target in crawler_config.crawling_targets:
        clazz = str_to_class(target['type'])
        sites.append(clazz(threshold=target['threshold'], page_max=target['page_max'], code=target['code']))

    thread_num = len(sites)
    for site in sites:
        queue.put(site)
    workers = []
    for i in range(thread_num):
        t = Crawler(queue)
        t.daemon = True
        workers.append(t)
        t.start()
    return workers


if __name__ == '__main__':
    l = logger.getChild('main')
    oldtime = datetime.now()
    l.info('crawler start')
    count = 0
    queue = Queue()
    while True:
        try:
            interval = crawler_config.crawler_interval
            seed = timedelta(minutes=random.randint(
                int(interval['minutes_min']), int(interval['minutes_max'])),
                seconds=int(interval['sec']))
            if datetime.now() >= (oldtime + seed):
                oldtime = datetime.now()
                workers = crawler(queue=queue)
                queue.join()
                for w in workers:
                    if w.is_stop:
                        raise TerminatedCrawler
                count += 1
                l.info("finish crawler: {}".format(count))
        except (KeyboardInterrupt, TerminatedCrawler):
            l.info('terminated crawler')
            exit()
