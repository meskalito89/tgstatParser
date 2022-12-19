from models.channel import Channel, UnfolovedLink, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
from bs4 import BeautifulSoup as bs
from pdb import set_trace
from re import compile
from os.path import exists
from requests.exceptions import *
from time import sleep

class PermissionDeniedException(Exception):
    pass


def is_link_in_database(link: str) -> bool:
    with Session(bind=engine) as session:
        exist = bool(session.query(Channel).filter_by(url=link).first())
    return exist

def get_bsobject(link: str) -> bs:
    response = requests.get(link)
    bsobj = bs(response.text, 'html.parser')
    set_trace()
    if response.status_code == 403:
        raise PermissionDeniedException
    return bsobj

def parse_channel_data(bsobj: bs) -> dict:
    channel_data = dict()
    channel_name_xpath = '/html/body/div/div/div[1]/div[2]/div[2]/div[1]/div/div/div[2]/h1'
    channel_name = bsobj.xpath(channel_name_xpath).text
    channel_data['channel_name'] = channel_name
    channel_description_xpath = '/html/body/div/div/div[1]/div[2]/div[2]/div[1]/div/div/div[2]'
    channel_description = bsobj.xpaht(channel_description_xpath).text
    channel_data["description"] = channel_description
    channel_url_xpath = '//*[@id="post-31047155831"]/div[1]/div/div/div/div[1]/a'
    channel_url = bsobj.xpath(channel_url_xpath).attrs['href']
    channel_data['url'] = channel_url


    return channel_data

def write_channel_to_db(channel: Channel) -> None:
    with Session(engine) as session:
        session.add(channel)
        session.commit()

def parse_channel_links(bsobj: bs) -> set:
    links = bsobj.find_all('a', href=True)
    links = map(lambda el: el.attrs['href'], links)
    links = filter(lambda el: '@' in el and "channel" in el, links)
    links = map(lambda el: start_url + el if el.startswith('/channel') else el, links)
    links = map(lambda el: "/".join(el.split('/')[:5]), links)

    return set(links)


def get_unfoloved_links() -> set:
    with Session(bind=engine) as session:
        queries = session.query(UnfolovedLink).all()
        unfoloved_links = {row.url for row in queries}
        return unfoloved_links

def remove_link_from_unfoloved_links(link: str) -> None:
    with Session(engine) as session:
        session.query(Channel).filter_by(url=link).delete()
        session.commit()

if __name__ == "__main__":
    database_path = "./db.db"
    database_url = "sqlite:///db.db"
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(engine)

    if not exists(database_path):
        Base.metadata.create_all(engine)

    start_url = 'https://tgstat.ru'
    unfoloved_links = get_unfoloved_links()

    while unfoloved_links:
        link = unfoloved_links.pop()
        if is_link_in_database(link):
            continue    

        bsobj = get_bsobject(link)
        if not bsobj:
            sleep(1000)
        if channel_data := parse_channel_data(bsobj):
            remove_link_from_unfoloved_links(link)
            channel = Channel(**channel_data)
            write_channel_to_db(channel)
            print("writing channel: \n", channel)
            channel_links = parse_channel_links(bsobj)
            unfoloved_links.update(channel_links)
        
        sleep(5)

        
