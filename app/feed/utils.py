from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser

def scrape_feed_info(feed_url):
    # get information about a feed
    try:
        # start the scraping tool
        r = requests.get(feed_url)
        soup = BeautifulSoup(r.content, features='xml')
        # get feed information
        feed = {
            "title": soup.title.text,
            "description": soup.description.text,
            "link": soup.link.text,
            "ttl": soup.ttl.text,
            "last_build_date": parser.parse(soup.lastBuildDate.text)
        }
        return feed
    except Exception as e:
        print(e)


def scrape_feed_items(feed_url):
    item_list = []
    try:
        # start the scraping tool
        r = requests.get(feed_url)
        soup = BeautifulSoup(r.content, features='xml')
        # get items in feed
        items = soup.findAll("item")

        # for each item in items parse it into a list of dictionaries
        for item in items:
            new_item = dict(
                title=item.find("title").text,
                link=item.find("link").text,
                description=item.find("description").text,
                author=item.find("author").text,
                category=item.find("category").text,
                guid=item.find("guid").text,
                published_at=parser.parse(item.find("pub_date").text),
                comments_url=item.find("comments_url").text
            )
            item_list.append(new_item)
        return item_list
    except Exception as e:
        print(e)


def scrape_feed(feed_url):
    item_list = []
    try:
        # start the scraping tool
        r = requests.get(feed_url)
        soup = BeautifulSoup(r.content, features='xml')

        print(parser.parse(soup.lastBuildDate.text), "====<><>")

        # get feed information
        feed = {
            "title": soup.title.text,
            "description": soup.description.text,
            "ttl": soup.ttl.text if soup.find("ttl") else None,
            "last_build_date": parser.parse(soup.lastBuildDate.text)
        }
        # get items in feed
        items = soup.findAll("item")

        # for each item in items parse it into a list of dictionaries
        for item in items:
            item_list.append(convert_to_dict(item))
        return feed, item_list
    except Exception as e:
        print(e)


def convert_to_dict(item):
    new_item = dict(
                title=item.find("title").text if item.find("title") else None,
                link=item.find("link").text if item.find("link") else None,
                description=item.find("description").text if item.find("description") else None,
                author=item.find("author").text if item.find("author") else None,
                category=item.find("category").text if item.find("category") else None,
                guid=item.find("guid").text if item.find("guid") else None,
                published_at=parser.parse(item.pubDate.text)if item.find("pubDate") else None,
                comments_url=item.find("comments_url").text if item.find("comments_url") else None
            )
    return new_item


def ping_for_feed(feed):
    feed_, items = scrape_feed(feed.link)
    if feed_.get('last_build_date') > feed.last_build_date:
        return feed_, items, True
    return feed_, items, False
