"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
import re
import requests
from bs4 import BeautifulSoup
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.concurrent import Future
from tornado import gen


Element = namedtuple('Element', 'naslov cijena')

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

def find_all_elements(soup):
    """Finds all articles and returns array of Element namedtuples which include title and price"""
    genatags = find_atags(soup)
    yield (Element(atag.text, make_price(atag.parent.parent.find_all(class_='price')))
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

def print_element(element):
    """Prints each element"""
    print('Naslov: ' +element.naslov, end=' ')
    if element.cijena:
        print('Cijena: ', end=' ')
    for cijena in element.cijena:
        print(cijena, end=' ')
    print()

def return_string_from_element(element):
    """Returns string for each element to print on web application"""
    elem = ''
    elem = elem + 'Naslov: ' +element.naslov+ ' '
    if element.cijena:
        elem = elem + 'Cijena: '
    for cijena in element.cijena:
        elem = elem + cijena + ' '
    elem = elem + "\r\n"
    return elem

def return_elements(listgenelements):
    """Returns all elements as a list of strings"""
    return (map(return_string_from_element,
                [element for genelements in listgenelements
                 for elements in genelements
                 for element in elements]))

def print_elements(listgenelements):
    """Prints all elements"""
    map(print_element,
        [element for genelements in listgenelements
         for elements in genelements
         for element in elements])

def soup_from_url(home):
    """Returns soup object for given url"""
    response = requests.get(home)
    return BeautifulSoup(response.content, 'lxml')

def parse_args():
    """Returns url from program arguments"""
    description_string = 'Finding items from njuskalo and prints title and price'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    return parser.parse_args().home

def print_ads(homeurl):
    """Print ads from homeurl"""
    links_articles = []
    url = homeurl + '?page='
    soup = soup_from_url(url)
    page_num = find_last_page_number(soup)

    for i in xrange(page_num):
        pageurl = url + str(i+1)
        soup = soup_from_url(pageurl)
        links_articles.append(find_all_elements(soup))
    
    return return_elements(links_articles)
    #print_elements(links_articles)

def main():
    """Main function"""
    homeurl = parse_args()
    return print_ads(homeurl)

    
class MainHandler(tornado.web.RequestHandler):
    """Main request handler"""
    def get(self):
        ads = main()
        print(ads)
        map(self.write, (element.encode('utf-8') for element in ads))

def make_app():
    """Makes web application"""
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

#@gen.coroutine
#def fetch_coroutine(url):
 #   http_client = AsyncHTTPClient()
 #   response = yield http_client.fetch(url)
  #  raise gen.Return(response.body)

if __name__ == "__main__":
    app = make_app()
    app.listen(8500)
    tornado.ioloop.IOLoop.current().start()
