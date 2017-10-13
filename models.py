from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql.base import LONGTEXT


Base = declarative_base()


class Ads(Base):
    """Defines table ads and its columns"""
    __tablename__ = 'ads'
    url = Column(String(100), index=True)
    data = Column(LONGTEXT)
    id = Column(Integer, primary_key=True)
