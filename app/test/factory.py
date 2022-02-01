import datetime

import pytz
from django.contrib.auth import get_user_model

import factory

from feed.models import Feed, Item, Followers


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Faker("email")
    password = 'password'
    firstname = factory.Faker("first_name")
    lastname = factory.Faker("last_name")


class FeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feed

    registered_by = factory.SubFactory(UserFactory)
    title = factory.Faker("name")
    description = factory.Faker("sentence")
    link = "http://www.nu.nl/rss/Algemeen"
    last_build_date = factory.Faker("date_time", tzinfo=pytz.timezone('UTC'))
    ttl = 60
    name = factory.Faker("name")


class FeedFactoryNoUser(factory.django.DjangoModelFactory):
    class Meta:
        model = Feed

    title = factory.Faker("name")
    description = factory.Faker("sentence")
    link = "http://www.nu.nl/rss/Algemeen"
    last_build_date = factory.Faker("date_time", tzinfo=pytz.timezone('UTC'))
    ttl = 60
    name = factory.Faker("name")


class CreateNewFeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feed
    link = "http://www.nu.nl/rss/Algemeen"
    name = factory.Faker("name")


class CreateNewFeedFactoryInvalid(factory.django.DjangoModelFactory):
    class Meta:
        model = Feed
    link = factory.Faker("image_url")
    name = factory.Faker("name")


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    title = factory.Faker("name")
    description = factory.Faker("sentence")
    link = factory.Faker("image_url")
    author = factory.Faker("name")
    guid = factory.Faker("image_url")
    category = factory.Faker("name")
    comments_url = factory.Faker("image_url")
    published_at = factory.Faker("date_time", tzinfo=pytz.timezone('UTC'))
    feed = factory.SubFactory(FeedFactory)


class FollowerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Followers

    feed = factory.SubFactory(FeedFactory)
    user = factory.SubFactory(UserFactory)




