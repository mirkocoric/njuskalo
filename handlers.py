'''Handlers'''
import fetch_ads
import database
import tornado.web
from tornado import gen
from sqlalchemy import exc


class AdsHandler(tornado.web.RequestHandler):
    """Returns soup object for given url"""

    def initialize(self, homeurl, session_registry):
        """Initializes url and session_registry"""
        self.homeurl = homeurl
        self.session_registry = session_registry

    @staticmethod
    """Commits and closes the session"""
    def commit_and_close(session):
        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
        finally:
            session.close()

    @gen.coroutine
    def get(self):
        """Returns ads from url and prints them in a web browser"""
        session = self.session_registry()
        ads = yield fetch_ads.ads_from_url(session, self.homeurl)
        self.write(''.join(ads))
        self.commit_and_close(session)



