'''Handlers'''
import fetch_ads
import tornado.web
from tornado import gen
from sqlalchemy import exc


class AdsHandler(tornado.web.RequestHandler):
    """Returns soup object for given url"""

    def initialize(self, homeurl, session_factory):
        """Initializes url and session_registry"""
        self.homeurl = homeurl
        self.session_factory = session_factory

    @staticmethod
    def commit_and_close(session):
        """Commits and closes the session"""
        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()

    @gen.coroutine
    def get(self):
        """Returns ads from url and prints them in a web browser"""
        session = self.session_factory()
        print 'session', session
        try:
            ads = yield fetch_ads.ads_from_url(session, self.homeurl)
            self.write(''.join(ads))
            self.commit_and_close(session)
        finally:
            session.close()



