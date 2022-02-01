import uuid
from unittest import mock
from unittest.mock import patch, Mock
#
from uuid import UUID

import pytest
from _pytest.python_api import raises
from celery.exceptions import Retry
from feed.tasks import scrape_new_feed_task, scrape_single_user_feed_update
from test.factory import FeedFactory

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
class TestCeleryTask:
    def test_scrape_feed(self):
        scrape_new_feed_task()

    def test_single_user_feeds(self, feed):
        scrape_single_user_feed_update.delay(feed.id)

    def test_do_sth(self, feed):
        mock_task = Mock()
        mock_task.feed.id = feed.id  # your test data here
        feed_id = feed.id  # more test data
        some_task_inner = scrape_new_feed_task.__wrapped__.__func__
        some_task_inner(mock_task)


    def test_fetch_data(self):
        task = scrape_new_feed_task.s().delay()
        result = task.get()
        assert (task.status, 'SUCCESS')

    @patch('feed.tasks.send_fail_notification')
    def test_send_failed_notification(self, feed):
        """Ensure the task runs in Celery and calls the correct function."""
        task = scrape_single_user_feed_update.s(feed.id).apply()
        assert (task.result, 'SUCCESS')

    @patch('feed.utils.ping_for_feed')
    @patch('feed.tasks.scrape_single_user_feed_update.retry')
    def test_failure(self, scrape_single_user_feed_update_retry, ping_feed, feed):
        # Set a side effect on the patched methods
        # so that they raise the errors we want.
        scrape_single_user_feed_update_retry.side_effect = Retry()
        with raises(Retry):
            scrape_single_user_feed_update(str(uuid.uuid4()))
