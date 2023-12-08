from utils import Log

from lk_law import Scraper

log = Log('scrape')
SCRAPE_TIME_S = 50 * 60
log.debug(f'{SCRAPE_TIME_S=}')


def main():
    Scraper.multi_scrape(SCRAPE_TIME_S)


if __name__ == '__main__':
    main()
