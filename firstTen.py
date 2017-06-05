from __future__ import print_function
from bs4 import BeautifulSoup
import requests

class Element:
    def __init__(self, naslov, cijena):
        self.naslov = naslov 
        self.cijena = cijena

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False   

def find_all_elements (elements, soup):  
    for li in soup.find_all('article'):
        data = []
        #print(li.find('a').text)
        for child in li.children:
            if child.name == 'h3':
                for ch in child.children:
                    if ch.name == 'a':
                        cijena = []
                        naslov =  ch.text
                        article = ch.parent.parent 
                        #soup2 = BeautifulSoup (article, 'lxml')
                        #soup2.find_all(class = 'price')                       
                        for entityPrice in article.descendants: 
                            if entityPrice.name:
                                if 'class' in entityPrice.attrs:
                                    if entityPrice['class'][0] == 'price':
                                        cijena.append(entityPrice.text)
                        elements.append(Element(naslov, cijena))
    return elements

def findPageNumbers (home):
    page = requests.get(home) 
    soup = BeautifulSoup (page.content, 'lxml')
    buttons = soup.find_all ('button')
    numbers = [] 
    for button in buttons:
        if 'data-page' in button.attrs:
            listNum = button.text.split("-")
            for num in listNum:
                numbers.append(num) 

    pageNum = 0
    for number in numbers:
     if is_int(number):
        num = int(number)
        if num > pageNum:
            pageNum = num
    return pageNum
    
def printElements (elements):
    for element in elements:
    #print(vars(element))
        print ('Naslov: ' + element.naslov, end = ' ')
        if element.cijena:
            print('Cijena: ', end = ' ') 
            for cijena in element.cijena:
                if cijena[-1:] == '~':               
                    print (cijena[:-1], end = ' ') 
                else:   
                    print (cijena, end = ' ') 
        print()

elements = []
home = 'http://www.njuskalo.hr/iznajmljivanje-poslovnih-prostora'
url = 'http://www.njuskalo.hr/iznajmljivanje-poslovnih-prostora?page='


pageNum = findPageNumbers (home)

for i in xrange(pageNum):
    newUrl = url + str(i+1)
    page = requests.get(newUrl)   
    soup = BeautifulSoup (page.content, 'lxml')
    elements = find_all_elements(elements, soup)

printElements (elements)

