'''Handlers'''
import njuskalo
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from bs4 import BeautifulSoup

class MainHandler(tornado.web.RequestHandler):
    """Returns soup object for given url"""
    @gen.coroutine
    def soup_from_url(self, url):
        """Return soup from given url"""
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(url)
        raise gen.Return(BeautifulSoup(response.body, 'lxml'))

    @gen.coroutine
    def find_ads(self, page_num, url):
        """Find ads from page_num pages from given url"""
        links_articles = []
        for i in xrange(page_num):
            pageurl = url + str(i+1)
            soup = yield self.soup_from_url(pageurl)
            links_articles.append(njuskalo.find_all_elements(soup))
        raise gen.Return(links_articles)

    @gen.coroutine
    def print_ads(self, homeurl):
        """Print ads from homeurl"""
        url = homeurl + '?page='
        soup = yield self.soup_from_url(url)
        page_num = njuskalo.find_last_page_number(soup)
        links_articles = yield self.find_ads(page_num, url)
        raise gen.Return(njuskalo.return_elements(links_articles))

    @gen.coroutine
    def get(self):
        """Main request handler"""
        homeurl = njuskalo.parse_args()
        ads = yield self.print_ads(homeurl)
        self.write(''.join(ads).encode('utf-8'))
        