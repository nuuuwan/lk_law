import os

from utils import Log

from lk_law import Scraper

log = Log('scrape')

IS_TEST_MODE = os.name != 'posix'
log.debug(f'{IS_TEST_MODE=}')


def main():
    ut = Scraper.get_t_start()
    n_i_days = 7
    Scraper.multi_scrape(ut, n_i_days)


if __name__ == '__main__':
    main()
