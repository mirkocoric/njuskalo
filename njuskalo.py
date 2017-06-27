"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
import re
import tornado.ioloop
import tornado.web
import handlers

class Adtuple(namedtuple('adtuple', 'naslov cijena')):
    '''Stores naslov and cijena for each ad in a single element'''
    def __str__(self):
        return ''.join(['Naslov: ', self.naslov, ' ', 'Cijena: ', ' '.join
                        (self.cijena), '\r\n']).encode('utf-8')

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
    yield (atag for article in soup.find_all('article')
           for h3tag in article.find_all(name='h3')
           for atag in h3tag.find_all(name='a'))

def find_all_ads(soup):
    """Finds all articles and returns array of ad namedtuples which include title and price"""
    genatags = find_atags(soup)
    yield (Adtuple(atag.text, make_price(atag.parent.parent.find_all(class_='price')))
           for atags in genatags
           for atag in atags)

def find_paging_links(soup):
    """Finds page link number"""
    yield (int(num) for button in soup.find_all('button')
           for num in button.text.split("-")
           if 'data-page' in button.attrs
           if is_int(num))

def find_last_page_number(soup):
    """Calculates number of pages with articles"""
    numbers = find_paging_links(soup)
    return map(max, numbers)[0]

def return_ads(listgenads):
    """Returns all ads as a list of strings"""
    return (map(str,
                [ad for genads in listgenads
                 for ads in genads
                 for ad in ads]))

def parse_args():
    """Parses program arguments (url with ads)"""
    description_string = 'Finding items from njuskalo and prints title and price'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    return parser.parse_args().home

def start_ad_service():
    """Launches the Tornado service for Ads"""
    app = make_app()
    app.listen(8500)
    tornado.ioloop.IOLoop.current().start()

def make_app():
    """Creates web application"""
    return tornado.web.Application([
        (r"/", handlers.MainHandler),
    ])

if __name__ == "__main__":
    start_ad_service()
