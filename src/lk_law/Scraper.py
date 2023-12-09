import random
import time
from functools import cached_property

import requests
from bs4 import BeautifulSoup
from utils import SECONDS_IN, Log, Time, TimeFormat

from lk_law.Document import Document

POST_REQUEST_TIMEOUT = 10  # seconds
URL_BASE = 'http://documents.gov.lk'
PUB_TYPE_LIST = ['a', 'egz']

log = Log('Scraper')


class Scraper:
    TIME_FORMAT = TimeFormat('%Y-%m-%d')

    def __init__(self, pub_type: str, date: str):
        assert pub_type in PUB_TYPE_LIST
        self.pub_type = pub_type
        self.date = date  # e.g. 2023-11-24

    @cached_property
    def url(self) -> str:
        return f'{URL_BASE}/pub.alink.php'

    @cached_property
    def post_data(self) -> dict[str, str]:
        # pubType=a&reqType=D&reqStr=2023-11-23&lang=E
        return dict(
            pubType=self.pub_type, reqType='D', reqStr=self.date, lang='E'
        )

    @cached_property
    def content(self):
        return requests.post(
            self.url, data=self.post_data, timeout=POST_REQUEST_TIMEOUT
        ).content

    @cached_property
    def doc_list(self) -> list:
        html = self.content
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        doc_list = []

        for tr in table.find_all('tr')[1:]:
            td_list = tr.find_all('td')
            date = td_list[1].text
            name = td_list[2].text
            a = td_list[3].find('a')
            url = a['href'].replace('..', URL_BASE)

            doc = Document(self.pub_type, date, name, url)
            doc.write()
            doc_list.append(doc)

        if len(doc_list) > 0:
            logger = log.info
            emoji = '✅'
        else:
            logger = log.warning
            emoji = '🤷🏽'

        logger(f'{emoji}Found {len(doc_list)} documents for {self.date}')
        return doc_list

    @staticmethod
    def multi_scrape_for_date(date: str):
        for pub_type in PUB_TYPE_LIST:
            scraper = Scraper(pub_type, date)

            try:
                scraper.doc_list
            except Exception as e:
                log.error(f'Failed to scrape {date}/{pub_type}: {e}')

    @staticmethod
    def multi_scrape(scrape_time_s: int):
        t_start = time.time()
        i_day = 0
        while True:
            t = t_start - i_day * SECONDS_IN.DAY
            date = Scraper.TIME_FORMAT.stringify(Time(t))

            Scraper.multi_scrape_for_date(date)

            delta_t = time.time() - t_start
            log.debug(f'{delta_t=:.2f}s')
            if delta_t > scrape_time_s:
                break

            i_day += 1
            t_sleep = random.random()
            log.debug(f'😴Sleeping for {t_sleep:.1f}s')
            time.sleep(t_sleep)
