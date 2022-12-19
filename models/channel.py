from sqlalchemy import Column, Integer, Text, VARCHAR
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Channel(Base):
    __tablename__ = 'channel'
    id = Column('id', Integer, primary_key=True, autoincrement=True, nullable=False)
    channel_name = Column("channel_name", VARCHAR(30))
    description = Column("description", Text)
    url = Column("url", Text)


class UnfolovedLink(Base):
    __tablename__ = "unfoloved_link"
    id = Column('id', Integer, primary_key=True, autoincrement=True, nullable=False)
    url = Column("url", Text)
