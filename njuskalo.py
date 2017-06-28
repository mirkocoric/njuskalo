"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
import re
import handlers
import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from bs4 import BeautifulSoup


class AdTuple(namedtuple('adtuple', 'naslov cijena')):
    '''Stores naslov and cijena for each ad in a single element'''
    def __str__(self):
        return ''.join(['Naslov: ', self.naslov, ' ',
                        'Cijena: ', ' '.join(self.cijena),
                        '\r\n']).encode('utf-8', errors='ignore')


def is_int(name):
    """Returns True if it is possible to convert string to integer"""
    try:
        int(name)
        return True
    except ValueError:
        return False


def make_price(pricetag_list):
    """Returns list of prices"""
    return [re.sub(r'~', '', pricetag.text) for pricetag in pricetag_list]


def find_atags(soup):
    """Finds all a tags in soup"""
    return (atag for article in soup.find_all('article')
            for h3tag in article.find_all(name='h3')
            for atag in h3tag.find_all(name='a'))


def find_all_ads(soup):
    """Finds all articles and returns array of AdTuples"""
    atags = find_atags(soup)
    return (AdTuple(atag.text, make_price(atag.parent.parent.find_all
                                          (class_='price')))
            for atag in atags)


def find_paging_links(soup):
    """Finds page link number"""
    return (int(num) for button in soup.find_all('button')
            for num in button.text.split("-")
            if 'data-page' in button.attrs
            if is_int(num))


def find_last_page_number(soup):
    """Calculates number of pages with articles"""
    numbers = find_paging_links(soup)
    return max(numbers)


def ads_to_strings(ads):
    """Returns all ads as a list of strings"""
    return map(str, ads)


def parse_args():
    """Parses program arguments
    Returns home url and port"""
    description_string = 'Finding ads and prints title and price'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    parser.add_argument('--port',
                        help='port',
                        default=8500)
    return parser.parse_args()


def create_url(url, number):
    '''Returns page url for given url and page number'''
    string = "%20s?page=%.2f" % (url, number+1)
    return string


@gen.coroutine
def find_ads(page_num, url):
    '''Find ads from page_num pages from given url
    Returns a list of pages where each page is a list of AdTuple objects'''
    links_articles = []
    for number in xrange(page_num):
        pageurl = create_url(url, number)
        soup = yield soup_from_url(pageurl)
        ads = find_all_ads(soup)
        links_articles += ads
    raise gen.Return(links_articles)


@gen.coroutine
def return_ads_from_url(homeurl):
    """Print ads from homeurl"""
    soup = yield soup_from_url(homeurl)
    page_num = find_last_page_number(soup)
    links_articles = yield find_ads(page_num, homeurl)
    raise gen.Return(ads_to_strings(links_articles))


@gen.coroutine
def soup_from_url(url):
    """Return soup from given url"""
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    raise gen.Return(BeautifulSoup(response.body, 'lxml'))


def start_ad_service(homeurl=None, port=None):
    """Launches the Tornado service for Ads"""
    if not homeurl or not port:
        args = parse_args()
        if not homeurl:
            homeurl = args.home
        if not port:
            port = args.port
    app = make_app(homeurl)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


def make_app(homeurl):
    """Creates web application"""
    return tornado.web.Application([
        (r"/", handlers.AdsHandler, dict(homeurl=homeurl))
    ])

if __name__ == "__main__":
    start_ad_service()
