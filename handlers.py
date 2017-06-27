'''Handlers'''
import njuskalo
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from bs4 import BeautifulSoup

class MainHandler(tornado.web.RequestHandler):
    """Returns soup object for given url"""

    def initialize(self, homeurl):
        """Initializes url argument"""
        self.homeurl = homeurl

    @gen.coroutine
    def soup_from_url(self, url):
        """Return soup from given url"""
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(url)
        raise gen.Return(BeautifulSoup(response.body, 'lxml'))

    def create_url(self, url, number):
        '''Returns page url for given url and page number'''
        string = "%20s%.2d" % (url, number+1)
        return string

    @gen.coroutine
    def find_ads(self, page_num, url):
        """Find ads from page_num pages from given url"""
        links_articles = []
        for number in xrange(page_num):
            pageurl = self.create_url(url, number)
            soup = yield self.soup_from_url(pageurl)
            links_articles.append(njuskalo.find_all_ads(soup))
        raise gen.Return(links_articles)

    @gen.coroutine
    def print_ads(self, homeurl):
        """Print ads from homeurl"""
        url = homeurl + '?page='
        soup = yield self.soup_from_url(url)
        page_num = njuskalo.find_last_page_number(soup)
        links_articles = yield self.find_ads(page_num, url)
        raise gen.Return(njuskalo.return_ads(links_articles))

    @gen.coroutine
    def get(self):
        """Main request handler"""
        ads = yield self.print_ads(self.homeurl)
        self.write(''.join(ads))

