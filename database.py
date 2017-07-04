'''Module with functions for database modification'''
from njuskalo import Ads


def update(session, url, data):
    '''Updates database with new url and corresponding data'''
    session.add(Ads(url=url, data=data))


def search(session, url):
    '''Searches if url exists in database'''
    return session.query(Ads).filter_by(url=url).first()
