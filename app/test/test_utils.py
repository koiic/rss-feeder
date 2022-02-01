import io
from datetime import datetime, date
import datetime
import pytest
import pytz
from django.urls import reverse
from lxml import etree

pytestmark = pytest.mark.django_db

from feed.utils import scrape_feed, convert_to_dict, ping_for_feed, update_new_feed


def test_scrape_feed_raise_exception():
    with pytest.raises(Exception) as e_info:
        scrape_feed("hhh")


def test_scrape_feed(scrape_feed_items):
    assert scrape_feed_items[0].get('title') == 'NU - Algemeen'
    assert scrape_feed_items[0].get('description') == 'Het laatste nieuws het eerst op NU.nl'
    assert scrape_feed_items[0].get('ttl') == '60'


def test_scrape_feed_get_items(scrape_feed_items):
    assert isinstance(scrape_feed_items[1], list)
    assert len(scrape_feed_items[1]) > 0


def test_scrape_feed_items_does_not_author(scrape_feed_items):
    assert scrape_feed_items[1][0].get('author') is None


def test_items_key(scrape_feed_items):
    new_dict = scrape_feed_items[1][0]
    assert isinstance(new_dict, dict)
    assert 'title' in new_dict.keys()
    assert 'author' in new_dict.keys()
    assert 'description' in new_dict.keys()
    assert 'category' in new_dict.keys()
    assert 'guid' in new_dict.keys()
    assert 'published_at' in new_dict.keys()


def test_ping_for_feed_new_update(feed):
    feed_, item, updated = ping_for_feed(feed)
    assert feed_.get('last_build_date') > feed.last_build_date
    assert updated is True


def test_update_new_feed(feed, scrape_feed_items):
    update_new_feed(feed, scrape_feed_items[0], scrape_feed_items[1])
    assert feed.last_build_date == scrape_feed_items[0].get('last_build_date')
    assert feed.updated_at.date() == date.today()


def test_ping_for_feed_no_new_update(feed):
    print("I got here now ..............")
    current_date_time = datetime.datetime.now(tz=pytz.timezone('UTC')) + datetime.timedelta(hours=1)
    feed.last_build_date = current_date_time
    feed_, item, updated = ping_for_feed(feed)
    print(feed.last_build_date, feed_.get('last_build_date'), "***************")
    assert feed_.get('last_build_date') < feed.last_build_date
    assert updated is False
    assert feed_ is not None
    assert isinstance(item, list)
