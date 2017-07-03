'''Handlers'''
import fetch_ads
import database
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
        db = database.Database(False)
        ads = yield fetch_ads.ads_from_url(self.homeurl, db)
        self.write(''.join(ads))
        db.commit()
        db.print_all()
