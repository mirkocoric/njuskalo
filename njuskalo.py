"""blabla"""
from __future__ import print_function
import argparse
import tornado.ioloop
import tornado.web
import handlers
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from models import Base


def parse_args():
    """Parses program arguments
    Returns home url and port
    """
    description_string = 'Finding ads and prints title and price'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    parser.add_argument('--port',
                        help='port',
                        default=8500)
    return parser.parse_args()


def create_session_factory(delete_table):
    """Creates session factory"""
    engine = create_engine("mysql://njuskalo:cola@localhost/njuskalo",
                           echo=True)
    if delete_table:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def start_ad_service(homeurl=None, port=None, delete_table=True):
    """Launches the Tornado service for Ads"""
    if not homeurl or not port:
        args = parse_args()
    homeurl = homeurl or args.home
    port = port or args.port
    session_factory = create_session_factory(delete_table)
    app = make_app(homeurl, session_factory)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


def make_app(homeurl, session_factory):
    """Creates web application"""
    return tornado.web.Application([
        (r"/", handlers.AdsHandler, dict(homeurl=homeurl,
                                         session_factory=session_factory))])

if __name__ == "__main__":
    start_ad_service()
