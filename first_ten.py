"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
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

def find_all_elements(elements, soup):
    """Finds all articles and returns array of Element namedtuples which include title and price"""
    for link in soup.find_all('article'):
        #print(li.find('a').text)
        for child in link.children:
            if child.name != 'h3':
                continue
            for character in child.children:  # nopylint
                if character.name != 'a':
                    continue
                cijena = []
                naslov = character.text
                article = character.parent.parent
                #soup2 = BeautifulSoup (article, 'lxml')
                #soup2.find_all(class = 'price')
                for entity_price in article.descendants:
                    if entity_price.name and \
                    'class' in entity_price.attrs and \
                    entity_price['class'][0] == 'price':
                        cijena.append(entity_price.text)
                elements.append(Element(naslov, cijena))
    return elements

def find_page_numbers(home):
    """Calculates number of pages with articles"""
    page = requests.get(home)
    soup = BeautifulSoup(page.content, 'lxml')
    buttons = soup.find_all('button')
    numbers = []
    for button in buttons:
        if 'data-page' in button.attrs:
            list_num = button.text.split("-")
            for num in list_num:
                numbers.append(num)

    page_num = 0
    for number in numbers:
        if is_int(number):
            num = int(number)
            if num > page_num:
                page_num = num
    return page_num

def print_elements(elements):
    """Prints all elements"""
    for element in elements:
    #print(vars(element))
        print('Naslov: ' +element.naslov, end=' ')
        if element.cijena:
            print('Cijena: ', end=' ')
            for cijena in element.cijena:
                if cijena[-1:] == '~':
                    print(cijena[:-1], end=' ')
                else:
                    print(cijena, end=' ')
        print()

def main():
    """Main function"""
    description_string = 'Finding items from njuskalo and prints title and price'
    links_articles = []
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    args = parser.parse_args()
    home = args.home
    #home = 'http://www.njuskalo.hr/iznajmljivanje-poslovnih-prostora'
    #url = 'http://www.njuskalo.hr/iznajmljivanje-poslovnih-prostora?page='
    url = home + '?page='

    page_num = find_page_numbers(home)

    for i in xrange(page_num):
        new_url = url + str(i+1)
        page = requests.get(new_url)
        soup = BeautifulSoup(page.content, 'lxml')
        links_articles = find_all_elements(links_articles, soup)

    print_elements(links_articles)

if __name__ == "__main__":
    main()
