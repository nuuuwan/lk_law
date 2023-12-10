import os

from utils import Log, Time

from lk_law import Scraper

log = Log('scrape')

IS_TEST_MODE = os.name != 'posix'
log.debug(f'{IS_TEST_MODE=}')


def main():
    ut = Time.now().ut
    n_i_days = 7
    Scraper.multi_scrape(ut, n_i_days)


if __name__ == '__main__':
    main()
