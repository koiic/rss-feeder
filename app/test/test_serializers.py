import factory
import pytest
from django.core.exceptions import ValidationError

from feed.serializers import FeedSerializer, ItemSerializer, FollowerSerializer
from test.factory import FeedFactory, ItemFactory, FollowerFactory, UserFactory
from user.serializers import CreateUserSerializer, CustomObtainTokenPairSerializer

pytestmark = pytest.mark.django_db


class TestFeedSerializer:

    def test_serializer_model(self):
        feed = FeedFactory.build()
        serializer = FeedSerializer(feed)

        assert serializer.data

    def test_serialized_data(self):
        valid_serializer_data = factory.build(
            dict,
            FACTORY_CLASS=FeedFactory
        )

        serializer = FeedSerializer(data=valid_serializer_data)
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestItemSerializer:

    def test_serializer_model(self):
        feed = ItemFactory.build()
        serializer = ItemSerializer(feed)

        assert serializer.data

    @pytest.mark.django_db
    def test_serialized_data(self):
        valid_serializer_data = factory.build(
            dict,
            FACTORY_CLASS=ItemFactory
        )

        serializer = ItemSerializer(data=valid_serializer_data)
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestFollowSerializer:

    def test_serializer_model(self):
        follower = FollowerFactory.build()
        serializer = FollowerSerializer(follower)

        assert serializer.data

    def test_serialized_data(self):
        valid_serializer_data = factory.build(
            dict,
            FACTORY_CLASS=FollowerFactory
        )

        serializer = FollowerSerializer(data=valid_serializer_data)
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestUserSerializer:

    def test_serializer_model(self):
        user = UserFactory.build()
        serializer = CreateUserSerializer(user)

        assert serializer.data

    def test_serialized_data(self):
        valid_serializer_data = factory.build(
            dict,
            FACTORY_CLASS=UserFactory
        )

        serializer = CreateUserSerializer(data=valid_serializer_data)
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestAuthSerializer:

    def test_serializer_model(self):
        user = UserFactory.build()
        serializer = CustomObtainTokenPairSerializer(user)

        assert serializer.data
