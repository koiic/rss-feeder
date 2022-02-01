from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser
import logging

from feed.models import Item

logger = logging.getLogger(__name__)


def scrape_feed(feed_url):
    """
    This function takes rss feed url and scrape it to return the items
    Args:
        feed_url (): the rss feed url

    Returns:
        tuple(feed, items): a tuple of feed and list of items
    """
    item_list = []
    print(feed_url, "::____::")
    try:
        # start the scraping tool

        r = requests.get(feed_url)

        soup = BeautifulSoup(r.content, features='xml')
        print(soup, "::____::")

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
        print(e, "====")
        raise Exception(str(e))


def convert_to_dict(item):
    """
    This function converts item pageElement to a dictionary of key, value
    Args:
        item (): The result of an item pageElement

    Returns:
        dict: A key, value pair of an item

    """
    new_item = dict(
        title=item.find("title").text if item.find("title") else None,
        link=item.find("link").text if item.find("link") else None,
        description=item.find("description").text if item.find("description") else None,
        author=item.find("author").text if item.find("author") else None,
        category=item.find("category").text if item.find("category") else None,
        guid=item.find("guid").text if item.find("guid") else None,
        published_at=parser.parse(item.pubDate.text) if item.find("pubDate") else None,
        comments_url=item.find("comments_url").text if item.find("comments_url") else None
    )
    return new_item


def ping_for_feed(feed):
    """
    function to check for item updates on a feed
    Args:
        feed (): A feed instance

    Returns:
        tuple(dictionary, list, bool): the feed object, the items list and the updated status

    """
    print("i entered ping for feed")
    feed_, items = scrape_feed(feed.link)
    if feed_.get('last_build_date') > feed.last_build_date:
        return feed_, items, True
    return feed_, items, False


def update_new_feed(feed_old, feed_new, items):
    """
    function to persist updated item to database
    Args:
        feed_old (): the feed instance
        feed_new (): the scrape feed object
        items (): list of scraped items
    """
    feed_old.last_build_date = feed_new.get('last_build_date')
    feed_old.save(update_fields=['last_build_date', 'updated_at'])
    for item in items:
        item_exist = Item.objects.filter(guid=item.get('guid'), published_at=item.get('published_at'),
                                         feed=feed_old).exists()
        if not item_exist:
            item['feed'] = feed_old
            Item.objects.create(**item)
