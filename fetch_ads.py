"""blabla"""
from __future__ import print_function
from collections import namedtuple
import re
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from bs4 import BeautifulSoup
import database


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
    return [re.sub(r'~', '', pricetag.text)
            for pricetag in pricetag_list]


def find_atags(soup):
    """Finds all a tags in soup"""
    return (atag for article in soup.find_all('article')
            for h3tag in article.find_all(name='h3')
            for atag in h3tag.find_all(name='a'))


@gen.coroutine
def find_all_ads(soup):
    """Finds all articles and returns sequence of AdTuples"""
    atags = find_atags(soup)
    raise gen.Return((AdTuple(atag.text, make_price
                     (atag.parent.parent.find_all(class_='price')))
                     for atag in atags))


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


def ads_to_string(ads):
    """Returns all ads as a string"""
    strings = map(str, ads)
    return ''.join(strings)


def create_url(url, number):
    '''Returns page url for given url and page number'''
    string = "%s?page=%d" % (url, number + 1)
    return string

@gen.coroutine
def fetch_from_url_and_store(url, session):
    '''Fetches url from url and stores data into database
    Returns data'''
    soup = yield soup_from_url(url)
    ads = yield find_all_ads(soup)
    data = ads_to_string(ads)
    database.update(url, data, session)
    raise gen.Return(data)


@gen.coroutine
def find_ads(page_num, homeurl, session):
    '''Find ads from page_num pages from given url
    First checks if url exists in database ads
    Returns a list of pages where each page is a list of AdTuple objects'''
    links_articles = []
    for number in xrange(page_num):
        url = create_url(homeurl, number)
        ads = yield database.search(url, session)
        if ads:
            links_articles += ads.data
        else:
            links_articles += yield fetch_from_url_and_store(url, session)
    raise gen.Return(links_articles)


@gen.coroutine
def ads_from_url(homeurl, session):
    """Returns ads from homeurl"""
    soup = yield soup_from_url(homeurl)
    ads = yield find_ads(find_last_page_number(soup),
                         homeurl, session)
    raise gen.Return(ads)


@gen.coroutine
def soup_from_url(url):
    """Return soup from given url"""
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    raise gen.Return(BeautifulSoup(response.body, 'lxml'))
