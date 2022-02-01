from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
import pytest

from feed.models import Feed, Item, Followers

User = get_user_model()


@pytest.mark.django_db(True)
def test_user_create(user):
    exist_user = User.objects.all()
    assert exist_user.count() == 1
    assert exist_user.filter(email=user.email)


@pytest.mark.django_db(True)
def test_feed_create(feed):
    exist_feed = Feed.objects.all()
    assert exist_feed.count() == 1
    assert exist_feed.filter(name__exact=feed.name)


@pytest.mark.django_db(True)
def test_item_exist(item, feed):
    assert Item.objects.count() == 1
    assert Item.objects.filter(title=item.title).exists()
