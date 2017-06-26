"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
import re
import tornado.ioloop
import tornado.web
import handlers

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
    listelements = ['Naslov: ', element.naslov, ' ', 'Cijena: ', ' '.join(element.cijena), '\r\n']
    return ''.join(listelements)

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

def parse_args():
    """Returns url from program arguments"""
    description_string = 'Finding items from njuskalo and prints title and price'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    return parser.parse_args().home

def main():
    """Main function"""
    app = make_app()
    app.listen(8500)
    tornado.ioloop.IOLoop.current().start()

def make_app():
    """Makes web application"""
    return tornado.web.Application([
        (r"/", handlers.MainHandler),
    ])

#@gen.coroutine
#def fetch_coroutine(url):
#   http_client = AsyncHTTPClient()
 #   response = yield http_client.fetch(url)
 #   raise gen.Return(response.body)

if __name__ == "__main__":
    main()
