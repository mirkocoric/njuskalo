"""blabla"""
from __future__ import print_function
import argparse
import logging
import handlers
import tornado.ioloop
import tornado.web
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql.base import LONGTEXT

Base = declarative_base()


class Ads(Base):
    __tablename__ = 'ads'
    url = Column(String(100), primary_key=True)
    data = Column(LONGTEXT)


def parse_args():
    """Parses program arguments
    Returns home url and port"""
    description_string = 'Finding ads and prints title and price'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('home',
                        help='home url')
    parser.add_argument('--port',
                        help='port',
                        default=8500)
    return parser.parse_args()


def create_session_registry(delete_table):
    engine = create_engine("mysql://njuskalo:cola@localhost/njuskalo",
                           echo=True)
    if delete_table:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


def start_ad_service(homeurl=None, port=None, delete_table=True):
    """Launches the Tornado service for Ads"""
    if not homeurl or not port:
        args = parse_args()
    homeurl = homeurl or args.home
    port = port or args.port
    session_registry = create_session_registry(delete_table)
    app = make_app(homeurl, session_registry)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


def make_app(homeurl, session_registry):
    """Creates web application"""
    return tornado.web.Application([
        (r"/", handlers.AdsHandler, dict(homeurl=homeurl,
         session_registry=session_registry))])

if __name__ == "__main__":
    start_ad_service()
