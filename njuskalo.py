"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
import re
import requests
from bs4 import BeautifulSoup


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

def print_elements(listgenelements):
    """Prints all elements"""
    map(print_element,
        [element for genelements in listgenelements
         for elements in genelements
         for element in elements])

def soup_from_url(home):
    """Returns soup objectg for given url"""
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

    print_elements(links_articles)

def main():
    """Main function"""
    homeurl = parse_args()
    print_ads(homeurl)

if __name__ == "__main__":
    main()
