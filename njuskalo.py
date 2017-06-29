"""blabla"""
from __future__ import print_function
import argparse
import handlers
import tornado.ioloop
import tornado.web


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


def start_ad_service(homeurl=None, port=None):
    """Launches the Tornado service for Ads"""
    if not homeurl or not port:
        args = parse_args()
    homeurl = homeurl or args.home
    port = port or args.port
    app = make_app(homeurl)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


def make_app(homeurl):
    """Creates web application"""
    return tornado.web.Application([
        (r"/", handlers.AdsHandler, dict(homeurl=homeurl))
    ])

if __name__ == "__main__":
    start_ad_service()
