"""blabla"""
from __future__ import print_function
import argparse
from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import itertools as it

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
    tags = [child for link in soup.find_all('article')
            for child in link.children
            if child.name == 'h3']
    link = [child for tag in tags for child in tag.children]# if child is not None if child.name == 'a']
    print([l.name for l in link])
    #tag = [j for link in soup.find_all('article')
     #      for child in link.children for i in child for j in i if child.name == 'h3']
    #char1 = it.chain(char1)
    #print(type(char1.children))
    #tag = [i.children for i in char1]
    
    entity_price = [i.parent.parent for i in link]
    entity_price = [child for i in entity_price for child in i.descendants]
#Z#NASAO GRESKU< BILA JE LISTA VISIH DSIMENZIJA - ISPRAVITI
    #character = [child.children for link in soup.find_all('article')
    #             for child in link.children if child.name == 'h3']
    #print(entity_price)
    #print(character)
    naslov = [i.text for i in link]
    #entity_price = [i.parent.parent.descendents for i in character if character.name == 'a']
    cijena = [price.text for price in entity_price if (price.name
                                                       and 'class' in price.attrs
                                                       and price['class'][0] == 'price')]
    for n, c in zip(naslov, cijena):
        elements.append(Element(n, c))
        #print(naslov)
    #print(cijena)
    #print(zip(n, c) for n in naslov for c in cijena)
    #gen = [zip(n, c) for n in naslov for c in cijena]
    #for i in gen:
    #    print(i)
    #print(map(Element, (zip(n, c) for n in naslov for c in cijena)))
    #elements.append(Element(naslov, cijena))
    return elements

    #for link in soup.find_all('article'):
        #print(li.find('a').text)
     #   for child in link.children:
     #       if child.name != 'h3':
    #            continue
     #       for character in child.children:
    #            if character.name != 'a':
    #                continue
    #            cijena = []
    #            naslov = character.text
    #            article = character.parent.parent
                #soup2 = BeautifulSoup (article, 'lxml')
                #soup2.find_all(class = 'price')
    #            for entity_price in article.descendants:
    #                if (entity_price.name
    #                        and 'class' in entity_price.attrs
    #                        and entity_price['class'][0] == 'price'):
    #                    cijena.append(entity_price.text)
    #            elements.append(Element(naslov, cijena))
    #return elements

# krivo imenovanje:
# kazes, nadji brojeve stranica
# a zapravo trazis posljednju stranicu
# sugestija: find_last_page_number
# ODG funkcija vraca sve stranice...
def find_paging_links(soup):
    """Finds page link number"""
    yield [int(num) for button in soup.find_all('button')
           for num in button.text.split("-")
           if 'data-page' in button.attrs
           if is_int(num)]

def find_last_page_number(soup):
    """Calculates number of pages with articles"""
    numbers = find_paging_links(soup)
    return map(max, numbers)[0]
    # napravi ovo kao generator stranica brojeva koristeci yield
    # ideja:
    # funkcija: find_paging_links(soup) ->
    #                  -> 1-5, 5-9, ... 11, ...
    #
    # ako kopas kroz neku stablastu strukturu, a nije ti bitna
    # samo struktura stabla, onda je ideja da napravis funkciju koja ti
    # pretvara stablastu strukturu u "ravnu" strukturu, tj. listu
    # ili nesto sto je tzv. lazy varijanta liste, tj. iterable, tj. generator
    #
    # koncept iza generatora je da umjesto da se izracunaju svi elementi odmah
    # se po potrebi generira sljedeci element
    # ovo se radi preko "korutina" (coroutines), jos jednog naprednog koncepta
    # iz programiranja

def print_elements(elements):
    """Prints all elements"""
   # el = (naslov, cijena for element in elements in zip(element.naslov, element.cijena))
    for element in elements:
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
    page = requests.get(home)
    soup = BeautifulSoup(page.content, 'lxml')

    page_num = find_last_page_number(soup)
    for i in xrange(page_num):
        new_url = url + str(i+1)
        page = requests.get(new_url)
        soup = BeautifulSoup(page.content, 'lxml')
        links_articles = find_all_elements(links_articles, soup)

    print_elements(links_articles)

if __name__ == "__main__":
    main()
