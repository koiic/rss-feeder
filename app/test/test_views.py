import json

import pytest

import factory

from core.messages import messages
from test.factory import FeedFactory, FeedFactoryNoUser, CreateNewFeedFactoryInvalid

pytestmark = pytest.mark.django_db


class TestFeedEndpoints:
    endpoint = '/api/v1/feeds/'

    def test_list(self, api_client, user):
        client = api_client()
        FeedFactory.create_batch(3)
        response = client.get(self.endpoint)
        content = response.content.decode(response.charset)
        assert 'title' in content
        assert response.status_code == 200

    def test_create(self, api_client, user):
        client = api_client()
        url = self.endpoint
        valid_serializer_data = factory.build(
            dict,
            FACTORY_CLASS=FeedFactoryNoUser
        )
        client.force_authenticate(user=user)
        response = client.post(url, valid_serializer_data, format='json')

        assert response.status_code == 201
        assert response.data['success'] is True
        assert response.data['message'] == messages['OK'].format('Feed')

    def test_create_raise_exception(self, api_client, user):
        client = api_client()
        url = self.endpoint
        valid_serializer_data = {
            "link":"'http://www.nu/Algemeen'",
            "name":"testlink"
        }
        client.force_authenticate(user=user)
        response = client.post(url, valid_serializer_data, format='json')
        assert response.status_code == 500
        assert response.data['success'] is False



