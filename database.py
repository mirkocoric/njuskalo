'''Module with functions for database modification'''
from tornado import gen
from njuskalo import Ads


@gen.coroutine
def update(url, data, session):
    '''Updates database with new url and corresponding data'''
    session.add(Ads(url=url, data=data))


@gen.coroutine
def search(url, session):
    '''Searches if url exists in database'''
    raise gen.Return(session.query(Ads).filter(Ads.url.in_([url])).first())
