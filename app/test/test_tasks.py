# from unittest.mock import patch
#
# import pytest
# from feed.models import Feed
# from feed.tasks import scrape_new_feed_task
# from test.factory import FeedFactory
#
# pytestmark = pytest.mark.django_db
#
#
# @pytest.mark.usefixtures('celery_session_app')
# @pytest.mark.usefixtures('celery_session_worker')
# class TestCeleryTask:
#     def test_scrape_feed(self):
#         scrape_new_feed_task()
#
#     @patch('feed.utils.ping_for_feed')
#     def test_ping_for_feed_success(self, ping_feed):
#         feeds = FeedFactory.create_batch(2)
#         scrape_new_feed_task()
#         # assert len(ping_feed.mock_calls) > 1
#         assert ping_feed.assert_called_with(feeds[0])
#
#
#     @patch('feed.utils.update_new_feed')
#     def test_called_update_new_feed_succeeds(self, function_mock):
#         scrape_new_feed_task()
#         function_mock.assert_any_call()
