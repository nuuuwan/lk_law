import json
import random
import time
from functools import cached_property

import requests
from bs4 import BeautifulSoup
from utils import Log, Time, TimeFormat, TimeUnit

from lk_law.Document import Document
from lk_law.PubType import PubType

POST_REQUEST_TIMEOUT = 10  # seconds
URL_BASE = 'http://documents.gov.lk'

log = Log('Scraper')


class Scraper:
    TIME_FORMAT = TimeFormat('%Y-%m-%d')

    def __init__(self, pub_type: PubType, date: str):
        self.pub_type = pub_type
        self.date = date  # e.g. 2023-11-24

    @cached_property
    def url(self) -> str:
        return f'{URL_BASE}/pub.alink.php'

    @cached_property
    def post_data(self) -> dict[str, str]:
        # pubType=a&reqType=D&reqStr=2023-11-23&lang=E
        return dict(
            pubType=self.pub_type.id, reqType='D', reqStr=self.date, lang='E'
        )

    @cached_property
    def content(self):
        # log.debug(f'POST {self.url} - {self.post_data}')
        return requests.post(
            self.url, data=self.post_data, timeout=POST_REQUEST_TIMEOUT
        ).content

    @cached_property
    def doc_list(self) -> list:
        if self.pub_type.isHTML:
            doc_list = self.doc_list_from_html
        elif self.pub_type.isJSON:
            doc_list = self.doc_list_from_json
        else:
            raise ValueError(f'Unknown pub_type: {self.pub_type.id}')

        for doc in doc_list:
            doc.write_data()

        if len(doc_list) > 0:
            logger = log.info
            emoji = '✅'
        else:
            logger = log.warning
            emoji = '🤷🏽'

        logger(
            f'{emoji}Found {len(doc_list)} documents'
            + f' for {self.pub_type.id}/{self.date}'
        )

    @cached_property
    def doc_list_from_json(self) -> list:
        data_json = json.loads(self.content)
        data_list = data_json['data']
        doc_list = []
        for data in data_list:
            name = data['egz_desc']
            date = data['egz_day']
            url = f'{URL_BASE}/{data["egz_path"]}/{data["egz_file_e"]}'

            doc = Document(self.pub_type, date, name, url)

            doc_list.append(doc)

        return doc_list

    @cached_property
    def doc_list_from_html(self) -> list:
        html = self.content

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')

        trs = table.find_all('tr')
        doc_list = []
        for tr in trs[1:]:
            td_list = tr.find_all('td')
            date = td_list[-3].text
            name = td_list[-2].text
            a = td_list[-1].find('a')
            url = a['href'].replace('..', URL_BASE)

            doc = Document(self.pub_type, date, name, url)

            doc_list.append(doc)

        return doc_list

    @staticmethod
    def multi_scrape_for_date(date: str):
        for pub_type in PubType.list_all():
            scraper = Scraper(pub_type, date)

            try:
                scraper.doc_list
            except Exception as e:
                log.error(f'Failed to scrape {date}/{pub_type.id}: {e}')

            t_sleep = random.random()
            log.debug(f'😴Sleeping for {t_sleep:.1f}s')
            time.sleep(t_sleep)

    @staticmethod
    def multi_scrape(t_end: float, n_i_days: int):
        for i_day in range(0, n_i_days):
            t = t_end - i_day * TimeUnit.SECONDS_IN.DAY
            date = Scraper.TIME_FORMAT.stringify(Time(t))

            Scraper.multi_scrape_for_date(date)

    @staticmethod
    def get_t_start() -> float:
        doc_list = Document.list_all()
        if len(doc_list) == 0:
            return Time.now().ut

        date_list = sorted([doc.date for doc in doc_list])
        date_start = date_list[0]
        return TimeFormat.DATE.parse(date_start).ut
