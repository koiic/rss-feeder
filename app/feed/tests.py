import datetime

import faker
from django.test import TestCase

# Create your tests here.
import pytest

from feed.models import Feed
from user.models import User


@pytest.mark.django_db
def test_feed_create():
    user = User.objects.create_user('lennon@thebeatles.com', 'johnpassword')
    Feed.objects.create({
        "title": "Nu-Algomeen",
        "description": "New dily rss feed",
        "link": "",
        "registered_by": user,
        "last_build_date": datetime.datetime.now(),
        "ttl": 60,
        "name": "test_feed"
    })

    assert Feed.objects.count() == 1
