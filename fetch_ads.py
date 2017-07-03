"""blabla"""
from __future__ import print_function
from collections import namedtuple
import re
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
    return [re.sub(r'~', '', pricetag.text)
            for pricetag in pricetag_list]


def find_atags(soup):
    """Finds all a tags in soup"""
    return (atag for article in soup.find_all('article')
            for h3tag in article.find_all(name='h3')
            for atag in h3tag.find_all(name='a'))


def find_all_ads(soup):
    """Finds all articles and returns sequence of AdTuples"""
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


def create_url(url, number):
    '''Returns page url for given url and page number'''
    string = "%s?page=%d" % (url, number + 1)
    return string


@gen.coroutine
def find_ads(page_num, url, database):
    '''Find ads from page_num pages from given url
    Returns a list of pages where each page is a list of AdTuple objects'''
    links_articles = []
    adstrings = ''
    for number in xrange(page_num):
        homeurl = create_url(url, number)
        ads = database.search_database(homeurl)
        if ads:
            print ("Fetched from database")
            adstring = ads
        else:
            print ("Connecting to njuskalo")
            soup = yield soup_from_url(create_url(url, number))
            ads = find_all_ads(soup)
            links_articles += ads
            adstring = ads_to_strings(links_articles)
            database.update_database(homeurl, adstring)
            print ("Database updated")
        adstrings.join(adstring)
    raise gen.Return(adstrings)


@gen.coroutine
def ads_from_url(homeurl, database):
    """Returns ads from homeurl"""
    soup = yield soup_from_url(homeurl)
    raise(gen.Return(find_ads(find_last_page_number(soup),
                              homeurl, database)))


@gen.coroutine
def soup_from_url(url):
    """Return soup from given url"""
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    raise gen.Return(BeautifulSoup(response.body, 'lxml'))
