import datetime

import faker
from django.test import TestCase

# Create your tests here.
import pytest

from user.models import User
from feed.models import Feed


class FeedTestCase(TestCase):
    def setUp(self):
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

    def test_feed_is_registered(self):
        """Animals that can speak are correctly identified"""
        user = User.objects.get(email="lennon@thebeatles.com")
        feed = Feed.objects.get(name="test_feed")
        self.assertEqual(feed.name, 'test_feed')
        self.assertEqual(feed.title, 'Nu-Algomeen')

# @pytest.mark.django_db
# def test_feed_create():
#     user = User.objects.create_user('lennon@thebeatles.com', 'johnpassword')
#     Feed.objects.create({
#         "title": "Nu-Algomeen",
#         "description": "New dily rss feed",
#         "link": "",
#         "registered_by": user,
#         "last_build_date": datetime.datetime.now(),
#         "ttl": 60,
#         "name": "test_feed"
#     })
#
#     assert Feed.objects.count() == 1
