import pytest

from core import settings
from feed.models import Feed, Item, Followers
from feed.utils import scrape_feed
from test.factory import UserFactory, FeedFactory, ItemFactory, FollowerFactory
from rest_framework.test import APIClient, APIRequestFactory


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def feed() -> Feed:
    return FeedFactory()


@pytest.fixture
def item() -> Item:
    return ItemFactory()


@pytest.fixture
def follow() -> Followers:
    return FollowerFactory()


@pytest.fixture(scope='class')
def scrape_feed_items() -> tuple:
    return scrape_feed('http://www.nu.nl/rss/Algemeen')


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': "redis://localhost:6379",
        'result_backend': "redis://localhost:6379",
        'task_always_eager': True
    }


@pytest.fixture(scope='session')
def api_client():
    return APIClient

