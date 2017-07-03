from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql.base import LONGTEXT
from tornado import gen


Base = declarative_base()


class Ads(Base):
    __tablename__ = 'ads'
    url = Column(String(100), primary_key=True)
    data = Column(LONGTEXT)


class Database:
    def __init__(self, deleteTable):
        engine = create_engine("mysql://njuskalo:cola@localhost/njuskalo")
        if deleteTable:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.session_registry = scoped_session(session_factory)
        self.session = self.session_registry()

    def find_url(self, url):
        q = self.session.query(Ads).filter(Ads.url.in_([url])).first()
        print q
        return q

    def update_database(self, url, data):
        urldata = Ads(url=url, data=data)
        self.session.add(urldata)
        self.session.commit()
        print self.session.query(Ads)

    def search_database(self, url):
        return self.find_url(url)

    def commit(self):
        self.session.commit()

    def print_all(self):
        ads = self.session.query(Ads).all()
        for ad in ads:
            print ad.url

