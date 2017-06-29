'''Handlers'''
import fetch_ads
import tornado.web
from tornado import gen


class AdsHandler(tornado.web.RequestHandler):
    """Returns soup object for given url"""

    def initialize(self, homeurl):
        """Initializes url argument"""
        self.homeurl = homeurl

    @gen.coroutine
    def get(self):
        """Returns ads from url and prints them in a web browser"""
        ads = yield fetch_ads.ads_from_url(self.homeurl)
        self.write(''.join(ads))
