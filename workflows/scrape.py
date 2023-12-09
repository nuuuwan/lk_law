import os

from utils import Log

from lk_law import Scraper

log = Log('scrape')

IS_TEST_MODE = os.name == 'nt'
log.debug(f'{IS_TEST_MODE=}')

SCRAPE_TIME_S = 1 if IS_TEST_MODE else 60 * 45
log.debug(f'{SCRAPE_TIME_S=}')


def main():
    Scraper.multi_scrape(SCRAPE_TIME_S)


if __name__ == '__main__':
    main()
